import fcntl
import os
import pty
import select
import struct
import termios

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView


class TerminalBridge(QObject):
    """Bridge for bidirectional communication between JS (xterm.js) and Python (PTY)."""

    input_received = Signal(str)
    resized = Signal(int, int)
    ready = Signal(int, int)

    @Slot(str)
    def send_input(self, data):
        self.input_received.emit(data)

    @Slot(int, int)
    def resize_pty(self, cols, rows):
        self.resized.emit(cols, rows)

    @Slot(int, int)
    def terminal_ready(self, cols, rows):
        self.ready.emit(cols, rows)


class PtyReaderThread(QThread):
    """Background thread to read stdout/stderr from PTY master and signal it."""

    output_received = Signal(str)

    def __init__(self, fd):
        super().__init__()
        self.fd = fd
        self.running = True

    def run(self):
        while self.running:
            try:
                # Poll PTY file descriptor for incoming data
                r, _, _ = select.select([self.fd], [], [], 0.1)
                if self.fd in r:
                    data = os.read(self.fd, 4096)
                    if not data:
                        break
                    # Send decoded output to main GUI thread
                    self.output_received.emit(data.decode("utf-8", errors="replace"))
            except (OSError, ValueError):
                break

    def stop(self):
        self.running = False
        self.wait()


class TerminalWidget(QWebEngineView):
    """Embedded interactive terminal utilizing xterm.js inside QtWebEngine."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fd = None
        self.child_pid = None
        self.reader_thread = None
        self.bridge = TerminalBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.page().setWebChannel(self.channel)

        # Wire signals
        self.bridge.input_received.connect(self.write_to_pty)
        self.bridge.resized.connect(self.resize_pty)
        self.bridge.ready.connect(self.on_terminal_ready)

        # Set up our minimalist HTML layout loading xterm.js
        self.html_content = """<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css" />
    <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: #121214;
            overflow: hidden;
        }
        #terminal {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <script>
        var term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#121214',
                foreground: '#F5F5F7',
                cursor: '#7C4DFF',
                black: '#1E1E24',
                red: '#FF5252',
                green: '#00E676',
                yellow: '#FFD740',
                blue: '#448AFF',
                magenta: '#7C4DFF',
                cyan: '#00E5FF',
                white: '#FFFFFF'
            },
            fontFamily: '"Cascadia Code", "Fira Code", "Courier New", monospace',
            fontSize: 14
        });
        var fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);
        term.open(document.getElementById('terminal'));
        fitAddon.fit();

        window.addEventListener('resize', function() {
            fitAddon.fit();
            if (window.bridge) {
                window.bridge.resize_pty(term.cols, term.rows);
            }
        });

        // Initialize QWebChannel
        new QWebChannel(qt.webChannelTransport, function (channel) {
            window.bridge = channel.objects.bridge;

            term.onData(function (data) {
                window.bridge.send_input(data);
            });

            window.bridge.terminal_ready(term.cols, term.rows);
        });

        function writeData(data) {
            term.write(data);
        }
    </script>
</body>
</html>
"""
        self.setHtml(self.html_content)

    def start_shell(self, cmd=None, args=None):
        """Fork a new PTY shell and launch the requested process command."""
        if cmd is None:
            cmd = "/bin/bash"
        if args is None:
            args = []

        # Fork PTY
        self.child_pid, self.fd = pty.fork()
        if self.child_pid == 0:
            # Child process: replace with specified command
            os.environ["TERM"] = "xterm-256color"
            try:
                os.execvp(cmd, [cmd] + args)
            except Exception as e:
                print(f"Failed to exec {cmd}: {e}")
                os._exit(1)
        else:
            # Parent process: set non-blocking and start background PTY reader thread
            fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            self.reader_thread = PtyReaderThread(self.fd)
            self.reader_thread.output_received.connect(self.write_to_xterm)
            self.reader_thread.start()

    @Slot(str)
    def write_to_xterm(self, text):
        # Escape backslashes and single quotes to prevent JS execution breaks
        escaped = (
            text.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )
        self.page().runJavaScript(f"writeData('{escaped}');")

    @Slot(str)
    def write_to_pty(self, text):
        if self.fd is not None:
            try:
                os.write(self.fd, text.encode("utf-8"))
            except OSError:
                pass

    @Slot(int, int)
    def resize_pty(self, cols, rows):
        if self.fd is not None:
            try:
                # Set PTY window size using ioctl
                s = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self.fd, termios.TIOCSWINSZ, s)
            except OSError:
                pass

    @Slot(int, int)
    def on_terminal_ready(self, cols, rows):
        # Resize PTY immediately
        self.resize_pty(cols, rows)

    def closeEvent(self, event):
        if self.reader_thread:
            self.reader_thread.stop()
        if self.child_pid:
            try:
                os.kill(self.child_pid, 9)
            except OSError:
                pass
        super().closeEvent(event)

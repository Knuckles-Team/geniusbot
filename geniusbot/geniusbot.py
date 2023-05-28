#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pkg_resources


def check_package(package="None"):
    found = False
    try:
        dist = pkg_resources.get_distribution(package)
        print('{} ({}) is installed'.format(dist.key, dist.version))
        found = True
    except pkg_resources.DistributionNotFound:
        print('{} is NOT installed'.format(package))
    return found


import os
import sys
import pandas as pd
from pathlib import Path
webarchiver_installed = check_package("webarchiver")
subshift_installed = check_package("subshift")
media_downloader_installed = check_package("media-downloader")
media_manager_installed = check_package("media-manager")
report_manager_installed = check_package("report-manager")
repository_manager_installed = check_package("repository-manager")
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QHBoxLayout, QCheckBox
)
from PyQt5.QtCore import QObject, pyqtSignal
from version import __version__, __author__, __credits__
from qt.scrollable_widget import ScrollLabel
from plugins.geniusbot_chat_plugin import GeniusBotChatTab
from plugins.systems_manager_plugin import SystemsManagerTab
if subshift_installed:
    from plugins.subshift_plugin import SubshiftTab
if webarchiver_installed:
    from plugins.webarchiver_plugin import WebarchiverTab
if media_downloader_installed:
    from plugins.media_downloader_plugin import MediaDownloaderTab
if media_manager_installed:
    from plugins.media_manager_plugin import MediaManagerTab
if report_manager_installed:
    from plugins.report_manager_plugin import ReportManagerTab
if repository_manager_installed:
    from plugins.repository_manager_plugin import RepositoryManagerTab


if os.name == "posix":
    import pwd
    user = pwd.getpwuid(os.geteuid()).pw_name
else:
    ukn = 'UNKNOWN'
    user = os.environ.get('USER', os.environ.get('USERNAME', ukn))
    if user == ukn and hasattr(os, 'getlogin'):
        user = os.getlogin()

if sys.platform == 'win32':
    import winshell
    import ctypes

    myappid = f'knucklesteam.geniusbot.geniusbot.{__version__}'  # arbitrary string
    myappid.encode("utf-8")
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

pd.set_option('display.max_rows', 250)
pd.set_option('display.max_columns', 9)
pd.set_option('display.expand_frame_repr', False)


class OutputWrapper(QObject):
    outputWritten = pyqtSignal(object, object)

    def __init__(self, parent, stdout=True):
        super().__init__(parent)
        if stdout:
            self._stream = sys.stdout
            sys.stdout = self
        else:
            self._stream = sys.stderr
            sys.stderr = self
        self._stdout = stdout

    def write(self, text):
        self._stream.write(text)
        self.outputWritten.emit(text, self._stdout)

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def __del__(self):
        try:
            if self._stdout:
                sys.stdout = self._stream
            else:
                sys.stderr = self._stream
        except AttributeError:
            pass


class GeniusBot(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repository_manager = None
        self.report_manager = None
        self.webarchiver = None
        self.media_manager = None
        self.video_downloader = None
        self.systems_manager = None
        self.hide_console_button = None
        self.buttonsWidgetLayout = None
        self.buttonsWidget = None
        self.centralWidget = None
        self.settings_tab = None
        self.repository_manager_tab = None
        self.report_manager_tab = None
        self.subshift_tab = None
        self.webarchiver_tab = None
        self.media_manager_tab = None
        self.media_downloader_tab = None
        self.geniusbot_chat_tab = None
        self.systems_manager_tab = None
        self.tab_widget = None
        self.repository_links_editor = None
        self.geniusbot_chatbot = None
        self.web_links_label = None
        self.web_links_editor = None
        self.archive_button = None
        self.open_webfile_button = None
        self.open_webfile_label = None
        self.save_web_location_button = None
        self.save_web_location_label = None
        self.web_dpi_label = None
        self.web_dpi_spin_box = None
        self.web_file_type_label = None
        self.web_links_file_type = None
        self.web_zoom_label = None
        self.web_zoom_spin_box = None
        self.web_progress_bar = None
        self.file_type_combobox = None
        self.chattybot_response = None
        self.systems_manager = None
        self.systems_manager_tab = None
        self.install_app_ticker = None
        self.install_python_ticker = None
        self.enable_windows_features_ticker = None
        self.install_theme_ticker = None
        self.install_font_ticker = None
        self.update_ticker = None
        self.clean_ticker = None
        self.silent_ticker = None
        self.theme_combobox = None
        self.font_combobox = None
        self.systems_manager_run_button = None
        self.application_install_edit = None
        self.python_module_install_edit = None
        self.enable_windows_feature_edit = None
        self.enable_windows_feature_list = None
        self.application_install_list = None
        self.webarchiver_installed = check_package("webarchiver")
        self.subshift_installed = check_package("subshift")
        self.media_downloader_installed = check_package("media-downloader")
        self.media_manager_installed = check_package("media-manager")
        self.report_manager_installed = check_package("report-manager")
        self.repository_manager_installed = check_package("repository-manager")
        self.initialize_user_interface()

    def initialize_user_interface(self):
        self.setWindowTitle(f"Genius Bot")
        self.setWindowIcon(QIcon(f'{os.path.dirname(os.path.realpath(__file__))}/img/geniusbot.ico'))
        self.setStyleSheet("background-color: #bfc3c9;")
        self.resize(900, 640)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("background-color: #f5f5f5;")

        GeniusBotChatTab(self.tab_widget)
        if media_downloader_installed:
            MediaDownloaderTab(self.tab_widget)
        if media_manager_installed:
            MediaManagerTab(self.tab_widget)
        if webarchiver_installed:
            WebarchiverTab(self.tab_widget)
        if subshift_installed:
            SubshiftTab(self.tab_widget)
        if report_manager_installed:
            ReportManagerTab(self.tab_widget)
        if repository_manager_installed:
            RepositoryManagerTab(self.tab_widget)
        SystemsManagerTab(self.tab_widget)
        self.settings_tab = QWidget()
        self.tab_widget.addTab(self.settings_tab, "⚙")
        self.settings_tab_settings()
        # Set the main gui layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.buttonsWidget = QWidget()
        self.buttonsWidgetLayout = QHBoxLayout(self.buttonsWidget)
        self.hide_console_button = QPushButton("Console ◳")
        self.hide_console_button.setStyleSheet("background-color: #211f1f; color: white; font: bold;")
        self.hide_console_button.clicked.connect(self.hide_console)
        self.buttonsWidgetLayout.addWidget(self.hide_console_button)
        self.buttonsWidgetLayout.setStretch(0, 24)
        self.buttonsWidgetLayout.setStretch(1, 1)
        self.buttonsWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.console = ScrollLabel(self)
        self.console.setScrollWheel(location="Bottom")
        self.console.setText(f"[Genius Bot] Version: {__version__}\n[Genius Bot] Console Output of Running Tasks\n")
        stdout = OutputWrapper(self, True)
        stdout.outputWritten.connect(self.console_output)
        stderr = OutputWrapper(self, False)
        stderr.outputWritten.connect(self.console_output)
        layout.addWidget(self.buttonsWidget)
        layout.addWidget(self.console)
        layout.setStretch(0, 24)
        layout.setStretch(1, 1)
        layout.setStretch(2, 3)
        self.centralWidget.setLayout(layout)


    def settings_tab_settings(self):
        layout = QHBoxLayout()
        self.desktop_icon_checkbox = QCheckBox("Create Desktop Icon")
        self.desktop_icon_checkbox.stateChanged.connect(self.create_desktop_icon)
        layout.addWidget(self.desktop_icon_checkbox)
        self.tab_widget.setTabText(100, "⚙")
        self.settings_tab.setLayout(layout)

    def create_desktop_icon(self):
        desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        script_parent_dir = Path(__file__).parent.absolute().parent.absolute()
        icon = str(script_parent_dir / "geniusbot" / "img" / "geniusbot.ico")
        working_directory = str(Path(script_parent_dir))
        if sys.platform == 'win32':
            win32_cmd = str(Path(winshell.folder('CSIDL_SYSTEM')) / 'cmd.exe')
            link_filepath = str(desktop + "/Genius Bot.lnk")
            arg_str = "/K " + str("geniusbot")
            if self.desktop_icon_checkbox.isChecked():
                with winshell.shortcut(link_filepath) as link:
                    link.path = win32_cmd
                    link.description = "Genius Bot"
                    link.arguments = arg_str
                    link.icon_location = (icon, 0)
                    link.working_directory = working_directory
                    print("Desktop Shortcut Created!")
            else:
                os.remove(link_filepath)
        elif sys.platform == 'linux':
            desktop_link_filepath = str(f"{desktop}/Genius Bot.desktop")
            link_filepath = os.path.join(os.path.join(os.path.expanduser('~')),
                                         '.local/share/applications/Genius Bot.desktop')
            if self.desktop_icon_checkbox.isChecked():
                with open(link_filepath, "w") as desktop_icon:
                    desktop_icon.write(
                        f"[Desktop Entry]\n"
                        f"Version={__version__}\n"
                        f"Name=Genius Bot\n"
                        f"Comment=Genius Bot\n"
                        f"Exec=geniusbot\n"
                        f"Icon={icon}\n"
                        f"Path={working_directory}\n"
                        f"Terminal=false\n"
                        f"Type=Application\n"
                        f"Categories=Utility;Application;\n"
                    )
                    with open(desktop_link_filepath, "w") as desktop_icon:
                        desktop_icon.write(
                            f"[Desktop Entry]\n"
                            f"Version={__version__}\n"
                            f"Name=Genius Bot\n"
                            f"Comment=Genius Bot\n"
                            f"Exec=geniusbot\n"
                            f"Icon={icon}\n"
                            f"Path={working_directory}\n"
                            f"Terminal=false\n"
                            f"Type=Application\n"
                            f"Categories=Utility;Application;\n"
                        )
                print("Desktop Shortcut Created!")
            else:
                os.remove(link_filepath)
                os.remove(desktop_link_filepath)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.chat_editor:
            if event.key() == Qt.Key_Return and self.chat_editor.hasFocus():
                self.chat_editor.setDisabled(True)
                self.chattybot_response()
        return super().eventFilter(obj, event)

    def console_output(self, text):
        self.console.setText(f"{self.console.text().strip()}\n{text.strip()}")

    def hide_console(self):
        if self.hide_console_button.text() == "Console ◳":
            self.hide_console_button.setText("Console _")
        else:
            self.hide_console_button.setText("Console ◳")
        self.console.hide()


def geniusbot(argv):
    app = QApplication(sys.argv)
    bot_window = GeniusBot()
    bot_window.show()
    sys.exit(app.exec())


def main():
    geniusbot(sys.argv[1:])


if __name__ == "__main__":
    geniusbot(sys.argv[1:])

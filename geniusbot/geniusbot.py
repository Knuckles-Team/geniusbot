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
import plugins
from pathlib import Path

webarchiver_installed = check_package("webarchiver")
subshift_installed = check_package("subshift")
media_downloader_installed = check_package("media-downloader")
media_manager_installed = check_package("media-manager")
report_manager_installed = check_package("report-manager")
repository_manager_installed = check_package("repository-manager")
# webarchiver_installed = False
# media_downloader_installed = False
# media_manager_installed = False
# report_manager_installed = False
# repository_manager_installed = False
from genius_chatbot import ChatBot
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QHBoxLayout, QCheckBox, QFileDialog, QTextEdit
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal

try:
    from version import __version__, __author__, __credits__
except Exception as e:
    print(f"Unable to import version\nError: {e}")
from qt.colors import yellow, green, orange, blue, red, purple
try:
    from qt.scrollable_widget import ScrollLabel
except Exception as e:
    print(f"Unable to import custom Scroll Label\nError: {e}")

try:
    from plugins.geniusbot_chat_plugin import GeniusBotWorker
except Exception as e:
    print(f"Geniusbot Chat Installed, however, we encountered an issue importing the module\nError: {e}")
if subshift_installed:
    print("Checking if subshift is installed first pass")
    from plugins.subshift_plugin import SubshiftWorker
if webarchiver_installed:
    from webarchiver import Webarchiver
    from plugins.webarchiver_plugin import WebarchiverWorker, webarchiver_tab
if media_downloader_installed:
    from media_downloader import MediaDownloader
    from plugins.media_downloader_plugin import MediaDownloaderWorker, media_downloader_tab
if media_manager_installed:
    from media_manager import MediaManager
    from plugins.media_manager_plugin import MediaManagerWorker, media_manager_tab
if report_manager_installed:
    from report_manager import ReportManager
    from plugins.report_manager_plugin import MergeReportWorker, ReportManagerWorker, report_manager_tab
if repository_manager_installed:
    from repository_manager import Git
    from plugins.repository_manager_plugin import RepositoryManagerWorker, repository_manager_tab
from systems_manager import SystemsManager
from plugins.systems_manager_plugin import SystemsManagerWorker, systems_manager_tab

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
        self.hide_console_button = None
        self.buttonsWidgetLayout = None
        self.buttonsWidget = None
        self.centralWidget = None
        self.tab8 = None
        self.tab7 = None
        self.tab6 = None
        self.tab5 = None
        self.tab4 = None
        self.tab3 = None
        self.tab2 = None
        self.tab1 = None
        self.tab_widget = None
        self.repository_links_editor = None
        self.geniusbot_chatbot = ChatBot()
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
        self.initialize_user_interface()

    def initialize_user_interface(self):
        self.setWindowTitle(f"Genius Bot")
        self.setWindowIcon(QIcon(f'{os.path.dirname(os.path.realpath(__file__))}/img/geniusbot.ico'))
        self.setStyleSheet("background-color: #bfc3c9;")
        self.resize(800, 640)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("background-color: #f5f5f5;")

        self.tab1 = QWidget()
        self.tab8 = QWidget()
        self.tab_widget.addTab(self.tab1, "Tab 1")
        self.tab1_home()

        if media_downloader_installed:
            self.video_downloader = MediaDownloader()
            self.tab2 = QWidget()
            self.tab_widget.addTab(self.tab2, "Tab 2")
            media_downloader_tab(self)
        if media_manager_installed:
            self.media_manager = MediaManager()
            self.tab3 = QWidget()
            self.tab_widget.addTab(self.tab3, "Tab 3")
            media_manager_tab(self)
        if webarchiver_installed:
            self.webarchiver = Webarchiver()
            self.tab4 = QWidget()
            self.tab_widget.addTab(self.tab4, "Tab 4")
            plugins.webarchiver_plugin.webarchiver_tab(self)
        if subshift_installed:
            self.tab5 = QWidget()
            self.tab_widget.addTab(self.tab5, "Tab 5")
            plugins.subshift_plugin.subshift_tab(self)
        if report_manager_installed:
            self.report_manager = ReportManager()
            self.tab6 = QWidget()
            self.tab_widget.addTab(self.tab6, "Tab 6")
            report_manager_tab(self)
        if repository_manager_installed:
            self.repository_manager = Git()
            self.tab7 = QWidget()
            self.tab_widget.addTab(self.tab7, "Tab 7")
            repository_manager_tab(self)

        self.tab_widget.addTab(self.tab8, "Tab 8")
        self.tab8_settings()
        # Set the main gui layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.buttonsWidget = QWidget()
        self.buttonsWidgetLayout = QHBoxLayout(self.buttonsWidget)
        # self.console_label = QLabel("Console")
        self.hide_console_button = QPushButton("Console ◳")
        self.hide_console_button.setStyleSheet("background-color: #211f1f; color: white; font: bold;")
        self.hide_console_button.clicked.connect(self.hide_console)
        # self.buttonsWidgetLayout.addWidget(self.console_label)
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

    def tab1_home(self):
        self.geniusbot_chat = ScrollLabel(self)
        self.geniusbot_chat.hide()
        self.geniusbot_chat.setFontColor(background_color="white", color="black")
        self.geniusbot_chat.setText(
            f"""[Genius Bot] ZzzzZzzz... (It appears Genius Bot is sleeping, click "Wake Up!")""")
        self.chat_editor = QTextEdit()
        self.chat_editor.installEventFilter(self)
        self.geniusbot_send_button = QPushButton("Wake Up!")
        self.geniusbot_send_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.geniusbot_send_button.clicked.connect(self.chattybot_response)
        self.chat_editor.setDisabled(False)
        layout = QVBoxLayout()
        layout.addWidget(self.geniusbot_chat)
        layout.addWidget(self.chat_editor)
        layout.addWidget(self.geniusbot_send_button)
        layout.setStretch(0, 24)
        layout.setStretch(1, 3)
        layout.setStretch(2, 1)
        self.tab_widget.setTabText(0, "Genius Bot Chat")
        self.tab1.setLayout(layout)

    def tab8_settings(self):
        layout = QHBoxLayout()
        self.desktop_icon_checkbox = QCheckBox("Create Desktop Icon")
        self.desktop_icon_checkbox.stateChanged.connect(self.create_desktop_icon)
        layout.addWidget(self.desktop_icon_checkbox)
        self.tab_widget.setTabText(7, "⚙")
        self.tab8.setLayout(layout)

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
            # print(f"Desktop: {desktop}\nScript Parent Directory: {script_parent_dir}\nwin32 Command: {win32_cmd}\nIcon: {icon}\nWorking Path: {working_directory}\nLink Path {link_filepath}\nArgs: {arg_str}")
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

    def report_manage(self):
        self.report_manager_thread = QThread()
        self.report_manager_worker = ReportManagerWorker(self.report_manager, self.report_name_editor,
                                                         self.custom_report_generate_label, self.action_type_combobox,
                                                         self.pandas_profiling_ticker, self.custom_report_ticker,
                                                         self.file_type_combobox)
        self.report_manager_worker.moveToThread(self.report_manager_thread)
        self.report_manager_thread.started.connect(self.report_manager_worker.run)
        self.report_manager_worker.finished.connect(self.report_manager_thread.quit)
        self.report_manager_worker.finished.connect(self.report_manager_worker.deleteLater)
        self.report_manager_thread.finished.connect(self.report_manager_thread.deleteLater)
        self.report_manager_worker.progress.connect(self.report_web_progress_bar)
        self.report_manager_thread.start()
        self.custom_report_generate_button.setEnabled(False)
        self.report_manager_thread.finished.connect(
            lambda: self.custom_report_generate_button.setEnabled(True)
        )
        self.report_manager_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Reporting Management Completed!\n")
        )

    def merge_reports(self):
        self.merge_report_thread = QThread()
        self.merge_report_worker = MergeReportWorker(self.report_manager, self.file1_columns, self.file2_columns,
                                                     self.action_type_combobox, self.merge_type_combobox,
                                                     self.merged_report_save_location_label, self.merge_file1_label,
                                                     self.merge_file2_label, self.merged_report_name_editor,
                                                     self.merge_file_type_combobox)
        self.merge_report_worker.moveToThread(self.merge_report_thread)
        self.merge_report_thread.started.connect(self.merge_report_worker.run)
        self.merge_report_worker.finished.connect(self.merge_report_thread.quit)
        self.merge_report_worker.finished.connect(self.merge_report_worker.deleteLater)
        self.merge_report_thread.finished.connect(self.merge_report_thread.deleteLater)
        self.merge_report_worker.progress.connect(self.report_web_progress_bar)
        self.merge_report_thread.start()
        self.merge_button.setEnabled(False)
        self.merge_report_thread.finished.connect(
            lambda: self.merge_button.setEnabled(True)
        )
        self.merge_report_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Reporting Merging Completed!\n")
        )

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.chat_editor:
            if event.key() == Qt.Key_Return and self.chat_editor.hasFocus():
                self.chat_editor.setDisabled(True)
                self.chattybot_response()
        return super().eventFilter(obj, event)

    def chattybot_response(self):
        # self.geniusbot_send_button.setEnabled(False)
        self.geniusbot_send_button.setText("Send")
        text = str(self.chat_editor.toPlainText().strip())
        self.geniusbot_chat.setText(f"""{self.geniusbot_chat.text()}\n[{user}] {text}""")
        self.chat_editor.setText("")
        self.geniusbot_thread = QThread()
        self.geniusbot_worker = GeniusBotWorker(geniusbot_chatbot=self.geniusbot_chatbot,
                                                geniusbot_chat=self.geniusbot_chat,
                                                text=text)
        self.geniusbot_worker.moveToThread(self.geniusbot_thread)
        self.geniusbot_thread.started.connect(self.geniusbot_worker.run)
        self.geniusbot_worker.finished.connect(self.geniusbot_thread.quit)
        self.geniusbot_worker.finished.connect(self.geniusbot_worker.deleteLater)
        self.geniusbot_thread.finished.connect(self.geniusbot_thread.deleteLater)
        self.geniusbot_thread.finished.connect(lambda: self.geniusbot_send_button.setDisabled(False))
        self.geniusbot_thread.finished.connect(lambda: self.chat_editor.setDisabled(False))
        self.geniusbot_thread.finished.connect(lambda: self.chat_editor.setText(""))
        self.geniusbot_thread.finished.connect(lambda: self.chat_editor.setFocus())
        self.geniusbot_thread.start()

    def console_output(self, text, stdout):
        # color = self.console.textColor()
        # self.console.moveCursor(QTextCursor.End)
        # self.console.setTextColor(color if stdout else self._err_color)
        self.console.setText(f"{self.console.text().strip()}\n{text.strip()}")
        # self.console.setTextColor(color)

    def hide_console(self):
        if self.hide_console_button.text() == "Console ◳":
            self.hide_console_button.setText("Console _")
        else:
            self.hide_console_button.setText("Console ◳")
        self.console.hide()

    def swap_report_layout(self):
        if self.action_type_combobox.currentText() == "Generate Report":
            self.custom_report_widget.show()
            self.merge_widget.hide()
        else:
            self.custom_report_widget.hide()
            self.merge_widget.show()

    def check_subtitle_seconds(self):
        if self.sub_time_spin_box.value() > 0:
            self.shift_subtitle_button.setEnabled(True)
        elif self.sub_time_spin_box.value() == 0:
            self.shift_subtitle_button.setEnabled(False)
        else:
            self.shift_subtitle_button.setEnabled(True)

    def shift_subtitle(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Shifting Subtitles...\n")
        self.subshift_thread = QThread()
        if self.sub_time_spin_box.value() > 0:
            mode = "+"
        else:
            mode = "-"
        time = abs(self.sub_time_spin_box.value())
        self.subshift_worker = SubshiftWorker(self.open_subtitlefile_label.text(), mode, time)
        self.subshift_worker.moveToThread(self.subshift_thread)
        self.subshift_thread.started.connect(self.subshift_worker.run)
        self.subshift_worker.finished.connect(self.subshift_thread.quit)
        self.subshift_worker.finished.connect(self.subshift_worker.deleteLater)
        self.subshift_thread.finished.connect(self.subshift_thread.deleteLater)
        self.subshift_worker.progress.connect(self.report_web_progress_bar)
        self.subshift_thread.start()
        self.shift_subtitle_button.setEnabled(False)
        self.subshift_thread.finished.connect(
            lambda: self.shift_subtitle_button.setEnabled(True)
        )
        self.subshift_thread.finished.connect(
            lambda: self.refresh_subtitlefile()
        )
        self.console.setText(f"[Genius Bot] Subtitle Shift Completed!\n")

    def refresh_subtitlefile(self):
        with open(self.open_subtitlefile_label.text(), 'r') as file:
            self.subtitles = file.read()
        self.subtitles = self.subtitles + self.subtitle_label.text()
        self.subtitles = self.subtitles.strip()
        self.subtitle_label.setText(self.subtitles)

    def open_subtitlefile(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening Subtitle file\n")
        self.subtitle_label.setText("")
        subtitle_file_name = QFileDialog.getOpenFileName(self, 'Subtitle File')
        print(subtitle_file_name[0])
        self.open_subtitlefile_label.setText(subtitle_file_name[0])
        with open(subtitle_file_name[0], 'r') as file:
            self.subtitles = file.read()
        self.subtitles = self.subtitles + self.subtitle_label.text()
        self.subtitles = self.subtitles.strip()
        self.subtitle_label.setText(self.subtitles)

    def report_video_progress_bar(self, n):
        self.video_progress_bar.setValue(n)

    def report_web_progress_bar(self, n):
        self.web_progress_bar.setValue(n)

    def report_repositories_progress_bar(self, n):
        self.repositories_progress_bar.setValue(n)

    def manage_media(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing media...\n")

        if self.subtitle_ticker.isChecked():
            subtitle_boolean = True
        else:
            subtitle_boolean = False

        if self.move_ticker.isChecked():
            move_boolean = True
        else:
            move_boolean = False

        self.media_manager_thread = QThread()
        self.media_manager_worker = MediaManagerWorker(media_manager=self.media_manager,
                                                       directory=self.media_manager_media_location_label.text(),
                                                       move=move_boolean,
                                                       destination=self.media_manager_move_location_label.text(),
                                                       subtitle=subtitle_boolean)
        self.media_manager_worker.moveToThread(self.media_manager_thread)
        self.media_manager_thread.started.connect(self.media_manager_worker.run)
        self.media_manager_worker.finished.connect(self.media_manager_thread.quit)
        self.media_manager_worker.finished.connect(self.media_manager_worker.deleteLater)
        self.media_manager_thread.finished.connect(self.media_manager_thread.deleteLater)
        self.media_manager_thread.start()
        self.media_manager_run_button.setEnabled(False)
        self.media_manager_thread.finished.connect(
            lambda: self.media_manager_run_button.setEnabled(True)
        )
        self.media_manager_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing media complete!\n")
        )
        self.media_manager_thread.finished.connect(
            lambda: self.media_manager_refresh_list()
        )

    def manage_repositories(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing Repositories...\n")
        self.repositories_progress_bar.setValue(1)

        self.repository_manager_thread = QThread()
        # (self, repository_manager, clone_ticker, set_default_branch_ticker, pull_ticker, repository_links_editor, repository_git_command, repository_manager_repositories_file_location_label, repository_manager_files_label, repository_manager_repositories_location_label)
        self.repository_manager_worker = RepositoryManagerWorker(self.repository_manager, self.clone_ticker,
                                                                 self.set_default_branch_ticker, self.pull_ticker,
                                                                 self.repository_links_editor,
                                                                 self.repository_git_command,
                                                                 self.repository_manager_repositories_file_location_label,
                                                                 self.repository_manager_files_label,
                                                                 self.repository_manager_repositories_location_label)
        self.repository_manager_worker.moveToThread(self.repository_manager_thread)
        self.repository_manager_thread.started.connect(self.repository_manager_worker.run)
        self.repository_manager_worker.finished.connect(self.repository_manager_thread.quit)
        self.repository_manager_worker.finished.connect(self.repository_manager_worker.deleteLater)
        self.repository_manager_thread.finished.connect(self.repository_manager_thread.deleteLater)
        self.repository_manager_worker.progress.connect(self.report_repositories_progress_bar)
        self.repository_manager_thread.start()
        self.repository_manager_run_button.setEnabled(False)
        self.repository_manager_thread.finished.connect(
            lambda: self.repository_manager_run_button.setEnabled(True)
        )
        self.repository_manager_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Repository actions complete!\n")
        )

    def open_report_manager_file(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening data!\n")
        report_manager_data_file = QFileDialog.getOpenFileName(self, 'Open data (CSV/XLSX)')
        self.report_manager.set_files(report_manager_data_file[0], "file4")
        self.report_manager.set_files(report_manager_data_file[0], "file1")
        self.report_manager.load_dataframe(file_instance=1)
        self.custom_data_file_label.setText(report_manager_data_file[0])
        dataframe = self.report_manager.get_df()
        dataframe_markdown = dataframe.to_markdown(tablefmt="grid")
        dataframe_html = dataframe.to_html(max_cols=9)

        self.dataframe_label.setText(f"{dataframe_markdown}")

    def open_data1_file(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening data file 1!\n")
        report_manager_data_file = QFileDialog.getOpenFileName(self, 'Open data file 1(CSV/XLSX)')
        self.merge_file1_label.setText(report_manager_data_file[0])
        self.report_manager.set_files(report_manager_data_file[0], "file2")
        self.report_manager.load_dataframe(file_instance=2)
        dataframe = self.report_manager.get_df1()
        self.file1_columns.addItems(dataframe.columns)

    def open_data2_file(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening data file 2!\n")
        report_manager_data_file = QFileDialog.getOpenFileName(self, 'Open data file 2(CSV/XLSX)')
        self.merge_file2_label.setText(report_manager_data_file[0])
        self.report_manager.set_files(report_manager_data_file[0], "file3")
        self.report_manager.load_dataframe(file_instance=3)
        dataframe = self.report_manager.get_df2()
        self.file2_columns.addItems(dataframe.columns)

    def open_repository_manager_file(self, projects=None):
        if projects:
            projects = projects
        else:
            projects = []
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting repositories location to clone and pull!\n")
        repository_manager_file_location_name = QFileDialog.getOpenFileName(self, 'Text File with Repositories')
        if repository_manager_file_location_name[0] == None or repository_manager_file_location_name[0] == "":
            repository_manager_file_location_name = os.path.expanduser("~")
        self.repository_manager_repositories_file_location_label.setText(repository_manager_file_location_name[0])
        if os.path.exists(repository_manager_file_location_name[0]):
            file_repositories = open(repository_manager_file_location_name[0], 'r')
            for repository in file_repositories:
                projects.append(repository)
            projects = list(dict.fromkeys(projects))
        self.repository_manager.set_git_projects(projects)

    def report_manager_save_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting save location for final report!\n")
        report_save_directory = QFileDialog.getExistingDirectory(None, 'Select a folder:', os.path.expanduser("~"),
                                                                 QFileDialog.ShowDirsOnly)
        if report_save_directory == None or report_save_directory == "":
            report_save_directory = os.path.expanduser("~")
        self.custom_report_generate_label.setText(report_save_directory)

    def report_merger_save_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting save location for final report!\n")
        report_save_directory = QFileDialog.getExistingDirectory(None, 'Select a folder:', os.path.expanduser("~"),
                                                                 QFileDialog.ShowDirsOnly)
        if report_save_directory == None or report_save_directory == "":
            report_save_directory = os.path.expanduser("~")
        self.merged_report_save_location_label.setText(report_save_directory)

    def repository_manager_repositories_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting repositories location to clone and pull!\n")
        repository_manager_repositories_location_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                                         os.path.expanduser("~"),
                                                                                         QFileDialog.ShowDirsOnly)
        if repository_manager_repositories_location_name == None or repository_manager_repositories_location_name == "":
            repository_manager_repositories_location_name = os.path.expanduser("~")
        self.repository_manager_repositories_location_label.setText(repository_manager_repositories_location_name)
        self.repository_manager.set_repository_directory(repository_manager_repositories_location_name)
        repositories_string = ""
        for project_directory in os.listdir(repository_manager_repositories_location_name):
            repositories_string = f"{repositories_string}\n{project_directory}"
        self.repository_manager_files_label.setText(f"{repositories_string.lstrip()}")
        # files = ""
        # for file in self.media_manager.get_media_list():
        #     files = f"{files}\n{file}"
        # self.media_manager_files_label.setText(files.strip())

    def download_videos(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Downloading videos...\n")
        self.video_progress_bar.setValue(1)
        videos = self.video_links_editor.toPlainText()
        videos = videos.strip()
        videos = videos.split('\n')

        if videos[0] != '':
            if self.video_type_combobox.currentText() == "Audio":
                audio_boolean = True
            else:
                audio_boolean = False
            self.video_thread = QThread()
            self.video_worker = MediaDownloaderWorker(self.video_downloader, videos, audio_boolean)
            self.video_worker.moveToThread(self.video_thread)
            self.video_thread.started.connect(self.video_worker.run)
            self.video_worker.finished.connect(self.video_thread.quit)
            self.video_worker.finished.connect(self.video_worker.deleteLater)
            self.video_thread.finished.connect(self.video_thread.deleteLater)
            self.video_worker.progress.connect(self.report_video_progress_bar)
            self.video_thread.start()
            self.video_download_button.setEnabled(False)
            self.video_thread.finished.connect(
                lambda: self.video_download_button.setEnabled(True)
            )
            self.video_thread.finished.connect(
                lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Videos downloaded!\n")
            )

    def add_channel_videos(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Adding Channel videos\n")
        self.video_downloader.get_channel_videos(self.channel_field_editor.text())
        videos = self.video_links_editor.toPlainText()
        videos = videos.strip()
        videos = videos.split('\n')
        videos = videos + self.video_downloader.get_links()
        videos = '\n'.join(videos)
        self.video_links_editor.setPlainText(videos)

    def open_video_file(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening Video URL file\n")
        video_file_name = QFileDialog.getOpenFileName(self, 'File with Video URL(s)')
        print(video_file_name[0])
        self.video_open_file_label.setText(video_file_name[0])

        with open(video_file_name[0], 'r') as file:
            videos = file.read()
        videos = videos + self.video_links_editor.toPlainText()
        videos = videos.strip()
        self.video_links_editor.setPlainText(videos)

    def media_manager_media_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting media location to look for media in!\n")
        media_manager_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                        os.path.expanduser("~"),
                                                                        QFileDialog.ShowDirsOnly)
        if media_manager_directory_name == None or media_manager_directory_name == "":
            media_manager_directory_name = os.path.expanduser("~")
        self.media_manager_media_location_label.setText(media_manager_directory_name)
        self.media_manager.set_media_directory(media_manager_directory_name)
        self.media_manager.find_media()
        files = ""
        for file in self.media_manager.get_media_list():
            files = f"{files}\n{file}"
        self.media_manager_files_label.setText(files.strip())

    def media_manager_refresh_list(self):
        self.media_manager.set_media_directory(self.media_manager_move_location_label.text())
        self.media_manager.find_media()
        files = ""
        for file in self.media_manager.get_media_list():
            files = f"{files}\n{file}"
        self.media_manager_files_label.setText(files.strip())

    def media_manager_move_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting move location for media\n")
        media_manager_move_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                             os.path.expanduser("~"),
                                                                             QFileDialog.ShowDirsOnly)
        if media_manager_move_directory_name == None or media_manager_move_directory_name == "":
            media_manager_move_directory_name = os.path.expanduser("~")
        self.media_manager_move_location_label.setText(media_manager_move_directory_name)

    def save_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting save location for videos\n")
        video_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', os.path.expanduser("~"),
                                                                QFileDialog.ShowDirsOnly)
        if video_directory_name == None or video_directory_name == "":
            video_directory_name = os.path.expanduser("~")
        self.video_save_location_label.setText(video_directory_name)
        self.video_downloader.set_save_path(video_directory_name)


def geniusbot(argv):
    app = QApplication(sys.argv)
    bot_window = GeniusBot()
    bot_window.show()
    sys.exit(app.exec())


def main():
    geniusbot(sys.argv[1:])


if __name__ == "__main__":
    geniusbot(sys.argv[1:])

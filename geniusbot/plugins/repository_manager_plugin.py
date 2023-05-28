#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append("..")
from PyQt5.QtWidgets import (
    QPushButton,
    QPlainTextEdit,
    QLineEdit,
    QLabel,
    QGridLayout,
    QCheckBox,
    QProgressBar, QWidget, QFileDialog
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
try:
    from qt.colors import yellow, green, orange, blue, red, purple
    from qt.scrollable_widget import ScrollLabel
except ModuleNotFoundError:
    from geniusbot.qt.colors import yellow, green, orange, blue, red, purple
    from geniusbot.qt.scrollable_widget import ScrollLabel
import pkg_resources
package = 'repository-manager'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    from repository_manager import Git
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class RepositoryManagerTab(QWidget):
    def __init__(self, console):
        super(RepositoryManagerTab, self).__init__()
        self.console = console
        self.repository_manager = Git()
        self.repository_manager_tab = QWidget()

        repository_manager_layout = QGridLayout()
        self.repository_manager_repositories_location_button = QPushButton("Repositories Location")
        self.repository_manager_repositories_location_button.setStyleSheet(
            f"background-color: {orange}; color: white; font: bold;")
        self.repository_manager_repositories_location_button.clicked.connect(
            self.repository_manager_repositories_location)
        self.repository_manager_repositories_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.repository_manager_repositories_file_location_button = QPushButton("Repositories File Location")
        self.repository_manager_repositories_file_location_button.setStyleSheet(
            f"background-color: {green}; color: white; font: bold;")
        self.repository_manager_repositories_file_location_button.clicked.connect(self.open_repository_manager_file)
        self.repository_manager_repositories_file_location_label = QLabel(
            f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.clone_ticker = QCheckBox("Clone")
        self.pull_ticker = QCheckBox("Pull")
        self.clone_ticker.setChecked(True)
        self.pull_ticker.setChecked(True)
        self.set_default_branch_ticker = QCheckBox("Checkout Default Branch")
        self.repository_git_command_label = QLabel("Git Command: ")
        self.repository_git_command_label.setStyleSheet(f"color: black; font-size: 11pt;")
        self.repository_git_command = QLineEdit()
        self.repository_links_editor_label = QLabel("Paste Repository URL(s) Below ↴")
        self.repository_links_editor_label.setStyleSheet(f"color: black; font-size: 11pt;")
        self.repository_links_editor = QPlainTextEdit()
        self.repository_manager_files_label = ScrollLabel(self)
        self.repository_manager_files_label.hide()
        self.repository_manager_files_label.setText(f"Repositories will be shown here\n")
        self.repository_manager_files_label.setFont("Arial")
        self.repository_manager_files_label.setFontColor(background_color="white", color="black")
        self.repository_manager_files_label.setScrollWheel("Top")
        self.repository_manager_run_button = QPushButton("Run ⥀")
        self.repository_manager_run_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.repository_manager_run_button.clicked.connect(self.manage_repositories)
        self.repositories_progress_bar = QProgressBar()
        repository_manager_layout.addWidget(self.repository_manager_repositories_location_button, 0, 0, 1, 1)
        repository_manager_layout.addWidget(self.repository_manager_repositories_location_label, 0, 1, 1, 2)
        repository_manager_layout.addWidget(self.repository_manager_repositories_file_location_button, 1, 0, 1, 1)
        repository_manager_layout.addWidget(self.repository_manager_repositories_file_location_label, 1, 1, 1, 2)
        repository_manager_layout.addWidget(self.clone_ticker, 2, 0, 1, 1)
        repository_manager_layout.addWidget(self.pull_ticker, 2, 1, 1, 1)
        repository_manager_layout.addWidget(self.set_default_branch_ticker, 2, 2, 1, 1)
        repository_manager_layout.addWidget(self.repository_git_command_label, 3, 0, 1, 3)
        repository_manager_layout.addWidget(self.repository_git_command, 4, 0, 1, 3)
        repository_manager_layout.addWidget(self.repository_links_editor_label, 5, 0, 1, 3)
        repository_manager_layout.addWidget(self.repository_links_editor, 6, 0, 1, 3)
        repository_manager_layout.addWidget(self.repository_manager_files_label, 7, 0, 1, 3)
        repository_manager_layout.addWidget(self.repository_manager_run_button, 8, 0, 1, 3)
        repository_manager_layout.addWidget(self.repositories_progress_bar, 9, 0, 1, 3)
        self.repository_manager_tab.setLayout(repository_manager_layout)

    def manage_repositories(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing Repositories...\n")
        self.repositories_progress_bar.setValue(1)

        self.repository_manager_thread = QThread()
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

    def report_repositories_progress_bar(self, n):
        self.repositories_progress_bar.setValue(n)

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


class RepositoryManagerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, repository_manager, clone_ticker, set_default_branch_ticker, pull_ticker,
                 repository_links_editor, repository_git_command, repository_manager_repositories_file_location_label,
                 repository_manager_files_label, repository_manager_repositories_location_label):
        super().__init__()
        self.repository_manager = repository_manager
        self.clone_ticker = clone_ticker
        self.set_default_branch_ticker = set_default_branch_ticker
        self.pull_ticker = pull_ticker
        self.repository_links_editor = repository_links_editor
        self.repository_git_command = repository_git_command
        self.repository_manager_repositories_file_location_label = repository_manager_repositories_file_location_label
        self.repository_manager_files_label = repository_manager_files_label
        self.repository_manager_repositories_location_label = repository_manager_repositories_location_label

    def run(self):
        """Long-running task."""
        if self.clone_ticker.isChecked():
            projects = self.repository_links_editor.toPlainText()
            projects = projects.strip()
            projects = projects.split('\n')
            if projects[0] == '':
                projects = []
            if os.path.exists(self.repository_manager_repositories_file_location_label.text()):
                try:
                    file_repositories = open(self.repository_manager_repositories_file_location_label.text(), 'r')
                    for repository in file_repositories:
                        projects.append(repository)
                    projects = list(dict.fromkeys(projects))
                except Exception as e:
                    print(f"File not found or unable to parse file contents: {e}")
            self.repository_manager.set_git_projects(projects)
            self.repository_manager.clone_projects()
            self.progress.emit(33)
        default_branch_flag = self.set_default_branch_ticker.isChecked()
        if self.pull_ticker.isChecked():
            self.repository_manager.pull_projects(set_to_default_branch=default_branch_flag)
            self.progress.emit(66)
        if self.repository_git_command.text() != "":
            projects = self.repository_manager_files_label.text()
            projects = projects.strip()
            projects = projects.split('\n')
            print(f"PROJECTS SO FAR: {projects}")
            if projects[0] == '':
                projects = []
            for project in projects:
                try:
                    result = self.repository_manager.git_action(command=f"{self.repository_git_command.text()}",
                                                                directory=f"{self.repository_manager_repositories_location_label.text()}/{project}")
                    print(result)
                except Exception as e:
                    print(
                        f"Unable to execute git command: {self.repository_git_command.text()} for directory: {self.repository_manager_repositories_location_label.text()}/{project}")
            self.progress.emit(99)
        self.progress.emit(100)
        self.finished.emit()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append("..")
from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QProgressBar,
    QCheckBox,
    QPlainTextEdit, QWidget
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from qt.colors import yellow, green, orange, blue, red, purple
from qt.scrollable_widget import ScrollLabel
from systems_manager import SystemsManager


def initialize_systems_manager_tab(self):
    self.systems_manager = SystemsManager()
    self.systems_manager_tab = QWidget()
    self.tab_widget.addTab(self.systems_manager_tab, "Systems Manager")
    systems_manager_layout = QGridLayout()
    # self.repository_manager_repositories_location_button = QPushButton("Repositories Location")
    # self.repository_manager_repositories_location_button.setStyleSheet(
    #     f"background-color: {orange}; color: white; font: bold;")
    # self.repository_manager_repositories_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
    # self.repository_manager_repositories_file_location_button = QPushButton("Repositories File Location")
    # self.repository_manager_repositories_file_location_button.setStyleSheet(
    #     f"background-color: {green}; color: white; font: bold;")
    # self.repository_manager_repositories_file_location_button.clicked.connect(self.open_repository_manager_file)
    # self.repository_manager_repositories_file_location_label = QLabel(
    #     f'{os.path.expanduser("~")}'.replace("\\", "/"))
    # self.clone_ticker = QCheckBox("Clone")
    # self.pull_ticker = QCheckBox("Pull")
    # self.clone_ticker.setChecked(True)
    # self.pull_ticker.setChecked(True)
    # self.set_default_branch_ticker = QCheckBox("Checkout Default Branch")
    # self.repository_git_command_label = QLabel("Git Command: ")
    # self.repository_git_command_label.setStyleSheet(f"color: black; font-size: 11pt;")
    # self.repository_git_command = QLineEdit()
    # self.repository_links_editor_label = QLabel("Paste Repository URL(s) Below ↴")
    # self.repository_links_editor_label.setStyleSheet(f"color: black; font-size: 11pt;")
    # self.repository_links_editor = QPlainTextEdit()
    # self.repository_manager_files_label = ScrollLabel(self)
    # self.repository_manager_files_label.hide()
    # self.repository_manager_files_label.setText(f"Repositories will be shown here\n")
    # self.repository_manager_files_label.setFont("Arial")
    # self.repository_manager_files_label.setFontColor(background_color="white", color="black")
    # self.repository_manager_files_label.setScrollWheel("Top")
    # self.repository_manager_run_button = QPushButton("Run ⥀")
    # self.repository_manager_run_button.setStyleSheet(
    #     f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
    # self.repository_manager_run_button.clicked.connect(self.manage_repositories)
    # self.repositories_progress_bar = QProgressBar()
    # systems_manager_layout.addWidget(self.repository_manager_repositories_location_button, 0, 0, 1, 1)
    # systems_manager_layout.addWidget(self.repository_manager_repositories_location_label, 0, 1, 1, 2)
    # systems_manager_layout.addWidget(self.repository_manager_repositories_file_location_button, 1, 0, 1, 1)
    # systems_manager_layout.addWidget(self.repository_manager_repositories_file_location_label, 1, 1, 1, 2)
    # systems_manager_layout.addWidget(self.clone_ticker, 2, 0, 1, 1)
    # systems_manager_layout.addWidget(self.pull_ticker, 2, 1, 1, 1)
    # systems_manager_layout.addWidget(self.set_default_branch_ticker, 2, 2, 1, 1)
    # systems_manager_layout.addWidget(self.repository_git_command_label, 3, 0, 1, 3)
    # systems_manager_layout.addWidget(self.repository_git_command, 4, 0, 1, 3)
    # systems_manager_layout.addWidget(self.repository_links_editor_label, 5, 0, 1, 3)
    # systems_manager_layout.addWidget(self.repository_links_editor, 6, 0, 1, 3)
    # systems_manager_layout.addWidget(self.repository_manager_files_label, 7, 0, 1, 3)
    # systems_manager_layout.addWidget(self.repository_manager_run_button, 8, 0, 1, 3)
    # systems_manager_layout.addWidget(self.repositories_progress_bar, 9, 0, 1, 3)
    self.tab_widget.setTabText(7, "Systems Manager")
    self.systems_manager_tab.setLayout(systems_manager_layout)


class SystemsManagerWorker(QObject):
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

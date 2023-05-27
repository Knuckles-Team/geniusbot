#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pkg_resources
sys.path.append("..")
from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QProgressBar,
    QCheckBox,
    QListWidget, QWidget, QComboBox
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from qt.colors import yellow, green, orange, blue, red, purple
from qt.scrollable_widget import ScrollLabel
from systems_manager import SystemsManager


def check_package(package="None"):
    found = False
    try:
        dist = pkg_resources.get_distribution(package)
        found = True
    except pkg_resources.DistributionNotFound:
        print('')
    return found

webarchiver_installed = check_package("webarchiver")
subshift_installed = check_package("subshift")
media_downloader_installed = check_package("media-downloader")
media_manager_installed = check_package("media-manager")
report_manager_installed = check_package("report-manager")
repository_manager_installed = check_package("repository-manager")


def initialize_systems_manager_tab(self):
    self.systems_manager = SystemsManager()
    self.systems_manager_tab = QWidget()
    self.tab_widget.addTab(self.systems_manager_tab, "Systems Manager")
    systems_manager_layout = QGridLayout()
    self.install_app_ticker = QCheckBox("Install Applications")
    self.install_python_ticker = QCheckBox("Install Python Modules")
    self.enable_windows_features_ticker = QCheckBox("Enable Windows Features")
    if sys.platform != 'win32':
        self.enable_windows_features_ticker.setEnabled(False)
    self.install_theme_ticker = QCheckBox("Install Theme")
    self.install_font_ticker = QCheckBox("Install Font")
    self.update_ticker = QCheckBox("Update")
    self.clean_ticker = QCheckBox("Clean")
    self.silent_ticker = QCheckBox("Silent")
    self.install_app_ticker.setChecked(False)
    self.install_app_ticker.stateChanged.connect(install_applications_button_selected)
    self.install_theme_ticker.stateChanged.connect(install_applications_button_selected)
    self.install_font_ticker.stateChanged.connect(install_applications_button_selected)
    self.install_font_ticker.stateChanged.connect(install_applications_button_selected)
    self.install_font_ticker.stateChanged.connect(install_applications_button_selected)
    self.update_ticker.setChecked(False)
    self.clean_ticker.setChecked(False)
    self.theme_combobox = QComboBox()
    self.theme_combobox.addItems(['Takayuma', 'Other'])
    self.theme_combobox.setItemText(0, "Takayuma")
    self.theme_combobox.setEnabled(False)
    self.font_combobox = QComboBox()
    self.font_combobox.addItems(['Hack NF', 'Meslo'])
    self.font_combobox.setItemText(0, "Hack NF")
    self.font_combobox.setEnabled(False)
    self.systems_manager_run_button = QPushButton("Run ⥀")
    self.systems_manager_run_button.setStyleSheet(f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
    self.application_install_edit = QLineEdit()
    self.python_module_install_edit = QLineEdit()
    self.enable_windows_feature_edit = QLineEdit()
    self.application_install_edit.setEnabled(False)
    self.python_module_install_edit.setEnabled(False)
    self.enable_windows_feature_edit.setEnabled(False)
    self.enable_windows_feature_list = QListWidget()
    self.enable_windows_feature_list.setSelectionMode(3)
    self.enable_windows_feature_list.setEnabled(False)
    self.enable_windows_feature_list.addItems(self.systems_manager.windows_features)
    self.application_install_list = QListWidget()
    self.application_install_list.setSelectionMode(3)
    self.application_install_list.setEnabled(False)
    self.application_install_list.addItems(self.systems_manager.applications)
    self.webarchiver_install_button = QCheckBox("Geniusbot - Webarchiver Plugin")
    if webarchiver_installed:
        self.webarchiver_install_button.setChecked(True)
        self.webarchiver_install_button.setEnabled(False)
    else:
        self.webarchiver_install_button.setChecked(False)
    self.subshift_install_button = QCheckBox("Geniusbot - Subshift Plugin")
    if subshift_installed:
        self.subshift_install_button.setChecked(True)
        self.subshift_install_button.setEnabled(False)
    else:
        self.subshift_install_button.setChecked(False)
    self.media_downloader_install_button = QCheckBox("Geniusbot - Media Downloader Plugin")
    if media_downloader_installed:
        self.media_downloader_install_button.setChecked(True)
        self.media_downloader_install_button.setEnabled(False)
    else:
        self.media_downloader_install_button.setChecked(False)
    self.media_manager_install_button = QCheckBox("Geniusbot - Media Manager Plugin")
    if media_manager_installed:
        self.media_manager_install_button.setChecked(True)
        self.media_manager_install_button.setEnabled(False)
    else:
        self.media_manager_install_button.setChecked(False)
    self.repository_manager_install_button = QCheckBox("Geniusbot - Repository Manager Plugin")
    if repository_manager_installed:
        self.repository_manager_install_button.setChecked(True)
        self.repository_manager_install_button.setEnabled(False)
    else:
        self.repository_manager_install_button.setChecked(False)
    self.report_manager_install_button = QCheckBox("Geniusbot - Report Manager Plugin")
    if report_manager_installed:
        self.report_manager_install_button.setChecked(True)
        self.report_manager_install_button.setEnabled(False)
    else:
        self.report_manager_install_button.setChecked(False)
    self.systems_manager_run_button.clicked.connect(manage_system)
    self.system_progress_bar = QProgressBar()
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
    systems_manager_layout.addWidget(self.update_ticker, 1, 0, 1, 1)
    systems_manager_layout.addWidget(self.clean_ticker, 1, 1, 1, 1)
    systems_manager_layout.addWidget(self.install_theme_ticker, 1, 2, 1, 1)
    systems_manager_layout.addWidget(self.install_font_ticker, 1, 3, 1, 1)
    systems_manager_layout.addWidget(self.theme_combobox, 2, 2, 1, 1)
    systems_manager_layout.addWidget(self.font_combobox, 2, 3, 1, 1)
    systems_manager_layout.addWidget(self.install_app_ticker, 3, 0, 1, 2)
    systems_manager_layout.addWidget(self.install_python_ticker, 3, 1, 1, 1)
    systems_manager_layout.addWidget(self.enable_windows_features_ticker, 3, 2, 1, 2)
    systems_manager_layout.addWidget(self.application_install_edit, 4, 0, 1, 1)
    systems_manager_layout.addWidget(self.application_install_list, 5, 0, 6, 1)
    systems_manager_layout.addWidget(self.python_module_install_edit, 4, 1, 1, 1)
    systems_manager_layout.addWidget(self.enable_windows_feature_edit, 4, 2, 1, 2)
    systems_manager_layout.addWidget(self.enable_windows_feature_list, 5, 2, 6, 2)
    systems_manager_layout.addWidget(self.webarchiver_install_button, 5, 1, 1, 1)
    systems_manager_layout.addWidget(self.subshift_install_button, 6, 1, 1, 1)
    systems_manager_layout.addWidget(self.media_downloader_install_button, 7, 1, 1, 1)
    systems_manager_layout.addWidget(self.media_manager_install_button, 8, 1, 1, 1)
    systems_manager_layout.addWidget(self.repository_manager_install_button, 9, 1, 1, 1)
    systems_manager_layout.addWidget(self.report_manager_install_button, 10, 1, 1, 1)
    systems_manager_layout.addWidget(self.systems_manager_run_button, 99, 0, 1, 4)
    systems_manager_layout.addWidget(self.system_progress_bar, 100, 0, 1, 4)
    self.tab_widget.setTabText(7, "Systems Manager")
    self.systems_manager_tab.setLayout(systems_manager_layout)


def install_applications_button_selected(self):
    if self.install_app_ticker.isChecked():
        self.application_install_edit.setEnabled(True)
    else:
        self.application_install_edit.setEnabled(False)


def install_python_button_selected(self):
    if self.install_python_modules_ticker.isChecked():
        self.python_install_edit.setEnabled(True)
    else:
        self.python_install_edit.setEnabled(False)


def enable_windows_features_selected(self):
    if self.enable_windows_features.isChecked():
        self.python_install_edit.setEnabled(True)
    else:
        self.python_install_edit.setEnabled(False)


def manage_system(self):
    print("TEST")


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

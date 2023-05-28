#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pkg_resources
sys.path.append("..")
from PyQt5.QtWidgets import (
    QGridLayout,
    QPushButton,
    QLineEdit,
    QProgressBar,
    QCheckBox,
    QListWidget, QWidget, QComboBox
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
try:
    from qt.colors import yellow, green, orange, blue, red, purple
    from qt.scrollable_widget import ScrollLabel
except ModuleNotFoundError:
    from geniusbot.qt.colors import yellow, green, orange, blue, red, purple
    from geniusbot.qt.scrollable_widget import ScrollLabel
from systems_manager import SystemsManager


class SystemsManagerTab(QWidget):

    def __init__(self, console):
        super(SystemsManagerTab, self).__init__()
        self.systems_manager = SystemsManager()
        self.systems_manager_tab = QWidget()
        self.console = console
        self.webarchiver_installed = self.check_package(package="webarchiver")
        self.subshift_installed = self.check_package(package="subshift")
        self.media_downloader_installed = self.check_package(package="media-downloader")
        self.media_manager_installed = self.check_package(package="media-manager")
        self.report_manager_installed = self.check_package(package="report-manager")
        self.repository_manager_installed = self.check_package(package="repository-manager")

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
        self.install_app_ticker.stateChanged.connect(self.install_applications_button_selected)
        self.install_theme_ticker.stateChanged.connect(self.enable_theme)
        self.install_font_ticker.stateChanged.connect(self.enable_font)
        self.install_python_ticker.stateChanged.connect(self.install_python_button_selected)
        self.enable_windows_features_ticker.stateChanged.connect(self.enable_windows_features_selected)
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
        if self.webarchiver_installed:
            self.webarchiver_install_button.setChecked(True)
            self.webarchiver_install_button.setEnabled(False)
        else:
            self.webarchiver_install_button.setChecked(False)
        self.subshift_install_button = QCheckBox("Geniusbot - Subshift Plugin")
        if self.subshift_installed:
            self.subshift_install_button.setChecked(True)
            self.subshift_install_button.setEnabled(False)
        else:
            self.subshift_install_button.setChecked(False)
        self.media_downloader_install_button = QCheckBox("Geniusbot - Media Downloader Plugin")
        if self.media_downloader_installed:
            self.media_downloader_install_button.setChecked(True)
            self.media_downloader_install_button.setEnabled(False)
        else:
            self.media_downloader_install_button.setChecked(False)
        self.media_manager_install_button = QCheckBox("Geniusbot - Media Manager Plugin")
        if self.media_manager_installed:
            self.media_manager_install_button.setChecked(True)
            self.media_manager_install_button.setEnabled(False)
        else:
            self.media_manager_install_button.setChecked(False)
        self.repository_manager_install_button = QCheckBox("Geniusbot - Repository Manager Plugin")
        if self.repository_manager_installed:
            self.repository_manager_install_button.setChecked(True)
            self.repository_manager_install_button.setEnabled(False)
        else:
            self.repository_manager_install_button.setChecked(False)
        self.report_manager_install_button = QCheckBox("Geniusbot - Report Manager Plugin")
        if self.report_manager_installed:
            self.report_manager_install_button.setChecked(True)
            self.report_manager_install_button.setEnabled(False)
        else:
            self.report_manager_install_button.setChecked(False)
        self.systems_manager_run_button.clicked.connect(self.manage_system)
        self.system_progress_bar = QProgressBar()
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
        self.systems_manager_tab.setLayout(systems_manager_layout)

    def install_applications_button_selected(self):
        if self.install_app_ticker.isChecked():
            self.application_install_edit.setEnabled(True)
            self.application_install_list.setEnabled(True)
        else:
            self.application_install_edit.setEnabled(False)
            self.application_install_list.setEnabled(False)

    def install_python_button_selected(self):
        if self.install_python_ticker.isChecked():
            self.python_module_install_edit.setEnabled(True)
        else:
            self.python_module_install_edit.setEnabled(False)

    def enable_windows_features_selected(self):
        if self.enable_windows_features_ticker.isChecked():
            self.enable_windows_feature_edit.setEnabled(True)
            self.enable_windows_feature_list.setEnabled(True)
        else:
            self.enable_windows_feature_edit.setEnabled(False)
            self.enable_windows_feature_list.setEnabled(False)

    def enable_theme(self):
        if self.install_theme_ticker.isChecked():
            self.theme_combobox.setEnabled(True)
        else:
            self.theme_combobox.setEnabled(False)

    def enable_font(self):
        if self.install_font_ticker.isChecked():
            self.font_combobox.setEnabled(True)
        else:
            self.font_combobox.setEnabled(False)

    def check_package(self, package="None"):
        found = False
        try:
            dist = pkg_resources.get_distribution(package)
            print('{} ({}) is installed'.format(dist.key, dist.version))
            found = True
        except pkg_resources.DistributionNotFound:
            print('{} is NOT installed'.format(package))
        return found

    def report_systems_progress_bar(self, n):
        self.system_progress_bar.setValue(n)

    def manage_system(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing System...\n")
        self.system_progress_bar.setValue(1)
        self.systems_manager_thread = QThread()
        self.systems_manager_worker = SystemsManagerWorker(systems_manager=self.systems_manager,
                                                           silent_ticker=self.silent_ticker,
                                                           update_ticker=self.update_ticker,
                                                           enable_windows_features_ticker=self.enable_windows_features_ticker,
                                                           enable_windows_feature_list=self.enable_windows_feature_list,
                                                           enable_windows_feature_edit=self.enable_windows_feature_edit,
                                                           install_app_ticker=self.install_app_ticker,
                                                           application_install_edit=self.application_install_edit,
                                                           install_python_ticker=self.install_python_ticker,
                                                           webarchiver_install_button=self.webarchiver_install_button,
                                                           subshift_install_button=self.subshift_install_button,
                                                           repository_manager_install_button=self.repository_manager_install_button,
                                                           report_manager_install_button=self.report_manager_install_button,
                                                           media_manager_install_button=self.media_manager_install_button,
                                                           media_downloader_install_button=self.media_downloader_install_button,
                                                           python_module_install_edit=self.python_module_install_edit,
                                                           install_font_ticker=self.install_font_ticker,
                                                           install_theme_ticker=self.install_theme_ticker,
                                                           clean_ticker=self.clean_ticker)
        self.systems_manager_worker.moveToThread(self.systems_manager_thread)
        self.systems_manager_thread.started.connect(self.systems_manager_worker.run)
        self.systems_manager_worker.finished.connect(self.systems_manager_thread.quit)
        self.systems_manager_worker.finished.connect(self.systems_manager_worker.deleteLater)
        self.systems_manager_thread.finished.connect(self.systems_manager_thread.deleteLater)
        self.systems_manager_worker.progress.connect(self.report_systems_progress_bar)
        self.systems_manager_thread.start()
        self.systems_manager_run_button.setEnabled(False)
        self.systems_manager_thread.finished.connect(
            lambda: self.systems_manager_run_button.setEnabled(True)
        )
        self.systems_manager_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] System actions complete!\n")
        )


class SystemsManagerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, systems_manager, silent_ticker, update_ticker, enable_windows_features_ticker, enable_windows_feature_list,
                 enable_windows_feature_edit, install_app_ticker, application_install_edit, install_python_ticker,
                 webarchiver_install_button, subshift_install_button, repository_manager_install_button,
                 report_manager_install_button, media_manager_install_button, media_downloader_install_button,
                 python_module_install_edit, install_font_ticker, install_theme_ticker, clean_ticker):
        super().__init__()
        self.systems_manager = systems_manager
        self.silent_ticker = silent_ticker
        self.update_ticker = update_ticker
        self.enable_windows_features_ticker = enable_windows_features_ticker
        self.enable_windows_feature_list = enable_windows_feature_list
        self.enable_windows_feature_edit = enable_windows_feature_edit
        self.install_app_ticker = install_app_ticker
        self.application_install_edit = application_install_edit
        self.install_python_ticker = install_python_ticker
        self.webarchiver_install_button = webarchiver_install_button
        self.subshift_install_button = subshift_install_button
        self.repository_manager_install_button = repository_manager_install_button
        self.report_manager_install_button = report_manager_install_button
        self.media_manager_install_button = media_manager_install_button
        self.media_downloader_install_button = media_downloader_install_button
        self.python_module_install_edit = python_module_install_edit
        self.install_font_ticker = install_font_ticker
        self.install_theme_ticker = install_theme_ticker
        self.clean_ticker = clean_ticker

    def run(self):
        """Long-running task."""
        if self.silent_ticker.isChecked():
            print("Setting Silent...")
            self.systems_manager.set_silent(silent=True)
        self.progress.emit(1)
        if self.update_ticker.isChecked():
            print("Performing Update...")
            self.systems_manager.update()
        self.progress.emit(5)
        if self.enable_windows_features_ticker.isChecked():
            features_ui = self.enable_windows_feature_list.selectedItems()
            features = []
            for i in range(len(features_ui)):
                features.append(str(self.enable_windows_feature_list.selectedItems()[i].text()))
            custom_features = self.enable_windows_feature_edit.text()
            custom_features = custom_features.replace(" ", "")
            custom_features = custom_features.split(",")
            features = features + custom_features
            print(f"Setting features: {features}")
            self.systems_manager.set_features(features=features)
            print("Enabling Windows Features...")
            self.systems_manager.enable_windows_features()
        self.progress.emit(20)
        if self.install_app_ticker.isChecked():
            applications_ui = self.enable_windows_feature_list.selectedItems()
            applications = []
            for i in range(len(applications_ui)):
                applications.append(str(self.enable_windows_feature_list.selectedItems()[i].text()))
            custom_applications = self.application_install_edit.text()
            custom_applications = custom_applications.replace(" ", "")
            custom_applications = custom_applications.split(",")
            applications = applications + custom_applications
            print(f"Setting applications from GUI: {applications}")
            self.systems_manager.set_applications(applications=applications)
            print("Installing...")
            self.systems_manager.install_applications()
        self.progress.emit(45)
        if self.install_python_ticker.isChecked():
            python_modules = []
            if self.webarchiver_install_button.isChecked():
                python_modules.append('webarchiver')
            if self.subshift_install_button.isChecked():
                python_modules.append('subshift')
            if self.repository_manager_install_button.isChecked():
                python_modules.append('repository-manager')
            if self.report_manager_install_button.isChecked():
                python_modules.append('report-manager')
            if self.media_manager_install_button.isChecked():
                python_modules.append('media-manager')
            if self.media_downloader_install_button.isChecked():
                python_modules.append('media-downloader')
            custom_python_modules = self.python_module_install_edit.text()
            custom_python_modules = custom_python_modules.replace(" ", "")
            custom_python_modules = custom_python_modules.split(",")
            python_modules = python_modules + custom_python_modules
            print(f"Setting Python Modules: {python_modules}")
            self.systems_manager.set_python_modules(modules=python_modules)
            print("Installing Python Modules...")
            self.systems_manager.install_python_modules()
        self.progress.emit(60)
        if self.install_font_ticker.isChecked():
            print("Setting Hack Font")
            self.systems_manager.font()
        self.progress.emit(75)
        if self.install_theme_ticker.isChecked():
            print("Setting Theme")
            self.systems_manager.theme()
        self.progress.emit(85)
        if self.clean_ticker.isChecked():
            print("Cleaning Recycle/Trash Bin")
            self.systems_manager.clean()
        self.progress.emit(95)

        self.progress.emit(100)
        self.finished.emit()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append("..")
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QGridLayout,
    QCheckBox, QWidget, QFileDialog,
    QSpinBox,
    QComboBox
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread

try:
    from qt.colors import yellow, green, orange, blue, red, purple
    from qt.scrollable_widget import ScrollLabel
except ModuleNotFoundError:
    from geniusbot.qt.colors import yellow, green, orange, blue, red, purple
    from geniusbot.qt.scrollable_widget import ScrollLabel
import pkg_resources

package = 'rom-manager'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    from rom_manager import RomManager
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class RomManagerTab(QWidget):
    def __init__(self, console):
        super(RomManagerTab, self).__init__()
        self.console = console
        self.rom_manager = RomManager()
        self.rom_manager_thread = None
        self.rom_manager_worker = None
        self.rom_manager_tab = QWidget()
        rom_manager_layout = QGridLayout()
        self.rom_manager_location_button = QPushButton("Game Location")
        self.rom_manager_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
        self.rom_manager_location_button.clicked.connect(self.rom_manager_location)
        self.rom_manager_location_label = QLabel(f'{os.path.normpath(os.path.expanduser("~"))}')

        self.force_ticker = QCheckBox("Force Overwrite")
        self.clean_origin_files_ticker = QCheckBox("Delete Original Files")
        self.verbose_ticker = QCheckBox("Verbose Output")
        self.cpu_count_label = QLabel("Parallel CPU(s)")
        self.cpu_count_spin_box = QSpinBox(self)
        self.cpu_count_spin_box.setRange(1, os.cpu_count())
        self.cpu_count_spin_box.setValue(int(os.cpu_count() / 2))
        self.iso_file_type_label = QLabel("ISO Type")
        self.iso_file_type = QComboBox()
        self.iso_file_type.addItems(['CHD', 'RVZ'])
        self.rom_manager_files_label = ScrollLabel(self)
        self.rom_manager_files_label.hide()
        self.rom_manager_files_label.setText(f"Game files found will be shown here\n")
        self.rom_manager_files_label.setFont("Arial")
        self.rom_manager_files_label.setFontColor(background_color="white", color="black")
        self.rom_manager_files_label.setScrollWheel("Top")
        self.rom_manager_run_button = QPushButton("Convert ⥀")
        self.rom_manager_run_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.rom_manager_run_button.clicked.connect(self.manage_roms)
        rom_manager_layout.addWidget(self.rom_manager_location_button, 0, 0, 1, 1)
        rom_manager_layout.addWidget(self.rom_manager_location_label, 0, 1, 1, 5)
        rom_manager_layout.addWidget(self.force_ticker, 1, 0, 1, 1)
        rom_manager_layout.addWidget(self.verbose_ticker, 1, 1, 1, 1)
        rom_manager_layout.addWidget(self.clean_origin_files_ticker, 1, 2, 1, 1)
        rom_manager_layout.addWidget(self.cpu_count_label, 1, 3, 1, 1)
        rom_manager_layout.addWidget(self.cpu_count_spin_box, 1, 4, 1, 1)
        rom_manager_layout.addWidget(self.iso_file_type_label, 1, 5, 1, 1)
        rom_manager_layout.addWidget(self.iso_file_type, 1, 6, 1, 1)
        rom_manager_layout.addWidget(self.rom_manager_files_label, 2, 0, 1, 7)
        rom_manager_layout.addWidget(self.rom_manager_run_button, 3, 0, 1, 7)
        self.rom_manager_tab.setLayout(rom_manager_layout)

    def manage_roms(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing ROM(s)...\n")

        if self.force_ticker.isChecked():
            force_boolean = True
        else:
            force_boolean = False

        if self.verbose_ticker.isChecked():
            verbose_boolean = True
        else:
            verbose_boolean = False

        if self.clean_origin_files_ticker.isChecked():
            clean_origin_files_boolean = True
        else:
            clean_origin_files_boolean = False

        cpu_count = self.cpu_count_spin_box.value()

        self.rom_manager_thread = QThread()
        self.rom_manager_worker = RomManagerWorker(rom_manager=self.rom_manager,
                                                   directory=self.rom_manager_location_label.text(),
                                                   verbose=verbose_boolean,
                                                   force=force_boolean,
                                                   clean_origin_files=clean_origin_files_boolean,
                                                   iso_type=self.iso_file_type.currentText(),
                                                   cpu_count=cpu_count)
        self.rom_manager_worker.moveToThread(self.rom_manager_thread)
        self.rom_manager_thread.started.connect(self.rom_manager_worker.run)
        self.rom_manager_worker.finished.connect(self.rom_manager_thread.quit)
        self.rom_manager_worker.finished.connect(self.rom_manager_worker.deleteLater)
        self.rom_manager_thread.finished.connect(self.rom_manager_thread.deleteLater)
        self.rom_manager_thread.start()
        self.rom_manager_run_button.setEnabled(False)
        self.rom_manager_thread.finished.connect(lambda: self.rom_manager_run_button.setEnabled(True))
        self.rom_manager_thread.finished.connect(lambda: self.console.setText(f"{self.console.text()}\n"
                                                                              f"[Genius Bot] Managing "
                                                                              f"ROM(s) complete!\n"))
        self.rom_manager_thread.finished.connect(lambda: self.rom_manager_refresh_list())

    def rom_manager_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting game location to look for ROMs in!\n")
        rom_manager_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                      os.path.normpath(os.path.expanduser("~")),
                                                                      QFileDialog.ShowDirsOnly)
        if rom_manager_directory_name is None or rom_manager_directory_name == "":
            rom_manager_directory_name = os.path.normpath(os.path.expanduser("~"))
        self.rom_manager_location_label.setText(rom_manager_directory_name)
        files = ""
        self.rom_manager.directory = rom_manager_directory_name
        for file in RomManager.get_files(directory=self.rom_manager.directory,
                                         extensions=self.rom_manager.supported_extensions):
            files = f"{files}\n{os.path.normpath(file)}"
        self.rom_manager_files_label.setText(files.strip())

    def rom_manager_refresh_list(self):
        self.rom_manager.directory = self.rom_manager_location_label.text()
        files = ""
        for file in self.rom_manager.get_files(directory=self.rom_manager.directory,
                                               extensions=self.rom_manager.supported_extensions):
            files = f"{files}\n{file}"
        self.rom_manager_files_label.setText(files.strip())


class RomManagerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, rom_manager, directory, verbose, force, clean_origin_files, iso_type, cpu_count):
        super().__init__()
        self.rom_manager = rom_manager
        self.directory = directory
        self.verbose = verbose
        self.force = force
        self.clean_origin_files = clean_origin_files
        self.iso_type = iso_type.lower()
        self.cpu_count = cpu_count

    def run(self):
        """Long-running task."""
        self.rom_manager.directory = os.path.normpath(self.directory)
        self.rom_manager.verbose = self.verbose
        self.rom_manager.force = self.force
        self.rom_manager.clean_origin_files = self.clean_origin_files
        self.rom_manager.iso_type = self.iso_type
        self.rom_manager.process_parallel(cpu_count=self.cpu_count)
        self.progress.emit(100)
        self.finished.emit()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append("..")
from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QLineEdit,
    QListWidget, QCheckBox, QAbstractItemView, QWidget
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
try:
    from qt.colors import yellow, green, orange, blue, red, purple
    from qt.scrollable_widget import ScrollLabel
except ModuleNotFoundError:
    from geniusbot.qt.colors import yellow, green, orange, blue, red, purple
    from geniusbot.qt.scrollable_widget import ScrollLabel
import pkg_resources
package = 'report-manager'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    from report_manager import ReportManager
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class ReportManagerTab(QWidget):
    def __init__(self, console):
        super(ReportManagerTab, self).__init__()
        self.console = console
        self.report_manager = ReportManager()
        self.report_manager_tab = QWidget()

        self.report_manager_layout = QGridLayout()
        self.action_type_combobox = QComboBox()
        self.action_type_combobox.addItems(['Generate Report', 'Merge Reports'])
        self.action_type_combobox.setItemText(0, "Generate Report")
        self.action_type_combobox.activated.connect(self.swap_report_layout)
        self.custom_report_widget = QWidget(self)
        self.merge_widget = QWidget(self)
        self.custom_report_layout = QGridLayout()
        self.merge_report_layout = QGridLayout()
        self.custom_report_layout.setContentsMargins(0, 0, 0, 0)
        self.merge_report_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_report_widget.setLayout(self.custom_report_layout)
        self.merge_widget.setLayout(self.merge_report_layout)
        self.report_manager_layout.addWidget(self.action_type_combobox, 0, 0, 1, 1)
        self.report_manager_layout.addWidget(self.custom_report_widget, 1, 0, 1, 1)
        self.report_manager_layout.addWidget(self.merge_widget, 2, 0, 1, 1)
        self.pandas_profiling_ticker = QCheckBox("Pandas Profiling")
        self.custom_report_ticker = QCheckBox("Custom Report")
        self.custom_report_generate_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.custom_report_generate_button = QPushButton("Generate ⦽")
        self.custom_report_generate_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.custom_report_generate_button.clicked.connect(self.report_manage)
        self.report_file_location_button = QPushButton("Data File")
        self.custom_data_file_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.report_file_location_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
        self.report_file_location_button.clicked.connect(self.open_report_manager_file)
        self.generated_report_save_location_button = QPushButton("Save Location")
        self.generated_report_save_location_button.setStyleSheet(
            f"background-color: {orange}; color: white; font: bold;")
        self.generated_report_save_location_button.clicked.connect(self.report_manager_save_location)
        self.report_name_label = QLabel("Report Name: ")
        self.report_name_editor = QLineEdit("Report Name")
        self.file_type_label = QLabel("Export Filetype")
        self.file_type_combobox = QComboBox()
        self.file_type_combobox.addItems(['CSV', 'XLSX'])
        self.file_type_combobox.setItemText(1, "XLSX")
        self.dataframe_label = ScrollLabel(self)
        self.dataframe_label.setText(f"Dataframe will appear here\n")
        self.dataframe_label.setFont("Arial")
        self.dataframe_label.setFontColor(background_color="white", color="black")
        self.dataframe_label.setScrollWheel("Top")
        self.dataframe_label.hide()
        self.custom_report_layout.addWidget(self.generated_report_save_location_button, 0, 0, 1, 1)
        self.custom_report_layout.addWidget(self.custom_report_generate_label, 0, 1, 1, 5)
        self.custom_report_layout.addWidget(self.report_file_location_button, 1, 0, 1, 1)
        self.custom_report_layout.addWidget(self.custom_data_file_label, 1, 1, 1, 5)
        self.custom_report_layout.addWidget(self.report_name_label, 2, 0, 1, 1)
        self.custom_report_layout.addWidget(self.report_name_editor, 2, 1, 1, 1)
        self.custom_report_layout.addWidget(self.file_type_label, 2, 2, 1, 1)
        self.custom_report_layout.addWidget(self.file_type_combobox, 2, 3, 1, 1)
        self.custom_report_layout.addWidget(self.pandas_profiling_ticker, 2, 4, 1, 1)
        self.custom_report_layout.addWidget(self.custom_report_ticker, 2, 5, 1, 1)
        self.custom_report_layout.addWidget(self.dataframe_label, 4, 0, 1, 6)
        self.custom_report_layout.addWidget(self.custom_report_generate_button, 5, 0, 1, 6)

        self.merged_report_save_location_button = QPushButton("Save Location")
        self.merged_report_save_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
        self.merged_report_save_location_button.clicked.connect(self.report_merger_save_location)
        self.merged_report_save_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.merged_report_name_label = QLabel("Report Name: ")
        self.merged_report_name_editor = QLineEdit("Report Name")
        self.merge_file_type_label = QLabel("Export Filetype")
        self.merge_file_type_combobox = QComboBox()
        self.merge_file_type_combobox.addItems(['CSV', 'XLSX'])
        self.merge_file_type_combobox.setItemText(1, "XLSX")
        self.merge_file1_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.merge_file2_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.merge_file1_location_button = QPushButton("Open Data File 1")
        self.merge_file2_location_button = QPushButton("Open Data File 2")
        self.merge_file1_location_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
        self.merge_file2_location_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
        self.merge_file1_location_button.clicked.connect(self.open_data1_file)
        self.merge_file2_location_button.clicked.connect(self.open_data2_file)
        self.file1_columns = QListWidget()
        self.file2_columns = QListWidget()
        self.file1_columns.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file2_columns.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.merge_type_label = QLabel("Merge Type: ")
        self.merge_type_combobox = QComboBox()
        self.merge_type_combobox.addItems(['Inner', 'Outer', 'Right', 'Left', 'Append'])
        self.merge_type_combobox.setItemText(0, "Inner")
        self.merge_button = QPushButton("Merge ⦽")
        self.merge_button.setStyleSheet(f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.merge_button.clicked.connect(self.merge_reports)
        self.merge_report_layout.addWidget(self.merged_report_name_label, 0, 0, 1, 1)
        self.merge_report_layout.addWidget(self.merged_report_name_editor, 0, 1, 1, 3)
        self.merge_report_layout.addWidget(self.merge_file_type_label, 1, 0, 1, 1)
        self.merge_report_layout.addWidget(self.merge_file_type_combobox, 1, 1, 1, 3)
        self.merge_report_layout.addWidget(self.merged_report_save_location_button, 2, 0, 1, 1)
        self.merge_report_layout.addWidget(self.merged_report_save_location_label, 2, 1, 1, 3)
        self.merge_report_layout.addWidget(self.merge_file1_location_button, 3, 0, 1, 1)
        self.merge_report_layout.addWidget(self.merge_file1_label, 3, 1, 1, 1)
        self.merge_report_layout.addWidget(self.merge_file2_location_button, 3, 2, 1, 1)
        self.merge_report_layout.addWidget(self.merge_file2_label, 3, 3, 1, 1)
        self.merge_report_layout.addWidget(self.file1_columns, 4, 0, 1, 2)
        self.merge_report_layout.addWidget(self.file2_columns, 4, 2, 1, 2)
        self.merge_report_layout.addWidget(self.merge_type_label, 5, 0, 1, 1)
        self.merge_report_layout.addWidget(self.merge_type_combobox, 5, 1, 1, 3)
        self.merge_report_layout.addWidget(self.merge_button, 6, 0, 1, 4)
        self.merge_widget.hide()

        self.report_manager_tab.setLayout(self.report_manager_layout)

    def swap_report_layout(self):
        if self.action_type_combobox.currentText() == "Generate Report":
            self.custom_report_widget.show()
            self.merge_widget.hide()
        else:
            self.custom_report_widget.hide()
            self.merge_widget.show()

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


class ReportManagerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, report_manager, report_name_editor, custom_report_generate_label, action_type_combobox,
                 pandas_profiling_ticker, custom_report_ticker, file_type_combobox):
        super().__init__()
        self.report_manager = report_manager
        self.report_name_editor = report_name_editor
        self.custom_report_generate_label = custom_report_generate_label
        self.action_type_combobox = action_type_combobox
        self.pandas_profiling_ticker = pandas_profiling_ticker
        self.custom_report_ticker = custom_report_ticker
        self.pandas_profiling_ticker = pandas_profiling_ticker
        self.file_type_combobox = file_type_combobox
        if self.file_type_combobox == "CSV":
            self.csv_flag = True
        else:
            self.csv_flag = False

    def run(self):
        """Long-running task."""
        self.report_manager.set_report_title(self.report_name_editor.text())
        self.report_manager.set_report_name(self.report_name_editor.text())
        self.report_manager.set_save_directory(self.custom_report_generate_label.text())
        if self.action_type_combobox.currentText() == "Generate Report":
            if self.pandas_profiling_ticker.isChecked:
                sample_flag = None  # Set to the sample size if you would like to do it on a sample instead.
                minimal_flag = False  # Quicker run if set to true, but not everything is captured.
                self.report_manager.create_pandas_profiling_report(sample_flag, minimal_flag)
                self.report_manager.export_pandas_profiling()
            if self.custom_report_ticker.isChecked():
                self.report_manager.run_analysis()
                self.report_manager.export_data(csv_flag=self.csv_flag,
                                                report_name=f"{self.report_name_editor.text()} - Dataset")
        self.finished.emit()


class MergeReportWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, report_manager, file1_columns, file2_columns, action_type_combobox, merge_type_combobox,
                 merged_report_save_location_label, merge_file1_label, merge_file2_label, merged_report_name_editor,
                 merge_file_type_combobox):
        super().__init__()
        self.report_manager = report_manager
        self.file1_columns = file1_columns
        self.file2_columns = file2_columns
        self.action_type_combobox = action_type_combobox
        self.merge_type_combobox = merge_type_combobox
        self.merge_file1_label = merge_file1_label
        self.merge_file2_label = merge_file2_label
        self.merged_report_save_location_label = merged_report_save_location_label
        self.merged_report_name_editor = merged_report_name_editor
        self.merge_file_type_combobox = merge_file_type_combobox
        if self.merge_file_type_combobox == "CSV":
            self.csv_flag = True
        else:
            self.csv_flag = False

    def run(self):
        """Long-running task."""
        self.report_manager.set_report_title(self.merged_report_name_editor.text())
        self.report_manager.set_report_name(self.merged_report_name_editor.text())
        self.report_manager.set_df1_join_keys(self.file1_columns.selectedItems())
        self.report_manager.set_df1_join_keys(self.file2_columns.selectedItems())
        self.report_manager.set_save_directory(self.merged_report_save_location_label.text())
        if self.action_type_combobox.currentText() == "Merge Reports" and self.merge_type_combobox.currentText() == "Append":
            self.report_manager.set_files(self.merge_file1_label.text(), "file2")
            self.report_manager.set_files(self.merge_file2_label.text(), "file3")
            self.report_manager.load_dataframe(file_instance=2)
            self.report_manager.load_dataframe(file_instance=3)
            self.report_manager.set_join_type(join_type=self.merge_type_combobox.currentText().lower())
            self.report_manager.join_data()
            self.report_manager.export_data(csv_flag=self.csv_flag,
                                            report_name=f"{self.merged_report_name_editor.text()} - Merged")
        elif self.action_type_combobox.currentText() == "Merge Reports" and self.merge_type_combobox.currentText() != "Append":
            self.report_manager.set_files(self.merge_file1_label.text(), "file2")
            self.report_manager.set_files(self.merge_file2_label.text(), "file3")
            self.report_manager.load_dataframe(file_instance=2)
            self.report_manager.load_dataframe(file_instance=3)
            self.report_manager.set_df1_join_keys(df_1_join_keys=self.file1_columns)
            self.report_manager.set_df2_join_keys(df_2_join_keys=self.file2_columns)
            self.report_manager.set_join_type(join_type=self.merge_type_combobox.currentText().lower())
            self.report_manager.join_data()
            self.report_manager.export_data(csv_flag=self.csv_flag,
                                            report_name=f"{self.merged_report_name_editor.text()} - Merged")
        self.finished.emit()

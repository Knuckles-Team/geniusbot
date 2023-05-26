#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal


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
        if self.file_type_comboox == "CSV":
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

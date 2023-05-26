#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal


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

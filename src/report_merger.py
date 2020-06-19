#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
import pandas as pd
import logging
import time
import os


# The Report Merge class takes two different files (CSV, or Excel) and Joins or appends.
class ReportMerge:
    log = None
    file_1 = None
    file_2 = None
    df_1 = None
    df_2 = None
    df_1_join_keys = None
    df_2_join_keys = None
    join_type = "inner"
    report_name = "joined_report_export"
    report_name_csv = str(report_name)+".csv"
    report_name_xlsx = str(report_name)+".xlsx"
    save_directory = os.getcwd()
    csv_export = save_directory + '\\' + report_name_csv
    excel_export = save_directory + '\\' + report_name_xlsx
    df_final = None

    # Initialize the Class
    def __init__(self, logger=None):
        if logger:
            self.log = logger
        else:
            self.log = None  # Replace with log call in logger class
        self.log.info("Initializing Web Archive Complete!")
        print("Initializing & Loading Files")

    def set_file_1(self, file_1):
        self.file_1 = file_1

    def set_file_2(self, file_2):
        self.file_2 = file_2

    def set_join_type(self, join_type):
        print("Join Type Selected: ", join_type)
        self.join_type = join_type

    def get_join_type(self):
        return self.join_type

    def set_report_name(self, report_name):
        if report_name != "":
            print("Report Name: ", report_name)
            self.report_name = report_name
            self.csv_export = self.save_directory + '\\' + str(self.report_name)+".csv"
            self.excel_export = self.save_directory + '\\' + str(self.report_name)+".xlsx"
        else:
            print("Report Name was Blank")

    def get_report_name(self):
        return self.report_name

    def set_save_directory(self, directory):
        self.save_directory = directory
        print("New Directory: ",  self.save_directory)
        self.csv_export = self.save_directory + '\\' + self.report_name_csv
        self.excel_export = self.save_directory + '\\' + self.report_name_xlsx

    # Load Files to Dataframe 1
    def load_dataframe_1(self):
        print("Loading Data to Dataframe 1")
        try:
            if self.file_1.endswith('.csv'):
                print("File 1 is a CSV")
                self.df_1 = pd.read_csv(self.file_1, engine='python')
            elif self.file_1.endswith('.xlsx'):
                print("File 1 is a Excel")
                self.df_1 = pd.read_excel(self.file_1)
            self.df_1.columns = self.df_1.columns.str.replace(' ', '_')
            #self.df_1 = self.df_1.astype(str)
            print("DTYPES Dataframe 1: ", self.df_1.dtypes)
            #self.df_1.columns = self.df_1.columns.str.strip()
            print(self.df_1)
        except pd.errors.ParserError:
            print("Error")
            return 1

    # Load Files to Dataframe
    def load_dataframe_2(self):
        print("Loading Data to Dataframe 2")
        try:
            if self.file_2.endswith('.csv'):
                print("File 2 is a CSV")
                self.df_2 = pd.read_csv(self.file_2, engine='python')
            elif self.file_2.endswith('.xlsx'):
                print("File 2 is a Excel")
                self.df_2 = pd.read_excel(self.file_2)
            self.df_2.columns = self.df_2.columns.str.replace(' ', '_')
            #self.df_2 = self.df_2.astype(str)
            print("DTYPES Dataframe 2: ", self.df_2.dtypes)
            #self.df_2.columns = self.df_2.columns.str.strip()
            print(self.df_2)
            return 0
        except pd.errors.ParserError:
            print("Error")
            return 1

    # Set Data Frame Column Type
    def set_columndtype(self, file, column, data_type):
        try:
            if file == 1:
                print("Changing Dtype File 1")
                if data_type == "string":
                    self.df_1[column] = self.df_1[column].astype(str)
                    return 0
                if data_type == "date":
                    self.df_1[column] = pd.to_datetime(self.df_1[column])
                    return 0
                if data_type == "int":
                    self.df_1[column] = self.df_1[column].astype(int)
                    return 0
            elif file == 2:
                print("Changing Dtype File 2")
                if data_type == "string":
                    self.df_2[column] = self.df_2[column].astype(str)
                    return 0
                if data_type == "date":
                    self.df_2[column] = pd.to_datetime(self.df_2[column])
                    return 0
                if data_type == "int":
                    self.df_2[column] = self.df_2[column].astype(int)
                    return 0
        except Exception as e:  # print(e)(pd.io.sql.DatabaseError, AttributeError) as Exception_e:
            print("Error Setting Data Type: ", e)
            return 1
        print("Completed Successfully")

    def get_features(self, df):
        concat_str = ""
        for col in df.columns:
            concat_str = concat_str + " " + str(col)
        return concat_str

    def get_df1(self):
        return self.df_1

    def get_df2(self):
        return self.df_2

    def set_df1_join_keys(self, df_1_join_keys):
        self.df_1_join_keys = df_1_join_keys

    def set_df2_join_keys(self, df_2_join_keys):
        self.df_2_join_keys = df_2_join_keys

    def get_df1_join_keys(self):
        return self.df_1_join_keys

    def get_df2_join_keys(self):
        return self.df_2_join_keys

    # Join Based off Condition
    def join_data(self, df_1_join_keys=None, df_2_join_keys=None):
        # You can use this function by calling it with your join keys already set. Otherwise you can manaully set them using the setters.
        if df_1_join_keys and df_2_join_keys:
            self.set_df1_join_keys(df_1_join_keys)
            self.set_df2_join_keys(df_2_join_keys)
        if self.join_type == "append":
            if len(self.df_1.columns) == len(self.df_2.columns):
                print("DataFrame 1 Before Append: ", self.df_1)
                self.df_final = self.df_1.append(self.df_2)
                print("DataFrame 1 After Append: ", self.df_1)
                #self.df_final = self.df_1.copy()
                print(self.df_final)
            else:
                print("Files Have Different Column Lengths")
                return "Files Have Different Column Lengths"
        else:
            print("Joining data")
            try:
                if len(self.df_1_join_keys) > 0 and len(self.df_2_join_keys) > 0:
                    self.df_final = pd.merge(self.df_1, self.df_2, left_on=self.df_1_join_keys, right_on=self.df_2_join_keys, how=self.join_type)
                else:
                    print("One of your keys was empty")
            except Exception as e:
                print("Error: ", e)

            #pd.merge(df_ci, df_sales_mobile, left_on=['Agent - HR Number', 'Customer - Account Number', 'MA'], right_on=['Agent - HR Number', 'Customer - Account Number', 'MA'], how='left')
            print(self.df_final)

    def export_data(self, csv_flag):
        print("Exporting Data")
        if csv_flag == 1:
            self.df_final.to_csv(self.csv_export, index=False)
            print("Exported to CSV Complete!")
        else:
            # Export large data by creating xlsxwriter first and setting archivezip64 option
            self.df_final.to_excel(self.excel_export, index=False, engine='xlsxwriter')
            print("Exported to Excel Complete!")

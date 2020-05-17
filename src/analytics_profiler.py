#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
https://github.com/kianweelee/Edator
"""

# Importing the required packages
import os.path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import SimpleImputer
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import linregress
from scipy.stats import chi2_contingency
import itertools
from sklearn.preprocessing import LabelEncoder
import model
import plot


class ReportAnalyzer:
    csv_path = "./"
    plot_path = "./"
    report_path = "./"
    clean_csv_path = "./"
    data = None
    nan_prop = None
    categorical_variable = None
    numerical_variable = None

    def __init__(self):
        print("Init")

    def set_csv_path(self, csv_path):
        self.csv_path = csv_path

    def set_plot_path(self, plot_path):
        self.plot_path = plot_path

    def set_report_path(self, report_path):
        self.report_path = report_path

    def set_clean_csv_path(self, clean_csv_path):
        self.clean_csv_path = clean_csv_path

    def run_analysis(self):
        # Creating a txt file in the report_path
        filename = os.path.join(self.report_path, "report" + ".txt")

        # Assigning csv file to a variable call 'data'
        self.data = pd.read_csv(self.csv_path)

        # Create a function to separate out numerical and categorical data
        ## Using this function to ensure that all non-numerical in a numerical column
        ## and non-categorical in a categorical column is annotated


        self.categorical_variable = self.cat_variable(self.data)
        self.numerical_variable = self.num_variable(self.data)

        # Assigning variable filename to report and enable writing mode
        report = open(filename, "w")

        # Execute overview function in model module
        self.data = model.overview(self.data, self.numerical_variable, report)

        # Create a function to decide whether to drop all NA values or replace them
        ## Drop it if NAN count < 5 %
        self.nan_prop = (self.data.isna().mean().round(2) * 100)  # Show % of NaN values per column

        cols_to_drop = self.drop_na()

        self.data = self.data.dropna(subset=cols_to_drop)

        ## Using Imputer to fill NaN values
        ## Counting the proportion of NaN
        cols_to_fill = self.fill_na()

        cat_var_tofill = []
        num_var_tofill = []

        for var in cols_to_fill:
            if var in self.categorical_variable:
                cat_var_tofill.append(var)
            else:
                num_var_tofill.append(var)

        imp_cat = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
        try:
            self.data[cat_var_tofill] = imp_cat.fit_transform(self.data[cat_var_tofill])
        except ValueError:
            pass

        imp_num = SimpleImputer(missing_values=np.nan, strategy='median')
        try:
            self.data[num_var_tofill] = imp_num.fit_transform(self.data[num_var_tofill])
        except ValueError:
            pass

        self.data = self.outlier()

        ## Creating possible combinations among a list of numerical variables
        num_var_combination = list(itertools.combinations(self.numerical_variable, 2))

        ## Creating possible combinations among a list of categorical variables
        cat_var_combination = list(itertools.combinations(self.categorical_variable, 2))

        ## Creating possible combinations among a list of numerical and categorical variuable
        catnum_combination = list(itertools.product(self.numerical_variable, self.categorical_variable))

        ## Running the report now
        model.run(num_var_combination, catnum_combination, cat_var_combination, report, self.data)

        # Create an output file that shows cleaned data
        data2 = self.data.copy()
        data2.to_csv(r'{}/cleaned_csv.csv'.format(self.clean_csv_path), index=False)

        # Running plot.py from Graph package
        plot.run(self.data, self.categorical_variable, self.numerical_variable, num_var_combination, cat_var_combination,
                 catnum_combination, self.plot_path)

    def cat_variable(self, df):
        return list(df.select_dtypes(include=['category', 'object']))

    def num_variable(self, df):
        return list(df.select_dtypes(exclude=['category', 'object']))

    def drop_na(self):
        return [i for i, v in self.nan_prop.items() if 5 > v > 0]

    # Create a function to process outlier data
    def outlier(self):
        z = np.abs(stats.zscore(self.data[self.numerical_variable]))
        z_data = self.data[(z < 3).all(axis=1)]  # Remove any outliers with Z-score > 3 or < -3
        return z_data

    def fill_na(self):
        return [i for i, v in self.nan_prop.items() if v > 5]

'''
# Running program
if __name__ == "__main__":
    csv_path = "./KHOU.csv"
    plot_path = "./"
    report_path = "./"
    clean_csv_path = "./"
    test = ReportAnalyzer()
    test.set_csv_path(csv_path)
    test.set_plot_path(plot_path)
    test.set_report_path(report_path)
    test.set_clean_csv_path(clean_csv_path)
    test.run_analysis()
'''
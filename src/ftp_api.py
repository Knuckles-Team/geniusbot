#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import zipfile
import pandas as pd
import glob
import os
import regex


# This class allows the user to interface with FTPs
class FTPAPI:
    # Create a log file
    paramiko.util.log_to_file("paramiko.log")
    host = None
    port = None
    transport = None
    username = None
    password = None
    sftp = None
    filepath = None
    localpath = None
    extract_dir = None

    def __init__(self, host, port, username, password):
        # Open an SFTP transport channel
        self.host = host
        self.port = port
        self.transport = paramiko.Transport((self.host, self.port))
        # Authenticate FTP Site Credentials
        self.username = username
        self.password = password
        self.transport.connect(None, self.username, self.password)
        # Initialize SFTPClient Transport Channel
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    # Filepath is the archive location within the FTP Site
    def set_filepath(self, path):
        self.filepath = path

    # Localpath is the location on the local machine to store the archive.zip
    def set_localpath(self, path):
        self.localpath = path

    def set_extract_dir(self, path):
        self.extract_dir = path

    # Download from FTP Site
    def ftp_download(self):
        print("Beginning Downloading")
        self.sftp.get(self.filepath, self.localpath)
        print("Download Complete")

    # Unzip to Extract directory in the Downloads folder.
    def unzip_files(self):
        with zipfile.ZipFile(self.localpath, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)

    # List the files in the DEU extract THIS IS NOT IMPLEMENTED YET
    def list_deu_files(self):
        for root, dirs, files in os.walk(self.extract_dir):
            for file in files:
                if regex.match(file):
                    print(file)

    # Load data to pandas data frame
    def load_dataframe(self):
        # Path of Folder with all the CSV files.
        path = os.curdir
        all_files = glob.glob(os.path.join(path, "*.csv"))

        # Load each CSV into a data frame, and concatenate all data frames into 1 data frame.
        df_from_each_file = (pd.read_csv(f) for f in all_files)
        concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
        # Load into Pandas
        print(pd.read_csv('./file.csv'))

    # Upload to FTP Site (If Necessary)
    def ftp_upload(self):
        filepath = "/home/zest.jpg"
        localpath = "/home/test.jpg"
        self.sftp.put(localpath, filepath)

    def ftp_close(self):
        # Close Connection to FTP Site
        print("Closing Connections")
        if self.sftp: self.sftp.close()
        if self.transport: self.transport.close()
        print("Done")

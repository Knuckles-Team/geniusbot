#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal


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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib.metadata
import os
import sys


def check_package(package: str = "None") -> bool:
    found = False
    try:
        version = importlib.metadata.version(package)
        print('{} ({}) is installed'.format(package, version))
        found = True
    except importlib.metadata.PackageNotFoundError:
        print('{} is NOT installed'.format(package))
    return found


def resource_path(relative_path: str = "None") -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS2
        except Exception:
            base_path = os.path.dirname(os.path.dirname(__file__))
    if not os.path.exists(base_path):
        base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

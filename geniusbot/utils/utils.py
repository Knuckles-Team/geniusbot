#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib.metadata
import os
import logging
logger = logging.getLogger('geniusbot')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('geniusbot.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def check_package(package: str = "None") -> bool:
    found = False
    try:
        version = importlib.metadata.version(package)
        logger.info('{} ({}) is installed'.format(package, version))
        found = True
    except importlib.metadata.PackageNotFoundError:
        logger.info('{} is NOT installed'.format(package))
    return found


def resource_path(relative_path: str = "None") -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = ""
    try:
        if "_MEIPASS" in os.environ:
            base_path = os.environ["_MEIPASS"]
        if "_MEIPASS2" in os.environ:
            base_path = os.environ["_MEIPASS2"]
    except Exception:
        base_path = os.path.dirname(os.path.dirname(__file__))
    if not os.path.exists(base_path) or base_path == "":
        base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

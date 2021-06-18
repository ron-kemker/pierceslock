# -*- coding: utf-8 -*-
"""
build.py
By Ronald Kemker
18 Jun 2021

Description: This compiles all of the code into a standalone application.

"""
import PyInstaller.__main__
import os, shutil

PyInstaller.__main__.run([
    'application.py',
    '--onefile',
    '-w',
    '-n pierceslock']
    )

shutil.rmtree('build')
shutil.copytree('img', 'dist/img')
shutil.copytree('keys', 'dist/keys')

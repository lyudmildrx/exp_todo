# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

version_filename = os.path.join(os.path.dirname(__file__), 'VERSION')
version = open(version_filename).read().strip()

setup(
    name = 'int_todo',
    version = version,
    author = 'Johannes Bornhold',
    author_email = 'johannes@bornhold.name',
    description = 'Example application to work with todo items',
    url = '',
    install_requires = [
        'distribute',
        # TODO: Make this work with Django 1.5 as well.
        'django<1.5',
        'django-piston',
        'south',
        ],
    package_dir = {'': '.'},
    packages = find_packages('.'),
    include_package_data = True,
    package_data = {
        },
    namespace_packages = [
        ],
    entry_points = {
        },
    zip_safe = False,
    )

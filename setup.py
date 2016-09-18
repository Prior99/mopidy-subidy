from __future__ import unicode_literals

import re
from setuptools import setup, get_packages


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']

setup(
    name='Mopidy-Subidy',
    version=get_version('mopidy_subidy/__init__.py'),
    url='http://github.com/prior99/mopidy-subidy/',
    license='MIT',
    author='ptiot99',
    author_email='fgnodtke@cronosx.de',
    description='Improved Subsonic extension for Mopidy',
    long_description=open('README.md').read(),
    packages=get_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 2.0',
        'py-sonic',
        'Pykka >= 1.1'
    ],
    entry_points={
        b'mopidy.ext': [
            'subidy = mopidy_subidy:SubidyExtension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players'
    ]
)

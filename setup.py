from __future__ import unicode_literals

import re
from setuptools import setup, find_packages


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']

setup(
    name='Mopidy-Subidy',
    version=get_version('mopidy_subidy/__init__.py'),
    url='http://github.com/prior99/mopidy-subidy/',
    license='BSD-3-Clause',
    author='prior99',
    author_email='fgnodtke@cronosx.de',
    description='Improved Subsonic extension for Mopidy',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 2.0',
        'py-sonic >= 0.6.1',
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
        'License :: OSI Approved :: BSD 3-Clause',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players'
    ]
)

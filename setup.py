import os
import re
from setuptools import setup


def get_version_from_init():
    file = open(os.path.join(os.path.dirname(__file__), 'pynats', '__init__.py'))

    regexp = re.compile(r".*__version__ = '(.*?)'", re.S)
    version = regexp.match(file.read()).group(1)
    file.close()

    return version


setup(
    name='pynats',
    license='MIT',
    author='Maximo Cuadros',
    author_email='mcuadros@gmail.com',
    version=get_version_from_init(),
    url='https://github.com/mcuadros/pynats',
    packages=[
        'pynats'
    ],
    install_requires=[
        'mocket == 1.1.1'
    ]
)

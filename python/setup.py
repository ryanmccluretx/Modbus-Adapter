import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cbModbus",
    version = "0.0.1",
    author = "Jim Bouquet",
    author_email = "jbouquet@clearblade.com",
    description = ("A modbus client and server adapter implementation for use with the ClearBlade Platform."),
    license = "BSD",
    keywords = "clearblade adapter modbus",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['cbModBus'],
    long_description=read('README.md'),
    install_requires=['twisted', 'service_identity', 'pymodbus', 'clearblade']
)
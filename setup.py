"""
Setup script.
"""
from setuptools import setup, find_packages

extras = {}

all_extras = set()
for key, libraries in extras.items():
    all_extras.update(libraries)

extras['all'] = all_extras

setup(name='pyinterp',
      version='0.8.0',
      description='Pre built pyinterp lib',
      packages=find_packages(),
      include_package_data=True,
      extras_require=extras,
      python_requires='~=3.8',
      )

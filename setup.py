
# python setup.py --dry-run --verbose install

from setuptools import setup, find_packages

from distutils.core import setup

setup(
    name='ISYlib',
    version='0.1.3',
    author='Peter Shipley',
    author_email='Peter.Shipley@gmail.com',
    packages=find_packages(),
    data_files=[('examples', ['bin/isy_find.py','bin/isy_nodes.py',
    'bin/isy_progs.py', 'bin/isy_log.py',
    'bin/isy_var.py','bin/isy_showevents.py', 'bin/isy_nestset.py',
    'bin/isy_net_wol.py'])],
    url='https://github.com/evilpete/ISYlib-python',
    license='BSD',
    description='Python API for the ISY home automation controller.',
    long_description=open('README.txt').read(),
)

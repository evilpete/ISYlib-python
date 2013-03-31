

from distutils.core import setup

setup(
    name='ISYlib',
    version='0.1.0',
    author='Peter Shipley',
    author_email='Peter.Shipley@gmail.com',
    packages=['ISY'],
    scripts=['bin/isy_find.py','bin/isy_list.py','bin/isy_log.py','bin/isy_showevents.py'],
    url='https://github.com/evilpete/ISYlib-python',
    license='LICENSE.txt',
    description='Python API for the ISY home automation controller.',
    long_description=open('README.txt').read(),
    install_requires=[],
)

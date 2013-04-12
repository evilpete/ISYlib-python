

from distutils.core import setup

setup(
    name='ISYlib',
    version='0.1.3',
    author='Peter Shipley',
    author_email='Peter.Shipley@gmail.com',
    packages=['ISY'],
    scripts=['bin/isy_find.py','bin/isy_nodes.py',
    'bin/isy_prog.py', 'bin/isy_log.py',
    'bin/isy_var.py','bin/isy_showevents.py', 'binisy_nestset.py'],
    url='https://github.com/evilpete/ISYlib-python',
    license='LICENSE.txt',
    description='Python API for the ISY home automation controller.',
    long_description=open('README.txt').read(),
)


# python setup.py --dry-run --verbose install

import os.path
from distutils.command.install_scripts import install_scripts
#from distutils.core import setup
from setuptools import setup, find_packages
# import ssl

# ssl._create_default_https_context = ssl._create_unverified_context

# python setup.py --dry-run --verbose install
# python setup.py install --record files.txt


class install_scripts_and_symlinks(install_scripts):
    '''Like install_scripts, but also replicating nonexistent symlinks'''
    def run(self):
        # print "=============install_scripts_and_symlinks run"
        install_scripts.run(self)
        # Replicate symlinks if they don't exist
        for script in self.distribution.scripts:
            # print  "\n---script = ",script
            if os.path.islink(script):
                target = os.readlink(script)
                newlink = os.path.join(self.install_dir, os.path.basename(script))

setup(
    name='ISYlib',
    version='0.1.20170829',
    author='Peter Shipley',
    author_email='Peter.Shipley@gmail.com',
    packages=find_packages(),
    scripts=['bin/isy_find.py', 'bin/isy_log.py', 'bin/isy_nestset.py',
             'bin/isy_net_wol.py', 'bin/isy_progs.py',
             'bin/isy_showevents.py', 'bin/isy_web.py',
             'bin/isy_nodes.py', 'bin/isy_var.py'],
    url='https://github.com/evilpete/ISYlib-python',
    license='BSD',
    download_url='https://github.com/evilpete/ISYlib-python/archive/0.1.20170829.tar.gz',
    description='Python API for the ISY home automation controller.',
    install_requires=['requests'],
    long_description=open('README.txt').read(),
    cmdclass={'install_scripts': install_scripts_and_symlinks}
)

#    data_files=[
#       ('examples', ['bin/isy_find.py', 'bin/isy_progs.py',
#               'bin/isy_log.py', 'bin/isy_net_wol.py']),
#       ('bin', ['bin/isy_nodes.py', 'bin/isy_var.py'])
#       ],

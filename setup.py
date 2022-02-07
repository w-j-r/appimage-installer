from setuptools import setup, find_packages
import os

setup(
    name='AppImage Installer',
    version='0.0.1',
    description='A simple program to integrate your AppImages.',
    license='GPL-3',
    author='w-j-r',
    author_email='completelyunrelated@live.com',
    packages=find_packages(),
    install_requires=['PyQt5'],
    classifiers=['Topic :: System :: Installation/Setup',
                 'Programming Language :: Python :: 3.9',
                 'Operating System :: POSIX :: Linux'],
    
    entry_points={'gui_scripts': ['appimage_installer = appimage_installer.appinstallerGUI:InstallerGUI']},
    
    data_files=[(f'/home/{os.getlogin()}/.local/share/applications',
                 ["appimage-installer.desktop"])]

)


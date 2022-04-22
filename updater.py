import os
import shutil
import sys
import urllib.request
import glob
import zipfile
import platform
from subprocess import Popen


# change working directory to script's location
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.y
    running_updater_path = sys._MEIPASS
else:
    running_updater_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(running_updater_path)


def download_zip(url: str):
    print('Downloading zip from {0}...'.format(url))
    urllib.request.urlretrieve(url, "archive.zip")


def backup_config(backend_folder: str):
    print('Backing up configuration...')
    config_backup_path = os.path.join(backend_folder, "configuration.txt")
    config_path = os.path.join('./../', config_backup_path)
    if os.path.exists(config_path):
        if not os.path.exists(backend_folder):
            os.makedirs(backend_folder)
        shutil.copyfile(config_path, config_backup_path)


def restore_config(backend_folder: str):
    print('Restoring configuration...')
    config_backup_path = os.path.join(backend_folder, "configuration.txt")
    config_path = os.path.join('./../', config_backup_path)
    if os.path.exists(config_backup_path):
        shutil.copyfile(config_backup_path, config_path)


def clear_converter_folder():
    print('Clearing converter folder...')

    paths = glob.glob('../*', recursive=False)
    path: str
    for path in paths:
        if os.path.isdir(path):
            if os.path.samefile(path, running_updater_path):
                continue
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)


def extract_zip():
    print('Extracting zip...')
    with zipfile.ZipFile("archive.zip", 'r') as zip_ref:
        zip_ref.extractall('..')


def open_frontend():
    os.chdir('../')

    # https://stackoverflow.com/a/13256908/10249243
    # set system/version dependent "start_new_session" analogs
    kwargs = {}

    if platform.system() == 'Windows':
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms684863%28v=vs.85%29.aspx
        DETACHED_PROCESS = 0x00000008
        kwargs.update(creationflags=DETACHED_PROCESS)
        Popen(["ConverterFrontend.exe"], close_fds=True, **kwargs)
    else:
        kwargs.update(start_new_session=True)
        Popen(["ConverterFrontend"], close_fds=True, **kwargs)


# First argument: URL of converter release .zip to download
# Second argument: name of converter backend folder
if len(sys.argv) != 3:
    print('Incorrect number of arguments! Should be 2.')
    sys.exit(1)

converterZipURL = sys.argv[1]
converterBackendFolder = sys.argv[2]
if not os.path.isdir(os.path.join('..', converterBackendFolder)):
    print('Converter backend folder {0} does not exist!'.format(converterBackendFolder))
    sys.exit(2)

download_zip(converterZipURL)
backup_config(converterBackendFolder)
clear_converter_folder()
extract_zip()
restore_config(converterBackendFolder)
print('Update completed successfully!')
open_frontend()
sys.exit(0)

import logging
import os
import shutil
import sys
import glob
import platform
from subprocess import Popen
from urllib.request import urlopen
from urllib.request import urlretrieve
import cgi
import pathlib


# change working directory to script's location
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS
    running_updater_path = sys._MEIPASS
else:
    running_updater_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(running_updater_path)


# Logging configuration: log to file and console.
LOG_FILE_NAME = 'updater.log'
logging.basicConfig(filename=LOG_FILE_NAME, encoding='utf-8', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def download_archive(url: str):
    remotefile = urlopen(url)
    content_header = remotefile.info()['Content-Disposition']
    value, params = cgi.parse_header(content_header)
    filename = params["filename"]
    logging.info('Downloading archive from {0}...'.format(url))
    urlretrieve(url, filename)

    return filename


def backup_config(backend_folder: str):
    logging.info('Backing up configuration...')
    config_backup_path = os.path.join(backend_folder, "configuration.txt")
    config_path = os.path.join('./../', config_backup_path)
    if os.path.exists(config_path):
        if not os.path.exists(backend_folder):
            os.makedirs(backend_folder)
        shutil.copyfile(config_path, config_backup_path)


def restore_config(backend_folder: str):
    logging.info('Restoring configuration...')
    config_backup_path = os.path.join(backend_folder, "configuration.txt")
    config_path = os.path.join('./../', config_backup_path)
    if os.path.exists(config_backup_path):
        shutil.copyfile(config_backup_path, config_path)


def clear_converter_folder():
    logging.info('Clearing converter folder...')

    paths = glob.glob('../*', recursive=False)
    path: str
    for path in paths:
        if os.path.isdir(path):
            # remove directory
            if os.path.samefile(path, running_updater_path):
                # Don't remove running updater folder.
                continue
            shutil.rmtree(path, ignore_errors=True)
        else:
            # remove file
            try:
                absolute_path = pathlib.Path(os.path.abspath(path))
                absolute_path.unlink()
            except FileNotFoundError:
                pass
            except Exception as e:
                logging.warning(f"Failed to remove file: {e}")


def extract_archive(archive_filename):
    logging.info(f'Extracting archive {archive_filename}...')
    shutil.unpack_archive(archive_filename, '../')


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
        Popen(["./ConverterFrontend"], close_fds=True, **kwargs)


# First argument: URL of converter release .zip to download
# Second argument: name of converter backend folder
if len(sys.argv) != 3:
    logging.error('Incorrect number of arguments! Should be 2.')
    sys.exit(1)

converterZipURL = sys.argv[1]
converterBackendFolder = sys.argv[2]
if not os.path.isdir(os.path.join('..', converterBackendFolder)):
    logging.error('Converter backend folder {0} does not exist!'.format(converterBackendFolder))
    sys.exit(2)

archive_filename = download_archive(converterZipURL)
backup_config(converterBackendFolder)
clear_converter_folder()
extract_archive(archive_filename)
restore_config(converterBackendFolder)
logging.info('Update completed successfully!')
open_frontend()
sys.exit(0)

import os
import shutil
import subprocess


def find_wkhtmltopdf() -> str or None:
    """
    Attempts to find the wkhtmltopdf executable in the system.
    :return:  The path to the executable, or None if not found.
    """
    # First, attempt to find wkhtmltopdf in the system PATH
    path = shutil.which('wkhtmltopdf')
    if path:
        try:
            subprocess.run([path, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # If not found, check common paths including the environment variable
    common_paths = [
        '/usr/local/bin/wkhtmltopdf',
        '/usr/bin/wkhtmltopdf',
        'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe',
        'C:/Program Files (x86)/wkhtmltopdf/bin/wkhtmltopdf.exe',
        os.environ.get('WKHTMLTOPDF_PATH')  # Include environment variable in the common paths
    ]

    # Filter out None in case WKHTMLTOPDF_PATH is not set
    common_paths = [path for path in common_paths if path]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return None

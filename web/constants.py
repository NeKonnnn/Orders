import os

############################################
# Paths to specific parts of project

# Where to save all pdf/xlsx/html reports
PATH_TO_REPORTS = 'reports/'

# Path to database
DB_PATH = 'demo.db'

# Path to app' icon
ICON_PATH = './images/favicon.ico'

# Path to app' general style
GENERAL_STYLE_PATH = './styles/general_style.qss'

# Path to app' consoles style
CONSOLE_STYLE_PATH = './styles/console_widget.qss'

############################################
# Constants specifically for functions in app

# The default name
DEFAULT_NAME = 'CRUD'

# The following tables will not be shown in the GUI for default users (for admins, all tables are shown)
TABLES_NOT_TO_SHOW = {'admin': [],
                      'user': ['sqlite_sequence', 'users', 'user_roles', 'translations'],
                      'viewer': ['sqlite_sequence', 'users', 'user_roles', 'translations'],
                      }

# Is registration allowed?
ALLOW_REGISTER = True

# Hash passwords?
HASH_PASSWORDS = False

# Shown plugins
PLUGINS = ['reports', 'languages', 'imports']

# Default language
DEFAULT_LANGUAGE = 'ru'

# Available langs
AVAILABLE_LANGUAGES = ['en', 'ru']

# Available for all CRUD buttons
AVAILABLE_BUTTONS = ['add_record', 'edit_record', 'delete_record']


###############
def allowed_to_see(user_role: str, table_name: str) -> bool:
    """
    Checks if a given user is allowed to see a given table.
    :param user_role:  The user's role.
    :param table_name:  The table to check.
    :return:  True if the user is allowed to see the table, False otherwise.
    """
    return table_name not in TABLES_NOT_TO_SHOW[user_role]


def get_absolute_path(relative_path: str, script_dir: str = None, add_file_prefix: bool = False) -> str:
    """
    Generates an absolute path for a given relative path. Optionally, it can add a 'file:///' prefix.

    :param relative_path: The relative file path to convert.
    :param script_dir: The directory of the script, if needed to construct the absolute path.
    :param add_file_prefix: If True (default), adds 'file:///' prefix to the absolute path.
                            Set to False to return the absolute path without the prefix.
    :return: The absolute file path, with or without 'file:///' prefix.
    """
    if script_dir:
        absolute_path = os.path.join(script_dir, relative_path)
    else:
        absolute_path = os.path.abspath(relative_path)

    normalized_path = absolute_path.replace('\\', '/')

    if add_file_prefix:
        return 'file:///' + normalized_path
    else:
        return normalized_path

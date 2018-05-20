"""Module responsible for reading/writing cheat sheet json to file."""
import os
import json
import warnings
import sjb.common.config
import sjb.cs.classes
import sjb.cs.display

_SUITE = 'sjb'
_APP = 'cheatsheet'
_DEFAULT_LIST_FILE='cheatsheet'
_LIST_FILE_EXTENSION = '.json'


def initialize_environment():
  """Checks that necessary user dirs exist and creates them if not.

  Raises:
    FileExistsError: if one of the required files already exists but it is of
      the wrong type (e.g. its a file instead of a directory).
    PermissionError: if program lacks permissions to create a needed directory.
    Exception: any other issue in setting up environment.
  """
  sjb.common.config.initialize_environment(_APP, suite_name=_SUITE)


def _get_default_list_file(list=None):
  """Gets the full pathname of the cheatsheet file named list.

  Args:
    list: str a short name giving the local list file name, e.g. 'bash'. This
      should not contain a file extension.
  """
  list = list or _DEFAULT_LIST_FILE
  return os.path.join(
    sjb.common.config.get_user_app_data_dir(_APP, suite_name=_SUITE),
    list + _LIST_FILE_EXTENSION)

def get_all_list_files():
  """Returns a list of all the cheatsheet lists stored in the data directory.

  Returns:
    List of the local file names (without the extensions) for all of the c
      heatsheet lists stored in the data directory.
  """
  dir = sjb.common.config.get_user_app_data_dir(_APP, suite_name=_SUITE)
  files = os.listdir(dir)
  matching = []
  for f in files:
    if not os.path.isfile(os.path.join(dir, f)):
      continue
    # Check that it has correct extension.
    if not f.endswith(_LIST_FILE_EXTENSION):
      continue
    matching.append(f[0:(len(f)-len(_LIST_FILE_EXTENSION))])
  return matching

def save_cheatsheet(cs, list=None, listpath=None):
  """Saves a cheatsheet list to a json file.

  Arguments:
    list: str An optional local list name to save the cheatsheet list as. The
      resulting file is saved in the default application directory with the
      local file name 'list.json'. This argument is mututally exclusive with
      listpath.
    listpath: str An optional full path name to save the cheatsheet list to.
      This argument is mututally exclusive with listpath.

  Raises:
    Exception: If both list and listpath are given.
  """
  if list and listpath:
    raise Exception(
      'Cannot set both list and listpath args (this should never happen')

  # First check list/listpath arguments, then try the file that the cheatsheet
  # was read from. If none of those exist, use the default list file.
  # TODO: reconsider this logic. Is this really the best behavior?
  if list:
    fname = _get_default_list_file(list=list)
  else:
    fname = listpath or cs.source_filename or _get_default_list_file()

  # TODO: Temporary replacement of poor validation-in-encoding code
  for item in cs.items:
    item.validate()

  json_file = open(fname, 'w')
  json_file.write(json.dumps(cs.to_dict(), indent=2))
  json_file.close()

def load_cheatsheet(list=None, listpath=None):
  """Loads a cheat sheet from a json file.

  Arguments:
    list: str An optional local list name to read the cheatsheet from. This
      looks for a file in the default application directory with the local
      file name 'list.json'. This argument is mututally exclusive with
      listpath.
    listpath: str An optional full path name to read the cheatsheet from.
      This argument is mututally exclusive with listpath.

  Returns:
    CheatSheet: object with contents given by the loaded file.

  Raises:
    Exception: If both list and listpath are given.
  """
  if list is not None and listpath is not None:
    raise Exception(
      'Cannot set both list and listpath args (this should never happen.)')

  fname = listpath or _get_default_list_file(list=list)

  # If file doesn't exist, return a new blank cheat sheet.
  if not os.path.isfile(fname):
    # TODO: Improve this
    warnings.warn('no cheatsheet file found', UserWarning)
    return sjb.cs.classes.CheatSheet(source_fname=fname)

  json_file = open(fname)
  json_dict = json.load(json_file)
  json_file.close()
  return sjb.cs.classes.CheatSheet.from_dict(json_dict, fname)

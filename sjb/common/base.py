"""Base classes file used in cheatsheet and todo."""
import abc
import time


class Error(Exception):
  """Base class for exceptions for this program."""
  pass


class ReadOnlyError(Error):
  """Raised when attempts to change a read only property."""
  pass


class IllegalStateError(Error):
  """Error used to signal something is wrong, but its not clear why."""
  def __init__(self, method, msg):
    Error.__init__(self)
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('IllegalStateError', method, msg)


class ValidationError(Error):
  """Error raised when item or list validation fails."""
  def __init__(self, msg):
    Error.__init__(self)
    self.message = '%s: %s' % ('ValidationError', msg)


class InvalidIDError(Error):
  """Error raised when a specified item oid does not exist."""

  def __init__(self, method, msg):
    Error.__init__(self)
    self.message = '%s in method %s\n\tMSG: %s' % (
      'InvalidIDError', method, msg)


class Item(abc.ABC):
  """Abstract class representing an item stored in a list."""

  def __init__(self, oid=None):
    self._oid = oid

  @property
  def oid(self):
    """int: the unique ID representing this Item."""
    return self._oid

  @oid.setter
  def oid(self, value):
    if self._oid is None:
      self._oid = value
    else:
      raise ReadOnlyError()

  @abc.abstractmethod
  def __eq__(self, other):
    """Tests if two items have all the exact same values."""
    return self.oid == other.oid

  @abc.abstractmethod
  def _validate(self):
    """Method that checks validity of item state before writing to database.

    Returns: nothing.

    Raises:
      ValidationError: If validation fails.
    """
    if not self._oid or not isinstance(self._oid, int):
      raise ValidationError('item ID not set or set to non-integer')
    return

  @abc.abstractmethod
  def _to_dict(self):
    """Converts data to a dict suitable for writing to a file as json.

    Returns:
      dict: stable dict of values suitable to be written as JSON.
    """
    return

class ItemMatcher(abc.ABC):
  """Abstract class representing a boolean condition for matching an Item."""

  @abc.abstractmethod
  def matches(self, item):
    """Returns true if item matches some criteria, false otherwise.

    Returns:
      bool: True if Item item matches some criteria. False otherwise.
    """
    return True


class ItemList(abc.ABC):
  """Abstract class representing a collection of Item objects."""

  def __init__(self, version=None, modified_date=None):
    self._version = version
    self._modified = False
    self._modified_date = modified_date

    self._items = []
    self._last_item_id = 0
    self._oid_set = set()

  @property
  def version(self):
    """str: The application version this item list uses."""
    return self._version

  @property
  def modified(self):
    """bool: Indicates if this list has been modified since it was loaded."""
    return self._modified

  @property
  def modified_date(self):
    """# TODO: Timestamp when this list was last modified."""
    return self._modified_date

  @property
  def items(self):
    """# TODO: list of Item objects in this ItemList."""
    return self._items

  def size(self):
    return len(self._items)

  def _mark_modified(self, timestamp=None):
    """Marks this list as modified at the given timestamp.

    If no timestamp is provided this uses the current time.
    """
    self._modified = True
    self._modified_date = timestamp if timestamp is not None else time.time()

  def _get_item_index(self, oid):
    """Returns the index of the Item with the given oid in self._items.

    Returns:
      int: The index in self._items of the Item with the given oid.

    Raises:
      InvalidIDError: If no Item object has the given oid.
    """
    for i in range(len(self._items)):
      if oid == self._items[i].oid:
        return i
    raise InvalidIDError(
      'ItemList.get_item_index', 'Item with given oid not found!')

  def get_item(self, oid):
    """Returns item with the given oid.

    Returns:
      Item: the Item object with the matching oid.

    Raises:
      InvalidIDError: If no item has a matching oid.
    """
    return self._items[self._get_item_index(oid)]

  @abc.abstractmethod
  def add_item(self, item, initial_load=False):
    """Adds an item to this list.

    Args:
      item (Item): The item to add to this list. It should not have its oid
        property set unless initial_load is True.
      initial_load (bool): Indicates that this item is being read from a
        database, i.e. not being added for this first time.

    Raises:
      IllegalStateError: If initial_load is False but the item has an oid.
      IllegalStateError: If initial_load is True but the item lacks an oid.
    """
    # Make sure any 'init load' item already has an oid
    if initial_load and not item.oid:
      raise IllegalStateError('ItemList.add_item', 'Old item missing oid!')
    # Make sure any new item does not have an oid
    if not initial_load and item.oid:
      raise IllegalStateError('ItemList.add_item', 'New item has oid!')

    if not initial_load:
      # Set the oid correctly
      self._last_item_id += 1
      item.oid = self._last_item_id

      # Mark the list as modified.
      self._mark_modified()
    else:
      # Check that id is not already used.
      if item.oid in self._oid_set:
        raise IllegalStateError('ItemList.add_item', 'Duplicate item ID')
      self._last_item_id = max(item.oid, self._last_item_id)

    self._oid_set.add(item.oid)
    self._items.append(item)

  def query_items(self, item_matcher):
    """Abstract method that queries item list for some subset.

    Args:
      ItemMatcher: object used to filter the items.

    Returns:
      # TODO: list of Item objects.
    """
    return [item for item in self.items if item_matcher.matches(item)]

  @abc.abstractmethod
  def remove_item(self, oid):
    """Removes the item with the specified oid and updates meta data.

    Returns:
      Item: The removed item object.

    Raises:
      InvalidIDError: If no item has a matching oid.
    """
    ind = self._get_item_index(oid)
    removed = self._items.pop(ind)
    # Mark as modified and remove id from id set
    self._mark_modified()
    self._oid_set.remove(removed.oid)
    return removed

  @abc.abstractmethod
  def to_dict(self):
    """Converts data to a dict suitable for writing to a file as json.

    Returns:
      dict: stable dict of values suitable to be written as JSON.
    """
    return

  def validate(self):
    """Method that checks validity of list state before writing to database.

    Returns: nothing.

    Raises:
      ValidationError: If validation fails.
    """
    for item in self.items:
      item._validate()

import json
import os  # For relative paths
from threading import Lock # For Singleton


class SingletonMeta(type):
    """Abstract base class used for the Singleton design pattern.

    Attributes
    ----------
    _instanced: dictionary
        Dictionary that stores each class' singleton instance.
    _lock: Lock object
        Locks access to the dictionary of instances when a thread is accessing it.

    Methods
    -------
    __call__(cls, *args, **kwargs):
        Returns a pointer to the single instance of the class.

        This is called whenever an object is created. It will create an instance of the class
        if it isn't found, otherwise it returns the previously created instance. This is thread-safe.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """Returns a pointer to the single instance of the class.

        This is called whenever an object is created. It will create an instance of the class
        if it isn't found, otherwise it returns the previously created instance. This is thread-safe.
        """

        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]



class AoBinData(metaclass=SingletonMeta):
    """Represents the AO Data from the game's extracted binaries.

    This should act as the primary interface to AO data.

    ...

    Properties
    ----------
    _item_name: dictionary
        Dictionary of "readable" item names and it's JSON data.

    Methods
    -------
    __init__(self, item_file, name_file)
        Constructor sets location of relevant data files.
    print_head(self, n)
        Prints the first n items of _item_name.
    _map_item_names(self, items, names)
        Builds the _item_name dictionary.
    """

    _item_name = {}

    def __init__(self, item_file='..\\items.json', name_file='..\\formatted\\items.json'):
        """Constructor sets location of relevant data files.

        Performs any additional initialization e.g. building complex class attributes.

        Parameters
        ----------
        item_file: str
            Location of JSON file containing item data.
        name_file: str
            Location of JSON file containing localization data for items.

        Raises
        ------
        Assertion Error
            If any file location is incorrect or fails to load.
        """

        try:
            fp_items = os.path.join(os.path.dirname(__file__), item_file)
            fp_names = os.path.join(os.path.dirname(__file__), name_file)

            items = []
            names = []

            with open(fp_items) as json_file:
                temp_items = json.load(json_file)
                items.extend(temp_items['items']['equipmentitem'])
                items.extend(temp_items['items']['weapon'])
                items.extend(temp_items['items']['mount'])
                assert len(items) > 0, "Failed to load items"

            with open(fp_names, encoding='utf8') as json_file:
                names = json.load(json_file)
                names = [x for x in names if x['LocalizedNames'] != None]
                assert len(names) > 0, "Failed to load item names"

            self._map_item_names(items, names)

        except Exception as e:
            print(f'Failed to create: {type(self).__name__}')
            print(f'{e}')
            raise


    def print_head(self, n=5):
        """Prints the first n items of _item_name.

        Parameters
        ----------
        n: int (Default: 5)
            The number of items to print.
        """

        i = 0
        for name, item in self._item_name.items():
            if i >= n:
                return

            print(f'{name}: {item}')
            i = i + 1

    
    def _map_item_names(self, items, names):
        """Builds the _item_name dictionary.

        Sets the keys to the item's localized name. Sets the value to the JSON data of the item.

        Parameters
        ----------
        items: JSON object
            Item data from the forked AO Binary Data repo.
        names: JSON object
            Localization data for the items from the forked AO Binary Data repo.

        Raises
        ------
        Assertion Error
            If there are no item/name pairs found in the given parameters.
        """
        
        res = {}
        try:
            for item in items:
                item_name = [x['LocalizedNames']['EN-US'] for x in names if x['UniqueName'] == item['@uniquename']]
                if len(item_name) == 1:
                    res[item_name[0]] = item                     

            assert len(res) > 0, 'Res is empty'

            self._item_name = res
        
        except Exception as e:
            print('Error in _map_item_names()')
            print(f'{e}')
            raise



if __name__ == "__main__":
    abu = AoBinData()

    abu.print_head()
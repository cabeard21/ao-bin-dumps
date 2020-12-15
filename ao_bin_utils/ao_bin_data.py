import json
import os  # For relative paths
from threading import Lock  # For Singleton


class SingletonMeta(type):
    """Abstract base class used for the Singleton design pattern.

    Attributes
    ----------
    _instanced: dictionary
        Dictionary that stores each class' singleton instance.
    _lock: Lock object
        Locks access to the dictionary of instances when a thread
        is accessing it.

    Methods
    -------
    __call__(cls, *args, **kwargs):
        Returns a pointer to the single instance of the class.

        This is called whenever an object is created. It will create
        an instance of the class if it isn't found, otherwise it returns
        the previously created instance. This is thread-safe.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """Returns a pointer to the single instance of the class.

        This is called whenever an object is created.
        It will create an instance of the class if it isn't found,
        otherwise it returns the previously created instance.
        This is thread-safe.
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
    _game: list
        List of dictionaries as read from the game JSON data file.

    Methods
    -------
    __init__(self, item_file, name_file)
        Constructor sets location of relevant data files.
    _map_item_names(self, items, names)
        Builds the _item_name dictionary.
    get_item(item_name, unique)
        Returns item information given the item's name.
    """

    def __init__(
        self,
        item_file='..\\items.json',
        name_file='..\\formatted\\items.json',
        game_file='..\\gamedata.json',
    ):
        """Constructor sets location of relevant data files.

        Performs any additional initialization
            e.g. building complex class attributes.

        Parameters
        ----------
        item_file: str
            Location of JSON file containing item data.
        name_file: str
            Location of JSON file containing localization data for items.
        game_file: str
            Location of JSON file containing game data.
        """

        fp_items = os.path.join(os.path.dirname(__file__), item_file)
        fp_names = os.path.join(os.path.dirname(__file__), name_file)
        fp_game = os.path.join(os.path.dirname(__file__), game_file)

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
            names = [x for x in names if x['LocalizedNames'] is not None]
            assert len(names) > 0, "Failed to load item names"

        with open(fp_game, encoding='utf8') as json_file:
            game = json.load(json_file)
            self._game = game['AO-GameData']

        self._map_item_names(items, names)

    def _map_item_names(self, items, names):
        """Builds the _item_name dictionary.

        Sets the keys to the item's localized name. Sets the value
        to the JSON data of the item.

        Parameters
        ----------
        items: JSON object
            Item data from the forked AO Binary Data repo.
        names: JSON object
            Localization data for the items from the forked
            AO Binary Data repo.
        """

        res = {}
        for item in items:
            item_name = [
                x['LocalizedNames']['EN-US']
                for x in names if x['UniqueName'] == item['@uniquename']
            ]
            if len(item_name) == 1:
                res[item_name[0]] = item

        self._item_name = res

    def get_item(self, item_name, unique=True) -> dict:
        """Returns item information given the item's name.

        Parameters
        ----------
        item_name: str
            The item's name.
        unique: bool
            If true, then item_name is the item's unque name,
            otherwise, it is the item's localized name.

        Returns
        -------
        dictionary
            The item's information as a dictionary, taken from the JSON file.
        """

        res = {}
        if not unique:
            res = self._item_name[item_name]
        else:
            for v in self._item_name.values():
                if v['@uniquename'] == item_name:
                    res = v
                    break

        return res

    def get_quality_table(self):
        """Returns the JSON dictionary portion containing the quality
        information for items.

        Returns
        -------
        dictionary
            The JSON information from game data.
        """

        return self._game['Items']['QualityLevels']['qualitylevel']

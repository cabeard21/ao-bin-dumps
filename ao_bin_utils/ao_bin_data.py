import json
import os  # For relative paths
from threading import Lock  # For Singleton
import re

TIER_FINDER = r"T\d_"


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
    TIER_IDENTIFIERS: list
        List of adjectives used to denote item tiers in local names.

    Methods
    -------
    __init__(self, item_file, name_file)
        Constructor sets location of relevant data files.
    _map_item_names(self, items, names)
        Builds the _item_name dictionary.
    get_item(item_name, unique)
        Returns item information given the item's name.
    get_quality_table(self):
        Returns the JSON dictionary portion containing the quality
        information for items.
    get_unique_name(self, item_name, enchant=0):
        Get an item's unque name from it's local name.
    generate_fixture(self):
        Generates a Django fixture file ready for import.
    """

    def __init__(
        self,
        item_file=os.path.join('..', 'items.json'),
        name_file=os.path.join('..', 'formatted', 'items.json'),
        game_file=os.path.join('..', 'gamedata.json'),
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

        self.TIER_IDENTIFIERS = [
            "Beginner's",
            "Novice's",
            "Journeyman's",
            "Adept's",
            "Expert's",
            "Master's",
            "Grandmaster's",
            "Elder's",
        ]

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
            The item's information as a dictionary, taken from the JSON file. If
            the item is not found, None is returned.
        """

        if unique:
            item_name = (self.get_local_name(item_name) or item_name)

        try:
            return self._item_name[item_name]

        except KeyError:
            return None

    def get_quality_table(self):
        """Returns the JSON dictionary portion containing the quality
        information for items.

        Returns
        -------
        dictionary
            The JSON information from game data.
        """

        return self._game['Items']['QualityLevels']['qualitylevel']

    def get_quality_name(self, quality):
        """Returns the quality level's name.

        Parameters
        ----------
        quality: int
            Number that represents the quality level.

        Returns
        -------
        string
            The name of the quality level in game.
        """

        quality_names = {
            1: 'Normal',
            2: 'Good',
            3: 'Outstanding',
            4: 'Excellent',
            5: 'Masterpiece',
        }
        return quality_names[quality]

    def get_unique_name(self, item_name, enchant=0):
        """Get an item's unque name from it's local name.

        Parameters
        ----------
        item_name: str
            The item's local name.
        enchant: int
            The item's enchant level to add to the unique name. (default: 0)

        Returns
        -------
        string
            Returns the item's unique name with it's enchant level
            appended after '@'. If the item is not found, None is returned.
        """

        if item_name in self._item_name.keys():
            item_data = self._item_name[item_name]
        else:
            # Only base item has been passed, find first tier that works
            for tier_name in self.TIER_IDENTIFIERS:
                test_name = f"{tier_name} {item_name}"
                if test_name in self._item_name.keys():
                    item_data = self._item_name[test_name]

        if item_data is None:
            return None

        return (
            item_data['@uniquename']
            + (f'@{enchant}' if enchant > 0 and enchant < 6 else "")
        )

    def get_local_name(self, item_name):
        """Get an item's local name from it's unique name.

        Parameters
        ----------
        item_name: str
            The item's unique name.

        Returns
        -------
        string
            The item's local name. Returns None if none are found.
        """
        item_name = item_name.split('@')[0]
        for k, v in self._item_name.items():
            if v['@uniquename'] == item_name:
                return k

        return None

    def get_item_tier(self, item):
        """Returns a string with the item's tier and enchant level as a string.

        Parameters
        ----------
        item: str
            The item's unique name w/ enchant level.

        Returns
        -------
        string
            The item's tier and enchant level formated as:

            {tier}.{enchant_lvl} e.g. 4.2
        """

        tier = re.compile(TIER_FINDER).search(item)[0][1]
        enchant_lvl = item.split('@')[-1] if '@' in item else 0
        return (
            f"{tier}" +
            (f".{enchant_lvl}" if enchant_lvl != 0 else '')
        )

    def generate_fixture(self):
        """Generates a Django fixture file ready for import.

        This file is formated to work with a specific Django app. The file
        generated will be in a "fixture" folder that can be software linked to
        the app using it.

        Returns
        -------
        boolean
            True if the statements execute without raising an exception.
        """

        try:
            import os
            output_file = os.sep.join([
                os.path.dirname(__file__), 'fixtures', 'ao_bin_fixture.json'
            ])
            with open(output_file, 'w') as f:

                res = []
                item_types = {}
                item_names = {}
                for k, v in self._item_name.items():
                    current_item_type = v['@shopsubcategory1']

                    # Item Type
                    if current_item_type not in item_types.keys():
                        item_types[current_item_type] = len(item_types) + 1
                        current_res = {
                            'model': 'Equipment.ItemType',
                            'pk': item_types[current_item_type],
                            'fields': {
                                'item_type': current_item_type,
                            }
                        }
                        res.append(current_res)

                    # Item
                    item_name_words = k.split()
                    item_name = [
                        word for word in item_name_words
                        if word not in self.TIER_IDENTIFIERS
                    ]
                    item_name = ' '.join(item_name)
                    if item_name not in item_names.keys():
                        item_names[item_name] = len(item_names) + 1
                        current_res = {
                            'model': 'Equipment.Item',
                            'pk': item_names[item_name],
                            'fields': {
                                'item_name': item_name,
                                'item_type': item_types[current_item_type]
                            }
                        }
                        res.append(current_res)

                json.dump(res, f)

            return True

        except Exception as e:
            print(e)
            raise

        return False

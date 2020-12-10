import json
import os  # For relative paths
from threading import Lock # For Singleton


class SingletonMeta(type):

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]


class AoBinUtils(metaclass=SingletonMeta):

    _item_name = {}

    def __init__(self, item_file='..\\items.json', name_file='..\\formatted\\items.json'):
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
        i = 0
        for name, item in self._item_name.items():
            if i >= n:
                return

            print(f'{name}: {item}')
            i = i + 1

    
    def _map_item_names(self, items, names):
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
    abu = AoBinUtils()

    abu.print_head()
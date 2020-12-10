import json
import os  # For relative paths


class AoBinUtils():

    _items = []
    _names = []
    _item_name = {}

    def __init__(self, *args, **kwargs):
        fp_items = kwargs.get('item_file', None)
        fp_names = kwargs.get('name_file', None)

        try:
            assert fp_items is not None, "Item file not supplied"
            assert fp_names is not None, "Name file not supplied"

            fp_items = os.path.join(os.path.dirname(__file__), fp_items)
            fp_names = os.path.join(os.path.dirname(__file__), fp_names)

            with open(fp_items) as json_file:
                temp_items = json.load(json_file)
                self._items.extend(temp_items['items']['equipmentitem'])
                self._items.extend(temp_items['items']['weapon'])
                self._items.extend(temp_items['items']['mount'])
                assert self._items is not None, "Failed to load items"

            with open(fp_names, encoding='utf8') as json_file:
                self._names = json.load(json_file)
                self._names = [x for x in self._names if x['LocalizedNames'] != None]
                assert self._names is not None, "Failed to load item names"

            self._map_item_names()

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

    
    def _map_item_names(self):
        res = {}
        try:
            del_indeces = []
            index = 0
            for item in self._items:
                item_name = [x['LocalizedNames']['EN-US'] for x in self._names if x['UniqueName'] == item['@uniquename']]
                if len(item_name) == 1:
                    res[item_name[0]] = item                     
                else:
                    del_indeces.append(index)

                index = index + 1

            i_offset = 0
            for i in del_indeces:
                del self._items[i - i_offset]
                i_offset = i_offset + 1

            assert len(res) > 0, 'Res is empty'
            assert len(self._items) == len(res), 'Res and _items size differ'

            self._item_name = res
        
        except Exception as e:
            print('Error in _map_item_names()')
            print(f'{e}')
            raise


if __name__ == "__main__":
    abu = AoBinUtils(item_file='..\\items.json', name_file='..\\formatted\\items.json')

    abu.print_head()
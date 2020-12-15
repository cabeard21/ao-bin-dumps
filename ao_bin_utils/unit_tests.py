import unittest

from ao_bin_data import AoBinData

class TestAoBinData(unittest.TestCase):

    def setUp(self):
        self._ao = AoBinData()

    def test_get_item(self):
        test_items = ['T5_OFF_SHIELD',]
        test_unique = [True,]
        test_results= [800,]

        for item, unique, res in zip(test_items, test_unique, test_results):
            item_data = self._ao.get_item(item, unique)
            self.assertEqual(item_data['@uniquename'], item)
            self.assertEqual(int(item_data['@itempower']), res)


if __name__ == "__main__":
    unittest.main()
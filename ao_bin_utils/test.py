import unittest

from ao_bin_data import AoBinData
from ao_bin_utilities import get_item_power

class UnitTests(unittest.TestCase):

    def setUp(self):
        self._ao = AoBinData()

    def test_get_item(self):
        unique_item = 'T5_OFF_SHIELD'
        non_unique_item = "Expert's Shield"
        ip = 800

        item_data = self._ao.get_item(unique_item, True)
        self.assertEqual(item_data['@uniquename'], unique_item)
        self.assertEqual(int(item_data['@itempower']), ip)

        item_data = self._ao.get_item(non_unique_item, False)
        self.assertEqual(item_data['@uniquename'], unique_item)
        self.assertEqual(int(item_data['@itempower']), ip)

    def test_get_item_power(self):
        test_item = "T4_SHOES_PLATE_HELL"
        self.assertEqual(get_item_power(test_item, 1, 0, self._ao), 750)

        test_item = "T5_OFF_SHIELD@1"
        self.assertEqual(get_item_power(test_item, 1, 0, self._ao), 900 * 1.05)
        self.assertEqual(get_item_power(test_item, 2, 0, self._ao), 910 * 1.05)
        self.assertEqual(get_item_power(test_item, 5, 100, self._ao), 1100 * 1.05)


if __name__ == "__main__":
    unittest.main()
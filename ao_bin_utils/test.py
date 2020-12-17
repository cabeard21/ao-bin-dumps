import unittest

from ao_bin_data import AoBinData
import ao_bin_utilities as abu


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

    def test_get_quality_table(self):
        level = ['2', '3', '4', '5']
        ip = ['10', '20', '50', '100']

        quality_table = self._ao.get_quality_table()
        self.assertListEqual([x['@level'] for x in quality_table], level)
        self.assertListEqual([x['@itempowerbonus'] for x in quality_table], ip)

    def test_get_unique_name(self):
        item_name = "Expert's Shield"
        unique_name = 'T5_OFF_SHIELD'
        enchant = 1

        self.assertEqual(self._ao.get_unique_name(item_name), unique_name)
        self.assertEqual(
            self._ao.get_unique_name(item_name, enchant), unique_name + '@1'
        )

    def test_get_item_power(self):
        test_item = "T4_SHOES_PLATE_HELL"
        self.assertEqual(abu.get_item_power(test_item, 1, 0, self._ao), 750)

        test_item = "T5_OFF_SHIELD@1"
        self.assertEqual(abu.get_item_power(test_item, 1, 0, self._ao), 900)
        self.assertEqual(abu.get_item_power(test_item, 2, 0, self._ao), 910)
        self.assertEqual(
            abu.get_item_power(test_item, 5, 100, self._ao), 1000 + (100*1.05))

    def test_remove_dupes(self):
        test_list = ['1', '1', 2, 3, 3]
        expected = ['1', 2, 3]

        self.assertListEqual(abu.remove_dupes(test_list), expected)

    def test_get_item_price(self):
        item = ["T4_BAG@1", "T5_BAG@1", "T6_BAG@1"]
        quality = [2, 2, 2]
        location = 'Lymhurst'

        prices = abu.get_item_price(item, quality, location)
        for item_name, item_price in prices.items():
            self.assertIn(item_name, item)
            self.assertEqual(type(item_price), int)

    def test_get_items_above_ip(self):
        item = "T4_OFF_SHIELD@1"
        ip = 1400
        mastery = 0
        expected = [
            ('T7_OFF_SHIELD@3', 5, 1400),
            ('T8_OFF_SHIELD@2', 5, 1400),
            ('T8_OFF_SHIELD@3', 1, 1400),
            ('T8_OFF_SHIELD@3', 2, 1410),
            ('T8_OFF_SHIELD@3', 3, 1420),
            ('T8_OFF_SHIELD@3', 4, 1450),
            ('T8_OFF_SHIELD@3', 5, 1500),
        ]

        self.assertListEqual(
            abu.get_items_above_ip(item, ip, mastery, self._ao),
            expected
        )


if __name__ == "__main__":
    unittest.main()

import unittest

from ao_bin_data import AoBinData
import ao_bin_utilities as abu
import ao_bin_utils.ao_bin_tools as aot

import sys
sys.path.insert(0, 'E:\\GitHub_Repos\\ao-bin-dumps\\')


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
        for i in range(len(prices)):
            self.assertEqual(item[i], list(prices.keys())[i])
            self.assertEqual(quality[i], list(prices.values())[i][0])
            self.assertEqual(int, type(list(prices.values())[i][1]))

    def test_get_items_above_ip(self):
        item = "T4_OFF_SHIELD@1"
        ip = 1400
        mastery = 0
        expected = [
            ('T7_OFF_SHIELD@3', 5),
            ('T8_OFF_SHIELD@2', 5),
            ('T8_OFF_SHIELD@3', 1),
            ('T8_OFF_SHIELD@3', 2),
            ('T8_OFF_SHIELD@3', 3),
            ('T8_OFF_SHIELD@3', 4),
            ('T8_OFF_SHIELD@3', 5),
        ]

        self.assertListEqual(
            abu.get_items_above_ip(item, ip, mastery, 4, self._ao),
            expected
        )

    def test_efficient_item_power(self):
        target_ip = 1090
        items = [
            self._ao.get_unique_name("Adept's Bloodletter")
        ]
        mastery = [
            148
        ]
        min_tiers = [
            5
        ]
        location = 'Lymhurst'

        expected_items = [
            self._ao.get_unique_name("Expert's Bloodletter") + '@1'
        ]

        eip = aot.AoBinTools(
            aot.EfficientItemPower(
                target_ip, items, mastery, min_tiers, location
            )
        )

        eip_res = eip.get_calculation()
        self.assertEqual(eip_res['item_names'], expected_items)

    def test_generate_fixture(self):
        self.assertTrue(self._ao.generate_fixture())


if __name__ == "__main__":
    unittest.main()

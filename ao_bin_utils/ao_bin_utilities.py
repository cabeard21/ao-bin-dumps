from __future__ import annotations
from typing import List

import requests

from ao_bin_data import AoBinData


def get_item_price(item_unique_name, quality, location) -> float:
    """Utility function to get an item's cheapest sell price at a given location.

    Parameters
    ----------
    item_unique_name: str
        Unique name of the item to be found.
    quality: int
        Quality level of the item (1 = Normal, 2 = Good, etc).
    location: str
        Name of the market whose price should be used.

    Returns
    -------
    float
        Cheapest sell price found at the location for the item.
    """

    url = (
        f"https://www.albion-online-data.com/api/v2/stats/prices/"
        f"{item_unique_name}"
    )

    params = {
        'locations': location,
        'qualities': quality,
    }

    response = requests.get(url, params=params).json()

    return response[0]['sell_price_min']


def get_item_power(
        item_unique_name,
        quality,
        mastery,
        ao_data: AoBinData) -> int:
    """Utility function to find an item's Item Power.

    Parameters
    ----------
    item_unique_name: str
        Unique name of the item to be found. An item with '@' character is
        added to the end for enchant level.
    quality: int
        Quality level of the item (1 = Normal, 2 = Good, etc).
    mastery: int
        Bonus from item mastery.
    ao_data: AoBinData object
        Pointer to the AoBinData object containing item information.

    Returns
    -------
    float
        The item's Item Power.
    """

    # Enchantment Level
    if '@' in item_unique_name:
        base_item_name, enchant_lvl = item_unique_name.split('@')
    else:
        base_item_name, enchant_lvl = item_unique_name, None

    item_data = ao_data.get_item(base_item_name)

    item_power_data = {}
    if enchant_lvl is not None:
        for enchantment in item_data['enchantments']['enchantment']:
            if enchantment['@enchantmentlevel'] == enchant_lvl:
                item_power_data = enchantment
                break
    else:
        item_power_data = item_data

    base_item_power = int(item_power_data['@itempower'])

    # Quality
    quality_item_power = 0
    if quality > 1 and quality < 6:
        quality_data = ao_data.get_quality_table()
        for quality_level in quality_data:
            if int(quality_level['@level']) == quality:
                quality_item_power = int(quality_level['@itempowerbonus'])
                break

    res = base_item_power + quality_item_power + mastery

    # Mastery Modifier
    mod = (1 + float(item_data['@masterymodifier']))
    res = res * mod

    return res


def get_items_above_ip(self, unique_item_name, ip, mastery) -> List:
    """Return a list of different tier/quality items that are above a given IP.

    Parameters
    ----------
    unique_item_name: str
        The unique item name of the item type. Only the base item matters.
    ip: int
        The IP above which items will be returned.
    mastery: int
        Bonus IP from mastery in the item.

    Returns
    -------
    list
        List of item tuples of the following format:

        (unique_item_name, quality, price, ip)

        The item's name will have the enchant level if present.
    """

    pass  # TODO: Implement

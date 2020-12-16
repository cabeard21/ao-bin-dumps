from __future__ import annotations
from typing import List

import requests
import re

TIER_FINDER = r"T\d_"

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

    # TODO: Implement minimum API calls for multiple items logic.
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

    res = base_item_power + quality_item_power

    # Mastery Modifier
    mod = (1 + float(item_data['@masterymodifier']))
    res = res + (mastery*mod)

    return res


def get_items_above_ip(
        unique_item_name,
        ip,
        mastery,
        ao_data: AoBinData) -> List:
    """Return a list of different tier/quality items that are above a given IP.

    Starting with the T4 version of the item:
        1. If IP >= min, add item at base quality (1)
        2. Increase quality by 1 and add if IP >= min until quality is > 5.
        3. Increase enchant level and repeat 1-2
        4. Increase tier until tier > 8 and repeat 1-3

        Should be 4*5*5 = 100 iterations

    Parameters
    ----------
    unique_item_name: str
        The unique item name of the item type. Only the base item matters.
    ip: int
        The IP above which items will be returned.
    mastery: int
        Bonus IP from mastery in the item.
    ao_data: AoBinData object
        Pointer to the AoBinData object containing item information.

    Returns
    -------
    list
        List of item tuples of the following format:

        (unique_item_name, quality, ip)

        The item's name will have the enchant level if present.
    """
    pattern = re.compile(TIER_FINDER)

    unique_item_name = unique_item_name.split('@')[0]

    res = []

    for tier in range(4, 9):
        for enchant in range(0, 4):
            item_name = (
                f"T{tier}_" + pattern.split(unique_item_name)[-1]
                + (f"@{enchant}" if enchant > 0 and enchant < 4 else '')
            )

            for quality in range(1, 6):
                curr_ip = get_item_power(item_name, quality, mastery, ao_data)
                if curr_ip >= ip:
                    res.append(
                        (item_name, quality, curr_ip)
                    )

    return res

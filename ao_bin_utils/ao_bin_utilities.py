from __future__ import annotations

from ao_bin_utils.ao_bin_data import AoBinData

from typing import List, Dict
import requests
import re
from time import sleep
from datetime import datetime
import math

TIER_FINDER = r"T\d_"


def make_sublists(a: list, n: int) -> list:
    """Split a into sublists of approximate n length"""

    k, m = divmod(len(a), n)
    return [a[i*k + min(i, m):(i + 1)*k + min(i + 1, m)] for i in range(n)]


def calculate_ema(prices: list, smoothing: float, days: int) -> int:
    """Calculate the Exponential Moving Average of prices."""

    if len(prices) < days:
        return prices[-1]

    ema_yesterday = prices[-days-1:-1]
    ema_yesterday = sum(ema_yesterday)/len(ema_yesterday)

    smoothing_factor = smoothing/(1 + days)
    result = math.floor(
        prices[-1]*smoothing_factor + ema_yesterday*(1 - smoothing_factor)
    )
    return result


def get_item_price(item_unique_name, quality, location) -> List:
    """Utility function to get an item's cheapest sell price at a given location.

    This method tries to minimize the amount of GET requests needed.
    The algorithm for the GET requests is:
        1. Do a GET request for all of the items and qualites passed in.
        2. Loop through the response and add the first match for each
            item/quality combo.
        3. Remove the item from the list of item names.
        4. Check if the quality can be removed from the list of qualites.
        5. Repeat 1-4 until item_unique_name is empty.

    This method pauses for 1 second between GET requests.

    Additionally, if the item can't be found at the location after a number of
    tries, all cities will be included in the search.

    Parameters
    ----------
    item_unique_name: list of str
        Unique names of the items to be found. Same length as quality.
    quality: list of int
        Quality levels of the items (1 = Normal, 2 = Good, etc).
        Same length as item_unique_name.
    location: str
        Name of the market whose price should be used.

    Returns
    -------
    list
        Cheapest sell price found at the location for each item.

        (item_name, quality, price).

        If a non-zero price is not found for an item, it will not be in
        the results.
    """
    names = item_unique_name.copy()
    quality_copy = quality.copy()

    res = []

    item_found = True  # First run
    fail_count = 0
    while len(names) > 0 and (item_found or len(res) == 0):
        item_found = False

        url = (
            f"https://www.albion-online-data.com/api/v2/stats/prices/"
            f"{','.join(remove_dupes(names))}"
        )

        quality_no_dupes = remove_dupes(quality_copy)
        params = {
            'locations': location,
            'qualities': ','.join([str(x) for x in quality_no_dupes]),
        }
        if fail_count > 10:
            print('/')
            params['locations'] = "Caerleon,Thetford,Lymhurst,Fort Sterling,Martlock,Bridgewatch"
            print(remove_dupes(names))
            if fail_count > 20:
                return res

        response = requests.get(url, params=params)
        print(
            '.' if response.status_code == 200 else '!',
            end=''
        )
        response = response.json()

        item_index_offset = 0
        for item_index in range(len(names)):
            item_index = item_index - item_index_offset
            for item in response:
                data_age = (
                    datetime.now() -
                    datetime.strptime(
                        item['sell_price_min_date'],
                        '%Y-%m-%dT%H:%M:%S'
                    )
                )

                if (
                    names[item_index] == item['item_id'] and
                    quality_copy[item_index] == item['quality'] and
                    item['sell_price_min'] > 0 and
                    data_age.days <= 1
                ):
                    res.append(
                        (
                            names.pop(item_index),
                            quality_copy.pop(item_index),
                            item['sell_price_min']
                        )
                    )

                    item_index_offset = item_index_offset + 1
                    item_found = True
                    fail_count = 0
                    break

        (item_found or len(res) == 0) and \
            sleep(0.5)  # Pause if another request

        if not item_found:
            print('*')
            fail_count += 1

    return res


def remove_dupes(input_list):
    """Helper function to remove duplicates from a list.

    Parameters
    ----------
    input_list: list
        The list whose duplicates will be removed.

    Returns
    -------
    list
        Returns a sorted list with dupilcates removed.
    """

    res = []

    [res.append(x) for x in input_list if x not in res]

    return sorted(res)


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
        The item's Item Power. If the item is not found, -1 is returned.
    """

    # Enchantment Level
    if '@' in item_unique_name:
        base_item_name, enchant_lvl = item_unique_name.split('@')
    else:
        base_item_name, enchant_lvl = item_unique_name, None

    item_data = ao_data.get_item(base_item_name)

    if not item_data:
        return -1

    item_power_data = {}
    if enchant_lvl is not None and 'enchantments' in item_data:
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
    mod = (1 + float(item_data.get('@masterymodifier', 0)))
    res = res + (mastery*mod)

    return res


def get_items_above_ip(
        unique_item_name,
        ip,
        mastery,
        min_tier,
        ao_data: AoBinData) -> List:
    """Return a list of different tier/quality items that are above a given IP.

    Starting with the minimum tier version of the item:
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
    min_tier: int
        The tier to start looking at for minimum IP's.
    ao_data: AoBinData object
        Pointer to the AoBinData object containing item information.

    Returns
    -------
    list
        List of item tuples of the following format:

        (unique_item_name, quality)

        The item's name will have the enchant level if present.
    """
    pattern = re.compile(TIER_FINDER)

    unique_item_name = unique_item_name.split('@')[0]

    ip = abs(ip)

    res = []

    for tier in range(min_tier, 9):
        for enchant in range(0, 4):
            item_name = (
                f"T{tier}_" + pattern.split(unique_item_name)[-1]
                + (f"@{enchant}" if enchant > 0 and enchant < 4 else '')
            )

            for quality in range(1, 6):
                curr_ip = get_item_power(item_name, quality, mastery, ao_data)
                if curr_ip >= ip:
                    res.append(
                        (item_name, quality)
                    )

    return res

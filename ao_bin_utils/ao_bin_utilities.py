from ao_bin_data import AoBinData

def get_item_price(item_unique_name, location) -> float:
    """Utility function to get an item's cheapest sell price at a given location.

    Parameters
    ----------
    item_unique_name: str
        Unique name of the item to be found.
    location: str
        Name of the market whose price should be used.

    Returns
    -------
    float
        Cheapest sell price found at the location for the item.
    """

    pass #TODO: Implement


def get_item_power(item_unique_name, quality, ao_data: AoBinData) -> int:
    """Utility function to find an item's Item Power.

    Parameters
    ----------
    item_unique_name: str
        Unique name of the item to be found.
    quality: int
        Quality level of the item (1 = Normal, 2 = Good, etc)
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
    

    res = base_item_power

    return res

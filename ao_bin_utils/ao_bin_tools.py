from __future__ import annotations
from .ao_bin_data import AoBinData
import ao_bin_utilities as abu

from abc import ABC, abstractmethod
from typing import Dict, List


class AoBinTools():
    """Allows for calculations to be perfomed on AO Bin data.

    Different Strategies can be used on AO Bin data by changing
    the Strategy attribute.

    ...

    Attributes
    ----------
    _ao_data: AoBinData object
        The data to be accessed by Strategy.

    Properties
    ----------
    strategy: Strategy object
        The Strategy that will perform an operation on AO Bin data.

    Methods
    -------
    get_calculation():
        Calls the Strategy's algorithm and passes _ao_data to it.
    """

    def __init__(self, strategy: Strategy):
        """Constructor that takes a Strategy

        Parameters
        ----------
        strategy: Strategy
            A concrete implementation of the Strategy abstract class.
            Performs the actual calculation.
        """
        self._strategy = strategy
        self._ao_data = AoBinData()

    # Getter and setter for strategy.
    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def get_calculation(self) -> Dict:
        """Calls the Strategy's algorithm and passes _ao_data to it.

        Returns
        -------
        dictionary
            A dictionary with keys and values that depend on the stratgey used.
        """

        return self._strategy.algorithm(self._ao_data)


class Strategy(ABC):
    """Abstract Strategy base class.

    ...

    Methods
    -------
    algorithm(ao_data):
        Abstract method that is used by client to call concrete
        Strategy algorithm.
    """

    @abstractmethod
    def algorithm(self, ao_data: AoBinData) -> Dict:
        """Abstract method that is used by client to call concrete Strategy algorithm.

        Parameters
        ----------
        ao_data: AoBinData object
            Allows the concrete class to access item data. Provided by the
            context class to avoid tight coupling.

        Returns
        -------
        dictionary
            A dictionary with keys and values that depend on the stratgey used.
        """

        pass


class EfficientItemPower(Strategy):
    """Strategy to return the cheapest items that are at least a specified IP.

    The idea is to find the cheapest version of each item in a build that
    is at least a minimum Item Power (IP).

    ...

    Attributes
    ----------
    target_ip: int
        The minimum IP each item must be.
    items: list
        A list of item unique names that represent the build.
    mastery: list
        A list of integers that are the bonus IP for each item.
    location: str
        The name of the market to use

    Methods
    -------
    algorithm(ao_data)
        Concrete implementation of the abstract method inherited from Strategy.
    """

    def __init__(
            self,
            target_ip: int,
            items: List,
            mastery: List,
            min_tiers: List,
            location: str,):
        """Constructor for the class.

        Parameters
        ----------
        target_ip: int
            The minimum IP each item must be.
        items: list
            A list of item unique names that represent the build.
        mastery: list
            A list of integers that are the bonus IP for each item.
        min_tiers: list
            A list of integers that are the tier above which items will be
            considered.
        location: str
            The name of the market to use
        """

        self._target_ip = target_ip
        self._items = items
        self._mastery = mastery
        self._min_tiers = min_tiers
        self._location = location

    def algorithm(self, ao_data: AoBinData) -> Dict:
        """Concrete implementation of the abstract method inherited from Strategy.

        The method accomplishes the class's goal by:
            1: Loop through each item stored by the class.
            2: For each item:
                a: Use ao_data to find all items that meet the minimum IP when
                    including mastery.
                b: Do a GET request to get the price for all items
                    found in (a).
                c: Add the cheapest item and price to the result dictionary.

        Parameters
        ----------
        ao_data: AoBinData object
            Allows the concrete class to access item data. Provided by the
            context class to avoid tight coupling.

        Returns
        -------
        dictionary
            'items': List of item unique names for the chosen items.
            'qualities': List of item quality for each item.
            'item_power': List of the item power for each item.
            'prices': List of floats that are the market prices for each
            item in 'Items'.
        """

        res = {
            'items': [],
            'qualities': [],
            'item_power': [],
            'prices': [],
        }
        for i in range(len(self._items)):
            item = self._items[i]
            mastery = self._mastery[i]
            min_tier = self._min_tiers[i]

            candidate_items = abu.get_items_above_ip(
                item,
                self._target_ip,
                mastery,
                min_tier,
                ao_data
            )

            item_names = [x[0] for x in candidate_items]
            qualities = [x[1] for x in candidate_items]
            price_data = abu.get_item_price(
                item_names, qualities, self._location
            )

            cheapest_item_name = sorted(price_data)[0]

            res['items'].append(cheapest_item_name)
            res['qualities'].append(price_data[cheapest_item_name][0])
            res['item_power'].append(
                abu.get_item_power(
                    cheapest_item_name,
                    price_data[cheapest_item_name][0],
                    mastery,
                    ao_data
                )
            )
            res['prices'].append(price_data[cheapest_item_name][1])

        return res

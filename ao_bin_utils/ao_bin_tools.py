from .ao_bin_data import AoBinData

from abc import ABC, abstractmethod
from typing import Dict, List
from __future__ import annotations


class AoBinTools():

    def __init__(self, strategy: Strategy):
        self._strategy = strategy
        self._ao_data = AoBinData()


    @property
    def strategy(self) -> Strategy:
        return self._strategy


    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy


    def get_calculation(self) -> Dict:
        return self._strategy.algorithm(self._ao_data)



class Strategy(ABC):

    @abstractmethod
    def algorithm(self, ao_data) -> Dict:
        pass



class EfficientItemPower(Strategy):
    """Strategy to return the cheapest items that are at least a specified IP"""

    def __init__(self, target_ip, shop_subcategory: List):
        self._target_ip = target_ip
        self._shop_subcategory = shop_subcategory
        
    
    def algorithm(self, ao_data) -> Dict:
        pass

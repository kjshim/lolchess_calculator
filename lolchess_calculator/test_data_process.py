import unittest
from lolchess_calculator import base_data


class TestBasicData(unittest.TestCase):
    def test_hero_reading(self):
        heroes = base_data.ALL_HEROES
        len([v for v in heroes if v.name == "올라프"]) == 1


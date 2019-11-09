import unittest
from pprint import pprint
from lolchess_calculator import base_data, operators


class TestBasicData(unittest.TestCase):
    def test_hero_reading(self):
        heroes = base_data.ALL_HEROES
        len([v for v in heroes if v.name == "올라프"]) == 1

    def test_simulate_random_pick(self):
        for lv in range(1, 10):
            print(f"Sample pick at level {lv}")
            pprint(operators.roll_at_level(lv))

    def test_synergy(self):
        a = set()
        b = set()
        for h in base_data.ALL_HEROES:
            a.update(h.origins)
            b.update(h.hero_classes)

        r = {}
        for aa in a:
            r[aa]= [1]
        for bb in b:
            r[bb] = [1]
        pprint(r)
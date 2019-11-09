import unittest
from pprint import pprint
from lolchess_calculator import base_data, operators
import random

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
            r[aa] = [1]
        for bb in b:
            r[bb] = [1]
        pprint(r)

    def test_sampling(self):
        n_run = 100
        total_seen, count_dict = operators.simulate_with_no_reroll(1, 0, 6, 0, n_run)
        results = []
        for k, v in count_dict.items():
            expected_to_see_per_round = v / n_run
            results.append(
                (expected_to_see_per_round, v, k, base_data.ALL_HEROES_DICT[k])
            )
        pprint(sorted(results, reverse=True))

    def test_synergy_calc(self):
        deck = random.choices(base_data.ALL_HEROES, k=8)
        pprint(deck)
        pprint(operators.get_synergy_from_deck(deck))

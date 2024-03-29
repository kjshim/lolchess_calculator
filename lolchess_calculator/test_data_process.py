import unittest
from pprint import pprint
from pathlib import Path

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
        deck = base_data.DECK_DATA[0]
        pprint(deck)
        synergy_info = operators.get_synergy_from_deck(deck.heroes)
        pprint(synergy_info)
        pprint(operators.calculate_synergy_score(synergy_info))

    def test_combinations(self):
        game_state = base_data.InGameState(
            6, 0, [
                base_data.get_hero_inst("쓰레쉬", 2),
                base_data.get_hero_inst("브라움", 2),
            ], [], []
        )
        deck = base_data.DECK_DATA[0]
        count_till_lev_2 = operators.calculate_round_till_level(1, 0, 2)
        seen_count = operators.simulate_with_no_reroll(1, 0, operators.calculate_round_till_level(1, 0, 4))
        synergy_chances = operators.calculate_synergy_likelyhood_from_seen_counter(seen_count, game_state)
        display = []
        for deck in synergy_chances:
            display.append((operators.score_deck(deck), deck))
        display.sort(reverse=True, key=lambda v:v[0])
        pprint(display[:30])
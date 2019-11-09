import random
from typing import List
import collections

from base_data import *

HEROES_BY_LEVEL = {}
for hero in ALL_HEROES:
    if hero.cost not in HEROES_BY_LEVEL:
        HEROES_BY_LEVEL[hero.cost] = []
    HEROES_BY_LEVEL[hero.cost].append(hero)


def calculate_synergy_score(synergy_type: Synergy) -> float:
    return float(synergy_type.count ** 2)


def roll_at_level(level: int) -> List[Hero]:
    assert 0 < level < 10
    n_per_roll = 5

    levels = list(range(1, 6))
    weights = REROLL_RATE[level]
    picked_levels = random.choices(population=levels, weights=weights, k=n_per_roll)
    result = []
    for lv in picked_levels:
        result.append(random.choice(HEROES_BY_LEVEL[lv]))
    return result


def get_synergy_from_deck(deck: Set[Hero]) -> List[Synergy]:
    class_count = collections.defaultdict(int)
    active_list = []
    for h in deck:
        for c in h.hero_classes:
            class_count[c] += 1
        for c in h.origins:
            class_count[c] += 1
    for k, v in class_count.items():
        possible_cnt = [cnt for cnt in ALL_SYNERGY[k.name] if cnt <= v]
        if possible_cnt:
            active_list.append((k, max(possible_cnt), v))
    return active_list


def simulate_with_no_reroll(start_level: int, start_exp: int, end_level: int, end_exp: int, n_try=10000):
    assert (start_level, start_exp) < (end_level, end_exp)
    total_seen = 0
    seen_count = collections.defaultdict(int)
    for i in range(n_try):
        cur_lv = start_level
        cur_exp = start_exp
        while (cur_lv, cur_exp) <= (end_level, end_exp):
            cards = roll_at_level(cur_lv)
            total_seen += len(cards)
            for c in cards:
                seen_count[c.name] += 1

            # round advance
            cur_exp += 2
            if cur_exp >= LVUP_EXP_REQUIRED_FROM_LEVEL[cur_lv]:
                cur_exp -= LVUP_EXP_REQUIRED_FROM_LEVEL[cur_lv]
                cur_lv += 1
    return total_seen, seen_count

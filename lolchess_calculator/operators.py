import random
from typing import List

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

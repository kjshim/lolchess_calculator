import random
from typing import List, Dict
import collections
from itertools import combinations
import json
import pathlib
from base_data import *
import math
import copy
from dataclasses import dataclass

HEROES_BY_LEVEL = {}
HEROES_BY_SYNERGY = {}

for hero in ALL_HEROES:
    if hero.cost not in HEROES_BY_LEVEL:
        HEROES_BY_LEVEL[hero.cost] = []
    HEROES_BY_LEVEL[hero.cost].append(hero)

    for origin in hero.origins:
        if origin not in HEROES_BY_SYNERGY:
            HEROES_BY_SYNERGY[origin] = []
        HEROES_BY_SYNERGY[origin].append(hero)

    for hero_class in hero.hero_classes:
        if hero_class not in HEROES_BY_SYNERGY:
            HEROES_BY_SYNERGY[hero_class] = []
        HEROES_BY_SYNERGY[hero_class].append(hero)


def calculate_synergy_score(synergy_info: list) -> float:
    """
    pnput : output from get_synergy_from_deck
    :param synergy_type:
    :return:
    """
    result = 0
    for s_type, s_lv, s_count in synergy_info:
        result += (s_lv * s_count)
    return result


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


def calculate_round_till_level(start_level: int, start_exp: int, end_level: int):
    count = 0
    cur_lv = start_level
    cur_exp = start_exp

    while cur_lv < end_level:
        cur_exp += 2
        if cur_exp >= LVUP_EXP_REQUIRED_FROM_LEVEL[cur_lv]:
            cur_exp -= LVUP_EXP_REQUIRED_FROM_LEVEL[cur_lv]
            cur_lv += 1
        count += 1
    return count


def simulate_with_no_reroll(start_level: int, start_exp: int, roll_count: int) -> Dict[str, float]:
    n_try = int(50000 / roll_count)
    total_seen = 0
    seen_count = collections.defaultdict(int)
    for i in range(n_try):
        cur_lv = start_level
        cur_exp = start_exp
        for j in range(roll_count):
            cards = roll_at_level(cur_lv)
            total_seen += len(cards)
            for c in cards:
                seen_count[c.name] += 1

            # round advance
            cur_exp += 2
            if cur_exp >= LVUP_EXP_REQUIRED_FROM_LEVEL[cur_lv]:
                cur_exp -= LVUP_EXP_REQUIRED_FROM_LEVEL[cur_lv]
                cur_lv += 1
    seen_count_per_game = collections.defaultdict(float)
    for k in seen_count:
        seen_count_per_game[k] = seen_count[k] / n_try
    return seen_count_per_game


def simulate_with_no_levup(start_level: int, roll_count: int) -> Dict[str, float]:
    n_try = int(50000 / roll_count)
    total_seen = 0
    seen_count = collections.defaultdict(int)
    for i in range(n_try):
        for j in range(roll_count):
            cards = roll_at_level(start_level)
            total_seen += len(cards)
            for c in cards:
                seen_count[c.name] += 1

    seen_count_per_game = collections.defaultdict(float)
    for k in seen_count:
        seen_count_per_game[k] = seen_count[k] / n_try
    return seen_count_per_game


def generate_precalculate_synergy_combinations(output_json_path: pathlib.Path):
    all_n_result = {}
    for n in range(1, 4):
        result = []
        all_combinations = list(combinations(ALL_HEROES, n))
        print(f"Calculating n: {n}, comb: {len(all_combinations)}")
        for c in all_combinations:
            synergy = get_synergy_from_deck(c)
            score = calculate_synergy_score(synergy)
            result.append(
                (score, [v.name for v in c])
            )
        all_n_result[n] = sorted(result, reverse=True)
    with output_json_path.open("w") as f:
        json.dump(all_n_result, f, indent=2)


def add_seen_count_plus_game_state(seen_count: Dict[str, float], game_state: InGameState):
    result = copy.deepcopy(seen_count)

    for h_inst in game_state.on_deck:
        if h_inst.hero.name in result.keys():
            result[h_inst.hero.name] += (3 ** (h_inst.star - 1))
    for h_inst in game_state.on_board:
        if h_inst.hero.name in result.keys():
            result[h_inst.hero.name] += (3 ** (h_inst.star - 1))
    for h in game_state.on_shop:
        if h.name in result.keys():
            result[hero.name] += 1

    return result


def calculate_chance_of_getting_deck(deck: List[Hero], game_state: InGameState,
                                     seen_count_per_game: Dict[str, float]):
    result = {}
    added = add_seen_count_plus_game_state(seen_count_per_game, game_state)
    for h in deck:
        result[h.name] = added[h.name]
    return result


@dataclass(frozen=True)
class SynergyLikelihoodItem:
    chance: float
    synergies: List[Tuple[str, int]]
    likely_heroes: List[Tuple[float, str]]

    def __repr__(self):
        syn_list_str = " + ".join([f"({v[0]} * {v[1]}" for v in self.synergies])
        hero_hints = "/".join([f"{v[1]}({v[0]:.2f})" for v in self.likely_heroes])
        return f"{self.chance*100:.2f}% - [{syn_list_str}] : {hero_hints}"


def calculate_synergy_likelyhood_from_seen_counter(seen_counter: Dict[str, float], game_state: InGameState) -> List[
    SynergyLikelihoodItem]:
    """
    :param seen_counter:
    :return:
    """
    seen_counter_with_mine = add_seen_count_plus_game_state(seen_counter, game_state)
    chances = []
    for synergy in HEROES_BY_SYNERGY:
        available_synergy_levels = ALL_SYNERGY[synergy.name]
        chance_to_hero = []
        for h in HEROES_BY_SYNERGY[synergy]:
            chance_to_hero.append((seen_counter_with_mine[h.name], h.name))
        chance_to_hero.sort(reverse=True, key=lambda v: v[0])
        for lv in reversed(available_synergy_levels):
            if len(chance_to_hero) >= lv:
                item = SynergyLikelihoodItem(
                    chance_to_hero[lv - 1][0],
                    [(synergy.name, lv)],
                    chance_to_hero[:lv]
                )
                chances.append(item)
    chances.sort(reverse=True, key=lambda v: v.chance)
    return chances

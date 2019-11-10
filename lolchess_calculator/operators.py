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
        if origin.name not in HEROES_BY_SYNERGY:
            HEROES_BY_SYNERGY[origin.name] = []
        HEROES_BY_SYNERGY[origin.name].append(hero)

    for hero_class in hero.hero_classes:
        if hero_class.name not in HEROES_BY_SYNERGY:
            HEROES_BY_SYNERGY[hero_class.name] = []
        HEROES_BY_SYNERGY[hero_class.name].append(hero)


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
            class_count[c.name] += 1
        for c in h.origins:
            class_count[c.name] += 1
    for k, v in class_count.items():
        possible_cnt = [cnt for cnt in ALL_SYNERGY[k] if cnt <= v]
        if possible_cnt:
            active_list.append(Synergy(k, possible_cnt[-1]))
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
            result[h.name] += 1

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
    synergies: List[Synergy]
    likely_heroes: List[Tuple[float, str]]

    def __repr__(self):
        syn_list_str = " + ".join([f"({v.name} * {v.count})" for v in self.synergies])
        hero_hints = " ".join([f"{v[1]} ({v[0]:.2f})" for v in self.likely_heroes])
        return f"{self.chance * 100:.2f}% \t- [{syn_list_str}]\t: {hero_hints}"


def create_synergy_to_chance_hero_sorted_list(seen_counter: Dict[str, float]):
    """
    Dict[synergy] = [ (chance, hero) ....]
    :param seen_counter:
    :return:
    """
    result = collections.defaultdict(list)
    for synergy in ALL_SYNERGY:
        for h in HEROES_BY_SYNERGY[synergy]:
            result[synergy].append((seen_counter[h.name], h.name))
        result[synergy].sort(reverse=True)
    return result


def calculate_likelihood_for_synergy(seen_counter: Dict[str, float],
                                     synergy_to_chance_map: Dict[str, List[Tuple[float, str]]],
                                     synergy_list: List[Synergy]) -> SynergyLikelihoodItem:
    cum_chance = 1.0
    required_hero = set()
    for synergy in synergy_list:
        chance_to_hero = synergy_to_chance_map[synergy.name]
        if len(chance_to_hero) < synergy.count:
            cum_chance *= 0.0
            break
        for i in range(synergy.count):
            cum_chance *= min(1.0, chance_to_hero[i][0])
            required_hero.add(chance_to_hero[i][1])
    if (len(required_hero) > 9):
        cum_chance *= 0.0
    hero_likelyhood = sorted([(seen_counter[h], h) for h in required_hero], reverse=True)
    result = SynergyLikelihoodItem(cum_chance, synergy_list, hero_likelyhood)
    return result


def score_deck(deck: SynergyLikelihoodItem) -> float:
    score = 0.0
    for h in deck.likely_heroes:
        hero = ALL_HEROES_DICT[h[1]]
        star_coeff = 1.0
        if h[0] > 3.0:
            star_coeff = 2.5
        if h[0] > 9.0:
            star_coeff = 4.0

        synergy_coeff = 1.0
        for syn_name in [v.name for v in hero.hero_classes] + [v.name for v in hero.origins]:
            for active_syn in deck.synergies:
                if syn_name == active_syn.name:
                    synergy_coeff *= (1.0 + ((active_syn.count * 0.3) ** 3))

        score += (hero.cost * star_coeff * synergy_coeff)
    return score * deck.chance


def calculate_synergy_likelyhood_from_seen_counter(seen_counter: Dict[str, float],
                                                   game_state: InGameState) -> List[
    SynergyLikelihoodItem]:
    """
    :param seen_counter:
    :return:
    """
    seen_counter_with_mine = add_seen_count_plus_game_state(seen_counter, game_state)
    synergy_likelihood_list = []
    synergy_to_chance_map = create_synergy_to_chance_hero_sorted_list(seen_counter_with_mine)

    synergies_to_check = []

    # 1 synergy
    for synergy in HEROES_BY_SYNERGY:
        for lv in ALL_SYNERGY[synergy]:
            synergies_to_check.append(Synergy(synergy, lv))

    synergy_combinations = []
    for i in range(4):
        synergy_combinations += combinations(synergies_to_check, i)

    for synergy_list in synergy_combinations:
        if len(set([v.name for v in synergy_list])) < len(synergy_list):
            continue
        item = calculate_likelihood_for_synergy(seen_counter_with_mine, synergy_to_chance_map,
                                                synergy_list)
        if item.chance > 0.0:
            synergy_likelihood_list.append(item)
        # assert get_synergy_from_deck()
    synergy_likelihood_list.sort(reverse=True, key=lambda v: v.chance)
    return synergy_likelihood_list

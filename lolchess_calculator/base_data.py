from typing import Set, List, Optional, Tuple
from dataclasses import dataclass
import difflib


@dataclass(frozen=True)
class Origin:
    name: str


@dataclass(frozen=True)
class HeroClass:
    name: str


@dataclass(frozen=True)
class Synergy:
    name: str
    count: int


@dataclass(frozen=True)
class Hero:
    name: str
    cost: int
    origins: Set[Origin]
    hero_classes: Set[HeroClass]
    hp: float
    armor: float
    attack: float
    attack_speed: float
    dps: float


@dataclass(frozen=True)
class Item:
    name: str


@dataclass
class HeroInstance:
    hero: Hero
    star: int
    items: List[Item]


@dataclass
class InGameState:
    level: int
    exp: int
    # on_board: List[Hero]
    # on_deck: List[Hero]
    on_board: List[HeroInstance]
    on_deck: List[HeroInstance]
    on_shop: List[Hero]


@dataclass(frozen=True)
class DeckTemplate:
    name: str
    desc: str
    heroes: Set[Hero]
    desired_items: List[Tuple[Hero, Item]]
    tier: int


# Row = level 0~, Col = tier
REROLL_RATE = [
    [.0, .0, .0, .0, .0],
    [1.0, .0, .0, .0, .0],
    [1.0, .0, .0, .0, .0],
    [0.7, .25, .05, .0, .0],
    [.5, .35, .15, .0, .0],
    [.35, .35, .25, .05, .0],
    [.25, .35, .30, .10, .0],
    [.20, .30, .33, .15, .02],
    [.15, .20, .35, .24, .06],
    [.10, .15, .30, .30, .15],
]

ALL_ITEMS = [Item(v) for v in
             [
                 "B.F. 대검",
                 "곡궁",
                 "쇠사슬 조끼",
                 "음전자 망토",
                 "쓸데없이 큰 지팡이",
                 "여신의 눈물",
                 "거인의 허리띠",
                 "뒤집개",
                 "연습용 장갑",
             ]]

# This data ame from data_proess
ALL_HEROES = [
    Hero(name='나미', cost=5, origins={Origin(name='바다')}, hero_classes={HeroClass(name='신비술사')}, hp=750.0, armor=25.0,
         attack=50.0, attack_speed=0.75, dps=38.0),
    Hero(name='나서스', cost=1, origins={Origin(name='빛')}, hero_classes={HeroClass(name='파수꾼')}, hp=650.0, armor=40.0,
         attack=50.0, attack_speed=0.55, dps=28.0),
    Hero(name='노틸러스', cost=3, origins={Origin(name='바다')}, hero_classes={HeroClass(name='파수꾼')}, hp=850.0, armor=40.0,
         attack=55.0, attack_speed=0.6, dps=33.0),
    Hero(name='녹턴', cost=3, origins={Origin(name='강철')}, hero_classes={HeroClass(name='암살자')}, hp=650.0, armor=25.0,
         attack=60.0, attack_speed=0.75, dps=45.0),
    Hero(name='니코', cost=2, origins={Origin(name='숲')}, hero_classes={HeroClass(name='드루이드')}, hp=500.0, armor=20.0,
         attack=45.0, attack_speed=0.7, dps=32.0),
    Hero(name='다이애나', cost=1, origins={Origin(name='지옥불')}, hero_classes={HeroClass(name='암살자')}, hp=550.0, armor=20.0,
         attack=50.0, attack_speed=0.7, dps=35.0),
    Hero(name='럭스', cost=7,
         origins={Origin(name='그림자'), Origin(name='지옥불'), Origin(name='빛'), Origin(name='수정'), Origin(name='바람'),
                  Origin(name='바다'), Origin(name='숲'), Origin(name='빙하'), Origin(name='전기'), Origin(name='강철')},
         hero_classes={HeroClass(name='아바타')}, hp=850.0, armor=25.0, attack=65.0, attack_speed=0.85, dps=55.0),
    Hero(name='레넥톤', cost=1, origins={Origin(name='사막')}, hero_classes={HeroClass(name='광전사')}, hp=600.0, armor=35.0,
         attack=60.0, attack_speed=0.6, dps=36.0),
    Hero(name='렉사이', cost=2, origins={Origin(name='강철')}, hero_classes={HeroClass(name='포식자')}, hp=650.0, armor=30.0,
         attack=65.0, attack_speed=0.7, dps=46.0),
    Hero(name='르블랑', cost=2, origins={Origin(name='숲')}, hero_classes={HeroClass(name='요술사'), HeroClass(name='암살자')},
         hp=550.0, armor=20.0, attack=55.0, attack_speed=0.7, dps=39.0),
    Hero(name='마스터 이', cost=5, origins={Origin(name='그림자')},
         hero_classes={HeroClass(name='신비술사'), HeroClass(name='검사')},
         hp=850.0, armor=30.0, attack=70.0, attack_speed=1.0, dps=70.0),
    Hero(name='마오카이', cost=1, origins={Origin(name='숲')}, hero_classes={HeroClass(name='드루이드')}, hp=650.0, armor=35.0,
         attack=55.0, attack_speed=0.5, dps=28.0),
    Hero(name='말자하', cost=2, origins={Origin(name='그림자')}, hero_classes={HeroClass(name='소환사')}, hp=550.0, armor=20.0,
         attack=40.0, attack_speed=0.65, dps=26.0),
    Hero(name='말파이트', cost=4, origins={Origin(name='대지')}, hero_classes={HeroClass(name='파수꾼')}, hp=800.0, armor=50.0,
         attack=60.0, attack_speed=0.55, dps=33.0),
    Hero(name='문도 박사', cost=3, origins={Origin(name='맹독')}, hero_classes={HeroClass(name='광전사')}, hp=750.0, armor=35.0,
         attack=60.0, attack_speed=0.6, dps=36.0),
    Hero(name='바루스', cost=2, origins={Origin(name='지옥불')}, hero_classes={HeroClass(name='정찰대')}, hp=550.0, armor=25.0,
         attack=60.0, attack_speed=0.75, dps=45.0),
    Hero(name='베이가', cost=3, origins={Origin(name='그림자')}, hero_classes={HeroClass(name='요술사')}, hp=600.0, armor=20.0,
         attack=50.0, attack_speed=0.6, dps=30.0),
    Hero(name='베인', cost=1, origins={Origin(name='빛')}, hero_classes={HeroClass(name='정찰대')}, hp=500.0, armor=25.0,
         attack=40.0, attack_speed=0.75, dps=30.0),
    Hero(name='볼리베어', cost=2, origins={Origin(name='전기'), Origin(name='빙하')}, hero_classes={HeroClass(name='광전사')},
         hp=650.0, armor=35.0, attack=60.0, attack_speed=0.7, dps=42.0),
    Hero(name='브라움', cost=2, origins={Origin(name='빙하')}, hero_classes={HeroClass(name='파수꾼')}, hp=750.0, armor=60.0,
         attack=40.0, attack_speed=0.6, dps=24.0),
    Hero(name='브랜드', cost=4, origins={Origin(name='지옥불')}, hero_classes={HeroClass(name='요술사')}, hp=700.0, armor=25.0,
         attack=55.0, attack_speed=0.7, dps=39.0),
    Hero(name='블라디미르', cost=1, origins={Origin(name='바다')}, hero_classes={HeroClass(name='요술사')}, hp=550.0, armor=30.0,
         attack=40.0, attack_speed=0.65, dps=26.0),
    Hero(name='사이온', cost=3, origins={Origin(name='그림자')}, hero_classes={HeroClass(name='광전사')}, hp=850.0, armor=35.0,
         attack=65.0, attack_speed=0.65, dps=42.0),
    Hero(name='소라카', cost=3, origins={Origin(name='빛')}, hero_classes={HeroClass(name='신비술사')}, hp=600.0, armor=20.0,
         attack=40.0, attack_speed=0.65, dps=26.0),
    Hero(name='스카너', cost=2, origins={Origin(name='수정')}, hero_classes={HeroClass(name='포식자')}, hp=650.0, armor=30.0,
         attack=60.0, attack_speed=0.65, dps=39.0),
    Hero(name='시비르', cost=3, origins={Origin(name='사막')}, hero_classes={HeroClass(name='검사')}, hp=600.0, armor=25.0,
         attack=50.0, attack_speed=0.7, dps=35.0),
    Hero(name='신드라', cost=2, origins={Origin(name='바다')}, hero_classes={HeroClass(name='요술사')}, hp=500.0, armor=20.0,
         attack=40.0, attack_speed=0.7, dps=28.0),
    Hero(name='신지드', cost=5, origins={Origin(name='맹독')}, hero_classes={HeroClass(name='연금술사')}, hp=1050.0, armor=50.0,
         attack=0.0, attack_speed=0.0, dps=0.0),
    Hero(name='쓰레쉬', cost=2, origins={Origin(name='바다')}, hero_classes={HeroClass(name='파수꾼')}, hp=700.0, armor=40.0,
         attack=55.0, attack_speed=0.55, dps=30.0),
    Hero(name='아이번', cost=1, origins={Origin(name='숲')}, hero_classes={HeroClass(name='드루이드')}, hp=600.0, armor=25.0,
         attack=50.0, attack_speed=0.6, dps=30.0),
    Hero(name='아지르', cost=3, origins={Origin(name='사막')}, hero_classes={HeroClass(name='소환사')}, hp=600.0, armor=20.0,
         attack=55.0, attack_speed=0.8, dps=44.0),
    Hero(name='아트록스', cost=3, origins={Origin(name='빛')}, hero_classes={HeroClass(name='검사')}, hp=700.0, armor=35.0,
         attack=65.0, attack_speed=0.7, dps=46.0),
    Hero(name='애니', cost=4, origins={Origin(name='지옥불')}, hero_classes={HeroClass(name='소환사')}, hp=700.0, armor=20.0,
         attack=45.0, attack_speed=0.7, dps=32.0),
    Hero(name='애쉬', cost=4, origins={Origin(name='수정')}, hero_classes={HeroClass(name='정찰대')}, hp=550.0, armor=20.0,
         attack=60.0, attack_speed=0.7, dps=42.0),
    Hero(name='야스오', cost=2, origins={Origin(name='바람')}, hero_classes={HeroClass(name='검사')}, hp=600.0, armor=30.0,
         attack=55.0, attack_speed=0.7, dps=39.0),
    Hero(name='오른', cost=1, origins={Origin(name='전기')}, hero_classes={HeroClass(name='파수꾼')}, hp=650.0, armor=40.0,
         attack=50.0, attack_speed=0.55, dps=28.0),
    Hero(name='올라프', cost=4, origins={Origin(name='빙하')}, hero_classes={HeroClass(name='광전사')}, hp=750.0, armor=35.0,
         attack=70.0, attack_speed=0.85, dps=60.0),
    Hero(name='요릭', cost=4, origins={Origin(name='빛')}, hero_classes={HeroClass(name='소환사')}, hp=800.0, armor=35.0,
         attack=65.0, attack_speed=0.7, dps=46.0),
    Hero(name='워윅', cost=1, origins={Origin(name='빙하')}, hero_classes={HeroClass(name='포식자')}, hp=650.0, armor=30.0,
         attack=50.0, attack_speed=0.6, dps=30.0),
    Hero(name='이즈리얼', cost=3, origins={Origin(name='빙하')}, hero_classes={HeroClass(name='정찰대')}, hp=600.0, armor=20.0,
         attack=65.0, attack_speed=0.7, dps=46.0),
    Hero(name='자이라', cost=1, origins={Origin(name='지옥불')}, hero_classes={HeroClass(name='소환사')}, hp=500.0, armor=20.0,
         attack=40.0, attack_speed=0.65, dps=26.0),
    Hero(name='잔나', cost=4, origins={Origin(name='바람')}, hero_classes={HeroClass(name='신비술사')}, hp=600.0, armor=20.0,
         attack=45.0, attack_speed=0.7, dps=32.0),
    Hero(name='잭스', cost=2, origins={Origin(name='빛')}, hero_classes={HeroClass(name='광전사')}, hp=650.0, armor=30.0,
         attack=50.0, attack_speed=0.8, dps=40.0),
    Hero(name='제드', cost=5, origins={Origin(name='전기')}, hero_classes={HeroClass(name='암살자'), HeroClass(name='소환사')},
         hp=850.0, armor=30.0, attack=80.0, attack_speed=1.0, dps=80.0),
    Hero(name='카직스', cost=4, origins={Origin(name='사막')}, hero_classes={HeroClass(name='암살자')}, hp=750.0, armor=25.0,
         attack=75.0, attack_speed=0.8, dps=60.0),
    Hero(name='코그모', cost=1, origins={Origin(name='맹독')}, hero_classes={HeroClass(name='포식자')}, hp=500.0, armor=20.0,
         attack=45.0, attack_speed=0.7, dps=32.0),
    Hero(name='키아나', cost=3, origins={Origin(name='대지'), Origin(name='지옥불'), Origin(name='바람'), Origin(name='바다')},
         hero_classes={HeroClass(name='암살자')}, hp=650.0, armor=25.0, attack=65.0, attack_speed=0.7, dps=46.0),
    Hero(name='킨드레드', cost=3, origins={Origin(name='그림자'), Origin(name='지옥불')}, hero_classes={HeroClass(name='정찰대')},
         hp=650.0, armor=20.0, attack=55.0, attack_speed=0.75, dps=41.0),
    Hero(name='타릭', cost=5, origins={Origin(name='수정')}, hero_classes={HeroClass(name='파수꾼')}, hp=850.0, armor=60.0,
         attack=60.0, attack_speed=0.65, dps=39.0),
    Hero(name='탈리야', cost=1, origins={Origin(name='대지')}, hero_classes={HeroClass(name='요술사')}, hp=500.0, armor=20.0,
         attack=40.0, attack_speed=0.65, dps=26.0),
    Hero(name='트위치', cost=4, origins={Origin(name='맹독')}, hero_classes={HeroClass(name='정찰대')}, hp=650.0, armor=20.0,
         attack=60.0, attack_speed=0.75, dps=45.0)]

ALL_HEROES_DICT = {
    v.name: v for v in ALL_HEROES
}
ALL_SYNERGY = {
    '신비술사': [2, 4],
    '파수꾼': [2, 4, 6],
    '암살자': [3, 6],
    '드루이드': [2],
    '아바타': [1],
    '광전사': [3, 6],
    '포식자': [2, 4, 6],
    '요술사': [3, 6],
    '검사': [2, 4, 6],
    '소환사': [3, 6],
    '정찰대': [2, 4, 6],
    '연금술사': [1],
    '바다': [2, 4, 6],
    '빛': [3, 6, 9],
    '강철': [2, 3, 4],
    '숲': [3],
    '지옥불': [3, 6, 9],
    '그림자': [2, 4],
    '수정': [2, 4],
    '바람': [2, 3, 4],
    '빙하': [2, 4, 6],
    '전기': [2, 3, 4],
    '사막': [2, 4],
    '대지': [2],
    '맹독': [3]
}

EXP_PER_ROUND = 2

LVUP_EXP_REQUIRED_FROM_LEVEL = [
    None,  # no 0 lv. NA
    0,
    2,
    6,
    10,
    20,
    32,
    50,
    66,
    9999999999,
]


def hero_csv_to_list(hero_csv: str) -> Set[Hero]:
    return [ALL_HEROES_DICT[v] for v in hero_csv.split(",")]


def fuzzy_get_hero(name: str) -> Optional[Hero]:
    r = difflib.get_close_matches(name, ALL_HEROES_DICT.keys(), 1, 0.1)
    if r:
        return r[0]
    else:
        raise RuntimeError(f"fuzzy_get_hero: Unknown name : {name}")


def get_hero_inst(name: str, star: int):
    return HeroInstance(get_hero(name), star, [])


def get_hero(name):
    return ALL_HEROES_DICT[fuzzy_get_hero(name)]


DECK_DATA = [
    DeckTemplate("deck1", "쪼렙 코그모/고렙 신지드 몰빵", hero_csv_to_list("워윅,코그모,렉사이,브라움,문도 박사,이즈리얼,올라프,신지드"), [], 1)
]

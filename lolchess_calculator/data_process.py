from pathlib import Path


import bs4
from pprint import pprint

SRC_PATH = Path(__file__)
CHAR_HTML_FILE = SRC_PATH / ".." / "data" / "champs.html"



def parse_table_data():
    # https://lolchess.gg/champions/set2/nami
    with CHAR_HTML_FILE.open("rb") as f:
        soup = bs4.BeautifulSoup(f.read(), features="lxml")
    table = soup.find("table")
    rows = table.find_all("tr")
    data = []
    for r in rows:
        r_data = []
        for c in r.find_all("td"):
            r_data.append(c.get_text().strip())
        if not r_data:
            continue
        v = Hero(
            r_data[0],
            int(r_data[1]),
            set([Origin(n) for n in r_data[2].split(" ")]),
            set([HeroClass(n) for n in r_data[3].split(" ")]),
            float(r_data[4]),
            float(r_data[5]),
            float(r_data[6]),
            float(r_data[8]),
            float(r_data[9]),
        )
        data.append(v)
    return data


if __name__ == '__main__':
    heroes = parse_table_data()
    pprint(heroes)
import tkinter as tk
import base_data, operators
from pprint import pprint, pformat

state = base_data.InGameState(1, 0, [], [], [])

root = tk.Tk()

default_height = 60


def clear():
    T_onboard.delete(1.0, tk.END)
    t_onshop.delete(1.0, tk.END)


def output(text):
    t_output.config(state=tk.NORMAL)
    t_output.delete(1.0, tk.END)
    t_output.insert(tk.END, text)
    t_output.config(state=tk.DISABLED)


def on_select(e):
    if e:
        try:
            print(e.__dict__)
            print(e.widget.selection_get())
        except:
            pass


def parse_game_state():
    level = int(e_level.get())
    r = base_data.InGameState(
        level, 0, hero_inst_from_textarea(T_onboard), [], hero_from_textarea(t_onshop)
    )
    return r


def hero_from_textarea(text_control):
    str_onboard = text_control.get(1.0, tk.END)
    hero_onboard = parse_hero_str(str_onboard)
    return hero_onboard


def hero_inst_from_textarea(text_control):
    str_onboard = text_control.get(1.0, tk.END)
    hero_onboard = parse_hero_inst_str(str_onboard)
    return hero_onboard


def parse_hero_inst_str(str_onboard):
    v1 = [str_tup.split(" ") for str_tup in str_onboard.strip().split("\n") if str_tup]
    result = []
    for v in v1:
        star = 1
        if len(v) > 1:
            star = int(v[1])
        result.append(base_data.get_hero_inst(v[0], star))
    return result


def parse_hero_str(str_onboard):
    v1 = [base_data.get_hero(v) for v in str_onboard.strip().split("\n") if v]
    return v1


def calculate():
    try:
        game_state = parse_game_state()

        roll_count = int(e_roll_count.get())
        seen_count = operators.simulate_with_no_reroll(state.level, 0, roll_count)
        deck_size = int(e_deck_size.get())
        synergy_chances = operators.calculate_synergy_likelyhood_from_seen_counter(seen_count, game_state)
        interested = []
        for v in synergy_chances:
            if len(v.likely_heroes) != deck_size:
                continue
            # if sum([syn.count for syn in v.synergies]) <= deck_size:
            #     continue
            interested.append((operators.score_deck(v), v))
        interested.sort(key=lambda v: v[0], reverse=True)
        msg = ""
        for v in interested[:20]:
            msg += f"{v[0]:.2f}\t{pformat(v[1])}\n"
        output(msg)
    except Exception as e:
        output(str(e))
        raise e


tk.Label(root, text="on_board").grid(row=3, column=1)
T_onboard = tk.Text(root, height=default_height, width=30)
T_onboard.grid(row=4, column=1)
T_onboard.insert(tk.END, "")

tk.Label(root, text="on_shop").grid(row=3, column=3)
t_onshop = tk.Text(root, height=default_height, width=30)
t_onshop.grid(row=4, column=3)
t_onshop.insert(tk.END, "")

tk.Label(root, text="output").grid(row=3, column=4)
t_output = tk.Text(root, height=default_height, width=200, bg="black", fg="white", wrap=tk.NONE)
t_output.grid(row=4, column=4)
t_output.insert(tk.END, "stdout/err")

tk.Label(root, text="reference").grid(row=3, column=5)
t_ref = tk.Text(root, height=default_height, width=30, bg="black", fg="white", wrap=tk.NONE)
t_ref.grid(row=4, column=5)
reftext = "\n".join(sorted([f"{h.cost} - {h.name}" for h in base_data.ALL_HEROES]))
t_ref.insert(tk.END, reftext)
t_ref.config(state=tk.DISABLED)
t_ref.bind("<<Selection>>", on_select)

tk.Label(root, text="Look forward re-rolls").grid(row=0, column=1)
e_roll_count = tk.Entry(root, width=5)
e_roll_count.grid(row=0, column=2)
e_roll_count.insert(tk.END, "5")

tk.Label(root, text="Level").grid(row=1, column=1)
e_level = tk.Entry(root, width=5)
e_level.grid(row=1, column=2)
e_level.insert(tk.END, "1")

tk.Label(root, text="Deck Size").grid(row=2, column=1)
e_deck_size = tk.Entry(root, width=5)
e_deck_size.grid(row=2, column=2)
e_deck_size.insert(tk.END, "4")

b = tk.Button(root, text="Calculate", command=calculate)
b.grid(row=0, column=0)

b = tk.Button(root, text="Clear", command=clear)
b.grid(row=1, column=0)

root.bind("<F5>", lambda x: calculate())

tk.mainloop()

import tkinter as tk
from tkinter import ttk
    
from Logic import estimate_equity, fold_chance, suggest_bet_sizing
  

def run_calculations():
    hero_hand = hero_entry.get().split()
    board_cards = board_entry.get().split()
    pot = float(pot_entry.get())
    bet = float(bet_entry.get())
    street = street_var.get()
    in_position = pos_var.get()
    profile = profile_var.get()

    equity = estimate_equity(hero_hand, board_cards)
    fc = fold_chance(bet, pot, street, in_position, profile, board_cards)
    best_size, evs = suggest_bet_sizing(equity, pot, fc)

    equity_label.config(text=f"Equity: {equity:.2%}")
    fc_label.config(text=f"Fold Chance: {fc:.2%}")
    best_label.config(text=f"Best Bet Size: {best_size*100:.0f}% pot")

    ev_text = "\n".join([f"{mult*100:.0f}% pot → EV: {ev:.2f}" for mult, ev in evs])
    ev_label.config(text=ev_text)


root = tk.Tk()
root.title("Heads-Up Poker Helper")

tk.Label(root, text="Hero Hand:").grid(row=0, column=0)
hero_entry = tk.Entry(root)
hero_entry.grid(row=0, column=1)

tk.Label(root, text="Board Cards:").grid(row=1, column=0)
board_entry = tk.Entry(root)
board_entry.grid(row=1, column=1)

tk.Label(root, text="Pot Size:").grid(row=2, column=0)
pot_entry = tk.Entry(root)
pot_entry.grid(row=2, column=1)

tk.Label(root, text="Bet Size:").grid(row=3, column=0)
bet_entry = tk.Entry(root)
bet_entry.grid(row=3, column=1)

tk.Label(root, text="Street:").grid(row=4, column=0)
street_var = tk.StringVar(value="flop")
ttk.Combobox(root, textvariable=street_var, values=["preflop", "flop", "turn", "river"]).grid(row=4, column=1)

pos_var = tk.BooleanVar()
tk.Checkbutton(root, text="In Position", variable=pos_var).grid(row=5, column=1, sticky="w")

tk.Label(root, text="Opponent Profile:").grid(row=6, column=0)
profile_var = tk.StringVar(value="neutral")
ttk.Combobox(root, textvariable=profile_var, values=["tight", "tag", "neutral", "lag", "station"]).grid(row=6, column=1)

tk.Button(root, text="Calculate", command=run_calculations).grid(row=7, column=0, columnspan=2)

equity_label = tk.Label(root, text="Equity: ")
equity_label.grid(row=8, column=0, columnspan=2)

fc_label = tk.Label(root, text="Fold Chance: ")
fc_label.grid(row=9, column=0, columnspan=2)

best_label = tk.Label(root, text="Best Bet Size: ")
best_label.grid(row=10, column=0, columnspan=2)

ev_label = tk.Label(root, text="", justify="left")
ev_label.grid(row=11, column=0, columnspan=2)

root.mainloop()
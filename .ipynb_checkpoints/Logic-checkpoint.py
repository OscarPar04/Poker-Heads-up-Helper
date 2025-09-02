import math
import random
from treys import Card, Deck, Evaluator

def estimate_equity(hero_hand, board_cards, num_simulations=1000):
    evaluator = Evaluator()
    hero_hand = [Card.new(c) for c in hero_hand]
    board_cards = [Card.new(c) for c in board_cards]
    deck = Deck()
    
    # Remove known cards from the deck
    known_cards = hero_hand + board_cards
    for card in known_cards:
        deck.cards.remove(card)
    
    wins = 0
    ties = 0

    for _ in range(num_simulations):
        random.shuffle(deck.cards)
        # Draw opponent hand
        opp_hand = deck.draw(2)

        # Fill in missing board cards
        total_board = board_cards[:]
        num_missing = 5 - len(total_board)
        total_board += deck.draw(num_missing)

        hero_score = evaluator.evaluate(total_board, hero_hand)
        opp_score = evaluator.evaluate(total_board, opp_hand)

        if hero_score < opp_score:
            wins += 1
        elif hero_score == opp_score:
            ties += 1
        # else: opponent wins (do nothing)

        # Return used cards to deck
        deck.cards += opp_hand + total_board[len(board_cards):]
    
    equity = (wins + ties * 0.5) / num_simulations
    return equity


def suggest_bet_sizing(equity, pot, fold_chance, bet_multipliers=[0.25, 0.5, 0.75, 1.0]):
    best_ev = float('-inf')
    best_size = None
    evs = []

    for mult in bet_multipliers:
        bet = pot * mult
        ev = fold_chance * pot + (1 - fold_chance) * (equity * (pot + bet) - (1 - equity) * bet)
        evs.append((mult, ev))

        if ev > best_ev:
            best_ev = ev
            best_size = mult

    return best_size, evs


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def board_texture_score(board_cards):
    # board_cards: ['Ah','7d','2c'] etc.
    ranks = [c[0] for c in board_cards]
    suits = [c[1] for c in board_cards]
    unique_suits = len(set(suits))
    is_paired = any(ranks.count(r) >= 2 for r in set(ranks))
    high_present = any(r in 'AKQ' for r in ranks)

    # connectivity: quick heuristic using rank order
    order = '23456789TJQKA'
    idxs = sorted(order.index(r) for r in ranks)
    gaps = [idxs[i+1]-idxs[i] for i in range(len(idxs)-1)]
    disconnected = all(g >= 3 for g in gaps) if len(gaps) >= 1 else True
    two_to_straight = any(g <= 2 for g in gaps)

    mod = 0.0
    if unique_suits == 3 and not is_paired and not high_present:
        mod += 0.15  # dry rainbow low
    if disconnected: 
        mod += 0.10 
    if unique_suits == 2:
        mod -= 0.15  # two-tone
    if unique_suits == 1:
        mod -= 0.20  # monotone
    if two_to_straight:
        mod -= 0.10
    if is_paired and any(r in 'AKQ' for r in set(ranks)):
        mod -= 0.10  # high card present

    return max(-0.20, min(0.20, mod))


def fold_chance(bet, pot, street='flop', in_position=False, profile='neutral', board=None):
    # Street params (alpha, beta)
    params = {
        'flop': (-1.0, 2.0),
        'turn': (-0.5, 2.2),
        'river': (0.0, 2.5),
        'preflop': (-1.5, 1.8),
    }
    alpha, beta = params.get(street, (-1.0, 2.0))
    ratio = max(0.01, min(3.0, bet / max(1e-9, pot)))  # cap 0.01x–3x

    base = sigmoid(alpha + beta * ratio)

    pos_mod = -0.05 if in_position else +0.05
    prof_mod = {
        'tight': +0.15, 'tag': +0.05, 'neutral': 0.0,
        'lag': -0.05, 'station': -0.15
    }.get(profile, 0.0)
    board_mod = board_texture_score(board or []) if board else 0.0

    p = base + pos_mod + prof_mod + board_mod
    return max(0.02, min(0.98, p))

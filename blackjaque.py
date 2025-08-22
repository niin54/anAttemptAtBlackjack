import random
import os

# ===== Colors =====
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"

# ===== Game Settings =====
NUM_DECKS = 6
SHUFFLE_POINT = 0.25
bankroll = 1000
base_unit = bankroll * 0.01

# ===== Card Values =====
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
          '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
hi_lo = {'2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 0, '8': 0, '9': 0,
         '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1}

# ===== Toggles =====
show_table = False
show_recommend = False
show_counts = False

# ===== Basic Strategy Table (Multi-Deck, S17) =====
strategy_table = {
    'hard': {
        8: ['H']*10,
        9: ['H','D','D','D','D','H','H','H','H','H'],
        10:['D']*8 + ['H','H'],
        11:['D']*10,
        12:['H','H','S','S','S','H','H','H','H','H'],
        13:['S']*5 + ['H']*5,
        14:['S']*5 + ['H']*5,
        15:['S']*5 + ['H']*5,
        16:['S']*5 + ['H']*5,
        17:['S']*10
    },
    'soft': {
        'A2':['H','H','H','D','D','H','H','H','H','H'],
        'A3':['H','H','H','D','D','H','H','H','H','H'],
        'A4':['H','H','D','D','D','H','H','H','H','H'],
        'A5':['H','H','D','D','D','H','H','H','H','H'],
        'A6':['H','D','D','D','D','H','H','H','H','H'],
        'A7':['S','D','D','D','D','S','S','H','H','H'],
        'A8':['S']*10,
        'A9':['S']*10
    },
    'pair': {
        '2':['P','P','P','P','P','P','H','H','H','H'],
        '3':['P','P','P','P','P','P','H','H','H','H'],
        '4':['H','H','H','P','P','H','H','H','H','H'],
        '6':['P','P','P','P','P','H','H','H','H','H'],
        '7':['P','P','P','P','P','P','H','H','H','H'],
        '8':['P']*10,
        '9':['P','P','P','P','P','S','P','P','S','S'],
        'A':['P']*10
    }
}

# ===== Shoe & Count =====
shoe = []
running_count = 0

def build_shoe():
    deck = list(values.keys()) * 4
    shoe.clear()
    for _ in range(NUM_DECKS):
        shoe.extend(deck)
    random.shuffle(shoe)

build_shoe()

def draw_card():
    global running_count
    if len(shoe) < NUM_DECKS*52*SHUFFLE_POINT:
        build_shoe()
        print(f"{YELLOW}*** Shoe reshuffled! ***{RESET}")
    card = shoe.pop()
    running_count += hi_lo[card]
    return card

def hand_value(hand):
    val = sum(values[c] for c in hand)
    aces = hand.count('A')
    while val > 21 and aces:
        val -= 10
        aces -= 1
    return val

def display_table():
    print(f"{BOLD}HARD TOTALS{RESET}")
    print("Player |  2  3  4  5  6  7  8  9  T  A")
    for k,v in strategy_table['hard'].items():
        row = f"{k:<6} |"
        for move in v:
            color = BLUE if move=='H' else GREEN if move=='S' else YELLOW
            row += f" {color}{move}{RESET} "
        print(row)
    print(f"\n{BOLD}SOFT TOTALS{RESET}")
    for k,v in strategy_table['soft'].items():
        row = f"{k:<6} |"
        for move in v:
            color = BLUE if move=='H' else GREEN if move=='S' else YELLOW
            row += f" {color}{move}{RESET} "
        print(row)
    print(f"\n{BOLD}PAIRS{RESET}")
    for k,v in strategy_table['pair'].items():
        row = f"{k*2:<6} |"
        for move in v:
            color = CYAN if move=='P' else BLUE if move=='H' else GREEN
            row += f" {color}{move}{RESET} "
        print(row)

def get_recommendation(hand, dealer_up):
    dealer_idx = "A" if dealer_up=='A' else dealer_up
    if len(hand)==2 and hand[0]==hand[1] and hand[0] in strategy_table['pair']:
        return strategy_table['pair'][hand[0]][index_for_card(dealer_up)]
    if 'A' in hand and hand_value(hand)<=21 and hand_value(hand)>=13:
        key = 'A'+str(hand_value(hand)-11)
        if key in strategy_table['soft']:
            return strategy_table['soft'][key][index_for_card(dealer_up)]
    hv = hand_value(hand)
    if hv in strategy_table['hard']:
        return strategy_table['hard'][hv][index_for_card(dealer_up)]
    return 'H' if hv < 17 else 'S'

def index_for_card(card):
    return {'2':0,'3':1,'4':2,'5':3,'6':4,'7':5,'8':6,'9':7,'10':8,'J':8,'Q':8,'K':8,'A':9}[card]

def true_count():
    decks_remaining = max(1, len(shoe)/52)
    return round(running_count/decks_remaining, 2)

# ===== Main Loop =====
while True:
    os.system('clear' if os.name=='posix' else 'cls')
    if show_counts:
        print(f"{CYAN}Running Count:{RESET} {running_count}  |  {CYAN}True Count:{RESET} {true_count()}")
    if show_table:
        display_table()

    player = [draw_card(), draw_card()]
    dealer = [draw_card(), draw_card()]

    recommended_bet = base_unit * max(1, int(true_count())) if true_count() > 0 else base_unit
    print(f"\nBankroll: {bankroll} | Recommended Bet: {recommended_bet:.2f}")
    bet = float(input("Enter bet: "))

    print(f"Dealer shows: {dealer[0]}  | Your hand: {player} ({hand_value(player)})")
    if show_recommend:
        rec = get_recommendation(player, dealer[0])
        print(f"{YELLOW}Recommended Move:{RESET} {rec}")

    while hand_value(player) < 21:
        action = input("[H]it, [S]tand, [D]ouble, [T]oggle table, [R]ec toggle, [C]ount toggle: ").upper()
        if action == 'H':
            player.append(draw_card())
            print(f"You drew {player[-1]} -> {player} ({hand_value(player)})")
        elif action == 'S':
            break
        elif action == 'D':
            bet *= 2
            player.append(draw_card())
            break
        elif action == 'T': show_table = not show_table
        elif action == 'R': show_recommend = not show_recommend
        elif action == 'C': show_counts = not show_counts

    if hand_value(player) > 21:
        print(f"{RED}BUST!{RESET} You lose.")
        bankroll -= bet
        input("Press Enter...")
        continue

    while hand_value(dealer) < 17:
        dealer.append(draw_card())

    print(f"Dealer's hand: {dealer} ({hand_value(dealer)})")
    pv, dv = hand_value(player), hand_value(dealer)
    if dv > 21 or pv > dv: bankroll += bet
    elif pv < dv: bankroll -= bet
    else: pass

    print(f"New bankroll: {bankroll}")
    input("Press Enter to continue...")

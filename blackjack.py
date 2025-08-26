# main_blackjack_game.py

import random
import os
import time

# --- Configuration ---
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
DEALER_HITS_ON_SOFT_17 = True
MAX_PLAYERS = 6 # Dealer + 5 others

# --- Helper Functions ---
def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_hand_value(hand):
    """Calculates the value of a hand, handling Aces correctly."""
    value = sum(VALUES[card.rank] for card in hand)
    num_aces = sum(1 for card in hand if card.rank == 'A')
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

# --- Classes ---
class Card:
    """Represents a single playing card."""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    """Represents the shoe of playing cards."""
    def __init__(self, num_decks=4):
        self.num_decks = num_decks
        self.cards = []
        self.build()

    def build(self):
        """Builds the deck with the specified number of 52-card decks."""
        self.cards = [Card(s, r) for _ in range(self.num_decks) for s in SUITS for r in RANKS]
        self.shuffle()

    def shuffle(self):
        """Shuffles the deck."""
        random.shuffle(self.cards)
        print("\n--- The deck has been shuffled. ---")
        time.sleep(1.5)

    def deal(self):
        """Deals one card from the deck."""
        if not self.cards:
            self.build() # Reshuffle if empty
        return self.cards.pop()

class Player:
    """Represents a player (or the dealer)."""
    def __init__(self, name, is_human=False, wallet=1000):
        self.name = name
        self.is_human = is_human
        self.wallet = wallet
        self.hands = []

    def clear_hands(self):
        """Clears all hands and bets for a new round."""
        self.hands = []

    def can_play(self):
        """Checks if the player has enough money to place a minimum bet."""
        return self.wallet >= 10 # Assuming min bet of 10

class Hand:
    """Represents a single hand for a player."""
    def __init__(self, bet):
        self.cards = []
        self.bet = bet
        self.status = 'playing'  # Can be 'playing', 'stand', 'bust', 'blackjack'
        self.insurance = 0

    def add_card(self, card):
        """Adds a card to the hand."""
        self.cards.append(card)

    def get_value(self):
        """Gets the hand's current value."""
        return get_hand_value(self.cards)

    def is_blackjack(self):
        """Checks if the hand is a natural blackjack."""
        return len(self.cards) == 2 and self.get_value() == 21

    def can_split(self):
        """Checks if the hand can be split."""
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    def __str__(self):
        return ' '.join(str(card) for card in self.cards)

class BlackjackGame:
    """Manages the entire Blackjack game flow and state."""
    def __init__(self):
        self.deck = None
        self.players = []
        self.dealer = Player("Dealer")
        self.settings = {}
        self.toggles = {
            'show_count': False,
            'show_recommendation': False,
            'show_strategy_chart': False
        }
        self.running_count = 0
        self.initial_deck_size = 0

    def get_game_settings(self):
        """Gets game settings from the user."""
        clear_screen()
        print("Welcome to Blackjack!")
        
        while True:
            try:
                num_players = int(input(f"Enter number of players (1-{MAX_PLAYERS-1}): "))
                if 1 <= num_players <= MAX_PLAYERS - 1:
                    break
                else:
                    print(f"Please enter a number between 1 and {MAX_PLAYERS-1}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        while True:
            try:
                num_decks = int(input("Enter number of decks (1-8): "))
                if 1 <= num_decks <= 8:
                    break
                else:
                    print("Please enter a number between 1 and 8.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        while True:
            try:
                shuffle_point = int(input("When to reshuffle? Enter a percentage (e.g., 50 for 50%): "))
                if 10 <= shuffle_point <= 80:
                    break
                else:
                    print("Please enter a percentage between 10 and 80.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        self.settings = {
            'num_players': num_players,
            'num_decks': num_decks,
            'shuffle_penetration': shuffle_point / 100.0
        }

    def setup_game(self):
        """Initializes the game based on settings."""
        self.deck = Deck(self.settings['num_decks'])
        self.initial_deck_size = len(self.deck.cards)
        self.running_count = 0
        
        self.players.append(Player("You", is_human=True, wallet=1000))
        for i in range(self.settings['num_players'] - 1):
            self.players.append(Player(f"CPU {i+1}", wallet=1000))
        self.players.append(self.dealer)

    def update_running_count(self, card):
        """Updates the Hi-Lo running count."""
        if card is None: return
        rank = card.rank
        if rank in ['2', '3', '4', '5', '6']:
            self.running_count += 1
        elif rank in ['10', 'J', 'Q', 'K', 'A']:
            self.running_count -= 1
    
    def get_true_count(self):
        """Calculates the true count."""
        decks_remaining = len(self.deck.cards) / 52
        return self.running_count / decks_remaining if decks_remaining > 0 else 0

    def place_bets(self):
        """Handles the betting phase for all players."""
        for player in self.players:
            if player.is_human and player.can_play():
                while True:
                    try:
                        bet_amount = int(input(f"{player.name}, you have ${player.wallet}. Place your bet: "))
                        if 10 <= bet_amount <= player.wallet:
                            player.hands.append(Hand(bet_amount))
                            player.wallet -= bet_amount
                            break
                        else:
                            print("Bet must be between $10 and your wallet amount.")
                    except ValueError:
                        print("Invalid bet amount.")
            elif not player.is_human and player.name != "Dealer" and player.can_play():
                bet_amount = 10 # Simple AI bet
                player.hands.append(Hand(bet_amount))
                player.wallet -= bet_amount
                print(f"{player.name} bets ${bet_amount}.")

    def deal_initial_cards(self):
        """Deals two cards to each player and the dealer."""
        print("\nDealing cards...")
        for _ in range(2):
            for player in self.players:
                if player.hands: # Player is in the round
                    card = self.deck.deal()
                    if player.name == "Dealer" and len(player.hands[0].cards) == 1:
                        # Dealer's second card is face down
                        player.hands[0].add_card(card)
                        self.update_running_count(player.hands[0].cards[0]) # Only up-card counts
                    else:
                        player.hands[0].add_card(card)
                        self.update_running_count(card)

        for player in self.players:
            if player.hands and player.hands[0].is_blackjack():
                player.hands[0].status = 'blackjack'

    def display_table(self, show_dealer_hole_card=False):
        """Displays the current state of the table."""
        clear_screen()
        print("--- Blackjack Table ---")
        
        # Dealer's Hand
        if show_dealer_hole_card:
            dealer_hand_str = str(self.dealer.hands[0])
            dealer_value = self.dealer.hands[0].get_value()
            print(f"Dealer's Hand: {dealer_hand_str} ({dealer_value})")
        else:
            dealer_up_card = str(self.dealer.hands[0].cards[0])
            dealer_up_value = VALUES[self.dealer.hands[0].cards[0].rank]
            print(f"Dealer's Hand: {dealer_up_card} [?] ({dealer_up_value})")
        print("-" * 25)

        # Players' Hands
        for player in self.players:
            if player.name != "Dealer":
                print(f"{player.name}'s Wallet: ${player.wallet}")
                for i, hand in enumerate(player.hands):
                    hand_label = f"Hand {i+1}: " if len(player.hands) > 1 else "Hand: "
                    hand_value = hand.get_value()
                    status_str = f" - {hand.status.upper()}" if hand.status != 'playing' else ""
                    print(f"  {hand_label}{str(hand)} ({hand_value}) Bet: ${hand.bet}{status_str}")
        
        print("-" * 25)
        if self.toggles['show_count']:
            print(f"Running Count: {self.running_count} | True Count: {self.get_true_count():.2f}")


    def play_round(self):
        """Executes a single round of Blackjack."""
        # 1. Check for reshuffle
        if len(self.deck.cards) / self.initial_deck_size < self.settings['shuffle_penetration']:
            self.deck.build()
            self.running_count = 0

        # 2. Clear hands and place bets
        for p in self.players:
            p.clear_hands()
        
        self.place_bets()
        active_players = [p for p in self.players if p.hands]
        if not any(p for p in active_players if p.is_human):
            print("You're out of money! Thanks for playing.")
            return False # End game

        # 3. Deal initial cards
        self.deal_initial_cards()
        self.display_table()
        
        # 4. Handle insurance if dealer shows Ace
        dealer_up_card = self.dealer.hands[0].cards[0]
        if dealer_up_card.rank == 'A':
            self.offer_insurance()

        # 5. Check for dealer blackjack
        if self.dealer.hands[0].is_blackjack():
            print("Dealer has Blackjack!")
            self.settle_bets()
            return True

        # 6. Player turns
        for player in self.players:
            if player.name != "Dealer":
                current_hand_index = 0
                while current_hand_index < len(player.hands):
                    hand = player.hands[current_hand_index]
                    if hand.status == 'blackjack':
                        current_hand_index += 1
                        continue
                    
                    if player.is_human:
                        self.human_turn(player, hand)
                    else:
                        self.cpu_turn(player, hand)
                    
                    current_hand_index += 1

        # 7. Dealer's turn
        self.dealer_turn()

        # 8. Settle bets
        self.settle_bets()

        return True

    def offer_insurance(self):
        """Offers the insurance side bet to players."""
        print("\nDealer is showing an Ace. Insurance is open.")
        for player in self.players:
            if not player.hands or player.hands[0].is_blackjack(): continue

            hand = player.hands[0]
            if player.is_human and player.wallet >= hand.bet / 2:
                choice = input("Take insurance? (y/n): ").lower()
                if choice == 'y':
                    insurance_bet = hand.bet / 2
                    hand.insurance = insurance_bet
                    player.wallet -= insurance_bet
                    print(f"You placed an insurance bet of ${insurance_bet}.")
            elif not player.is_human and player.wallet >= hand.bet / 2:
                # CPU takes insurance if true count is high
                if self.get_true_count() >= 3:
                    insurance_bet = hand.bet / 2
                    hand.insurance = insurance_bet
                    player.wallet -= insurance_bet
                    print(f"{player.name} takes insurance.")

    def human_turn(self, player, hand):
        """Manages the human player's turn for a specific hand."""
        while hand.status == 'playing':
            self.display_table()
            
            # Show toggled info
            if self.toggles['show_strategy_chart']:
                self.display_strategy_chart()
            if self.toggles['show_recommendation']:
                move = self.get_recommended_move(hand, self.dealer.hands[0].cards[0])
                print(f"Basic Strategy Suggests: {move}")

            # Get player action
            actions = ['(H)it', '(S)tand']
            if len(hand.cards) == 2 and player.wallet >= hand.bet:
                actions.append('(D)ouble Down')
            if hand.can_split() and player.wallet >= hand.bet:
                actions.append('s(P)lit')
            
            action = input(f"\n{player.name}, what's your move for hand [{str(hand)}]? {' / '.join(actions)}: ").lower()

            # Process action
            if action == 'h':
                new_card = self.deck.deal()
                hand.add_card(new_card)
                self.update_running_count(new_card)
                print(f"You drew a {new_card}.")
                if hand.get_value() > 21:
                    hand.status = 'bust'
                    print("Bust!")
            
            elif action == 's':
                hand.status = 'stand'
            
            elif action == 'd' and '(D)ouble Down' in actions:
                player.wallet -= hand.bet
                hand.bet *= 2
                new_card = self.deck.deal()
                hand.add_card(new_card)
                self.update_running_count(new_card)
                print(f"You doubled down and drew a {new_card}.")
                if hand.get_value() > 21:
                    hand.status = 'bust'
                    print("Bust!")
                else:
                    hand.status = 'stand'
            
            elif action == 'p' and 's(P)lit' in actions:
                # Create a new hand
                new_hand = Hand(hand.bet)
                # Move one card to the new hand
                new_hand.add_card(hand.cards.pop())
                # Deduct bet for new hand
                player.wallet -= hand.bet
                # Add new hand to player's hands list
                player.hands.append(new_hand)
                # Deal a new card to each split hand
                card1 = self.deck.deal()
                hand.add_card(card1)
                self.update_running_count(card1)
                card2 = self.deck.deal()
                new_hand.add_card(card2)
                self.update_running_count(card2)
                print("You split your hand.")
            else:
                print("Invalid action.")
            
            time.sleep(1)

    def cpu_turn(self, player, hand):
        """Manages a computer player's turn using basic strategy."""
        while hand.status == 'playing':
            self.display_table()
            print(f"\n{player.name}'s turn for hand [{str(hand)}]...")
            time.sleep(1.5)

            move = self.get_recommended_move(hand, self.dealer.hands[0].cards[0])
            
            if move == "Split" and hand.can_split() and player.wallet >= hand.bet:
                new_hand = Hand(hand.bet)
                new_hand.add_card(hand.cards.pop())
                player.wallet -= hand.bet
                player.hands.append(new_hand)
                card1, card2 = self.deck.deal(), self.deck.deal()
                hand.add_card(card1)
                new_hand.add_card(card2)
                self.update_running_count(card1)
                self.update_running_count(card2)
                print(f"{player.name} splits.")
            elif move == "Double Down" and len(hand.cards) == 2 and player.wallet >= hand.bet:
                player.wallet -= hand.bet
                hand.bet *= 2
                new_card = self.deck.deal()
                hand.add_card(new_card)
                self.update_running_count(new_card)
                print(f"{player.name} doubles down and gets a {new_card}.")
                if hand.get_value() > 21:
                    hand.status = 'bust'
                else:
                    hand.status = 'stand'
            elif move == "Hit":
                new_card = self.deck.deal()
                hand.add_card(new_card)
                self.update_running_count(new_card)
                print(f"{player.name} hits and gets a {new_card}.")
                if hand.get_value() > 21:
                    hand.status = 'bust'
            else: # Stand
                hand.status = 'stand'
                print(f"{player.name} stands.")
            
            time.sleep(1.5)

    def dealer_turn(self):
        """Manages the dealer's turn."""
        dealer_hand = self.dealer.hands[0]
        # Reveal hole card and update count
        self.update_running_count(dealer_hand.cards[1])
        self.display_table(show_dealer_hole_card=True)
        print("\nDealer's turn...")
        time.sleep(1.5)

        while dealer_hand.status == 'playing':
            hand_value = dealer_hand.get_value()
            if hand_value > 21:
                dealer_hand.status = 'bust'
            elif hand_value >= 17:
                if hand_value == 17 and any(c.rank == 'A' for c in dealer_hand.cards) and DEALER_HITS_ON_SOFT_17:
                    pass # Continue to hit
                else:
                    dealer_hand.status = 'stand'
            
            if dealer_hand.status == 'playing':
                new_card = self.deck.deal()
                dealer_hand.add_card(new_card)
                self.update_running_count(new_card)
                self.display_table(show_dealer_hole_card=True)
                print(f"Dealer hits and gets a {new_card}.")
                time.sleep(1.5)
        
        self.display_table(show_dealer_hole_card=True)
        print(f"Dealer stands with {dealer_hand.get_value()}.")
        time.sleep(1)

    def settle_bets(self):
        """Compares hands and settles all bets for the round."""
        print("\n--- Round Over ---")
        dealer_hand = self.dealer.hands[0]
        dealer_value = dealer_hand.get_value()
        dealer_has_blackjack = dealer_hand.is_blackjack()

        # Settle insurance first
        for player in self.players:
            if player.hands and player.hands[0].insurance > 0:
                if dealer_has_blackjack:
                    payout = player.hands[0].insurance * 3 # 2:1 payout + original bet back
                    player.wallet += payout
                    print(f"{player.name} wins ${payout} on insurance.")
                else:
                    print(f"{player.name} loses insurance bet.")

        # Settle main bets
        for player in self.players:
            if player.name != "Dealer":
                for hand in player.hands:
                    player_value = hand.get_value()
                    msg = f"{player.name}'s hand [{str(hand)}] ({player_value}): "

                    if hand.status == 'blackjack':
                        if dealer_has_blackjack:
                            msg += "Push."
                            player.wallet += hand.bet
                        else:
                            payout = hand.bet * 2.5 # 3:2 payout
                            msg += f"Blackjack! You win ${payout}."
                            player.wallet += payout
                    elif hand.status == 'bust':
                        msg += "Bust. You lose."
                    elif dealer_hand.status == 'bust':
                        msg += f"Dealer busts. You win ${hand.bet*2}."
                        player.wallet += hand.bet * 2
                    elif player_value > dealer_value:
                        msg += f"You win ${hand.bet*2}."
                        player.wallet += hand.bet * 2
                    elif player_value == dealer_value:
                        msg += "Push."
                        player.wallet += hand.bet
                    else: # player_value < dealer_value
                        msg += "You lose."
                    print(msg)
    
    def manage_toggles(self):
        """Allows the user to turn on/off helper features."""
        clear_screen()
        print("--- Feature Toggles ---")
        print(f"1. Show Running Count ..... {'ON' if self.toggles['show_count'] else 'OFF'}")
        print(f"2. Show Recommendation .... {'ON' if self.toggles['show_recommendation'] else 'OFF'}")
        print(f"3. Show Strategy Chart .... {'ON' if self.toggles['show_strategy_chart'] else 'OFF'}")
        print("Enter a number to toggle a feature, or press Enter to continue.")
        
        choice = input("> ")
        if choice == '1':
            self.toggles['show_count'] = not self.toggles['show_count']
        elif choice == '2':
            self.toggles['show_recommendation'] = not self.toggles['show_recommendation']
        elif choice == '3':
            self.toggles['show_strategy_chart'] = not self.toggles['show_strategy_chart']
        else:
            return
        self.manage_toggles() # Recursive call to show updated menu

    def get_recommended_move(self, player_hand, dealer_up_card):
        """Determines the best move based on basic strategy."""
        player_value = player_hand.get_value()
        dealer_value = VALUES[dealer_up_card.rank]
        is_soft = any(c.rank == 'A' for c in player_hand.cards) and player_value - 11 < 11
        
        # Pairs
        if player_hand.can_split():
            p_rank = VALUES[player_hand.cards[0].rank]
            if p_rank == 11 or p_rank == 8: return "Split"
            if p_rank == 9 and dealer_value not in [7, 10, 11]: return "Split"
            if p_rank == 7 and dealer_value <= 7: return "Split"
            if p_rank == 6 and dealer_value <= 6: return "Split"
            if p_rank == 4 and dealer_value in [5, 6]: return "Split"
            if p_rank in [3, 2] and dealer_value <= 7: return "Split"

        # Soft totals
        if is_soft:
            if player_value >= 19: return "Stand"
            if player_value == 18:
                return "Stand" if dealer_value <= 8 else "Hit"
            return "Hit"

        # Hard totals
        if player_value >= 17: return "Stand"
        if player_value <= 8: return "Hit"
        if player_value == 12 and dealer_value in [4, 5, 6]: return "Stand"
        if player_value in [13, 14, 15, 16] and dealer_value <= 6: return "Stand"
        if player_value == 11: return "Double Down"
        if player_value == 10 and dealer_value <= 9: return "Double Down"
        if player_value == 9 and dealer_value in [3,4,5,6]: return "Double Down"

        return "Hit" # Default action
    
    def display_strategy_chart(self):
        chart = """
--- Basic Strategy Chart (Dealer Hits Soft 17) ---
   |  2   3   4   5   6   7   8   9   10  A
---+-----------------------------------------  (H)it  (S)tand  (D)ouble  (P)air-Split
H 17+| S | S | S | S | S | S | S | S | S | S |
H 16 | S | S | S | S | S | H | H | H | H | H |
H 15 | S | S | S | S | S | H | H | H | H | H |
H 14 | S | S | S | S | S | H | H | H | H | H |
H 13 | S | S | S | S | S | H | H | H | H | H |
H 12 | H | H | S | S | S | H | H | H | H | H |
H 11 | D | D | D | D | D | D | D | D | D | D |
H 10 | D | D | D | D | D | D | D | D | H | H |
H 9  | H | D | D | D | D | H | H | H | H | H |
H 5-8| H | H | H | H | H | H | H | H | H | H |
---+-----------------------------------------
S A,8+| S | S | S | S | S | S | S | S | S | S |
S A,7 | S | D | D | D | D | S | S | H | H | H |
S A,6 | H | D | D | D | D | H | H | H | H | H |
S A,4-5| H | H | D | D | D | H | H | H | H | H |
S A,2-3| H | H | H | D | D | H | H | H | H | H |
---+-----------------------------------------
P A,A| P | P | P | P | P | P | P | P | P | P |
P 10,10| S | S | S | S | S | S | S | S | S | S |
P 9,9| P | P | P | P | P | S | P | P | S | S |
P 8,8| P | P | P | P | P | P | P | P | P | P |
P 7,7| P | P | P | P | P | P | H | H | H | H |
P 6,6| P | P | P | P | P | H | H | H | H | H |
P 5,5| D | D | D | D | D | D | D | D | H | H |
P 4,4| H | H | H | P | P | H | H | H | H | H |
P 2-3| P | P | P | P | P | P | H | H | H | H |
---------------------------------------------"""
        print(chart)


# --- Main Game Loop ---
if __name__ == "__main__":
    game = BlackjackGame()
    game.get_game_settings()
    game.setup_game()

    playing = True
    while playing:
        game.manage_toggles()
        if not game.play_round():
            break

        play_again = input("\nPlay another round? (y/n): ").lower()
        if play_again != 'y':
            playing = False
    
    print("Thanks for playing!")

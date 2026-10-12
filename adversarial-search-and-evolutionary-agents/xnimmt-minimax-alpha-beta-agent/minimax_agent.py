__author__ = "Siddharth Barjatya"
__organization__ = "University of Otago"

agentName = "alpha_beta_agent"

# Importing necessary libraries
# These are tested for 3.11.13(cosc343) virtual eniornment
import copy
import random
import pandas as pd
from xnimmt import table_resolve

class XNimmtAgent():
   """
   A class that encapsulates the code dictating the
   behaviour of the agent playing the game of X Nimmt!.

   ...

   Attributes
   ----------
   deck : list of tuples with (card number, card value) in
           the card deck
   num_rows : number of rows on the table
   num_cards_in_hand : number of cards in hand
   xth_card_takes: the card that take the row

   Methods
   -------
   AgentFunction(percepts)
      Returns the card from hand to play with.
   """

   def __init__(self, deck, num_rows, max_cards_in_hand, xth_card_takes):
        """
        :param deck: list of tuples with (card number, card value) in the deck. 
        :param num_rows: number of rows on the table
        :param max_cards_in_hand: number of cards in hand
        :param xth_card_takes: the card that take the row
    
        """
        self.deck = deck
        self.num_rows = num_rows
        self.max_cards_in_hand = max_cards_in_hand
        self.xth_card_takes = xth_card_takes

        # Initialize global variables to track hidden and taken cards
        # These variables are used within the track_cards function
        self.taken_out = set()
        self.seen_previously = set() 
      
   def AgentFunction(self, percepts):
      """Returns the card from hand to play with

      :param percepts: a tuple three items: (my_hand, table, cards_played), where
      
         - my_hand - is a list of cards in hand, each a tuple with (card number, card value),
      
         - table - is a list of 4 lists of cards on the table.
      
      :return: int - card number from my_hand to play.
      """

      
      def track_cards(table, my_hand):
        '''
        Helper function to track hidden and taken cards. The functions remembers
        cards that were seen previously seen on the table and/or taken out. It resets the memory of
        the stored cards everytime a new hand is dealt (i.e., when the number of cards in hand is 
        equal to max_cards_in_hand). Keeping track of previously seen and hidden cards helps in 
        dealing a random hand for the opponent, which is necessary for the minimax algorithm to 
        work efficiently as it helps in limiting the search space. 
        '''
        # Flatten the table to get all cards on the table
        on_table = [card for row in table for card in row]

        # Reset global variables if first round (ie fresh hand)
        # This is done to ensure that the agent does not remember the cards from the previous round
        if len(my_hand) == self.max_cards_in_hand:
            self.taken_out = set()
            self.seen_previously = set()

        # Update the seen cards with the current hand and the cards on the table
        currently_visible = set(on_table) | set(my_hand)
        self.taken_out = self.seen_previously - currently_visible
        self.seen_previously |= currently_visible

        # Cards that are not on the table or taken out are considered hidden
        cards_hidden = set(self.deck) - currently_visible - self.taken_out
        return list(cards_hidden)

      def evaluate(my_hand):
         # Sum of card values left in hand (lower is better) used as a heuristic
         return -sum(c[1] for c in my_hand)
      
      '''
      Minimax with alpha-beta pruning : This function recursively evaluates the game states and 
      returns the best card to play. It uses alpha-beta pruning to optimize the search process to 
      avoid unnecessary evaluations. This function evaluates the game to a max depth. The max depth
      is a hard coded value in order to limit the search space and improve performance. 
      '''
      def minimax(table, my_hand, opp_hand, depth, alpha, beta, maximizing_player):
         if depth == 0 or not my_hand:
            return evaluate(my_hand), None

         if maximizing_player:
            max_eval = float('-inf')
            best_card = None
            for card in my_hand:
               table_copy = copy.deepcopy(table)
               # table_resolve function is imported from xnimmt.py
               # Loss is expressed as a positive value (though table_resolve function returns a negative penalty)
               loss = -table_resolve(table_copy, card, self.xth_card_takes)[1]
               # The table is updated with the card played by my agent
               table_copy = table_resolve(table_copy, card, self.xth_card_takes)[0]
               # My hand is updated by removing the card played
               new_my_hand = [c for c in my_hand if c != card]
               eval_score, _ = minimax(table_copy, new_my_hand, opp_hand, depth-1, alpha, beta, False)
               # We want to minimize the loss, so it needs to be subtracted from the evaluation score
               eval_score -= loss
               if eval_score > max_eval:
                  max_eval = eval_score
                  best_card = card
               alpha = max(alpha, eval_score)
               if beta <= alpha:
                  break
            return max_eval, best_card
         else:
            min_eval = float('inf')
            for card in opp_hand:
               table_copy = copy.deepcopy(table)
               # table_resolve function is imported from xnimmt.py
               # Loss is expressed as a positive value (though table_resolve function returns a negative penalty)
               loss = -table_resolve(table_copy, card, self.xth_card_takes)[1]
               # The table is updated with the card played by random agent
               table_copy = table_resolve(table_copy, card, self.xth_card_takes)[0]
               # The opponent's hand is updated by removing the card played
               new_opp_hand = [c for c in opp_hand if c != card]
               eval_score, _ = minimax(table_copy, my_hand, new_opp_hand, depth-1, alpha, beta, True)
               eval_score += loss  # Add loss to my score (opponent's penalty is good for me)
               if eval_score < min_eval:
                  min_eval = eval_score
               beta = min(beta, eval_score)
               if beta <= alpha:
                  break
            return min_eval, None

      '''
      All the function calls are made below to get the best card to play 
      '''

      my_hand = percepts[0]
      table = percepts[1]

      # Selected after multiple trials to balance performance and win rate
      # The max depth is the depth to which the minimax algorithm evaluates the game states
      max_depth = 7

      # The max width is the number of random hands generated for the opponent hand
      # The width in way depicts the mutliple possiblities for the minimax algorithm to explore
      # Selected after multiple trials to balance performance and win rate
      max_width = 5

      # Later used to store multiple instances of opponent's random set of hands
      opp_hands = []

      # percepts[2] param (ie cards_played) is NOT provided so need to track cards
      # Funtion call to track hidden cards 
      # (ie cards never seen on the table or in my_hand and/or taken out
      cards_hidden = track_cards(table, my_hand)     

      # Later used to store the good card choices fetched from one run of the minimax function
      good_cards = pd.DataFrame(columns=["Card"])

      # Iterating over the max width to generate multiple random hands for the opponent
      # This is done to simulate the uncertainty of the opponent's hand
      for _ in range(max_width):
        # Choosing a random hand for the opponent from the hidden cards
        # Since we do not know the opponent's hand, multiple random hands are generated
        random_hand = copy.deepcopy(cards_hidden)
        random.shuffle(random_hand)
        random_hand = random_hand[:len(my_hand)]
        opp_hands.append(random_hand)

      # Run minimax for each random hand of the opponent and collect the good card choices
      # As we are unsure of the opponent's hand, we run minimax multiple times
      for opp_hand in opp_hands:
        _, card_choice = minimax(copy.deepcopy(table), my_hand, opp_hand, max_depth, float('-inf'), float('inf'), True)
        card_number, _ = card_choice
        good_cards = pd.concat([good_cards, pd.DataFrame({"Card": [card_choice]})], ignore_index=True)
      
      # The best card is the one that appears most frequently in the good cards
      # This is a simple heuritic to choose the most promising card across any opponent's hand
      # Since a random opponent hand is equally likely, the most common card is the best choice
      best_card = good_cards["Card"].value_counts().idxmax()

      card = best_card
      if best_card is None:
        best_card = my_hand[0]
      else :
        card_number, _ = card
        action = card_number
        # Return the bid
        return action  
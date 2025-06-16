Hand Evaluation | SirRender00/texasholdem | DeepWiki
DeepWiki
SirRender00/texasholdem

Try DeepWiki for private repos in
Devin

Share

Last indexed: 25 April 2025 (84aaee)
Home
Installation and Setup
Core Game System
Game Logic
Card System
Hand Evaluation
User Interfaces
Text GUI
Game Agents
Creating Custom Agents
Game History
Development Guide
Project Structure
Testing
CI/CD Pipeline
API Reference
TexasHoldEm Class
Card and Deck
Game History
Hand Evaluation
Relevant source files
The Hand Evaluation system in the Texas Hold'em package is responsible for determining the relative strength of poker hands. It uses an optimized algorithm based on prime number encoding and lookup tables to efficiently evaluate hands, capable of ranking any poker hand on a scale from 1 (best) to 7,462 (worst).

This page details the evaluation algorithm, data structures, and API for comparing poker hands. For information about the Card representation itself, see Card System.

Overview of Hand Evaluation System
The hand evaluation system is designed with performance in mind, using a combination of bitwise operations and pre-computed lookup tables to rapidly determine hand strength. The key components are:

Prime Number Encoding: Each card rank is assigned a unique prime number, enabling combinations to be efficiently represented
Lookup Tables: Pre-computed tables mapping hand signatures to numerical ranks
Two-step Evaluation: Special detection for flushes, followed by general hand evaluation
7,462 Distinct Hand Ranks: A comprehensive ranking of all possible 5-card poker hands
5-Card Evaluation

Hand Evaluation Flow

Yes

No

Input: Hand + Board Cards

Generate all 5-card
combinations

Evaluate each 5-card combination

Find best (lowest) rank

Output: Final Hand Rank (1-7462)

Check 5 cards

Is Flush?

Use flush_lookup table

Use unsuited_lookup table

Return numerical rank

Sources: 
texasholdem/evaluator/evaluator.py
14-35
 
texasholdem/evaluator/evaluator.py
38-52

Hand Ranks and Categories
Texas Hold'em poker hands are divided into 9 rank classes, each containing multiple distinct hand ranks. The system maps every possible 5-card hand to a unique numerical rank between 1 and 7,462.

The number of distinct hand values in each category:

Rank Class	Hand Type	Distinct Values	Range
1	Straight Flush	10	1-10
2	Four of a Kind	156	11-166
3	Full House	156	167-322
4	Flush	1,277	323-1,599
5	Straight	10	1,600-1,609
6	Three of a Kind	858	1,610-2,467
7	Two Pair	858	2,468-3,325
8	Pair	2,860	3,326-6,185
9	High Card	1,277	6,186-7,462
Sources: 
texasholdem/evaluator/lookup_table.py
1-27
 
texasholdem/evaluator/lookup_table.py
45-77

Prime Number Encoding
The evaluation system uses prime number encoding as a clever way to identify hand combinations. Each card rank is assigned a unique prime number:

2: 2, 3: 3, 4: 5, 5: 7, 6: 11, 7: 13, 8: 17, 9: 19, T: 23, J: 29, Q: 31, K: 37, A: 41
When cards are multiplied together, they create a unique product that can only be formed by that specific combination of ranks. This property allows for efficient lookup and comparison operations.

Prime Number Encoding Example

Hand: A♥ A♠ K♦ K♣ Q♥

Prime Values: 41, 41, 37, 37, 31

Product: 41² × 37² × 31 = 73,629,937

Lookup in Table

Rank: 167 (Full House)

Sources: 
texasholdem/evaluator/lookup_table.py
180-264
 
texasholdem/evaluator/evaluator.py
34-35

Lookup Table Structure
The lookup table consists of two main dictionaries:

flush_lookup: Maps prime products of suited 5-card hands to their ranks
unsuited_lookup: Maps prime products of mixed-suit 5-card hands to their ranks
The tables are pre-computed when the module is first imported, using a carefully designed algorithm that generates all possible hand combinations.

LookupTable Construction

Initialize empty lookup tables

Generate flush_lookup
Table

Generate straights in
unsuited_lookup

Generate high cards in
unsuited_lookup

Generate four of a kind in
unsuited_lookup

Generate full house in
unsuited_lookup

Generate three of a kind in
unsuited_lookup

Generate two pair in
unsuited_lookup

Generate pair in
unsuited_lookup

Lookup table complete

Sources: 
texasholdem/evaluator/lookup_table.py
78-264
 
texasholdem/evaluator/lookup_table.py
286-289

Evaluation Algorithm
The evaluation process determines the best possible 5-card hand from a player's hole cards and the community cards on the board:

Combine the player's cards with the board cards
Generate all possible 5-card combinations from these cards
Evaluate each combination to determine its rank
Return the best (lowest) rank found
For each 5-card hand, the evaluation uses this algorithm:

Check if the hand is a flush (all cards share the same suit)
If it's a flush, use the flush_lookup table with the prime product of the ranks
If not a flush, use the unsuited_lookup table with the prime product of the cards
Return the numerical rank of the hand
"LOOKUP_TABLE"
"Card Utilities"
"_five()"
"evaluate()"
"Game Logic"
"LOOKUP_TABLE"
"Card Utilities"
"_five()"
"evaluate()"
"Game Logic"
alt
[Is flush]
[Not flush]
loop
[For each combination]
evaluate(player_cards, board)
Generate all 5-card combinations
_five(cards)
Check if flush
prime_product_from_rankbits(rankbits)
prime product
lookup in flush_lookup
prime_product_from_hand(cards)
prime product
lookup in unsuited_lookup
hand rank
hand rank
Find minimum rank
Best hand rank (1-7462)
Sources: 
texasholdem/evaluator/evaluator.py
14-52

API Reference
The evaluator module provides the following key functions:

evaluate(cards, board)
The main function for evaluating poker hands. Takes a player's cards and the community board cards, and returns the rank of the best possible 5-card hand.

# Example usage:
player_cards = [Card("Ah"), Card("Kh")]
board = [Card("Qh"), Card("Jh"), Card("Th"), Card("2s"), Card("3c")]
hand_rank = evaluate(player_cards, board)  # Returns 1 (Royal Flush)
get_rank_class(hand_rank)
Converts a numerical hand rank (1-7462) to a rank class (1-9).

rank_to_string(hand_rank)
Returns a human-readable string describing the hand type (e.g., "Flush", "Full House").

get_five_card_rank_percentage(hand_rank)
Returns the percentile strength of a hand - what percentage of all possible hands are worse than this one.

Sources: 
texasholdem/evaluator/evaluator.py
38-100

Integration with Game Logic
The hand evaluator is used during the settlement phase of a hand to determine the winner(s). The game logic obtains the best hand for each player and compares their ranks to distribute the pot.

Game System

At settlement

get_hand()

board

Winner determination

TexasHoldEm Class

Hand Phases

Hand Evaluation

Player Cards

Board Cards

Pot Distribution

Sources: 
tests/game/test_game.py
221-226

Performance Considerations
The evaluation system is designed for speed and efficiency:

Pre-computed Lookup Tables: All calculations are done once at import time
Prime Number Encoding: Provides a unique signature for hand combinations
Bitwise Operations: Used for fast suit comparison in flush detection
Minimal Memory Usage: Only stores necessary lookup data
This approach allows the evaluation of thousands of hands per second, making it suitable for simulations and analysis.

Sources: 
texasholdem/evaluator/evaluator.py
1-4
 
texasholdem/evaluator/lookup_table.py
1-27

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Hand Evaluation
Overview of Hand Evaluation System
Hand Ranks and Categories
Prime Number Encoding
Lookup Table Structure
Evaluation Algorithm
API Reference
evaluate(cards, board)
get_rank_class(hand_rank)
rank_to_string(hand_rank)
get_five_card_rank_percentage(hand_rank)
Integration with Game Logic
Performance Considerations
Ask Devin about SirRender00/texasholdem
Deep Research

Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
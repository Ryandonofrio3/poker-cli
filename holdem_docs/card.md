Card System | SirRender00/texasholdem | DeepWiki
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
Card System
Relevant source files
The Card System provides efficient representations of playing cards and decks in the Texas Hold'em implementation. It uses a specialized binary encoding for cards to enable fast poker hand evaluation and memory-efficient storage. This page documents the core components of the card system, their implementation details, and how they interact with other parts of the framework.

For information about hand evaluation using these card representations, see Hand Evaluation.

Card Representation
The Card class employs a compact 32-bit integer representation where different bit segments encode specific card properties. This approach optimizes memory usage and enables efficient poker operations like detecting flushes, straights, and evaluating hand rankings.

32-bit Card Representation

BitRank (bits 31-17)

Suit (bits 16-13)

Rank (bits 12-9)

Prime (bits 8-0)

Used for straight detection

Used for flush detection

Determines card value
(0=2, 1=3, ..., 12=A)

Used for hand evaluation

Sources: 
texasholdem/card/card.py
11-50

Bit Layout Structure
Bit Section	Format	Purpose
31-17	xxxbbbbb bbbbbbbb	BitRank: Bit is set at position corresponding to rank
16-13	cdhs	Suit: Clubs=8, Diamonds=4, Hearts=2, Spades=1
12-9	rrrr	Rank: Numerical rank value (0-12)
8-0	xxpppppp	Prime: Prime number associated with the rank
This representation allows for:

Unique identification of cards
Fast flush detection (by bitwise AND of suit bits)
Fast straight detection (by shifting and comparing bit patterns)
Fast hand strength evaluation (using prime number multiplication)
Sources: 
texasholdem/card/card.py
11-50
 
texasholdem/evaluator/evaluator.py
14-35

Card Examples
Here are examples of card binary representations:

Card	Binary Representation	Integer Value
King of Diamonds	00001000 00000000 01001011 00100101	134236965
Five of Spades	00000000 00001000 00010011 00000111	8389639
Jack of Clubs	00000010 00000000 10001001 00011101	33559069
Sources: 
tests/card/conftest.py
9-13

Card Class
The Card class extends the native Python int type, providing specialized methods and properties for card operations. This inheritance allows cards to be used in contexts where integers are expected while maintaining card-specific functionality.

«extends int»

Card

+STR_RANKS: str

+INT_RANKS: tuple

+PRIMES: tuple

+CHAR_RANK_TO_INT_SUIT: dict

+INT_SUIT_TO_CHAR_SUIT: str

+PRETTY_SUITS: dict

+rank: int

+suit: int

+bitrank: int

+prime: int

+pretty_string: str

+binary_string: str

+new(arg: str|int) : Card

+from_string(string: str) : Card

+from_int(card_int: int) : Card

+str() : str

+repr() : str

Sources: 
texasholdem/card/card.py
7-238

Card Creation
Cards can be created from string representations or directly from their binary integer form:

# From string (rank + suit)
card1 = Card("Kd")  # King of Diamonds
card2 = Card("As")  # Ace of Spades

# From integer
card3 = Card(134236965)  # Same as King of Diamonds
The from_string method converts a two-character string (rank + suit) to the internal integer representation, while from_int accepts an already-encoded card integer.

Sources: 
texasholdem/card/card.py
79-127

Card Properties
The Card class provides properties to access different components of the card:

Property	Description	Example for "Kd"
rank	Numerical rank (0-12)	11
suit	Numerical suit (1,2,4,8)	4
bitrank	Bit position for rank (2^rank)	2048
prime	Prime number for rank	37
pretty_string	Human-readable representation	"[ K ♦ ]"
binary_string	Binary representation for debugging	Binary format
These properties are implemented as bitwise operations on the underlying integer value, making them very efficient.

Sources: 
texasholdem/card/card.py
146-238
 
tests/card/test_card.py
32-62

Helper Functions
The card module provides several utility functions for working with collections of cards:

Card Helper Functions

Converts

Calculates

Calculates

Creates

card_strings_to_int()

prime_product_from_hand()

prime_product_from_rankbits()

card_list_to_pretty_str()

String cards to Card objects

Product of card primes

Prime product from bit pattern

Human-readable card display

Sources: 
texasholdem/card/card.py
241-312
 
tests/card/test_card.py
65-86

Deck Class
The Deck class manages a collection of Card objects representing a standard 52-card playing deck. It provides methods for common deck operations like shuffling and drawing cards.

contains

Deck

-_FULL_DECK: List[Card]

+cards: List[Card]

+init()

+shuffle() : None

+draw(num: int) : List[Card]

+str() : str

+copy(shuffle: bool) : Deck

+copy() : Deck

+deepcopy(memodict) : Deck

-_get_full_deck() : List[Card]

Card

Sources: 
texasholdem/card/deck.py
9-87

Deck Initialization and Management
When a Deck is created, it's initialized with a complete set of 52 cards and automatically shuffled. The implementation uses a static cache (_FULL_DECK) to avoid recreating the full deck for each instance.

Key methods:

shuffle(): Randomly reorders the remaining cards in the deck
draw(num=1): Removes and returns the specified number of cards from the top of the deck
copy(shuffle=True): Creates a copy of the deck with the option to shuffle it
__str__(): Returns a pretty-printed string representation of the deck
Sources: 
texasholdem/card/deck.py
19-87
 
tests/card/conftest.py
26-31

Card System Integration
The Card System serves as a foundation for several key components of the Texas Hold'em implementation. This diagram illustrates how the Card and Deck classes interact with other system components:

User Interface

Game Logic

Hand Evaluation

Card System

Used by

Manipulated by

Evaluated by

Encoded in

Uses

Provides cards to

Represented in

Displayed by

Card Class

Deck Class

Helper Functions

Evaluator Module

LOOKUP_TABLE

TexasHoldEm Class

TextGUI Class

Sources: 
texasholdem/evaluator/evaluator.py
38-52
 
texasholdem/evaluator/lookup_table.py
79-180

Hand Evaluation System
The hand evaluation system leverages the Card representation to efficiently assess hand strengths:

Flush Detection: Uses the suit bits of cards to quickly identify flushes with bitwise operations
Straight Detection: Uses the bitrank property to identify consecutive card sequences
Hand Ranking: Uses prime number multiplication for unique hand identification
For example, the _five function in the evaluator efficiently determines if a five-card hand is a flush by performing bitwise AND on the suit bits:

if cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000:
    # It's a flush, handle accordingly
This operation is significantly faster than comparing suit attributes in a traditional object-oriented approach.

Sources: 
texasholdem/evaluator/evaluator.py
14-35

Prime Number Pattern Recognition
The prime number encoding allows for unique identification of card combinations by multiplication:

Each card rank is assigned a unique prime number
Multiplying these primes creates a unique product for any combination of cards
These products serve as keys in lookup tables for rapid hand evaluation
This approach is more efficient than comparing individual card combinations
The LOOKUP_TABLE contains pre-computed mappings of prime products to hand ranks, enabling constant-time hand evaluation.

Sources: 
texasholdem/evaluator/lookup_table.py
19-27
 
texasholdem/card/card.py
59

Performance Considerations
The card representation design prioritizes performance for poker-specific operations:

Memory Efficiency: Each card requires only 4 bytes (32 bits) of memory
Fast Comparisons: Cards can be compared directly as integers
Bitwise Operations: Detecting hand patterns uses fast CPU-level bitwise operations
Lookup-Based Evaluation: Hand strength calculations use pre-computed lookup tables
Prime Number Uniqueness: Prime multiplication guarantees unique identifiers for card combinations
This efficient design enables the system to quickly evaluate millions of poker hands, making it suitable for both gameplay and statistical analysis.

Sources: 
texasholdem/card/card.py
43-49
 
texasholdem/evaluator/lookup_table.py
5-18

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Card System
Card Representation
Bit Layout Structure
Card Examples
Card Class
Card Creation
Card Properties
Helper Functions
Deck Class
Deck Initialization and Management
Card System Integration
Hand Evaluation System
Prime Number Pattern Recognition
Performance Considerations
Ask Devin about SirRender00/texasholdem
Deep Research

Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Card and Deck | SirRender00/texasholdem | DeepWiki
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
Card and Deck
Relevant source files
This documentation covers the card representation and deck management components of the texasholdem package. It focuses on the internal bit representation of cards and deck management functionality that forms the foundation of the game engine.

For information about hand evaluation using these cards, see Hand Evaluation.

Card Representation
The Card class implements an efficient 32-bit integer representation of standard playing cards. This representation allows for fast operations essential to poker hand evaluation, including prime number-based hand ranking, bit manipulation for detecting straights and flushes, and compact storage.

Card Bit Structure

bits 0-5

bits 8-11

bits 12-15

bits 16-28

Bit representation

Prime number (p)

Rank (r)

Suit (cdhs)

Bitrank (b)

Sources: 
texasholdem/card/card.py
7-50

Bit Structure
Each card is encoded as a 32-bit integer with the following bit pattern:

xxxbbbbb bbbbbbbb cdhsrrrr xxpppppp
Where:

p = Prime number representing the card rank (2, 3, 5, ..., 41)
r = Binary representation of card rank (0-12)
cdhs = Bits representing card suit (club, diamond, heart, spade)
b = Bit turned on based on rank (for fast straight detection)
x = Unused bits
Example card encodings:

Card	Binary Representation	Integer Value
King of Diamonds	00001000 00000000 01001011 00100101	134236965
Five of Spades	00000000 00001000 00010011 00000111	1057287
Jack of Clubs	00000010 00000000 10001001 00011101	33594141
Sources: 
texasholdem/card/card.py
7-50
 
texasholdem/card/card.py
146-213

Creating Cards
Cards can be created either from string representations or from pre-formed integer values:

Card()

Card()

.rank

.suit

.prime

.bitrank

.str()

.pretty_string

String (e.g., 'Kd')

Card object

Integer (e.g., 134236965)

Card rank (0-12)

Card suit (1,2,4,8)

Prime value

Bitrank

String representation

Pretty string with Unicode suits

Sources: 
texasholdem/card/card.py
79-144
 
texasholdem/card/card.py
216-238

Card Properties
The Card class provides several properties for accessing different aspects of a card:

Property	Return Type	Description	Example
rank	int	Rank as number (0-12)	Card("Kd").rank → 11
suit	int	Suit as bit value (1,2,4,8)	Card("Kd").suit → 4
prime	int	Prime number for the rank	Card("Kd").prime → 37
bitrank	int	Binary rank (2^rank)	Card("Kd").bitrank → 2048
pretty_string	str	Formatted string with Unicode suits	Card("Kd").pretty_string → "[ K ♦ ]"
Sources: 
texasholdem/card/card.py
146-238

Card Utility Functions
The module provides several utility functions for working with cards:

Function	Purpose	Example Usage
card_strings_to_int()	Convert a list of card strings to Card objects	card_strings_to_int(["Ah", "Kd"])
prime_product_from_hand()	Calculate prime product from cards	prime_product_from_hand([Card("Ah"), Card("Kd")])
prime_product_from_rankbits()	Calculate prime product from rankbits	Used in hand evaluation
card_list_to_pretty_str()	Format a list of cards with Unicode suits	card_list_to_pretty_str([Card("Ah"), Card("Kd")])
Sources: 
texasholdem/card/card.py
241-312

Deck Management
The Deck class implements a standard 52-card deck with operations for shuffling and drawing cards.

contains

52
Deck

-_FULL_DECK: List[Card] [static]

+cards: List[Card]

+init()

+shuffle()

+draw(num) : : List[Card]

+copy(shuffle) : : Deck

-_get_full_deck() : : List[Card] [static]

Card

+rank: int

+suit: int

+prime: int

+bitrank: int

+str() : : str

Sources: 
texasholdem/card/deck.py
9-87

Deck Initialization and Management
When a Deck is created, it initializes with all 52 standard playing cards and then shuffles them. The deck is implemented as a list of Card objects.

Card
Deck
Client
Card
Deck
Client
Initializes standard 52-card deck if needed
Random shuffling of cards
Cards removed from deck
__init__()
_get_full_deck()
Create Card for each rank/suit combination
shuffle()
draw(num)
List[Card]
Sources: 
texasholdem/card/deck.py
19-49

Key Methods
Method	Parameters	Return Type	Description
__init__()	None	None	Initializes with standard 52 cards and shuffles
shuffle()	None	None	Randomizes the order of remaining cards
draw(num=1)	num: int	List[Card]	Draws and removes n cards from the deck
copy(shuffle=True)	shuffle: bool	Deck	Creates a copy of the current deck
__str__()	None	str	Returns pretty string representation of the deck
Sources: 
texasholdem/card/deck.py
23-87

Static Deck Generation
The Deck class uses a static _FULL_DECK list to store the standard 52-card deck. This list is generated once and then reused when creating new Deck instances, improving performance:

Deck Creation

Yes

No

init()

_get_full_deck()

_FULL_DECK exists?

Return copy of _FULL_DECK

Generate all 52 cards

Store in _FULL_DECK

Return new deck

shuffle()

Sources: 
texasholdem/card/deck.py
54-64

Card and Deck in the Game System
The Card and Deck components form the foundation of the Texas Hold'em implementation. They are used throughout the game logic for representing player hands, community cards, and the remaining deck.

Card Usage

bit representation

prime numbers

Card

Bitwise operations

Prime product

Hand detection (flushes, straights)

Hand ranking

Game Logic Flow

draw(2) for each player

draw(3)

draw(1)

draw(1)

TexasHoldEm

Deck

Player Hands

Flop

Turn

River

Hand Evaluation

Sources: 
texasholdem/card/card.py
7-13
 
texasholdem/card/deck.py
9-15
 
texasholdem/evaluator/evaluator.py
38-52

Performance Considerations
The bit-based representation of cards offers several performance advantages:

Memory Efficiency: Each card is represented as a single 32-bit integer
Fast Hand Evaluation: Bitwise operations allow for rapid detection of straights and flushes
Unique Hand Identification: Prime number encoding enables fast hand comparison and ranking
The Deck class also implements efficient operations:

Lazy Initialization: The full 52-card deck is created only once and then copied
In-Place Modification: Cards are removed from the deck when drawn to maintain state
Shallow Copying: The copy() method allows creating deck variations without redundant card creation
Sources: 
texasholdem/card/card.py
41-50
 
texasholdem/card/deck.py
54-64
 
texasholdem/evaluator/evaluator.py
14-36

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Card and Deck
Card Representation
Bit Structure
Creating Cards
Card Properties
Card Utility Functions
Deck Management
Deck Initialization and Management
Key Methods
Static Deck Generation
Card and Deck in the Game System
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
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0

#!/usr/bin/env python3
"""
🎮 Texas Hold'em CLI API Client
Your familiar CLI experience, now powered by the FastAPI backend!
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import argparse

import requests
import websockets
from colorama import init, Fore, Back, Style
import threading
import time

# Initialize colorama for Windows compatibility
init()

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_V1_PREFIX = "/api/v1"


class PokerAPIClient:
    """Client for interacting with Texas Hold'em FastAPI backend"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_game_id: Optional[str] = None
        self.websocket = None
        self.websocket_task = None
        self.current_state: Optional[Dict[str, Any]] = None

    def _api_url(self, endpoint: str) -> str:
        """Construct full API URL"""
        return f"{self.base_url}{API_V1_PREFIX}{endpoint}"

    def _handle_api_error(self, response: requests.Response):
        """Handle API errors with user-friendly messages"""
        if response.status_code == 404:
            print(
                f"{Fore.RED}❌ Not found: {response.json().get('detail', 'Unknown error')}{Style.RESET_ALL}"
            )
        elif response.status_code == 400:
            print(
                f"{Fore.RED}❌ Bad request: {response.json().get('detail', 'Invalid input')}{Style.RESET_ALL}"
            )
        elif response.status_code >= 500:
            print(
                f"{Fore.RED}❌ Server error: {response.json().get('detail', 'Internal server error')}{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.RED}❌ API Error ({response.status_code}): {response.text}{Style.RESET_ALL}"
            )

    def check_health(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(
                    f"{Fore.GREEN}✅ API is healthy - {health['active_games']} active games{Style.RESET_ALL}"
                )
                return True
            else:
                print(
                    f"{Fore.RED}❌ API unhealthy (status {response.status_code}){Style.RESET_ALL}"
                )
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Cannot connect to API: {e}{Style.RESET_ALL}")
            return False

    def list_agents(self) -> Dict[str, Any]:
        """Get available agents"""
        try:
            response = self.session.get(self._api_url("/agents"))
            if response.status_code == 200:
                return {"agents": response.json()}
            else:
                self._handle_api_error(response)
                return {"agents": []}
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting agents: {e}{Style.RESET_ALL}")
            return {"agents": []}

    def list_presets(self) -> Dict[str, Any]:
        """Get available presets"""
        try:
            response = self.session.get(self._api_url("/games/presets"))
            if response.status_code == 200:
                return {"presets": response.json()}
            else:
                self._handle_api_error(response)
                return {"presets": []}
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting presets: {e}{Style.RESET_ALL}")
            return {"presets": []}

    def create_game(self, config: Dict[str, Any]) -> Optional[str]:
        """Create a new game"""
        try:
            response = self.session.post(self._api_url("/games"), json=config)
            if response.status_code == 201:
                result = response.json()
                self.current_game_id = result["game_id"]
                self.current_state = result["initial_state"]
                print(f"{Fore.GREEN}🎮 {result['message']}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}🎯 Game ID: {self.current_game_id}{Style.RESET_ALL}")
                return self.current_game_id
            else:
                self._handle_api_error(response)
                return None
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating game: {e}{Style.RESET_ALL}")
            return None

    def get_game_state(self) -> Optional[Dict[str, Any]]:
        """Get current game state"""
        if not self.current_game_id:
            print(f"{Fore.RED}❌ No active game{Style.RESET_ALL}")
            return None

        try:
            response = self.session.get(
                self._api_url(f"/games/{self.current_game_id}/state")
            )
            if response.status_code == 200:
                self.current_state = response.json()
                return self.current_state
            else:
                self._handle_api_error(response)
                return None
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting game state: {e}{Style.RESET_ALL}")
            return None

    def execute_action(
        self, player_id: int, action_type: str, amount: Optional[int] = None
    ) -> bool:
        """Execute a player action"""
        if not self.current_game_id:
            print(f"{Fore.RED}❌ No active game{Style.RESET_ALL}")
            return False

        action_data = {
            "player_id": player_id,
            "action_type": action_type.upper(),
        }
        if amount is not None:
            action_data["amount"] = amount

        try:
            response = self.session.post(
                self._api_url(f"/games/{self.current_game_id}/actions"),
                json=action_data,
            )
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print(f"{Fore.GREEN}✅ {result['message']}{Style.RESET_ALL}")
                    if result.get("new_state"):
                        self.current_state = result["new_state"]
                    return True
                else:
                    print(f"{Fore.RED}❌ {result['message']}{Style.RESET_ALL}")
                    return False
            else:
                self._handle_api_error(response)
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Error executing action: {e}{Style.RESET_ALL}")
            return False

    async def start_websocket(self):
        """Start WebSocket connection for real-time updates"""
        if not self.current_game_id:
            return

        websocket_url = f"ws://localhost:8000/ws/games/{self.current_game_id}"

        try:
            async with websockets.connect(websocket_url) as websocket:
                self.websocket = websocket
                print(f"{Fore.CYAN}🔌 Connected to real-time updates{Style.RESET_ALL}")

                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "game_update":
                            self.current_state = data.get("game_state")
                            # Don't print updates here to avoid cluttering CLI
                        elif data.get("type") == "error":
                            print(
                                f"{Fore.RED}🔌 WebSocket error: {data.get('message')}{Style.RESET_ALL}"
                            )
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ WebSocket disconnected: {e}{Style.RESET_ALL}")
        finally:
            self.websocket = None


class PokerCLI:
    """Enhanced CLI interface using the API backend"""

    def __init__(self):
        self.client = PokerAPIClient()
        self.running = True

    def display_banner(self):
        """Display the poker CLI banner"""
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                   🃏 TEXAS HOLD'EM POKER 🃏                   ║
║                     {Fore.YELLOW}CLI API Client Edition{Fore.CYAN}                      ║
║              {Fore.GREEN}Powered by FastAPI Backend{Fore.CYAN}                       ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)

    def display_game_state(self):
        """Display current game state (matches original CLI format)"""
        if not self.client.current_state:
            return

        state = self.client.current_state

        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}🎮 Game: {state['game_id'][:8]}... | Hand #{state['hand_number']}/{state['max_hands']}{Style.RESET_ALL}"
        )
        print(
            f"{Fore.GREEN}Phase: {state['phase']} | Pot: ${state['total_pot']}{Style.RESET_ALL}"
        )

        # Display board
        if state["board"]:
            board_str = " ".join([card["pretty_string"] for card in state["board"]])
            print(f"{Fore.MAGENTA}Board: {board_str}{Style.RESET_ALL}")

        # Display players
        print(f"\n{Fore.CYAN}Players:{Style.RESET_ALL}")
        for player in state["players"]:
            status_color = Fore.GREEN if player["is_current_player"] else Fore.WHITE
            status_marker = "👉" if player["is_current_player"] else "  "

            chips_color = (
                Fore.GREEN
                if player["chips"] > 1000
                else Fore.YELLOW
                if player["chips"] > 500
                else Fore.RED
            )

            # Show hole cards if available (debug mode or player's own cards)
            cards_str = ""
            if player.get("hole_cards"):
                cards_str = f" [{' '.join([card['pretty_string'] for card in player['hole_cards']])}]"

            print(
                f"{status_marker} {status_color}Player {player['player_id']}: {player['agent_name']}{Style.RESET_ALL}"
            )
            print(
                f"     {chips_color}${player['chips']} chips{Style.RESET_ALL} | {player['state']}{cards_str}"
            )

        # Display available actions for current player
        if state.get("current_player") is not None and state.get("available_actions"):
            actions = ", ".join(state["available_actions"])
            print(f"\n{Fore.YELLOW}Available actions: {actions}{Style.RESET_ALL}")
            if state.get("min_raise_amount"):
                print(
                    f"{Fore.YELLOW}Minimum raise: ${state['min_raise_amount']}{Style.RESET_ALL}"
                )

    def select_game_preset(self) -> Optional[str]:
        """Let user select a game preset"""
        presets_data = self.client.list_presets()
        presets = presets_data.get("presets", [])

        if not presets:
            print(f"{Fore.RED}❌ No presets available{Style.RESET_ALL}")
            return None

        print(f"\n{Fore.CYAN}Available Game Presets:{Style.RESET_ALL}")
        for i, preset in enumerate(presets, 1):
            print(
                f"{i}. {Fore.YELLOW}{preset['name']}{Style.RESET_ALL} - {preset['description']}"
            )

        while True:
            try:
                choice = input(
                    f"\n{Fore.GREEN}Select preset (1-{len(presets)}) or 'custom' for manual config: {Style.RESET_ALL}"
                )

                if choice.lower() == "custom":
                    return None

                choice_num = int(choice)
                if 1 <= choice_num <= len(presets):
                    return presets[choice_num - 1]["preset_id"]
                else:
                    print(
                        f"{Fore.RED}❌ Please enter a number between 1 and {len(presets)}{Style.RESET_ALL}"
                    )
            except ValueError:
                print(
                    f"{Fore.RED}❌ Please enter a valid number or 'custom'{Style.RESET_ALL}"
                )

    def create_custom_game(self) -> Dict[str, Any]:
        """Create custom game configuration"""
        print(f"\n{Fore.CYAN}Creating Custom Game Configuration:{Style.RESET_ALL}")

        # Get basic settings
        max_players = self.get_int_input("Number of players (2-6)", 6, 2, 6)
        buyin = self.get_int_input("Buy-in amount", 1000, 100, 10000)
        big_blind = self.get_int_input("Big blind", 20, 2, buyin // 10)
        small_blind = self.get_int_input(
            "Small blind", big_blind // 2, 1, big_blind - 1
        )
        max_hands = self.get_int_input("Maximum hands", 15, 1, 100)

        # Configure agents
        agents_data = self.client.list_agents()
        agents = agents_data.get("agents", [])

        print(f"\n{Fore.CYAN}Available Agents:{Style.RESET_ALL}")
        for i, agent in enumerate(agents):
            if agent["is_available"]:
                status = f"{Fore.GREEN}✅{Style.RESET_ALL}"
            else:
                status = f"{Fore.RED}❌{Style.RESET_ALL}"
            print(f"{i + 1:2}. {status} {agent['name']} ({agent['category']})")

        # Configure each player
        agent_config = {}
        for player_id in range(max_players):
            print(f"\n{Fore.YELLOW}Configure Player {player_id}:{Style.RESET_ALL}")

            while True:
                try:
                    choice = input(f"Agent number (1-{len(agents)}): ")
                    choice_num = int(choice) - 1

                    if 0 <= choice_num < len(agents):
                        selected_agent = agents[choice_num]
                        if selected_agent["is_available"]:
                            agent_config[player_id] = selected_agent["agent_id"]
                            print(
                                f"{Fore.GREEN}✅ Player {player_id}: {selected_agent['name']}{Style.RESET_ALL}"
                            )
                            break
                        else:
                            print(f"{Fore.RED}❌ Agent not available{Style.RESET_ALL}")
                    else:
                        print(
                            f"{Fore.RED}❌ Please enter a number between 1 and {len(agents)}{Style.RESET_ALL}"
                        )
                except ValueError:
                    print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

        return {
            "max_players": max_players,
            "buyin": buyin,
            "big_blind": big_blind,
            "small_blind": small_blind,
            "max_hands": max_hands,
            "agents": agent_config,
            "debug_mode": False,
        }

    def get_int_input(
        self, prompt: str, default: int, min_val: int, max_val: int
    ) -> int:
        """Get integer input with validation"""
        while True:
            try:
                value = input(f"{prompt} (default {default}): ").strip()
                if not value:
                    return default

                num = int(value)
                if min_val <= num <= max_val:
                    return num
                else:
                    print(
                        f"{Fore.RED}❌ Please enter a number between {min_val} and {max_val}{Style.RESET_ALL}"
                    )
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

    def handle_human_input(self) -> bool:
        """Handle human player input"""
        if not self.client.current_state:
            return False

        state = self.client.current_state
        current_player = state.get("current_player")

        if current_player is None:
            return False

        # Check if current player is human
        player_info = None
        for player in state["players"]:
            if player["player_id"] == current_player:
                player_info = player
                break

        if not player_info or player_info["agent_type"] != "human":
            return False

        # Get human input
        available_actions = state.get("available_actions", [])
        print(
            f"\n{Fore.GREEN}🧑‍💻 Your turn, Player {current_player}!{Style.RESET_ALL}"
        )

        while True:
            action_input = (
                input(
                    f"{Fore.CYAN}Enter action (fold/check/call/raise X): {Style.RESET_ALL}"
                )
                .strip()
                .lower()
            )

            if not action_input:
                continue

            parts = action_input.split()
            action = parts[0]

            if action in ["fold", "f"] and "FOLD" in available_actions:
                return self.client.execute_action(current_player, "FOLD")

            elif action in ["check", "c"] and "CHECK" in available_actions:
                return self.client.execute_action(current_player, "CHECK")

            elif action in ["call", "ca"] and "CALL" in available_actions:
                return self.client.execute_action(current_player, "CALL")

            elif action in ["raise", "r"] and "RAISE" in available_actions:
                try:
                    if len(parts) >= 2:
                        amount = int(parts[1])
                        min_raise = state.get("min_raise_amount", 0)
                        if amount >= min_raise:
                            return self.client.execute_action(
                                current_player, "RAISE", amount
                            )
                        else:
                            print(
                                f"{Fore.RED}❌ Minimum raise is ${min_raise}{Style.RESET_ALL}"
                            )
                    else:
                        print(
                            f"{Fore.RED}❌ Please specify raise amount (e.g., 'raise 40'){Style.RESET_ALL}"
                        )
                except ValueError:
                    print(f"{Fore.RED}❌ Invalid raise amount{Style.RESET_ALL}")
            else:
                print(
                    f"{Fore.RED}❌ Invalid action. Available: {', '.join(available_actions)}{Style.RESET_ALL}"
                )

    async def game_loop(self):
        """Main game loop"""
        # Start WebSocket connection
        if self.client.current_game_id:
            asyncio.create_task(self.client.start_websocket())

        while self.running:
            # Get latest game state
            self.client.get_game_state()

            if not self.client.current_state:
                break

            # Display current state
            self.display_game_state()

            state = self.client.current_state

            # Check if game is complete
            if state["status"] == "COMPLETED":
                print(f"\n{Fore.GREEN}🏁 Game completed!{Style.RESET_ALL}")
                self.show_final_results()
                break

            # Handle human input if needed
            if state.get("current_player") is not None:
                if not self.handle_human_input():
                    # If no human input needed, wait a bit for AI actions
                    await asyncio.sleep(2)
            else:
                await asyncio.sleep(1)

    def show_final_results(self):
        """Show final game results"""
        if not self.client.current_game_id:
            return

        try:
            response = self.client.session.get(
                self.client._api_url(f"/games/{self.client.current_game_id}/history")
            )
            if response.status_code == 200:
                history = response.json()

                print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}🏆 FINAL RESULTS 🏆{Style.RESET_ALL}")
                print(f"Game Duration: {history['duration_minutes']:.1f} minutes")
                print(f"Total Hands: {history['total_hands']}")

                print(f"\n{Fore.CYAN}Final Standings:{Style.RESET_ALL}")
                for i, result in enumerate(history["final_results"], 1):
                    profit_color = (
                        Fore.GREEN
                        if result["profit_loss"] > 0
                        else Fore.RED
                        if result["profit_loss"] < 0
                        else Fore.YELLOW
                    )
                    print(
                        f"{i}. {result['agent_name']}: ${result['final_chips']} "
                        f"({profit_color}{result['profit_loss']:+}${Style.RESET_ALL})"
                    )

        except Exception as e:
            print(f"{Fore.RED}❌ Error getting results: {e}{Style.RESET_ALL}")

    async def run(self):
        """Main CLI run method"""
        self.display_banner()

        # Check API health
        if not self.client.check_health():
            print(
                f"{Fore.RED}❌ Cannot connect to API. Make sure the backend is running:{Style.RESET_ALL}"
            )
            print(f"   {Fore.CYAN}cd backend && python run.py{Style.RESET_ALL}")
            return

        # Game setup
        print(f"\n{Fore.CYAN}🎮 Game Setup{Style.RESET_ALL}")

        preset = self.select_game_preset()

        if preset:
            # Use preset
            config = {"preset": preset}
        else:
            # Create custom game
            config = self.create_custom_game()

        # Create game
        game_id = self.client.create_game(config)
        if not game_id:
            print(f"{Fore.RED}❌ Failed to create game{Style.RESET_ALL}")
            return

        # Start game loop
        try:
            await self.game_loop()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Game interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Game error: {e}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Thanks for playing! 🃏{Style.RESET_ALL}")


def main():
    """Main entry point"""
    # API Configuration
    API_BASE_URL = "http://localhost:8000"
    parser = argparse.ArgumentParser(description="Texas Hold'em CLI API Client")
    parser.add_argument("--api-url", default=API_BASE_URL, help="API base URL")
    args = parser.parse_args()

    # Run the CLI
    cli = PokerCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()

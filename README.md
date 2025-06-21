# 🃏 Texas Hold'em Poker CLI with AI & LLM Agents

Welcome to the Texas Hold'em Poker CLI, a sophisticated command-line interface where you can play poker, test different AI strategies, and watch advanced Large Language Model (LLM) agents battle it out on the felt.

This project uses the `texasholdem` library to create a robust poker environment and integrates with modern AI and LLM technologies to bring unique, intelligent opponents to life.

![Poker CLI Screenshot](https://i.imgur.com/your-screenshot.png) <!-- Replace with an actual screenshot -->

## ✨ Features

- **Multiple Game Modes:** Play against AI, LLMs, or watch them compete against each other.
- **Human Player Support:** Join the game and test your skills in realistic or debug modes.
- **Advanced AI Agents:** A variety of built-in AI opponents with distinct personalities (Passive, Aggressive, Tight, Loose, Bluffer).
- **LLM Integration:** Watch powerful LLM agents like **GPT-4.1**, **Llama 3.1**, and **Gemma 3** play poker with strategic reasoning and "thought" processes.
- **Custom Game Configurations:** Set up your own custom games, choosing the agents, buy-ins, and blind structures.
- **Colorful CLI:** A clean, colorful, and easy-to-read interface for visualizing the game state.
- **Game History:** All games can be exported to PGN (Portable Game Notation) files for review.

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### 1. Prerequisites

- Python 3.12+
- `uv` (or `pip`) for package management. It is recommended to use `uv` for faster dependency installation.

### 2. Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ryandonofrio3/poker-cli
    cd poker-cli
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies using `uv`:**
    ```bash
    uv pip install -r pyproject.toml
    ```
    *If you don't have `uv`, you can install it with `pip install uv` or use `pip install -e .`*

4.  **Set up your environment variables (for LLM agents):**
    - Create a file named `.env` in the root of the project.
    - Add your API key to this file. The project uses OpenRouter to access various LLM models.
      ```env
      # .env
      OPENROUTER_API_KEY="your_openrouter_api_key"
      ```
    - **Note:** If you don't provide an API key, the game will still run, but all LLM-related game modes will be disabled.

### 3. Running the CLI

Once everything is installed, you can start the main application from your terminal:

```bash
python main.py
```

This will launch the main menu, where you can choose from a variety of game modes.

## 🎮 Game Modes

The CLI offers a rich selection of game modes, divided into three categories:

#### Human Player Modes
- **Human vs AI (Realistic):** Play against 5 AI opponents with their cards hidden.
- **Human vs AI (Debug):** Play against 5 AI opponents, but you can see their cards.
- **Human vs LLM (Realistic):** Test your skills against 5 advanced LLM agents.
- **Human vs LLM (Debug):** Play against LLMs while seeing their cards and strategic reasoning.
- **Human Heads-Up:** Go one-on-one against a strong AI opponent.

#### AI-Only Modes
- **Quick Test Game:** A fast, two-player game to see the system in action.
- **Balanced 6-Player Game:** A table of 6 different traditional AI agents.
- **Custom Agent Showcase:** A game featuring a curated list of custom AI agents with unique play styles.
- **LLM Agent Showcase:** A battle between 6 different LLM agents.
- **LLM vs Traditional AI:** A 3 vs 3 battle between LLMs and traditional AI.
- **Premium vs Free LLM Battle:** See if premium models (GPT-4.1) have an edge over high-performing free models (Llama, Gemma).

#### Utilities
- **List Available Agents:** See a list of all configured AI and LLM agents.
- **Custom Game Configuration:** Create your own game from scratch.

## 🛠️ Future Development: FastAPI Backend

This project also includes a powerful FastAPI backend designed to turn the CLI application into a full-fledged web app. While the backend is under active development, the primary and most stable way to experience the application is through the CLI as described above.

The backend will eventually support:
- A thin, modern Next.js frontend.
- Real-time gameplay via WebSockets.
- RESTful APIs for game and agent management.

Stay tuned for updates!

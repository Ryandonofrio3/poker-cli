"""
Detailed game flow test to observe complete poker game mechanics
Shows step-by-step game progression and validates all states
"""

from texasholdem import TexasHoldEm, ActionType, HandPhase
from agent_manager import create_test_config, get_agent_action, get_agent_name
from display import display_full_game_state
import time


def detailed_hand_analysis(game: TexasHoldEm, agent_config: dict, hand_number: int):
    """Run a detailed analysis of a single hand"""
    print(f"\n{'=' * 60}")
    print(f"🎮 HAND {hand_number} - DETAILED ANALYSIS")
    print(f"{'=' * 60}")

    # Record pre-hand state
    pre_hand_chips = {i: game.players[i].chips for i in range(game.max_players)}
    print(f"💰 Pre-hand chips: {pre_hand_chips}")

    # Start hand
    game.start_hand()
    print(f"🎯 Hand started - Phase: {game.hand_phase}")

    # Track hand progression
    phases_seen = []
    actions_taken = []
    pot_progression = []

    action_count = 0
    max_actions = 100  # Safety limit

    while game.is_hand_running() and action_count < max_actions:
        current_phase = game.hand_phase
        if current_phase not in phases_seen:
            phases_seen.append(current_phase)
            print(f"\n🎪 PHASE: {current_phase.name}")
            if current_phase != HandPhase.PREFLOP:
                print(f"🎴 Board: {[str(card) for card in game.board]}")

        current_player = game.current_player
        current_pot = sum(pot.get_total_amount() for pot in game.pots)

        # Get available moves
        moves = game.get_available_moves()
        available_actions = list(moves.action_types)

        # Get agent action
        agent_name = get_agent_name(current_player, agent_config)
        action, amount = get_agent_action(game, current_player, agent_config)

        # Record action
        action_info = {
            "player": current_player,
            "agent": agent_name,
            "action": action,
            "amount": amount,
            "phase": current_phase,
            "pot_before": current_pot,
            "available": available_actions,
        }
        actions_taken.append(action_info)

        print(
            f"🤖 Player {current_player} ({agent_name}): {action} {amount if amount else ''}"
        )
        print(f"   Available: {[a.name for a in available_actions]}")
        print(f"   Pot before: {current_pot}")

        # Execute action
        try:
            game.take_action(action, amount)
            action_count += 1

            # Record pot after action
            pot_after = sum(pot.get_total_amount() for pot in game.pots)
            action_info["pot_after"] = pot_after
            pot_progression.append(pot_after)

            if pot_after != current_pot:
                print(f"   Pot after: {pot_after} (change: +{pot_after - current_pot})")

        except Exception as e:
            print(f"❌ Action failed: {e}")
            break

        time.sleep(0.1)  # Brief pause for readability

    # Post-hand analysis
    post_hand_chips = {i: game.players[i].chips for i in range(game.max_players)}
    chip_changes = {
        i: post_hand_chips[i] - pre_hand_chips[i] for i in range(game.max_players)
    }

    print(f"\n📊 HAND {hand_number} SUMMARY:")
    print(f"   Phases seen: {[p.name for p in phases_seen]}")
    print(f"   Actions taken: {action_count}")
    print(
        f"   Final pot progression: {pot_progression[-3:] if len(pot_progression) > 3 else pot_progression}"
    )
    print(f"💰 Chip changes: {chip_changes}")
    print(f"💰 Post-hand chips: {post_hand_chips}")

    # Validate chip conservation
    total_pre = sum(pre_hand_chips.values())
    total_post = sum(post_hand_chips.values())
    if total_pre != total_post:
        print(f"⚠️  CHIP CONSERVATION ISSUE: {total_pre} -> {total_post}")
    else:
        print(f"✅ Chip conservation verified: {total_post}")

    return {
        "hand_number": hand_number,
        "phases": phases_seen,
        "actions": actions_taken,
        "chip_changes": chip_changes,
        "total_actions": action_count,
        "chip_conservation_ok": total_pre == total_post,
    }


def test_complete_game_flow():
    """Test a complete multi-hand game with detailed observation"""
    print("🚀 COMPLETE GAME FLOW TEST")
    print("=" * 60)

    # Create game
    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=3)
    agent_config = create_test_config()

    # Extend config for 3 players
    agent_config[2] = agent_config[0]  # Copy agent

    print(f"🎯 Game created: {game.max_players} players, ${game.buyin} buy-in")
    print(f"🎯 Blinds: ${game.small_blind}/${game.big_blind}")
    print(
        f"🎯 Agent config: {[get_agent_name(i, agent_config) for i in range(game.max_players)]}"
    )

    # Track game statistics
    hand_results = []
    game_statistics = {
        "hands_played": 0,
        "total_actions": 0,
        "phases_distribution": {},
        "chip_conservation_issues": 0,
        "eliminations": 0,
    }

    max_hands = 5

    for hand_num in range(1, max_hands + 1):
        if not game.is_game_running():
            print(f"🏁 Game ended after {hand_num - 1} hands")
            break

        # Run detailed hand analysis
        hand_result = detailed_hand_analysis(game, agent_config, hand_num)
        hand_results.append(hand_result)

        # Update statistics
        game_statistics["hands_played"] += 1
        game_statistics["total_actions"] += hand_result["total_actions"]

        for phase in hand_result["phases"]:
            phase_name = phase.name
            game_statistics["phases_distribution"][phase_name] = (
                game_statistics["phases_distribution"].get(phase_name, 0) + 1
            )

        if not hand_result["chip_conservation_ok"]:
            game_statistics["chip_conservation_issues"] += 1

        # Check for eliminations
        current_chips = [game.players[i].chips for i in range(game.max_players)]
        if any(chips <= 0 for chips in current_chips):
            game_statistics["eliminations"] += 1

        # Show current standings
        print(f"\n🏆 STANDINGS after Hand {hand_num}:")
        for i in range(game.max_players):
            agent_name = get_agent_name(i, agent_config)
            chips = game.players[i].chips
            status = "ELIMINATED" if chips <= 0 else "ACTIVE"
            print(f"   Player {i} ({agent_name}): ${chips} - {status}")

    # Final game analysis
    print(f"\n{'=' * 60}")
    print("🏁 COMPLETE GAME ANALYSIS")
    print(f"{'=' * 60}")

    print(f"📊 Game Statistics:")
    print(f"   Hands played: {game_statistics['hands_played']}")
    print(f"   Total actions: {game_statistics['total_actions']}")
    print(
        f"   Avg actions per hand: {game_statistics['total_actions'] / max(1, game_statistics['hands_played']):.1f}"
    )
    print(f"   Chip conservation issues: {game_statistics['chip_conservation_issues']}")
    print(f"   Player eliminations: {game_statistics['eliminations']}")

    print(f"\n🎪 Phase Distribution:")
    for phase, count in game_statistics["phases_distribution"].items():
        print(f"   {phase}: {count}")

    # Final chip analysis
    final_chips = {i: game.players[i].chips for i in range(game.max_players)}
    total_final_chips = sum(final_chips.values())
    expected_chips = game.max_players * game.buyin

    print(f"\n💰 Final Chip Analysis:")
    print(f"   Expected total: ${expected_chips}")
    print(f"   Actual total: ${total_final_chips}")
    print(
        f"   Conservation: {'✅ PASS' if total_final_chips == expected_chips else '❌ FAIL'}"
    )

    # Success criteria
    success_criteria = [
        game_statistics["hands_played"] > 0,
        game_statistics["chip_conservation_issues"] == 0,
        total_final_chips == expected_chips,
        len(game_statistics["phases_distribution"]) > 1,  # Saw multiple phases
    ]

    print(f"\n🎯 Success Criteria:")
    print(f"   Hands played: {'✅' if success_criteria[0] else '❌'}")
    print(f"   Chip conservation: {'✅' if success_criteria[1] else '❌'}")
    print(f"   Total chips correct: {'✅' if success_criteria[2] else '❌'}")
    print(f"   Multiple phases seen: {'✅' if success_criteria[3] else '❌'}")

    overall_success = all(success_criteria)
    print(
        f"\n🏁 OVERALL RESULT: {'🎉 SUCCESS' if overall_success else '⚠️ ISSUES FOUND'}"
    )

    return overall_success, game_statistics, hand_results


def main():
    """Run the complete game flow test"""
    success, stats, hands = test_complete_game_flow()

    if success:
        print("\n🎉 All poker mechanics working correctly! 🎉")
    else:
        print("\n⚠️ Some mechanics need attention.")

    return success


if __name__ == "__main__":
    main()

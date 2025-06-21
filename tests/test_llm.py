"""
Test script for LLM integration with structured outputs
"""

from llm_agents import test_llm_connection
from llm_client import create_llm_client, AVAILABLE_MODELS


def test_structured_outputs():
    """Test structured outputs with different models"""
    print("🧪 Testing Structured Outputs...")
    print("=" * 60)

    client = create_llm_client()

    # Test models in order of likelihood to support structured outputs
    test_models = [
        ("openai/gpt-4.1-mini", "gpt-4.1 Mini (definitely supports)"),
        ("openai/gpt-4.1", "gpt-4.1 (definitely supports)"),
        ("google/gemma-3-27b-it:free", "Gemma 3 27B (should support)"),
        ("meta-llama/llama-3.1-8b-instruct", "Llama 3.1 8B (should support)"),
    ]

    successful_models = []

    for model, description in test_models:
        print(f"\n🔍 Testing {description}...")
        print(f"Model: {model}")

        if client.test_structured_output_specifically(model):
            successful_models.append((model, description))

        print("-" * 40)

    print(f"\n📊 RESULTS:")
    print(f"✅ Models with working structured outputs: {len(successful_models)}")
    for model, desc in successful_models:
        print(f"  • {desc}")

    if not successful_models:
        print(
            "❌ No models support structured outputs - will use text parsing fallback"
        )

    return successful_models


def test_basic_connection():
    """Test basic LLM connection"""
    print("🤖 Testing Basic LLM Connection...")
    print("=" * 50)

    # Test basic connection
    if test_llm_connection():
        print("\n✅ LLM connection successful!")
        return True
    else:
        print("\n❌ LLM connection failed!")
        print("Please check your .env file and API key.")
        return False


def main():
    print("🚀 COMPREHENSIVE LLM TESTING")
    print("=" * 60)

    # Test 1: Basic connection
    if not test_basic_connection():
        return

    print("\n" + "=" * 60)

    # Test 2: Structured outputs
    successful_models = test_structured_outputs()

    print("\n" + "=" * 60)
    print("🎯 FINAL SUMMARY:")

    if successful_models:
        print(f"✅ {len(successful_models)} models support structured outputs!")
        print("🎮 Ready for advanced LLM poker games with reliable parsing!")

        # Update our available models to prioritize working ones
        print("\n🔧 Recommended model configuration:")
        for model, desc in successful_models[:2]:  # Top 2 working models
            print(f"  • {model}")
    else:
        print("⚠️  No structured output support found, but text parsing works!")
        print("🎮 Ready for LLM poker games with text parsing fallback!")


if __name__ == "__main__":
    main()

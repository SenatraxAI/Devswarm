"""
Quick test script to verify Gemma 3 integration
"""
import asyncio
from models.model_manager import ModelManager


async def test_model():
    print("🧪 Testing Gemma 3 integration...\n")
    
    # Initialize model manager
    manager = ModelManager()
    await manager.initialize()
    
    if not manager.initialized:
        print("❌ Model not initialized - is Ollama running?")
        return
    
    print("\n💬 Sending test message to Gemma 3:4b...\n")
    
    # Test generation
    response_parts = []
    async for token in manager.generate(
        prompt="Say hello and introduce yourself as Sarah Chen, the Product Manager.",
        system_prompt="You are Sarah Chen, a Product Manager with a cognitive psychology background.",
        temperature=0.7,
        stream=True
    ):
        print(token, end="", flush=True)
        response_parts.append(token)
    
    full_response = "".join(response_parts)
    print(f"\n\n✅ Response received ({len(full_response)} characters)")
    print(f"📊 VRAM usage: {manager.get_vram_usage()}")
    
    await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(test_model())

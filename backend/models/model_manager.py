"""
Model Manager for DevSwarm
Manages Phi-4 model via Ollama API
"""
import asyncio
import httpx
import psutil
from typing import Optional, AsyncGenerator
import json


class ModelManager:
    """Singleton model manager using Ollama"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self.model_name = "gemma3:4b"  # Gemma 3 4B model
            self.ollama_url = "http://localhost:11434"  # Default Ollama API
            self.client = None
    
    async def initialize(self):
        """Initialize Ollama connection"""
        print("📦 Initializing ModelManager...")
        print(f"🔗 Connecting to Ollama at {self.ollama_url}")
        
        # Create HTTP client
        self.client = httpx.AsyncClient(timeout=300.0)  #5 min timeout for long responses
        
        # Test connection
        try:
            response = await self.client.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                
                if self.model_name in model_names:
                    print(f"✅ Model '{self.model_name}' ready")
                    self.initialized = True
                else:
                    print(f"⚠️  Model '{self.model_name}' not found. Available: {model_names}")
                    print(f"   Run: ollama pull {self.model_name}")
                    self.initialized = False
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                self.initialized = False
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("   Make sure Ollama is running: ollama serve")
            self.initialized = False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Generate response from Phi-4 via Ollama
        
        Args:
            prompt: User/agent prompt
            system_prompt: System prompt for agent personality
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream tokens
            
        Yields:
            Generated tokens (if stream=True)
        """
        if not self.initialized:
            yield "⚠️ Model not initialized. Please wait for model download."
            return
        
        # Build request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            if stream:
                # Streaming response
                async with self.client.stream(
                    "POST",
                    f"{self.ollama_url}/api/generate",
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            
                            if data.get("done", False):
                                break
            else:
                # Non-streaming response
                response = await self.client.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload
                )
                result = response.json()
                yield result.get("response", "")
                
        except Exception as e:
            yield f"❌ Generation error: {str(e)}"
    
    def get_vram_usage(self) -> dict:
        """Get VRAM/RAM usage"""
        memory = psutil.virtual_memory()
        return {
            "used_mb": memory.used / (1024 ** 2),
            "total_mb": memory.total / (1024 ** 2),
            "percent": memory.percent
        }
    
    async def shutdown(self):
        """Cleanup"""
        if self.client:
            await self.client.aclose()
        print("🛑 Model manager shut down")

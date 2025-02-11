import os 
from together import Together
from dotenv import load_dotenv
from typing import Optional

def initialize_llm():
    """Initialize the Together AI client"""
    load_dotenv()
    api_key = os.getenv("TOGETHER_AI_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_AI_API_KEY not found in environment variables")
    return Together(api_key=api_key)

def generate_response(client: Together, prompt: str, max_tokens: int = 1024) -> Optional[str]:
    """Generate a response using the LLM model"""
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return None


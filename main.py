import asyncio

from client.llm_client import LLMClient


async def main():
  print("--- Starting Application ---")
  client = LLMClient() 
  messages =[{"role":"user", "content": "What's up?"}]
  
  print("--- Calling chat_completions (generator created) ---")
  # generator = client.chat_completions(messages, False)
  generator = client.chat_completions(messages,True)
  
  print("--- Iterating over the generator ---")
  async for event in generator:
    print(event)

  print("--- Done! ---")
  
if __name__ == "__main__":
  asyncio.run(main())
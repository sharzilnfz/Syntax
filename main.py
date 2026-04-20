import asyncio
import sys
from typing import Any

import click
from dotenv import load_dotenv
from ui.tui import get_console

from agent.agent import Agent
from agent.events import AgentEventType
from client.llm_client import LLMClient
from ui.tui import TUI

load_dotenv()

console = get_console()

class CLI:
  def __init__(self):
    self.agent: Agent | None = None
    self.tui = TUI(console )
  async def run_single(self, message: str) -> str | None:
    async with Agent () as agent:
      self.agent = agent
      return await self._process_message(message)
  async def _process_message(self, message: str) -> str | None:
    if not self.agent:
      return None
    
    assistant_streaming = False
    final_response: str | None = None
    async for event in self. agent. run (message):
      if event. type == AgentEventType.TEXT_DELTA:
        content = event.data.get ("content", "")
        if not assistant_streaming:
          self.tui.begin_assistant ()
          assistant_streaming = True
        self.tui. stream_assistant_delta(content)
      elif event. type == AgentEventType.TEXT_COMPLETE:
        final_response = event. data. get ("content")
        if assistant_streaming:
          self.tui. end_assistant ()
          assistant_streaming = False
      elif event. type == AgentEventType. AGENT_ERROR:
        error = event. data. get ("error", "Unknown error")
        # Truncate very long errors (like HTML dumps) to prevent console lag
        if len(error) > 500:
          error = error[:500] + "... [truncated]"
        console.print(f"\n[error]Error:[/error] {error}", highlight=False)
    return final_response
  
  
async def run(messages: list[dict[str, Any]]):
  client = LLMClient() 
  generator = client.chat_completions(messages, False)
  async for event in generator:
    print(event)

@click.command()
@click.argument("prompt", required=False)
def main(prompt: str | None):
  # print(prompt)
  cli = CLI ()
  # messages = [{"role": "user", "content": prompt}] 
  if prompt:
    result = asyncio.run(cli. run_single(prompt))
    if result is None:
     sys.exit(1)
  
main()
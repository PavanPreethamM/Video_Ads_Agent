import openrouter_patch
import asyncio
from hermes.core import Agent
import config


async def main():
    agent = Agent(
        provider="openai",
        model= "openai/gpt-4o-mini",
        api_key=config.OPENROUTER_API_KEY,
        name="TestAgent",
        description="A minimal agent to verify hermes + OpenRouter work together.",
        prompt="You are a helpful assistant. Keep answers short.",
    )
    response = await agent.execute(input_data="Say hello and confirm you're working.")
    print(response)

asyncio.run(main())
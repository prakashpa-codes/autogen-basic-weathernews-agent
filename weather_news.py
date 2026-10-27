import asyncio
import os

from dotenv import load_dotenv
from ddgs import DDGS
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


load_dotenv()


def search_weather_news(city: str) -> str:
    """Search for today's weather-related news in the specified city and return the top results."""

    try:
        results = DDGS().news(
            query=f"{city} weather today",
            max_results=5
        )
        return str(results)

    except Exception as error:
        return f"Weather news search failed: {error}"


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file."
        )

    city = input("Which city? ").strip()

    if not city:
        print("Please enter a city.")
        return

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini"
    )

    try:
        agent = AssistantAgent(
            name="weather_news",
            model_client=model_client,
            tools=[search_weather_news],
            system_message=(
                "You are a weather news assistant. "
                "Use the search_weather_news tool to find current "
                "weather-related news for the requested city. "
                "Summarize the results in exactly three short lines. "
                "Do not add a heading or introductory text. "
                "Do not invent weather conditions or news."
            ),
            reflect_on_tool_use=True
        )

        task = (
            f"Find today's weather-related news for {city}. "
            "Return exactly three short lines based on the search results."
        )

        await Console(agent.run_stream(task=task))

    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
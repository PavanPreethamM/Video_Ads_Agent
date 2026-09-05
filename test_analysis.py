import openrouter_patch

import asyncio
import json
from hermes.core import Agent
import config


async def main():
    print("Step 1: Loading JSON file...")
    with open("data/raw_ads/test_scrape_20260903_154700.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print("Step 1 done. Loaded", len(data.get("ads", [])), "ads.")

    ads = data["ads"]

    ad_texts = []
    for ad in ads:
        text = ad.get("snapshot", {}).get("body", {}).get("text", "")
        page_name = ad.get("snapshot", {}).get("page_name", "unknown")
        if text:
            ad_texts.append(f"[{page_name}]: {text}")

    print("Step 2 done. Extracted", len(ad_texts), "ad texts.")

    combined_ads = "\n\n---\n\n".join(ad_texts)
    print("Step 3 done. Combined text length:", len(combined_ads), "characters.")

    print("Step 4: Creating agent...")
    agent = Agent(
        provider="openai",
        model="openai/gpt-4o-mini",
        api_key=config.OPENROUTER_API_KEY,
        name="AdAnalysisAgent",
        description="Analyzes competitor ad copy to extract marketing patterns.",
        prompt=(
            "You are a senior direct-response marketing analyst. "
            "Given real ad copy, identify recurring patterns advertisers use. "
            "Be specific and concrete, not generic — quote or closely paraphrase "
            "actual phrases from the ads. "
            "You must respond with ONLY valid JSON, no other text, no markdown "
            "code fences, matching exactly this structure: "
            '{"pain_points": ["...", "..."], "hooks": ["...", "..."], '
            '"marketing_concepts": ["...", "..."]}'
        ),
    )
    print("Step 4 done. Agent created.")

    task = f"""Analyze these {len(ad_texts)} trading-education ads and answer:

1. What PAIN POINTS do these ads target? (specific frustrations, fears)
2. What HOOKS do they use to grab attention in the first line?
3. What MARKETING CONCEPTS/ANGLES appear repeatedly? (e.g. urgency, social proof, "us vs them")

Ads:
{combined_ads}
"""

    print("Step 5: Sending to LLM... (this may take 10-30 seconds)")
    response = await agent.execute(input_data=task)
    print("Step 5 done. Got a response back.")

    print("\n=== RAW RESPONSE ===")
    print(response)

    print("\n=== PARSED AS JSON ===")
    response_text = response.response.content
    parsed = json.loads(response_text)
    print(json.dumps(parsed, indent=2))

asyncio.run(main())
import openrouter_patch

from hermes.core import Agent
import asyncio
import json
import config

async def main():
    with open("data/analyzed_ads/analysis_20260905_114846.json", "r" , encoding="utf-8") as f:
        ad_analysis = json.load(f)

    print("Loaded ad analysis with", len(ad_analysis.get("pain_points", [])), "pain points.")

    agent = Agent(
        provider="openai",
        model="openai/gpt-4o-mini",
        api_key=config.OPENROUTER_API_KEY,
        name="ScriptTestAgent",
        description="Writes short video ad scripts based on marketing research.",
        prompt=(
            "You are a senior direct-response video ad scriptwriter. "
            "You must respond with ONLY valid JSON, no other text, no markdown "
            "code fences. Follow the exact structure requested."
        )
    )
    task = f"""Based on this research, write exactly 3 video ad scripts for
CrowdWisdomTrading (a trading education/alerts service).

PAIN POINTS TO ADDRESS:
{ad_analysis.get('pain_points', [])}

HOOKS THAT WORK IN THIS NICHE:
{ad_analysis.get('hooks', [])}

Return ONLY valid JSON matching exactly this structure:
{{
  "scripts": [
    {{
      "script_type": "pain_agitate_solve",
      "visual_hook": "description of the first 2 seconds on screen",
      "duration_seconds": 45,
      "scenes": [
        {{"scene_number": 1, "voiceover": "...", "on_screen_text": "..."}}
      ],
      "cta": "closing call to action"
    }}
  ]
}}

Write 3 scripts total, with script_type values: "pain_agitate_solve",
"social_proof_results", "myth_bust_contrarian". Each script needs 3-4 scenes.
"""
    print("Sending Script generation request ti LLM ...")
    response = await agent.execute(input_data=task)
    response_txt = response.response.content

    print("\n=== RAW REAPONSE (first 500 char's) ===")
    print(response_txt[:500])

    print("\n=== ATTEMPTING TO PARSE ===")
    parsed = json.loads(response_txt)
    print("Success! Number of scripts returned:", len(parsed.get("scripts", [])))
    for script in parsed.get("scripts", []):
        print(f"- {script.get('script_type')}: {len(script.get('scenes', []))} scenes")


asyncio.run(main())

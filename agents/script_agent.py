import openrouter_patch

import json
from datetime import datetime
from tavily import TavilyClient
from hermes.core import Agent
import asyncio

import config


class ScriptAgent:
    def __init__(self):
        self.tavily = TavilyClient(api_key=config.TAVILY_API_KEY)

    def research_pain_points(self, pain_points: list, max_results: int = 5) -> list:
        query = " ".join(pain_points[:2]) + " traders"

        print(f"Searching Tavily for: '{query}'...")
        results = self.tavily.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
        )

        research_items = results.get("results", [])
        print(f"Found {len(research_items)} research articles.")
        return research_items
    
    async def generate_scripts(self, ad_analysis: dict, research: list) -> dict:
        research_snippets = [item.get("content", "")[:300] for item in research]

        unique_data = (
            "CrowdWisdomTrading provides data-driven trade alerts, options flow "
            "analysis, and a community of traders sharing real-time setups. "
            "[Replace this with real performance stats/testimonials later.]"
        )

        agent = Agent(
            provider="openai",
            model="openai/gpt-4o-mini",
            api_key=config.OPENROUTER_API_KEY,
            name="ScriptGeneratorAgent",
            description="Writes short video ad scripts based on marketing research.",
            prompt=(
                "You are a senior direct-response video ad scriptwriter. "
                "You must respond with ONLY valid JSON, no other text, no markdown "
                "code fences. Follow the exact structure requested."
            ),
        )

        task = f"""Based on this research, write exactly 3 video ad scripts for
CrowdWisdomTrading (a trading education/alerts service).

PAIN POINTS TO ADDRESS:
{ad_analysis.get('pain_points', [])}

HOOKS THAT WORK IN THIS NICHE:
{ad_analysis.get('hooks', [])}

RECENT RESEARCH VALIDATING THESE PAIN POINTS:
{research_snippets}

CROWDWISDOMTRADING'S UNIQUE VALUE:
{unique_data}

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

        print("Generating scripts...")
        response = await agent.execute(input_data=task)
        response_text = response.response.content

        scripts_data = json.loads(response_text)
        print(f"Generated {len(scripts_data.get('scripts', []))} scripts.")
        return scripts_data

    def save_results(self , scripts_data: dict , search_term: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        scripts_filename = f"data/scripts/scripts_{timestamp}.json"

        with open(scripts_filename , "w" , encoding="utf-8") as f:
            json.dump({
                "search_term" : search_term,
                "generated_at" : datetime.now().isoformat(),
                **scripts_data,
            }, f , indent=2 , ensure_ascii=False)

        print(f"Scipts saved to {scripts_filename}")
        return scripts_filename

async def main():
    import glob

    analysis_files = sorted(glob.glob("data/analyzed_ads/*.json"))
    if not analysis_files:
        print("No ad analysis found .First run agents/ads_manager_agent.py ")
        return
    
    latest_file = analysis_files[-1]
    print(f"Using ad analysis from : {latest_file}")

    with open(latest_file, "r" ,  encoding="utf-8") as f:
        ad_analysis = json.load(f)

    agent = ScriptAgent()
    research = agent.research_pain_points(ad_analysis.get("pain_points", []))
    scripts_data = await agent.generate_scripts(ad_analysis, research)
    agent.save_results(scripts_data, search_term=ad_analysis.get("search_term", "unknown"))


if __name__ == "__main__":
    asyncio.run(main())
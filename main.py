"""
Runs the full CrowdWisdomTrading ad-generation pipeline end to end:

    AdsManagerAgent -> ScriptAgent -> VideoAgent

Each agent's real, already-proven logic (see agents/) is reused as-is —
this file just wires them together in sequence.
"""
import asyncio

from agents.ads_manager_agent import AdsManagerAgent
from agents.script_agent import ScriptAgent
from agents.video_agent import VideoAgent


async def main():
    print("=" * 60)
    print("STEP 1/3 — Ads Manager Agent")
    print("=" * 60)
    ads_agent = AdsManagerAgent()
    ads = ads_agent.scrape_ads(search_term="stock trading alerts", max_int=10,country="US")
    ad_analysis = await ads_agent.analyze_ads(ads)
    ads_agent.save_results(ads, ad_analysis, search_term="stock trading alerts")

    print("\n" + "=" * 60)
    print("STEP 2/3 — Script Agent")
    print("=" * 60)
    script_agent = ScriptAgent()
    research = script_agent.research_pain_points(ad_analysis.get("pain_points", []))
    scripts_data = await script_agent.generate_scripts(ad_analysis, research)
    script_agent.save_results(scripts_data, search_term="stock trading alerts")

    print("\n" + "=" * 60)
    print("STEP 3/3 — Video Agent")
    print("=" * 60)
    video_agent = VideoAgent()
    script = video_agent.select_best_script(scripts_data, script_type="pain_agitate_solve")
    brief = video_agent.build_production_brief(script)
    print("\n=== PRODUCTION BRIEF ===\n")
    print(brief)
    video_agent.save_brief(brief, script.get("script_type", "unknown"))

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
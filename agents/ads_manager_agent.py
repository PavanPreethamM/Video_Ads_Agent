import openrouter_patch

import asyncio
import json
from datetime import datetime
from apify_client import ApifyClient
from hermes.core import Agent

import config

class AdsManagerAgent:
    def __init__(self):
        self.apify = ApifyClient(config.APIFY_TOKEN)

#This Function is used to scrape Data:
    def scrape_ads(self , search_term : str , max_int : int = 10 , country : str ="US"):

        ad_library_url = (
            "https://www.facebook.com/ads/library/"
            f"?active_status=active&ad_type=all&country={country}"
            f"&q={search_term.replace(' ', '%20')}"
            "&search_type=keyword_unordered"
        )

        run_input = {
            "urls" : [{"url" : ad_library_url}],
            "count" : 10,
            "scrapePageAds.period" : "last30d",
            "scrapePageAds.activeStatus" : "active",
            "scrapePageAds.SortBy" : "impressions_desc",
        }
        print(f"Scraping Ads of Search Term '{search_term}'...")
        run = self.apify.actor("curious_coder/facebook-ads-library-scraper").call(run_input=run_input)

        dataset_id = run.default_dataset_id
        items = list(self.apify.dataset(dataset_id).iterate_items())

        print(f"Retrived {len(items)} ads")

        return items

    async def analyze_ads(self,ads : list ) -> dict:
        ad_texts = []
        for ad in ads:
            text = ad.get("snapshot" , {}).get("body" , {}).get("text" , {})
            page_name = ad.get("snapshot" , {}).get("page_name" , "Unkonown")
            if text:
                ad_texts.append(f"[{page_name}] : {text}")

        combined_ads = "/n/n---/n/n".join(ad_texts)

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
            )
        )
        task = f"""Analyze these {len(ad_texts)} trading-education ads and answer:

    1. What PAIN POINTS do these ads target? (specific frustrations, fears)
    2. What HOOKS do they use to grab attention in the first line?
    3. What MARKETING CONCEPTS/ANGLES appear repeatedly? (e.g. urgency, social proof, "us vs them")

    Ads:
    {combined_ads}
    """
        print("Sending ads data to LLM for analysis ...")
        response = await agent.execute(input_data=task)
        response_txt = response.response.content

        analysis = json.loads(response_txt)
        print("Analysis Complete")
        return analysis

    def save_results(self , ads: list, analysis: dict, search_term : str) -> tuple:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        raw_filename = f"data/raw_ads/ads_{timestamp}.json"
        with open(raw_filename , "w" , encoding="utf-8") as f :
            json.dump({
                "search_term" : search_term,
                "scraped_at" : datetime.now().isoformat(),
                "total_ads" : len(ads),
                "ads" : ads,
            } , f , indent=2 , ensure_ascii=False)

        analysis_filename = f"data/analyzed_ads/analysis_{timestamp}.json"
        with open(analysis_filename , "w" , encoding="utf-8") as f:
            json.dump({
                    "search_term": search_term,
                    **analysis,
                }, f, indent=2, ensure_ascii=False)

        print(f"Raw ads saved to {raw_filename}")
        print(f"analysis file saved to {analysis_filename}")
        return raw_filename , analysis_filename

async def main():
    agent = AdsManagerAgent()
    ads = agent.scrape_ads(search_term="stock trading alerts", max_int =10)
    analysis = await agent.analyze_ads(ads)
    agent.save_results(ads , analysis , search_term="stock trading alerts")

if __name__ == "__main__" :
    asyncio.run(main())

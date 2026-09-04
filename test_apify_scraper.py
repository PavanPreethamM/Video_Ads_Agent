from apify_client import ApifyClient
import config
import json

client = ApifyClient(config.APIFY_TOKEN)

# This is the exact URL format Meta's own Ad Library website uses when
# you type a search into facebook.com/ads/library yourself. We're
# building it manually so the Actor can "visit" it on our behalf.
search_term = "stock trading alerts"
ad_library_url = (
    "https://www.facebook.com/ads/library/"
    f"?active_status=active&ad_type=all&country=US"
    f"&q={search_term.replace(' ', '%20')}"
    "&search_type=keyword_unordered"
)

run_input = {
    "urls": [{"url": ad_library_url}],
    "count": 10,  # small number for testing — real run will ask for more
    "scrapePageAds.period": "last30d",  # matches the project's 30-day requirement
    "scrapePageAds.activeStatus": "active",
    "scrapePageAds.sortBy": "impressions_desc",  # closest public proxy for "best working"
}

print("Starting Apify Actor run... (this takes a bit — it's a real scrape)")
run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input=run_input)

# The Actor doesn't hand results back directly — it writes them into
# a "dataset" (think: a temporary results table) and gives us that
# table's ID so we can go read from it.
dataset_id = run.default_dataset_id
items = list(client.dataset(dataset_id).iterate_items())

print(f"\nGot {len(items)} ads back.")
if items:
    print("\nFirst result (pretty-printed):")
    print("\n--- Checking all 10 ads for consistent structure ---")
    for i, item in enumerate(items):
        body_text = item.get("snapshot", {}).get("body", {}).get("text")
        page_name = item.get("snapshot", {}).get("page_name")
        print(f"{i+1}. [{page_name}] {'HAS body text' if body_text else 'MISSING body text!'}")
    print(json.dumps(items[0], indent=2)[:1500])  # trimmed so it's readable

import json as json_module 
from datetime import datetime

sorted_ads = sorted(items, key=lambda ad: ad.get("is_active", False), reverse=True)
output_data = {
    "search_term": search_term,
    "scraped_at": datetime.now().isoformat(),
    "total_ads": len(sorted_ads),
    "ads": sorted_ads,
}
filename = f"data/raw_ads/test_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, "w", encoding="utf-8") as f:
    json_module.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(sorted_ads)} ads to {filename}")

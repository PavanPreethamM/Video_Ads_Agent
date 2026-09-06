from tavily import TavilyClient
import config

client = TavilyClient(api_key=config.TAVILY_API_KEY)

results = client.search(
    query="opyion trading fear of losing money",
    search_depth="basic",
    max_results= 3,
)

print("No. of results:" , len(results.get("results",[])))
for item in results.get("results", []):
    print("\nTitle:", item.get("title"))
    print("URL:", item.get("url"))
    print("Snippet:", item.get("content", "")[:200])
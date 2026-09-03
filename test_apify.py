from apify_client import ApifyClient
import config

client = ApifyClient(config.APIFY_TOKEN)

user_info = client.user().get()
print("Connected as:", user_info.username)
print("Account email:", user_info.email)
print(user_info)
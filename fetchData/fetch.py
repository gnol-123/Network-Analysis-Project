from pathlib import Path
import pandas as pd 
import json, tweepy, time
from datetime import datetime, timezone
import os

proj_root = Path(__file__).parent
output = proj_root / "artifacts"

# CONFIG ==========================================================================================================================================================================

apiKey = os.getenv("X_API_KEY")

if apiKey != None:
    apiCheck = input(f"Is this your api key: {apiKey[:8]}...? (Y/n): ")
    if apiCheck == "Y":
        api_key = apiKey
    else:
        api_key = input("Please enter X_API_KEY:\n")
else:
    api_key = input("Please enter X_API_KEY:\n")

os.environ["X_API_KEY"] = api_key


TOKEN = os.getenv("X_API_KEY")

QUERY = "(#metgala OR #metgala2026) lang:en -is:retweet"

START_TIME = datetime(2026, 5, 3, 0, 0, 0, tzinfo=timezone.utc)
END_TIME   = datetime(2026, 5, 9, 0, 0, 0, tzinfo=timezone.utc)

MAX_RESULT_PER_PAGE = 100
TOTAL_TWEETS = 10
OUTPUT_JSON = output / "dataDump.json"
OUTPUT_CSV = output / "dataDump.csv"

TWEET_FIELDS = [
    "id", "text", "author_id", "created_at",
    "public_metrics",       # retweet_count, reply_count, like_count, quote_count
    "entities",             # hashtags, mentions, urls
    "conversation_id",      # thread grouping
    "in_reply_to_user_id",  # reply relationships
    "referenced_tweets",    # retweets / quotes
    "lang",
]

USER_FIELDS = [
    "id", "name", "username",
    "public_metrics",
    "verified",
    "description",
]

EXPANSIONS = [
    "author_id",
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
    "in_reply_to_user_id",
    "entities.mentions.username",
]

# Initialise Client ==========================================================================================================================================================================

client = tweepy.Client(bearer_token=TOKEN, wait_on_rate_limit=True)

# fetchData ==========================================================================================================================================================================

def fetchData(query, tweet_limit):
    
    collected = []
    user_lookup = {}

    paginator = tweepy.Paginator(
        client.search_recent_tweets,
        query=query,
        tweet_fields=TWEET_FIELDS,
        user_fields=USER_FIELDS,
        expansions=EXPANSIONS,
        max_results=MAX_RESULT_PER_PAGE,
        start_time=START_TIME,
        end_time=END_TIME,    
    )

    # if no data break
    for page_num, response in enumerate(paginator, start=1):
        if response.data is None:
            print("No more data...")
            break

    # userID map
    if response.includes and "users" in response.includes:
        for user in response.includes["users"]:
            user_lookup[user.id] = user

    
    for tweet in response.data:
        author = user_lookup.get(tweet.author_id)

        # Hashtags and mentions --------------------------------------------------------------------------------------------

        hashtags = []
        mentions = []
        if tweet.entities:
            if "hashtags" in tweet.entities:
                hashtags = [tag["tag"].lower() for tag in tweet.entities["hashtags"]]
            if "mentions" in tweet.entities:
                mentions = [mention["username"] for mention in tweet.entities["mentions"]]

        # Tweet type ------------------------------------------------------------------------------------------------------

        tweet_type = "original"
        referenced_tweet_id = None
        referenced_tweet_type = None
        if tweet.referenced_tweets:
            ref = tweet.referenced_tweets[0]
            referenced_tweet_type = ref.type
            referenced_tweet_id   = str(ref.id)
            tweet_type = ref.type

        # Format row -------------------------------------------------------------------------------------------------------

        row = {

                "tweet_id":             str(tweet.id),
                "conversation_id":      str(tweet.conversation_id) if tweet.conversation_id else None,
                "created_at":           tweet.created_at.isoformat() if tweet.created_at else None,
                "text":                 tweet.text,
                "lang":                 tweet.lang,

                "author_id":            str(tweet.author_id),
                "author_name":          author.name     if author else None,
                "author_username":      author.username if author else None,
                "author_followers":     author.public_metrics["followers_count"] if author else None,
                "author_following":     author.public_metrics["following_count"] if author else None,
                "author_tweet_count":   author.public_metrics["tweet_count"]     if author else None,
                "author_verified":      author.verified if author else None,                

                "retweet_count":        tweet.public_metrics["retweet_count"],
                "reply_count":          tweet.public_metrics["reply_count"],
                "like_count":           tweet.public_metrics["like_count"],
                "quote_count":          tweet.public_metrics["quote_count"],

                "tweet_type":           tweet_type,             # original | retweeted | quoted | replied_to
                "in_reply_to_user_id":  str(tweet.in_reply_to_user_id) if tweet.in_reply_to_user_id else None,
                "referenced_tweet_id":  referenced_tweet_id,
                "referenced_tweet_type": referenced_tweet_type,

                "hashtags":             "|".join(hashtags),
                "mentions":             "|".join(mentions),

        }

        collected.append(row)

        if len(collected) >= tweet_limit:
            print(f"Reached total limit of {tweet_limit} tweets.")
            return collected, user_lookup

        print(f"  Page {page_num}: collected {len(collected)} tweets so far...")
        return collected
        

# main ========================================================================================================================================================

def main():

    print(f"Collecting data from \n\tQuery: {QUERY}, \n\tNum_tweets: {TOTAL_TWEETS}")
    tweets = fetchData(QUERY, TOTAL_TWEETS)

    print(f"exporting tweets to .csv...")
    df = pd.DataFrame(tweets)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"exporting tweets to .json...")
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=4)

    # EXTRA STATS ------------------------------------------------------------------------------------------

    # Top hashtags
    all_tags = []
    for tags in df["hashtags"].dropna():
        all_tags.extend(tags.split("|"))

    tag_series = pd.Series(all_tags).value_counts().head(15)

    print(f"\n  Top co-occurring hashtags:\n{tag_series.to_string()}")

    # Top mentioned users

    all_mentions = []
    for ms in df["mentions"].dropna():
        all_mentions.extend(ms.split("|"))

    mention_series = pd.Series(all_mentions).value_counts().head(10)

    print(f"\n  Top mentioned users:\n{mention_series.to_string()}")

    print("\nDone.")

# ==========================================================================================================================================================================






if __name__ == "__main__":
    main()
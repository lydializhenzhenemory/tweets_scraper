from playwright.sync_api import sync_playwright
import csv
import jmespath
from typing import Dict
import logging
import time

def scrape_tweet(url: str) -> dict:
    _xhr_calls = []

    def intercept_response(response):
        """capture all background requests and save them"""
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    browser = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)  # Set headless=False to run browser in visible mode
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.on("response", intercept_response)
            page.goto(url)
            page.wait_for_selector("[data-testid='tweet']", timeout=1500)

            tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
            for xhr in tweet_calls:
                data = xhr.json()
                return data['data']['tweetResult']['result']
    except Exception as e:
        logging.error(f"Error loading tweet from {url}: {e}")
        return None
    finally:
        if browser:
            time.sleep(1.5)
            try:
                browser.close()
            except Exception as e:
                logging.error(f"Error closing browser: {e}")

def parse_tweet(data: Dict) -> Dict:
    """Parse Twitter tweet JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        id: legacy.id_str,
        created_at: legacy.created_at,
        attached_urls: legacy.entities.urls[].expanded_url,
        attached_urls2: legacy.entities.url.urls[].expanded_url,
        attached_media: legacy.entities.media[].media_url_https,
        tagged_users: legacy.entities.user_mentions[].screen_name,
        tagged_hashtags: legacy.entities.hashtags[].text,
        favorite_count: legacy.favorite_count,
        bookmark_count: legacy.bookmark_count,
        quote_count: legacy.quote_count,
        reply_count: legacy.reply_count,
        retweet_count: legacy.retweet_count,
        text: legacy.full_text,
        is_quote: legacy.is_quote_status,
        is_retweet: legacy.retweeted,
        language: legacy.lang,
        user_id: legacy.user_id_str,
        source: source,
        views: views.count
    }""",
        data,
    )
    result["poll"] = {}
    poll_data = jmespath.search("card.legacy.binding_values", data) or []
    for poll_entry in poll_data:
        key, value = poll_entry["key"], poll_entry["value"]
        if "choice" in key:
            result["poll"][key] = value["string_value"]
        elif "end_datetime" in key:
            result["poll"]["end"] = value["string_value"]
        elif "last_updated_datetime" in key:
            result["poll"]["updated"] = value["string_value"]
        elif "counts_are_final" in key:
            result["poll"]["ended"] = value["boolean_value"]
        elif "duration_minutes" in key:
            result["poll"]["duration"] = value["string_value"]
    user_data = jmespath.search("core.user_results.result", data)
    if user_data:
        user_info = parse_user(user_data)
        result.update(user_info)  # Flatten user info into the result dictionary
    return result

def parse_user(data: Dict) -> Dict:
    """Parse user information from Twitter JSON dataset"""
    return jmespath.search(
        """{
        user_id: rest_id,
        username: legacy.screen_name,
        display_name: legacy.name,
        user_created_at: legacy.created_at,
        description: legacy.description,
        followers_count: legacy.followers_count,
        friends_count: legacy.friends_count,
        statuses_count: legacy.statuses_count,
        profile_image_url: legacy.profile_image_url_https,
        verified: legacy.verified
    }""",
        data,
    )

def save_to_csv(data: list, file_name: str):
    """
    Save parsed tweet data to a CSV file.
    """
    if not data:
        return

    keys = data[0].keys()
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def append_to_csv(data: list, file_name: str):
    """
    Append parsed tweet data to a CSV file.
    """
    if not data:
        return

    keys = data[0].keys()
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writerows(data)

def read_tweet_ids_from_csv(file_name: str) -> list:
    """
    Read tweet IDs from a CSV file.
    """
    tweet_ids = []
    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tweet_ids.append(row['status_id'])
    return tweet_ids

def append_error_ids_to_csv(error_ids: list, file_name: str):
    """
    Append error tweet IDs to a CSV file.
    """
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for tweet_id in error_ids:
            writer.writerow([tweet_id])

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    tweet_ids = read_tweet_ids_from_csv('BLM/2020-05-2.csv')

    all_tweet_data = []
    error_ids = []

    for tweet_id in tweet_ids:
        url = f"https://x.com/users/status/{tweet_id}"
        try:
            tweet_data = scrape_tweet(url)
            if tweet_data:
                parsed_data = parse_tweet(tweet_data)
                all_tweet_data.append(parsed_data)
            else:
                error_ids.append(tweet_id)
        except Exception as e:
            logging.error(f"Error processing tweet {tweet_id}: {e}")
            error_ids.append(tweet_id)
            continue

    save_to_csv(all_tweet_data, "tweet_data.csv")

    # Save error IDs to a file
    if error_ids:
        append_error_ids_to_csv(error_ids, "retry.csv")

    # Retry for error IDs
    retry_tweet_data = []
    for tweet_id in error_ids:
        url = f"https://x.com/users/status/{tweet_id}"
        try:
            tweet_data = scrape_tweet(url)
            if tweet_data:
                parsed_data = parse_tweet(tweet_data)
                retry_tweet_data.append(parsed_data)
        except Exception as e:
            logging.error(f"Error processing tweet {tweet_id} on retry: {e}")
            continue
        
    if retry_tweet_data:
        append_to_csv(retry_tweet_data, "tweet_data1.csv")

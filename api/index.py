from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta, timezone
import os

app = Flask(__name__)

# === Configuration ===
SENT_LOG = "sent_bounties.txt"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# === Firecrawl Scraper using /search endpoint ===
def get_bounties():
    print("📡 Fetching bounties via Firecrawl /scrape API...")

    url = "https://api.firecrawl.dev/v1/scrape"
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "url": "https://replit.com/bounties",
        "formats": ["json"],
        "onlyMainContent": False,
        "waitFor": 2000,
        "jsonOptions": {
            "prompt": (
                "Extract an array called bounties with objects containing "
                "title, reward, link, and posted_time (ISO8601 or RFC3339 format) from the replit.com bounties page. "
                "The posted_time should be the actual posting date/time of the bounty."
            )
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload)
        data = resp.json()
        print(data)  # debug

        if not data.get("success") or not data.get("data"):
            print("⚠️ No data returned by Firecrawl scrape")
            return []

        result = data["data"]
        bounties_arr = result.get("json", {}).get("bounties", [])
        if not bounties_arr:
            print("⚠️ No bounties extracted from json")
            return []

        bounties = []
        for item in bounties_arr:
            try:
                title = item.get("title", "Unknown")
                link = item.get("link", "")
                if link.startswith("/"):
                    link = "https://replit.com" + link
                reward_str = item.get("reward", "$0")
                value = int(''.join(filter(str.isdigit, reward_str)))
                posted_time_str = item.get("posted_time")
                if posted_time_str:
                    try:
                        created_at = datetime.fromisoformat(posted_time_str.replace("Z", "+00:00"))
                    except Exception:
                        created_at = datetime.now(timezone.utc)
                else:
                    created_at = datetime.now(timezone.utc)
                bounties.append({
                    "title": title,
                    "value": value,
                    "link": link,
                    "created_at": created_at
                })
            except Exception as e:
                print(f"❌ Parse error on bounty {item}: {e}")

        print(f"✅ Parsed {len(bounties)} bounties")
        return bounties

    except Exception as e:
        print(f"❌ Firecrawl API error: {e}")
        return []

# === Utility functions ===
def filter_recent(bounties):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    return [b for b in bounties if b["created_at"] > cutoff]

def read_sent_links():
    return set(open(SENT_LOG).read().splitlines()) if os.path.exists(SENT_LOG) else set()

def write_sent_link(link):
    with open(SENT_LOG, "a") as f:
        f.write(link + "\n")

def send_to_slack(bounty):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack webhook not configured")
        return
    msg = {
        "text": f"🔥 New Top Bounty!\n*{bounty['title']}*\n💰 ${bounty['value']}\n🔗 {bounty['link']}"
    }
    res = requests.post(SLACK_WEBHOOK_URL, json=msg)
    print("✅ Slack sent" if res.status_code == 200 else f"❌ Slack error: {res.text}")

# === Flask endpoint ===
@app.route("/scrape", methods=["GET"])
def scrape_bounties():
    bounties = get_bounties()
    recent = filter_recent(bounties)
    sent = read_sent_links()
    unsent = [b for b in recent if b["link"] not in sent]

    if not unsent:
        return jsonify({"message": "No new bounties found."})

    top = max(unsent, key=lambda b: b["value"])
    send_to_slack(top)
    write_sent_link(top["link"])
    return jsonify({"message": "Sent top bounty to Slack.", "bounty": top})

if __name__ == "__main__":
    app.run(debug=True)

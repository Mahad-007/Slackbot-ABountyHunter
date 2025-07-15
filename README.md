# Replit Bounty Slack Bot

## Objective

A Flask app that scrapes the latest open bounties from [Replit Bounties](https://replit.com/bounties?status=open&order=creationDateDescending), identifies the highest-valued bounty posted in the last 24 hours, and sends it to a Slack channel. Deployed on Vercel and scheduled to run every 24 hours.

## Features
- Flask API endpoint `/scrape` to trigger the bot
- Scrapes Replit bounties using FireCrawl
- Filters bounties posted in the last 24 hours
- Sends the top-valued new bounty to Slack (no duplicates)
- Tracks sent bounties in `sent_bounties.txt`
- Deployable on Vercel (free tier)
- Easy to schedule with Vercel Cron or external services

## Setup

1. **Clone the repo**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**
   - Copy `.env.example` to `.env` and fill in your values:
     - `SLACK_WEBHOOK_URL`: Your Slack Incoming Webhook URL
     - `FIRECRAWL_API_KEY`: Your FireCrawl API key
4. **Run locally**
   ```bash
   flask run --app api/index.py
   # or
   python api/index.py
   ```
5. **Test**
   - Visit `http://localhost:5000/scrape` to trigger the bot

## Deployment (Vercel)

1. **Push your code to GitHub**
2. **Import your repo on [Vercel](https://vercel.com/import)**
3. **Set environment variables in Vercel dashboard**
   - `SLACK_WEBHOOK_URL`
   - `FIRECRAWL_API_KEY`
4. **Deploy!**

## Scheduling (Cron)

- **Vercel Cron**: Add a schedule in the Vercel dashboard to hit `/scrape` every 24 hours.
- **External Cron**: Use GitHub Actions, EasyCron, or UptimeRobot to make a GET request to your deployed `/scrape` endpoint every 24 hours.

## Notes
- Only bounties posted in the last 24 hours are considered.
- Sent bounties are tracked in `sent_bounties.txt` to avoid duplicates.
- For local testing, use a private Slack channel.

---

**Happy hacking!** 
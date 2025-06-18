import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime
from collections import defaultdict

# --- Load secrets ---
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")

if not API_KEY or not PROJECT_ID:
    raise ValueError("Missing OPENAI_API_KEY or OPENAI_PROJECT_ID in .env")

client = OpenAI(api_key=API_KEY, project=PROJECT_ID)
MODEL = "gpt-4o"
OUTPUT_JSON = f"rns_summaries_{datetime.now().strftime('%Y%m%d')}.json"

# --- Fixed Sectors ---
SECTORS = [
    "Retail & Leisure",
    "Industrials",
    "Technology, Media and Telecoms",
    "Financial & Professional Services",
    "Real Estate & Construction",
    "Energy, Chemicals, Mining & Utilities",
    "Healthcare & Pharma"
]

# --- AI Summary ---
def summarise_rns(rns_text):
    prompt = (
        "You're a financial journalist. Summarise this UK RNS announcement in 1–3 bullet points. "
        "Write in clear, concise, one-line summaries. Each summary should:\n"
        "- Begin with the company name in **bold**, followed by an en dash\n"
        "- Start the summary in lowercase, unless the first word is a proper name\n"
        "- Use 'has announced' if relaying a company action\n"
        "- Use 'has said that' when referring to third-party actions or external events\n"
        "- Correctly capitalise initials in personal names (e.g. 'J.T. Starzecki')\n"
        "- End each summary with (Link)\n\n"
        f"RNS:\n{rns_text}"
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# --- Main function (for CLI-style testing) ---
def main():
    grouped = defaultdict(list)
    print("Paste your RNS content and press Enter twice.\n")

    while True:
        company = input("Company Name: ").strip()
        if not company:
            break
        url = input("RNS Link (URL): ").strip()
        print("Paste RNS text (end with a blank line):")
        lines = []
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        rns_text = "\n".join(lines)

        print("Available Sectors:")
        for i, s in enumerate(SECTORS, 1):
            print(f"{i}. {s}")
        sector_idx = int(input("Choose sector number: ").strip()) - 1
        sector = SECTORS[sector_idx]

        print("Summarising...")
        summary = summarise_rns(rns_text)

        grouped[sector].append({
            "company": company,
            "link": url,
            "summary": summary
        })

        print(f"✅ Summary added for {company}.\n---")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(grouped, f, indent=2)
    print(f"🎉 Summaries saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()

# Hugging Face healthcheck workaround
import os

if os.environ.get("HF_SPACE_ID"):
    import socket
    import http.server
    import threading

    class HealthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")

    def run_health_server():
        server_address = ('', 7861)
        httpd = http.server.HTTPServer(server_address, HealthHandler)
        httpd.serve_forever()

    thread = threading.Thread(target=run_health_server)
    thread.daemon = True
    thread.start()

# --- Actual App Starts Below ---

import streamlit as st
import json
from openai import OpenAI
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime
from io import BytesIO

# --- Load OpenAI credentials from Streamlit secrets ---
api_key = st.secrets["OPENAI_API_KEY"]
project_id = st.secrets["OPENAI_PROJECT_ID"]
MODEL = "gpt-4o"

SECTORS = [
    "Retail & Leisure",
    "Industrials",
    "Technology, Media and Telecoms",
    "Financial & Professional Services",
    "Real Estate & Construction",
    "Energy, Chemicals, Mining & Utilities",
    "Healthcare & Pharma"
]

def get_client():
    return OpenAI(api_key=api_key, project=project_id)

def format_summary(company, summary_text):
    summary_clean = summary_text.replace("(Link)", "").strip()
    while summary_clean.endswith("*"):
        summary_clean = summary_clean[:-1].rstrip()
    dash_index = summary_clean.find("–")
    if dash_index == -1:
        dash_index = summary_clean.find("-")
    if dash_index != -1:
        body = summary_clean[dash_index + 1:].strip()
        if body.startswith("**"):
            body = body.lstrip("*").strip()
        if body and not body[0].isupper():
            body = body[0].lower() + body[1:]
        return f"**{company}** – {body} (Link)"
    else:
        return f"**{company}** – {summary_clean} (Link)"

def generate_summary(rns_text):
    client = get_client()
    prompt = f"""
You're a financial journalist. Summarise this UK RNS announcement in one bullet point.

Editorial rules:
- Begin with the company name in **bold**, followed by an en dash (–)
- Do not repeat the company name in the body
- Use "has announced" for company-led updates
- Use "has said that" for third-party or external developments
- Begin the sentence after the dash in lowercase, unless it's a proper noun
- Correctly capitalise initials in names (e.g. "J.T. Starzecki")
- Include only strategic, financial, or operational business facts
- End each summary with: (Link)

RNS:
{rns_text}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    rStyle = OxmlElement('w:rStyle')
    rStyle.set(qn('w:val'), 'Hyperlink')
    rPr.append(rStyle)

    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0000FF')
    rPr.append(color)

    underline = OxmlElement('w:u')
    underline.set(qn('w:val'), 'single')
    rPr.append(underline)

    run.append(rPr)
    t = OxmlElement('w:t')
    t.text = text
    run.append(t)

    hyperlink.append(run)
    paragraph._p.append(hyperlink)

def docx_export(summaries):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    grouped = {sector: [] for sector in SECTORS}
    for item in summaries:
        grouped[item["sector"]].append(item)

    for sector in SECTORS:
        entries = sorted(grouped[sector], key=lambda x: x["company"])
        if entries:
            p = doc.add_paragraph()
            run = p.add_run(sector)
            run.bold = True
            run.underline = True
            run.font.color.rgb = RGBColor(0, 0, 0)

            for item in entries:
                para = doc.add_paragraph()
                summary_clean = item["summary"].replace(" (Link)", "").strip()
                dash_index = summary_clean.find("–")
                if dash_index != -1:
                    summary_part = summary_clean[dash_index + 1:].strip()
                    while summary_part.endswith("*"):
                        summary_part = summary_part[:-1].rstrip()
                    if summary_part.startswith("**"):
                        summary_part = summary_part.lstrip("*").strip()
                else:
                    summary_part = summary_clean
                para.add_run(item["company"]).bold = True
                para.add_run(" – ")
                para.add_run(summary_part + " ")
                add_hyperlink(para, "(Link)", item["link"])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def today():
    return datetime.now().strftime("%Y-%m-%d")

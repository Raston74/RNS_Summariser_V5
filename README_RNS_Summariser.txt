📄 README — How to Run the RNS Summariser Tool

✅ Step-by-Step Instructions

1. Open PowerShell or Command Prompt
   - Press `Windows + R`, type `powershell`, press `Enter`

2. Navigate to your RNS Summariser folder
   cd "C:\Users\Richard Aston\OneDrive - Early Morning Media\Desktop\RNS Summariser"

3. Launch the tool
   streamlit run streamlit_app.py

4. Use the tool in your browser
   - The app will automatically open at:
     http://localhost:8501
   - You will see input boxes for:
     • RNS Text
     • Company Name
     • RNS URL
     • Sector Dropdown
   - Click 'Summarise & Add' to generate a summary.

📝 Summary Format

Each summary:
- Begins with the company name in bold, followed by an en dash (–)
- Starts with a lowercase letter, unless it’s a name
- Ends with (Link) — which becomes clickable in Word export
- Example:
  **Peel Hunt** – has announced that...

📤 Exporting Summaries

- Click ⬇️ Download as Word (.docx) to export a formatted Word file
- Or use ⬇️ Download as JSON for structured data output
- Word exports include:
  • Bold company names
  • Clickable (Link) anchors
  • Grouped summaries under sector headings

💡 Troubleshooting

- If you see `ModuleNotFoundError: No module named 'streamlit'`, run:
  pip install streamlit openai python-dotenv python-docx

- If the app doesn't open automatically, copy and paste the terminal link into your browser (e.g. http://localhost:8501)

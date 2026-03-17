# Code Health Dashboard

This is a full-stack project I built to analyze Python code quality and translate technical signals into something that’s easy to understand for both technical and non-technical users.

---

## Overview

Most code quality tools like pylint and radon are powerful, but they’re built for developers and can be hard to interpret at a glance.

The goal of this project was to bridge that gap.

Instead of just showing raw output, this dashboard:
- assigns a **Code Health Score (0–100)**
- breaks down issues and complexity in plain language
- highlights **what matters most**
- and provides **actionable recommendations**

It’s meant to feel less like a tool and more like a product.

---

## Features

### Upload Python Files or Projects
- Upload a single `.py` file or a `.zip` archive
- Automatically extracts and analyzes all valid Python files inside the zip

---

### Code Health Score
- Custom scoring system based on:
  - lint issues (pylint)
  - cyclomatic complexity (radon)
- Outputs a normalized score from **0 to 100**
- Includes human-readable labels like:
  - "Excellent health"
  - "Needs noticeable revision"
  - "Critical condition"

---

### File Breakdown
- Per-file analysis showing:
  - score
  - number of issues
  - complexity
- Each metric includes plain-English explanations so it’s easy to interpret

---

### Issues Found
- Displays all detected issues across files
- Includes:
  - file name
  - line number
  - issue type (error, warning, etc.)
  - description

This helps explain *why* the score landed where it did.

---

### Top Recommendations
- Dynamically generated based on:
  - files with the most issues
  - files with the highest complexity
  - severity of findings
- Focuses on the **highest-impact improvements first**

---

### Zip File Support (Multi-file Analysis)
- Supports full project uploads via `.zip`
- Handles edge cases like macOS zip artifacts:
  - ignores `__MACOSX`
  - ignores `.DS_Store`
  - ignores `._*` metadata files
- Only analyzes valid Python source files

---

## Tech Stack

### Frontend
- React (Vite)
- Custom CSS

### Backend
- Flask
- Python

### Code Analysis
- pylint → issue detection
- radon → complexity analysis

---

## Project Structure

```
server/
  app/
    routes/
      analysis.py
    services/
      analyzer.py
      scoring.py
  run.py

client/
  src/
    components/
      UploadForm.jsx
      ScoreCard.jsx
      FileTable.jsx
      IssuesList.jsx
      RecommendationList.jsx
    services/
      api.js
    App.jsx
```

---

## How It Works

1. Upload a `.py` file or `.zip`
2. Backend:
   - extracts files (if zip)
   - runs pylint for issues
   - runs radon for complexity
3. Results are processed into:
   - scores
   - summaries
   - recommendations
4. Frontend renders everything into a dashboard view

---

## Running the Project

### Backend

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Note: Flask is run with `use_reloader=False` to prevent intermittent connection issues during analysis.

---

### Frontend

```bash
cd client
npm install
npm run dev
```

---

## Example Output

- Code Health Score: `92 (Excellent health)`
- Issues: `24 (Heavy issue load)`
- Complexity: `3 (Easy to understand)`
- Files analyzed: `7`

---

## Design Goals

The main goal was to make code quality:

- easier to understand
- easier to act on
- easier to explain to someone who isn’t deep in the code

This project focuses on:
- turning raw technical output into **clear insights**
- prioritizing **what to fix first**
- presenting everything in a way that feels like a real product

---

## Future Improvements

Some ideas I’d like to explore next:

- GitHub repo integration (analyze repos directly)
- AI-generated recommendations
- score tracking over time
- grouping similar issues together
- visual analytics (charts, heatmaps)

---

## Why I Built This

I’m currently transitioning into software engineering and product management, and I wanted to build something that reflects both sides.

This project isn’t just about analyzing code.

It’s about:
- understanding how to structure data
- deciding what actually matters to users
- and presenting technical information in a way that drives decisions

---

## Author

Rowvin Dizon 2026

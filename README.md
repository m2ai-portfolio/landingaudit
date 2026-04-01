

#LandingFlow Audit  
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)  
![License: MIT](https://img.shields.io/badge/license-MIT-green)  


## Overview
LandingFlow Audit is an automated SaaS landing‑page analysis tool that scans local HTML files to detect navigation and conversion‑flow issues. It runs entirely offline, using only the Python standard library, and produces actionable CSV and JSON reports that highlight broken links, orphaned pages, missing CTAs, form‑validation problems, and other factors that hurt user journeys and conversion rates. The tool is aimed at SaaS founders, product marketers, and growth teams who need a fast, data‑driven way to audit their landing‑page portfolio without external dependencies.

## Problem Statement
Many SaaS landing pages suffer from broken navigation flows, unclear conversion funnels, and missing or weak calls‑to‑action. Founders and growth teams lack a systematic, automated method to discover these issues across dozens or hundreds of pages, leading to missed conversion opportunities and wasted ad spend.

## Features
- Recursive discovery of all `.html` files in a configurable input directory  
- Extraction of anchors, forms, and visible text using `html.parser`  
- Construction of a navigation graph to detect:
  - Orphaned pages (zero inbound links)  
  - Circular navigation (cycles > 2 nodes)  
  - Excessive redirect chains (> 3 hops)  
  - Missing primary CTAs on a page  
- Conversion‑focused heuristics that evaluate:
  - Form visibility (above the fold, not obscured)  
  - CTA prominence (contrast, surrounding whitespace)  
  - Form field validation (missing `required`, incorrect input types)  
- Scoring of each issue (1‑10) and reporting only those ≥ 3  
- Generation of both CSV (RFC 4180) and JSON (RFC 8259) reports  
- Deterministic, offline execution with zero external API calls  
- Easy integration into CI/CD or local scripts via a simple CLI  

## Tech Stack
- **Language**: Python 3.11+  
- **Standard‑library only**: `pathlib`, `json`, `csv`, `re`, `typing`, `dataclasses`, `html.parser`  
- No third‑party packages required  

## Quick Start / Installation
1. **Clone the repository**  
   ```bash
   git clone <repo‑url>
   cd landingflow_audit
   ```
2. **(Optional) Create a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```
3. **Ensure Python 3.11+ is installed**  
   ```bash
   python --version
   ```
4. **Run the audit** (points to the folder containing your HTML files)  
   ```bash
   python -m landingflow_audit.main --input ./landing_pages --output ./reports
   ```
   - `--input` – directory with local HTML files (defaults to `./landing_pages`)  
   - `--output` – directory where `audit_report.csv` and `audit_report.json` will be written (defaults to `./reports`)  
   - `--min-confidence` – minimum severity threshold (defaults to `0.7` → score ≥ 3)  

## Usage
- **Basic audit**  
  ```bash
  python -m landingflow_audit.main
  ```
- **Custom directories**  
  ```bash
  python -m landingflow_audit.main --input ./my_pages --output ./my_reports
  ```
- **Adjust sensitivity** (e.g., only show critical issues, severity ≥ 7)  
  ```bash
  python -m landingflow_audit.main --min-confidence 0.7
  ```
- **Integrate into CI** – add the command to your test pipeline; non‑zero exit code is returned if any issue meets the threshold.  
- **View results**  
  - Open `reports/audit_report.csv` in a spreadsheet or `reports/audit_report.json` in any JSON viewer.  

## Architecture
```
landingflow_audit/
├── main.py                # CLI entry point, argument handling, orchestrator
├── core/
│   ├── crawler.py        # File discovery, HTML parsing, extraction of anchors/forms
│   ├── navigator.py      # Graph construction, navigation‑flow detection (orphans, cycles, redirects, missing CTA)
│   └── reporter.py       # Issue scoring, CSV/JSON report generation
└── data/
    └── models.py         # Dataclasses: Issue, AuditResult
```
- **Data flow**: `main.py` → `crawler.py` (collects raw elements) → `navigator.py` (analyzes navigation & conversion heuristics) → `reporter.py` (produces final reports).  
- All modules depend only on the Python standard library, making the tool portable and easy to test.  

## License
MIT License – see the `LICENSE` file for details.
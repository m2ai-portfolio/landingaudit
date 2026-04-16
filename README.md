

<p align="center">
  <img src="assets/infographic.png" alt="LandingFlow Audit" width="800">
</p>

<h3 align="center">USE THE PLAIN-SPEAK DESCRIPTION PROVIDED ABOVE -- DO NOT INVENT</h3>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#examples">Examples</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

LandingFlow Audit scans a folder of local HTML landing pages and produces actionable navigation and conversion‑flow insights. It is aimed at SaaS founders, product marketers, and growth teams who want to improve conversion rates without manual UX audits.

```
$ python landingflow_audit/main.py --input ./landing_pages
Scanned 57 pages, found 12 issues (3 critical, 5 high, 4 medium).
Reports written to ./reports/audit_report.csv and ./reports/audit_report.json
```

Most SaaS landing pages have broken navigation flows that hurt conversions, but founders lack systematic ways to identify these issues. Manual analysis is time‑consuming and requires UX expertise. Companies need data‑driven insights about what's working across their industry to benchmark their own pages.

| Feature | Description |
|---------|-------------|
| Page Crawl & Data Extraction | Recursively walks the input directory, loads each HTML file, and extracts anchors, forms, and CTA‑related text using only the Python standard library. |
| Navigation Flow Detection | Builds a directed graph from extracted links to surface orphaned pages, circular navigation, missing CTAs, and excessive redirect chains. |
| Conversion Issue Reporting | Evaluates forms and CTA prominence, flags missing required attributes, incorrect input types, low contrast, and forms hidden below the fold. |
| Offline‑First Analysis | Runs entirely offline with zero external API calls; all parsing, graph building, and scoring use the standard library, ensuring data never leaves the machine. |
| Configurable Sensitivity | Adjust the minimum confidence threshold via the `LF_MIN_CONFIDENCE` environment variable to tune how aggressively issues are reported. |
| Structured Report Generation | Emits both CSV (RFC 4180) and JSON (RFC 8259) files that downstream tools can ingest without schema validation errors. |

### Quick Start
1. Clone the repository: `git clone https://github.com/yourorg/landingflow_audit.git`
2. Change into the project directory: `cd landingflow_audit`
3. Ensure Python 3.11+ is installed (`python --version`).
4. (Optional) Set environment variables: `export LF_DATA_DIR=./landing_pages`, `export LF_OUTPUT_DIR=./reports`, `export LF_MIN_CONFIDENCE=0.7`.
5. Place your HTML landing pages in the `landing_pages` folder.
6. Run the audit: `python landingflow_audit/main.py`

### Examples
**Basic audit of a sample landing page set**  
```bash
$ python landingflow_audit/main.py --input ./demo_pages
Scanned 23 pages.
Issues found:
- ./demo_pages/pricing.html: missing_cta (severity 8) – Add a prominent CTA button above the fold.
- ./demo_pages/features.html: broken_navigation (severity 6) – Fix orphaned anchor pointing to /non‑existent.
Reports written to ./reports/audit_report.csv and ./reports/audit_report.json
```

**Audit with a higher confidence threshold to surface only critical issues**  
```bash
$ LF_MIN_CONFIDENCE=0.9 python landingflow_audit/main.py
Scanned 23 pages.
Issues found (confidence ≥ 0.9):
- ./demo_pages/checkout.html: missing_cta (severity 9) – Primary CTA not detectable.
Reports written to ./reports/audit_report.csv and ./reports/audit_report.json
```

**Specify a custom output directory**  
```bash
$ python landingflow_audit/main.py --output ./custom_reports
Scanned 23 pages.
Issues found: 12.
CSV report: ./custom_reports/audit_report.csv
JSON report: ./custom_reports/audit_report.json
```

### File Structure
```
LandingFlow Audit/
├─ landingflow_audit/
│   ├─ __init__.py
│   ├─ main.py
│   ├─ core/
│   │   ├─ __init__.py
│   │   ├─ crawler.py      # HTML traversal and extraction
│   │   ├─ navigator.py    # Graph building and issue detection
│   │   └─ reporter.py     # CSV/JSON report generation
│   └─ data/
│       ├─ __init__.py
│       └─ models.py       # Issue and AuditResult dataclasses
├─ landing_pages/          # Place your HTML files here
├─ reports/                # Generated audit reports (CSV/JSON)
├─ assets/
│   └─ infographic.png    # Banner image used in README
├─ screenshots/           # Verification screenshots (optional)
├─ .gitignore
├─ LICENSE
└─ README.md
```

### Tech Stack
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Runtime language |
| pathlib | Filesystem traversal |
| html.parser | HTML parsing |
| re | Pattern matching for CTA detection |
| json | Structured report output |
| csv | Tabular report output |
| typing | Type hints for clarity |
| dataclasses | Lightweight data models |

### Contributing
Fork the repository, create a feature branch, make your changes, ensure existing tests pass, and submit a pull request. Please follow the existing code style and add unit tests for new functionality.

### License
MIT

### Author
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)
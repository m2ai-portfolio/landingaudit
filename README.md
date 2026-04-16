

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

## What is this?
LandingFlow Audit is an offline tool that scans local HTML files to find navigation and conversion problems on SaaS landing pages. It helps founders, product marketers, and growth teams quickly spot broken links, missing CTAs, and form issues that hurt conversions.  
Example usage:
```
$ python -m landingflow_audit.main
Scanning 23 pages... Done.
Report written to reports/audit_report.csv
Report written to reports/audit_report.json
```

## Problem
Most SaaS landing pages have broken navigation flows that hurt conversions, but founders lack systematic ways to identify these issues. Manual analysis is time-consuming and requires UX expertise. Companies need data-driven insights about what's working across their industry to benchmark their own pages.

## Features
| Feature | Description |
|---------|-------------|
| HTML Crawl | Recursively loads all HTML files from a directory, extracting anchors, forms, and CTA‑like text using only the standard library. |
| Navigation Graph | Builds a directed graph from extracted links to detect orphaned pages, circular navigation, and missing primary calls‑to‑action. |
| Redirect Chain Check | Flags navigation paths where redirect depth exceeds three hops without intermediate value. |
| Form Visibility Scan | Determines whether a form appears above the fold or is obscured by fixed positioning elements. |
| CTA Prominence Test | Evaluates contrast and whitespace around CTA elements to ensure they stand out visually. |
| Field Validation | Inspects form inputs for missing `required` attributes or incorrect types (e.g., using `text` for email). |
| Issue Scoring | Assigns a severity score (1‑10) to each finding and outputs only those with a score of 3 or higher. |
| Report Generation | Emits both CSV and JSON reports that conform to RFC 4180 and RFC 8259 for easy downstream consumption. |

## Quick Start
1. Clone the repository:  
   `git clone https://github.com/yourorg/landingflow_audit.git`
2. Change into the project directory:  
   `cd landingflow_audit`
3. Ensure Python 3.11+ is installed (no extra packages needed).  
4. Place your HTML landing pages in the `landing_pages` folder or set `LF_DATA_DIR` to another path.  
5. Run the audit:  
   `python -m landingflow_audit.main`  
   Reports will appear in the `reports` directory (or the path set by `LF_OUTPUT_DIR`).

## Examples
**Basic audit of local pages**  
```
$ python -m landingflow_audit.main
Scanning 17 pages... Done.
Found 5 issues (severity >= 3).
CSV report: reports/audit_report.csv
JSON report: reports/audit_report.json
```
Sample `audit_report.csv` (first two rows):
```
page_path,issue_type,description,severity,recommendation
landing_pages/pricing.html,missing_cta,"No CTA button or link found above the fold",8,"Add a prominent CTA such as 'Start Free Trial' near the hero section."
landing_pages/features.html,orphaned_page,"Page has zero inbound links from other audited pages",6,"Add a link from the navigation menu or homepage to this page."
```

**Custom directories and confidence threshold**  
```
$ LF_DATA_DIR="./demo-sites" LF_OUTPUT_DIR="./demo-reports" LF_MIN_CONFIDENCE="0.8" python -m landingflow_audit.main
Scanning 12 pages... Done.
Found 2 issues (severity >= 3).
CSV report: demo-reports/audit_report.csv
JSON report: demo-reports/audit_report.json
```
Sample `audit_report.json`:
```json
[
  {
    "page_path": "demo-sites/home.html",
    "issue_type": "circular_nav",
    "description": "Navigation contains a cycle of length 4: Home -> Features -> Pricing -> Feedback -> Home",
    "severity": 7,
    "recommendation": "Remove or re‑link one of the edges to break the cycle, e.g., change Feedback link to point to Contact instead of Home."
  },
  {
    "page_path": "demo-sites/signup.html",
    "issue_type": "form_field_type",
    "description": "Email input uses type='text' instead of type='email'",
    "severity": 4,
    "recommendation": "Change the input type to email to enable native validation and improve keyboard UX on mobile."
  }
]
```

**High‑volume batch with logging**  
```
$ LF_DATA_DIR="./large-set" LF_OUTPUT_DIR="./large-reports" LOGGING=INFO python -m landingflow_audit.main 2>&1 | tee run.log
Scanning 142 pages... Done.
Found 27 issues (severity >= 3).
CSV report: large-reports/audit_report.csv
JSON report: large-reports/audit_report.json
```
Excerpt from `run.log`:
```
INFO:loader:Loaded 142 HTML files from ./large-set
INFO:navigator:Detected 3 orphaned pages
INFO:reporter:Writing CSV report to large-reports/audit_report.csv
```

## File Structure
```
LandingFlow Audit/
├── landingflow_audit/
│   ├── __init__.py
│   ├── main.py                 # Entry point, loads env vars and runs pipeline
│   ├── core/
│   │   ├── __init__.py
│   │   ├── crawler.py          # Recursively walks directories, extracts tags
│   │   ├── navigator.py        # Builds graph, detects nav/issues
│   │   └── reporter.py         # Generates CSV/JSON reports
│   └── data/
│       ├── __init__.py
│       └── models.py           # Issue and AuditResult dataclasses
├── landing_pages/              # Place HTML files to audit here
├── reports/                    # Generated CSV and JSON reports (gitignored)
├── assets/
│   └── infographic.png         # Banner image for README
├── .gitignore
└── LICENSE
```

## Tech Stack
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language and runtime |
| pathlib | Filesystem traversal |
| html.parser | Extracting anchors, forms, visible text |
| re | Pattern matching for CTA detection |
| json | Structured output of audit results |
| csv | Exporting reports in RFC 4180 format |
| typing, dataclasses | Type safety and clean data models |

## Contributing
- Fork the repository and create a feature branch.  
- Make changes, add tests if applicable, and ensure the tool still runs.  
- Submit a pull request with a clear description of your work.  
- Please follow the existing code style and keep external dependencies absent.

## License
MIT

## Author
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)
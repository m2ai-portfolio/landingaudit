

<p align="center">
  <img src="assets/infographic.png" alt="Landingflow Audit" width="800">
</p>

<h3 align="center">Automated SaaS landing‑page audit for navigation and conversion issues</h3>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#examples">Examples</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

## What is this?
Landingflow Audit scans a directory of local HTML files to build a navigation graph, evaluate forms and CTAs, and flag issues that hurt user journeys or conversion rates. It outputs actionable findings in CSV and JSON formats for easy downstream consumption. The tool is aimed at SaaS founders, product marketers, and growth teams who need quick, data‑driven insights without external API calls.

Example usage:
```
$ python -m landingflow_audit.main
Processed 12 pages
Found 3 issues:
- orphaned_page: ./landing_pages/pricing.html (severity 8)
- missing_cta: ./landing_pages/features.html (severity 6)
- low_contrast_cta: ./landing_pages/signup.html (severity 4)
Reports written to ./reports/audit_report.csv and ./reports/audit_report.json
```

## Features
| Feature | Description |
|---|---|
| Recursive HTML crawler | Depth‑first traversal of `landing_pages` directory, respects symbolic links and extracts anchors, forms, and visible text. |
| Navigation graph analysis | Detects orphaned pages (zero inbound links), navigation cycles (>2 nodes), missing primary CTAs, and excessive redirect chains (>3 hops). |
| Form & CTA evaluation | Checks form visibility above the fold, CTA text contrast, whitespace padding, presence of `required` attributes, and correct input types (e.g., email vs. text). |
| Severity scoring | Assigns a 1‑10 score to each finding; only issues with score ≥ `LF_MIN_CONFIDENCE` (default 0.7 → 7) are reported. |
| Multi‑format reporting | Generates RFC 4180‑compliant CSV and RFC 8259‑compliant JSON reports in the configured output directory. |
| Stdlib‑only operation | Uses only the Python 3.11+ standard library; no network requests or third‑party packages. |

## Quick Start
1. Clone the repository: `git clone https://github.com/your-org/landingflow_audit.git`
2. Change directory: `cd landingflow_audit`
3. Verify Python 3.11+ is installed (`python --version`).
4. (Optional) Adjust environment variables: `LF_DATA_DIR`, `LF_OUTPUT_DIR`, `LF_MIN_CONFIDENCE`.
5. Run the audit: `python -m landingflow_audit.main`
6. Inspect the generated reports in the `reports/` directory.

## Examples
**Basic audit with defaults**
```
$ python -m landingflow_audit.main
Processed 15 pages
Found 5 issues:
- redirect_chain: ./landing_pages/onboarding.html (severity 9)
- missing_cta: ./landing_pages/docs.html (severity 5)
- low_contrast_cta: ./landing_pages/pricing.html (severity 6)
- form_below_fold: ./landing_pages/demo.html (severity 4)
- email_input_as_text: ./landing_pages/signup.html (severity 7)
Reports written to ./reports/audit_report.csv and ./reports/audit_report.json
```

**Custom directories via environment variables**
```
$ LF_DATA_DIR=./sites/v2 LF_OUTPUT_DIR=./sites/v2/reports python -m landingflow_audit.main
Processed 8 pages
Found 2 issues:
- orphaned_page: ./sites/v2/legacy.html (severity 8)
- missing_required: ./sites/v2/contact.html (severity 6)
Reports written to ./sites/v2/reports/audit_report.csv and ./reports/audit_report.json
\]

**Lower confidence threshold to surface more findings**
```
$ LF_MIN_CONFIDENCE=0.4 python -m landingflow_audit.main
Processed 15 pages
Found 9 issues:
- redirect_chain: ./landing_pages/onboarding.html (severity 9)
- missing_cta: ./landing_pages/docs.html (severity 5)
- low_contrast_cta: ./landing_pages/pricing.html (severity 6)
- form_below_fold: ./landing_pages/demo.html (severity 4)
- email_input_as_text: ./landing_pages/signup.html (severity 7)
- unnamed_anchor: ./landing_pages/faq.html (severity 3)
- duplicate_id: ./landing_pages/features.html (severity 3)
- noscript_fallback: ./landing_pages/index.html (severity 2)
- meta_viewport_missing: ./landing_pages/blog.html (severity 2)
Reports written to ./reports/audit_report.csv and ./reports/audit_report.json
```

## File Structure
```
Landingflow Audit/
├── landingflow_audit/
│   ├── main.py                 # Entry point for the audit
│   ├── core/
│   │   ├── crawler.py         # HTML traversal and element extraction (pathlib, html.parser)
│   │   ├── navigator.py       # Navigation graph analysis and issue detection
│   │   └── reporter.py        # CSV/JSON report generation (csv, json)
│   ├── data/
│   │   └── models.py          # Issue and AuditResult dataclasses (typing, dataclasses)
│   └── __init__.py
├── reports/                   # Generated audit reports (gitignored)
├── landing_pages/            # Sample HTML pages to audit (gitignored)
├── .gitignore
└── README.md
```

## Tech Stack
| Technology | Purpose |
|---|---|
| Python 3.11+ | Core language and runtime |
| pathlib | Filesystem traversal and path handling |
| html.parser | Standard‑library HTML parsing |
| json | Structured output of audit results |
| csv | Tabular report export (RFC 4180) |
| re | Pattern matching for CTA text and validation rules |
| typing | Type hints for maintainable code |
| dataclasses | Structured models for `Issue` and `AuditResult` |

## Contributing
To contribute:
1. Fork the repository.
2. Make changes and run any existing tests.
3. Submit a pull request with a clear description.

## License
MIT

## Author
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)
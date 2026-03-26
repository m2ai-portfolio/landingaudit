# LandingFlow Audit

An automated SaaS landing page analysis tool that detects navigation and conversion flow issues impacting user journeys and conversion rates.

## Overview

LandingFlow Audit processes local HTML files using only the Python standard library, providing actionable insights without relying on any external APIs or services.

## Features

- **Page Crawl & Data Extraction**: Recursively discovers and loads HTML files, extracting anchors, forms, and CTA text
- **Navigation Flow Detection**: Analyzes navigation graphs to find orphaned pages, circular nav, missing CTAs, and redirect chains
- **Conversion Issue Reporting**: Evaluates forms and CTAs against conversion heuristics with prioritized issue reports (CSV/JSON)

## Tech Stack

- Python 3.11+
- Standard library only (no external dependencies)

## Quick Start

```bash
./init.sh
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LF_DATA_DIR` | `./landing_pages` | Directory containing HTML files to audit |
| `LF_OUTPUT_DIR` | `./reports` | Directory for analysis reports |
| `LF_MIN_CONFIDENCE` | `0.7` | Minimum confidence threshold for flagging issues |

## Usage

```bash
python landingflow_audit/main.py
```

## File Structure

```
landingflow_audit/
├── main.py
├── core/
│   ├── crawler.py
│   ├── navigator.py
│   └── reporter.py
├── data/
│   └── models.py
└── reports/
```

"""LandingFlow Audit - Main entry point for the SaaS landing page analysis tool."""

import os
import sys
from landingflow_audit.core.crawler import PageCrawler
from landingflow_audit.core.navigator import NavigationAnalyzer


def main():
    """Main entry point for LandingFlow Audit.

    Reads configuration from environment variables and orchestrates the
    audit process: crawling, analysis, and report generation.

    Environment Variables:
        LF_DATA_DIR: Directory containing landing pages (default: ./landing_pages)
        LF_OUTPUT_DIR: Directory for generated reports (default: ./reports)
        LF_MIN_CONFIDENCE: Minimum confidence threshold for issues (default: 0.7)
    """
    # Read environment variables with defaults
    data_dir = os.getenv("LF_DATA_DIR", "./landing_pages")
    output_dir = os.getenv("LF_OUTPUT_DIR", "./reports")
    min_confidence = float(os.getenv("LF_MIN_CONFIDENCE", "0.7"))

    print("LandingFlow Audit - Initializing...")
    print(f"Data directory: {data_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Minimum confidence: {min_confidence}")
    print()

    # Initialize PageCrawler and crawl the data directory
    print("Step 1: Crawling landing pages...")
    crawler = PageCrawler(data_dir)
    crawl_data = crawler.crawl()

    # Display crawl results
    print(f"Pages discovered: {len(crawl_data['pages'])}")
    print(f"Anchors found: {len(crawl_data['anchors'])}")
    print(f"Forms found: {len(crawl_data['forms'])}")
    print(f"CTAs found: {len(crawl_data['ctas'])}")
    print()

    # Show details if data was found
    if crawl_data['pages']:
        print("Discovered pages:")
        for page in crawl_data['pages']:
            print(f"  - {page}")
        print()

    # Step 2: Analyze navigation flow
    print("Step 2: Analyzing navigation flow...")
    analyzer = NavigationAnalyzer(min_confidence)
    issues = analyzer.analyze(crawl_data)
    print(f"Navigation issues found: {len(issues)}")
    for issue in issues:
        print(f"  [{issue.severity}/10] {issue.issue_type}: {issue.description}")
    print()

    # Future: Initialize ReportGenerator
    # Future: Execute report generation workflow

    sys.exit(0)


if __name__ == "__main__":
    main()

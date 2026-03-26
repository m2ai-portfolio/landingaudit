"""LandingFlow Audit - Main entry point for the SaaS landing page analysis tool."""

import os
import sys
from landingflow_audit.core.crawler import PageCrawler
from landingflow_audit.core.navigator import NavigationAnalyzer
from landingflow_audit.core.reporter import ReportGenerator
from landingflow_audit.data.models import AuditResult


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
    nav_issues = analyzer.analyze(crawl_data)
    print(f"Navigation issues found: {len(nav_issues)}")
    for issue in nav_issues:
        print(f"  [{issue.severity}/10] {issue.issue_type}: {issue.description}")
    print()

    # Step 3: Conversion analysis
    reporter = ReportGenerator(output_dir)
    print("Step 3: Analyzing conversion issues...")
    conversion_issues = reporter.analyze_conversion_issues(crawl_data)
    print(f"Conversion issues found: {len(conversion_issues)}")
    for issue in conversion_issues:
        print(f"  [{issue.severity}/10] {issue.issue_type}: {issue.description}")
    print()

    # Combine all issues
    all_issues = nav_issues + conversion_issues

    # Create AuditResult
    result = AuditResult(
        audited_pages=crawl_data['pages'],
        issues=all_issues,
        summary={
            "total_pages": len(crawl_data['pages']),
            "total_issues": len(all_issues),
            "critical_issues": len([i for i in all_issues if i.severity >= 7]),
            "navigation_issues": len(nav_issues),
            "conversion_issues": len(conversion_issues)
        }
    )

    # Step 4: Generate reports
    print("Step 4: Generating reports...")
    reporter.generate(result)
    print(f"Reports saved to: {output_dir}")
    print(f"  - audit_report.csv")
    print(f"  - audit_report.json")
    print()

    # Summary
    print(f"=== Audit Summary ===")
    print(f"Pages audited: {result.summary['total_pages']}")
    print(f"Total issues: {result.summary['total_issues']}")
    print(f"Critical issues: {result.summary['critical_issues']}")

    sys.exit(0)


if __name__ == "__main__":
    main()

"""ReportGenerator module for creating audit reports."""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

from landingflow_audit.data.models import AuditResult, Issue


class ReportGenerator:
    """Generates formatted audit reports from analysis results.

    The ReportGenerator takes AuditResult data and produces human-readable
    reports in various formats (text, JSON, etc.). Reports are saved to
    the specified output directory.
    """

    def __init__(self, output_dir: str = "./reports"):
        """Initialize the ReportGenerator with an output directory.

        Args:
            output_dir: Path to the directory where reports will be saved.
        """
        self.output_dir = Path(output_dir)

    def analyze_conversion_issues(self, crawl_data: dict) -> List[Issue]:
        """Analyze forms and CTAs for conversion issues.

        Args:
            crawl_data: Dictionary containing pages, anchors, forms, and ctas.

        Returns:
            List of Issue objects with severity >= 3.
        """
        issues = []
        issues.extend(self._check_form_fields(crawl_data))
        issues.extend(self._check_cta_prominence(crawl_data))
        # Filter by severity >= 3
        return [i for i in issues if i.severity >= 3]

    def generate(self, result: AuditResult) -> None:
        """Generate and save audit reports from analysis results.

        Args:
            result: AuditResult object containing the complete audit data.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._generate_csv(result)
        self._generate_json(result)

    def _check_form_fields(self, crawl_data: dict) -> List[Issue]:
        """Check forms for conversion issues.

        Args:
            crawl_data: Dictionary containing forms data.

        Returns:
            List of Issue objects related to form fields.
        """
        issues = []
        forms = crawl_data.get("forms", [])

        for form in forms:
            source_page = form.get("source_page", "unknown")
            inputs = form.get("inputs", [])

            # Count total inputs (excluding submit buttons)
            input_count = len([i for i in inputs if i.get("type", "text") not in ["submit", "button"]])

            # Check for missing required attribute on email/password fields
            for input_field in inputs:
                input_type = input_field.get("type", "text")
                input_name = input_field.get("name", "")
                is_required = input_field.get("required", False)

                # Missing required attribute on email/password fields → severity 7
                if input_type in ["email", "password"] or "email" in input_name.lower() or "password" in input_name.lower():
                    if not is_required:
                        issues.append(Issue(
                            page_path=source_page,
                            issue_type="missing_required_attribute",
                            description=f"Critical form field (type={input_type}, name={input_name}) is missing 'required' attribute",
                            severity=7,
                            recommendation="Add 'required' attribute to email and password fields to ensure data collection"
                        ))

                # Incorrect input type (using text for email) → severity 6
                if "email" in input_name.lower() and input_type == "text":
                    issues.append(Issue(
                        page_path=source_page,
                        issue_type="incorrect_input_type",
                        description=f"Email field '{input_name}' uses type='text' instead of type='email'",
                        severity=6,
                        recommendation="Use type='email' for email inputs to enable browser validation and mobile keyboard optimization"
                    ))

                # Similarly for password fields
                if "password" in input_name.lower() and input_type == "text":
                    issues.append(Issue(
                        page_path=source_page,
                        issue_type="incorrect_input_type",
                        description=f"Password field '{input_name}' uses type='text' instead of type='password'",
                        severity=6,
                        recommendation="Use type='password' for password inputs to ensure secure input masking"
                    ))

            # Forms with too many fields (>5 inputs) → severity 4
            if input_count > 5:
                issues.append(Issue(
                    page_path=source_page,
                    issue_type="excessive_form_fields",
                    description=f"Form has {input_count} input fields, which may reduce conversion rates",
                    severity=4,
                    recommendation="Reduce form fields to 5 or fewer to improve conversion. Consider multi-step forms or progressive profiling"
                ))

            # Forms without submit button text → severity 5
            # Check if there's any submit button in inputs
            submit_buttons = [i for i in inputs if i.get("type", "text") in ["submit", "button"]]
            if not submit_buttons and input_count > 0:
                # No submit button found in inputs (might be a separate button element)
                # This is checked via the button element during parsing
                # For now, we'll check if there are inputs but the form seems incomplete
                pass  # This would require additional parsing logic

        return issues

    def _check_cta_prominence(self, crawl_data: dict) -> List[Issue]:
        """Check CTAs for prominence issues.

        Args:
            crawl_data: Dictionary containing ctas data.

        Returns:
            List of Issue objects related to CTA prominence.
        """
        issues = []
        ctas = crawl_data.get("ctas", [])

        # Group CTAs by page
        ctas_by_page = {}
        for cta in ctas:
            source_page = cta.get("source_page", "unknown")
            if source_page not in ctas_by_page:
                ctas_by_page[source_page] = []
            ctas_by_page[source_page].append(cta)

        # Check each page for CTA issues
        for page_path, page_ctas in ctas_by_page.items():
            # Pages with multiple competing CTAs → severity 4
            if len(page_ctas) > 2:
                cta_texts = [c.get("text", "") for c in page_ctas]
                issues.append(Issue(
                    page_path=page_path,
                    issue_type="multiple_competing_ctas",
                    description=f"Page has {len(page_ctas)} CTAs which may dilute conversion focus: {', '.join(cta_texts[:3])}",
                    severity=4,
                    recommendation="Reduce to 1-2 primary CTAs per page to improve conversion clarity and user decision-making"
                ))

            # CTA text that's too generic → severity 5
            generic_patterns = ["click here", "submit", "click", "here"]
            for cta in page_ctas:
                cta_text = cta.get("text", "").lower()
                if cta_text in generic_patterns:
                    issues.append(Issue(
                        page_path=page_path,
                        issue_type="generic_cta_text",
                        description=f"CTA uses generic text: '{cta.get('text', '')}'",
                        severity=5,
                        recommendation="Use action-oriented, value-driven CTA text (e.g., 'Start Free Trial', 'Get Your Demo') to improve conversion"
                    ))

        return issues

    def _generate_csv(self, result: AuditResult) -> None:
        """Generate CSV report (RFC 4180 compliant).

        Args:
            result: AuditResult object containing the complete audit data.
        """
        csv_path = self.output_dir / "audit_report.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["page_path", "issue_type", "severity", "description", "recommendation"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)

            writer.writeheader()

            for issue in result.issues:
                writer.writerow({
                    "page_path": issue.page_path,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommendation": issue.recommendation
                })

    def _generate_json(self, result: AuditResult) -> None:
        """Generate JSON report (RFC 8259 compliant).

        Args:
            result: AuditResult object containing the complete audit data.
        """
        json_path = self.output_dir / "audit_report.json"

        # Build the report structure
        report = {
            "audit_date": datetime.now().isoformat(),
            "total_pages": result.summary.get("total_pages", len(result.audited_pages)),
            "total_issues": result.summary.get("total_issues", len(result.issues)),
            "critical_issues": result.summary.get("critical_issues", len([i for i in result.issues if i.severity >= 7])),
            "issues": [
                {
                    "page_path": issue.page_path,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommendation": issue.recommendation
                }
                for issue in result.issues
            ],
            "summary": result.summary
        }

        with open(json_path, "w", encoding="utf-8") as jsonfile:
            json.dump(report, jsonfile, indent=2, ensure_ascii=False)

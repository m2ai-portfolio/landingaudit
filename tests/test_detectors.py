"""Tests that run the real detectors against the tests/fixtures HTML set.

Fixture layout (tests/fixtures/):
  - index.html   links to pricing.html (in-set) and /get-started (external, ignored by crawl)
  - pricing.html links to /signup (external, ignored by crawl)
  - orphan.html  has zero inbound links from other fixture pages (should be
                 flagged as an orphaned page) and contains a form with an
                 email/password field missing the 'required' attribute plus
                 an email field using type="text" instead of type="email"
                 (should be flagged by the conversion-issue checks).
"""

import unittest
from pathlib import Path

from landingaudit.core.crawler import PageCrawler
from landingaudit.core.navigator import NavigationAnalyzer
from landingaudit.core.reporter import ReportGenerator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.crawl_data = PageCrawler(FIXTURES_DIR).crawl()

    def test_crawler_discovers_all_fixture_pages(self):
        self.assertEqual(
            set(self.crawl_data["pages"]),
            {"index.html", "pricing.html", "orphan.html"},
        )

    def test_orphan_page_is_flagged(self):
        analyzer = NavigationAnalyzer(min_confidence=0.0)
        issues = analyzer.analyze(self.crawl_data)
        orphan_issues = [
            i for i in issues
            if i.issue_type == "orphaned_page" and i.page_path == "orphan.html"
        ]
        self.assertEqual(
            len(orphan_issues), 1,
            "orphan.html has no inbound links and should be detected as orphaned",
        )

    def test_index_page_is_not_flagged_as_orphan(self):
        analyzer = NavigationAnalyzer(min_confidence=0.0)
        issues = analyzer.analyze(self.crawl_data)
        index_orphans = [
            i for i in issues
            if i.issue_type == "orphaned_page" and i.page_path == "index.html"
        ]
        self.assertEqual(len(index_orphans), 0, "index.html is the entry point and is exempt")

    def test_bad_form_missing_required_is_flagged(self):
        reporter = ReportGenerator(output_dir="/tmp/landingaudit-test-reports")
        issues = reporter.analyze_conversion_issues(self.crawl_data)
        missing_required = [
            i for i in issues
            if i.issue_type == "missing_required_attribute" and i.page_path == "orphan.html"
        ]
        # orphan.html's form has two critical fields (user_email, password)
        # neither of which carries the 'required' attribute.
        self.assertEqual(len(missing_required), 2)

    def test_bad_form_incorrect_input_type_is_flagged(self):
        reporter = ReportGenerator(output_dir="/tmp/landingaudit-test-reports")
        issues = reporter.analyze_conversion_issues(self.crawl_data)
        incorrect_type = [
            i for i in issues
            if i.issue_type == "incorrect_input_type" and i.page_path == "orphan.html"
        ]
        # user_email uses type="text" instead of type="email", and the
        # password field uses type="text" instead of type="password".
        self.assertEqual(len(incorrect_type), 2)

    def test_min_confidence_filters_lower_severity_navigation_issues(self):
        # orphaned_page has severity 7 -> confidence 0.7. A threshold of 0.8
        # should filter it out; a threshold of 0.7 should keep it.
        lenient = NavigationAnalyzer(min_confidence=0.7).analyze(self.crawl_data)
        strict = NavigationAnalyzer(min_confidence=0.8).analyze(self.crawl_data)

        lenient_orphans = [i for i in lenient if i.issue_type == "orphaned_page"]
        strict_orphans = [i for i in strict if i.issue_type == "orphaned_page"]

        self.assertEqual(len(lenient_orphans), 1)
        self.assertEqual(len(strict_orphans), 0)


if __name__ == "__main__":
    unittest.main()

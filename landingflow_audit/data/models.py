from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Issue:
    """Represents a single actionable finding from the audit."""
    page_path: str
    issue_type: str  # e.g., "broken_navigation", "missing_cta"
    description: str
    severity: int  # 1-10, where 10 is critical
    recommendation: str


@dataclass
class AuditResult:
    """Container for the complete analysis of a landing page set."""
    audited_pages: List[str]
    issues: List[Issue]
    summary: dict  # e.g., {"total_pages": 42, "critical_issues": 5}

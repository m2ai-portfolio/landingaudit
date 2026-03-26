"""NavigationAnalyzer module for analyzing navigation patterns and issues."""

from typing import List, Dict, Set
from landingflow_audit.data.models import Issue


class NavigationAnalyzer:
    """Analyzes navigation patterns and identifies navigation-related issues.

    The NavigationAnalyzer examines crawled page data to detect broken links,
    missing navigation elements, inconsistent navigation patterns, and other
    navigation-related problems in the landing page set.
    """

    def __init__(self, min_confidence: float = 0.7):
        """Initialize the NavigationAnalyzer.

        Args:
            min_confidence: Minimum confidence threshold for reporting issues (0.0-1.0).
        """
        self.min_confidence = min_confidence

    def analyze(self, crawl_data: dict) -> List[Issue]:
        """Analyze crawled data for navigation issues.

        Args:
            crawl_data: Dictionary of crawled page data from PageCrawler.

        Returns:
            List[Issue]: List of navigation-related issues found during analysis.
        """
        issues = []

        # Build graph from anchors
        graph = self._build_graph(crawl_data)

        # Run detections
        issues.extend(self._detect_orphaned_pages(crawl_data, graph))
        issues.extend(self._detect_circular_navigation(graph))
        issues.extend(self._detect_missing_ctas(crawl_data))
        issues.extend(self._detect_redirect_chains(graph, crawl_data))

        return issues

    def _build_graph(self, crawl_data: dict) -> Dict[str, List[str]]:
        """Build directed graph: {source: [destinations]}.

        Args:
            crawl_data: Dictionary with 'anchors' list.

        Returns:
            Dictionary mapping source pages to list of destination hrefs.
        """
        graph = {}

        # Initialize all pages as nodes (even if no outbound links)
        for page in crawl_data['pages']:
            if page not in graph:
                graph[page] = []

        # Add edges from anchors
        for anchor in crawl_data['anchors']:
            source = anchor['source_page']
            dest = anchor['href']

            if source not in graph:
                graph[source] = []

            graph[source].append(dest)

        return graph

    def _detect_orphaned_pages(self, crawl_data: dict, graph: Dict[str, List[str]]) -> List[Issue]:
        """Find pages with zero inbound links.

        Args:
            crawl_data: Dictionary with 'pages' list.
            graph: Directed graph of page links.

        Returns:
            List of Issue objects for orphaned pages.
        """
        issues = []

        # Build inbound links mapping
        inbound = {}
        for page in crawl_data['pages']:
            inbound[page] = []

        for source, destinations in graph.items():
            for dest in destinations:
                if dest in inbound:
                    inbound[dest].append(source)

        # Detect orphans (pages with zero inbound links)
        # Exception: index.html is the entry point, so it's not orphaned
        for page in crawl_data['pages']:
            if len(inbound[page]) == 0 and page != 'index.html':
                issues.append(Issue(
                    page_path=page,
                    issue_type='orphaned_page',
                    description=f'Page "{page}" has no inbound links from other pages',
                    severity=7,
                    recommendation='Add navigation links from other pages to improve discoverability'
                ))

        return issues

    def _detect_circular_navigation(self, graph: Dict[str, List[str]]) -> List[Issue]:
        """Find cycles longer than 2 nodes using DFS.

        Args:
            graph: Directed graph of page links.

        Returns:
            List of Issue objects for circular navigation patterns.
        """
        issues = []
        visited_global = set()

        def dfs_detect_cycle(node: str, path: List[str], visited_path: Set[str]) -> bool:
            """DFS to detect cycles of length > 2."""
            if node in visited_path:
                # Found a cycle - check if it's longer than 2 nodes
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                if len(cycle) >= 3:
                    # Create issue for this cycle
                    cycle_description = ' -> '.join(cycle) + f' -> {node}'
                    issues.append(Issue(
                        page_path=node,
                        issue_type='circular_navigation',
                        description=f'Circular navigation detected: {cycle_description}',
                        severity=6,
                        recommendation='Break circular navigation patterns to improve user flow'
                    ))
                    return True
                return False

            if node not in graph:
                return False

            visited_path.add(node)
            path.append(node)

            for neighbor in graph[node]:
                dfs_detect_cycle(neighbor, path, visited_path)

            path.pop()
            visited_path.remove(node)
            return False

        # Run DFS from each unvisited node
        for start_node in graph:
            if start_node not in visited_global:
                visited_global.add(start_node)
                dfs_detect_cycle(start_node, [], set())

        return issues

    def _detect_missing_ctas(self, crawl_data: dict) -> List[Issue]:
        """Flag pages without any CTA.

        Args:
            crawl_data: Dictionary with 'pages' and 'ctas' lists.

        Returns:
            List of Issue objects for pages missing CTAs.
        """
        issues = []

        # Build set of pages that have CTAs
        pages_with_ctas = set()
        for cta in crawl_data['ctas']:
            pages_with_ctas.add(cta['source_page'])

        # Check each page
        for page in crawl_data['pages']:
            if page not in pages_with_ctas:
                issues.append(Issue(
                    page_path=page,
                    issue_type='missing_cta',
                    description=f'Page "{page}" has no call-to-action elements',
                    severity=8,
                    recommendation='Add clear call-to-action to guide user conversion'
                ))

        return issues

    def _detect_redirect_chains(self, graph: Dict[str, List[str]], crawl_data: dict) -> List[Issue]:
        """Find chains where depth exceeds 3 hops.

        A redirect chain is a path through pages without CTAs or forms.

        Args:
            graph: Directed graph of page links.
            crawl_data: Dictionary with 'ctas' and 'forms' lists.

        Returns:
            List of Issue objects for excessive redirect chains.
        """
        issues = []

        # Build sets of pages with CTAs or forms (these are "endpoint" pages)
        endpoint_pages = set()
        for cta in crawl_data['ctas']:
            endpoint_pages.add(cta['source_page'])
        for form in crawl_data['forms']:
            endpoint_pages.add(form['source_page'])

        # For each page, follow links and track depth to endpoints
        def find_chain_depth(start_page: str, visited: Set[str] = None, depth: int = 0) -> int:
            """Find longest chain from start_page without reaching an endpoint."""
            if visited is None:
                visited = set()

            if start_page in visited:
                return depth

            if start_page in endpoint_pages:
                return depth

            if start_page not in graph or not graph[start_page]:
                # Dead end
                return depth

            visited.add(start_page)
            max_depth = depth

            for dest in graph[start_page]:
                chain_depth = find_chain_depth(dest, visited.copy(), depth + 1)
                max_depth = max(max_depth, chain_depth)

            return max_depth

        # Check each page
        for page in graph:
            if page not in endpoint_pages:
                chain_depth = find_chain_depth(page)
                if chain_depth > 3:
                    issues.append(Issue(
                        page_path=page,
                        issue_type='redirect_chain',
                        description=f'Page "{page}" leads to excessive redirect chain (depth: {chain_depth})',
                        severity=5,
                        recommendation='Reduce navigation depth or add CTAs/forms to intermediate pages'
                    ))

        return issues

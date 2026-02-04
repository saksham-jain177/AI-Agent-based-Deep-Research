"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_sources():
    """Sample source data for testing."""
    return [
        {
            "title": "Climate Change Effects on Agriculture",
            "url": "https://example.com/climate",
            "authors": ["John Smith", "Jane Doe"],
            "publication_date": "2024-01-15",
        },
        {
            "title": "Machine Learning in Healthcare",
            "url": "https://example.org/ml-health",
            "authors": ["Alice Johnson"],
            "publication_date": "2023-06-20",
        },
        {
            "title": "Quantum Computing Advances",
            "url": "https://research.edu/quantum",
        },
    ]


@pytest.fixture
def sample_query():
    """Sample research query."""
    return "effects of climate change on global agriculture production"

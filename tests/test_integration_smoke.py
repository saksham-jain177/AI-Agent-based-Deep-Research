"""
Integration smoke test - validates end-to-end pipeline.

This test covers the glue logic between components without requiring
Streamlit runtime or external API calls.
"""

import pytest
from datetime import date


@pytest.mark.smoke
class TestIntegrationSmoke:
    """Smoke tests for end-to-end pipeline validation."""
    
    def test_query_to_citations_pipeline(self, sample_sources):
        """
        Smoke test: sources → citations → all export formats.
        
        This validates the integration between:
        - Source parsing
        - Citation formatting
        - All export format generation
        """
        from citation_formatter import Source, CitationFormatter
        
        # Parse sources (simulating research agent output)
        sources = [Source.from_dict(s) for s in sample_sources]
        assert len(sources) == len(sample_sources)
        
        # Create formatter
        formatter = CitationFormatter(sources)
        
        # Verify all export formats work
        apa = formatter.format_apa()
        assert apa and len(apa) > 0
        
        mla = formatter.format_mla()
        assert mla and len(mla) > 0
        
        ieee = formatter.format_ieee()
        assert ieee and len(ieee) > 0
        
        bibtex = formatter.format_bibtex()
        assert bibtex and len(bibtex) > 0
    
    def test_bibtex_roundtrip_validation(self, sample_sources):
        """
        Validate BibTeX can be re-parsed after generation.
        
        This catches malformed output that would break user workflows.
        """
        try:
            import bibtexparser
        except ImportError:
            pytest.skip("bibtexparser not installed")
        
        from citation_formatter import Source, CitationFormatter
        
        sources = [Source.from_dict(s) for s in sample_sources]
        formatter = CitationFormatter(sources)
        
        bibtex = formatter.format_bibtex()
        parsed = bibtexparser.loads(bibtex)
        
        # All entries should survive round-trip
        assert len(parsed.entries) == len(sources)
        
        # Each entry should have required fields
        for entry in parsed.entries:
            assert "title" in entry
            assert "url" in entry
    
    def test_cost_estimation_integration(self, sample_query):
        """
        Test cost estimation doesn't crash with real-world inputs.
        """
        from cost_estimator import estimate_research_cost
        
        # Shallow research
        shallow = estimate_research_cost(
            query=sample_query,
            deep_research=False,
            target_word_count=1000
        )
        assert shallow["tokens"]["avg"] > 0
        assert shallow["cost_usd"]["avg"] >= 0
        
        # Deep research
        deep = estimate_research_cost(
            query=sample_query,
            deep_research=True,
            target_word_count=3000
        )
        assert deep["tokens"]["avg"] > shallow["tokens"]["avg"]
    
    def test_source_from_research_output_format(self):
        """
        Test Source handles format from research_agent.py output.
        
        This validates compatibility with existing research output.
        """
        from citation_formatter import Source
        
        # Format from research_agent.py
        research_output = {
            "title": "Example Research Article",
            "content": "This is the article content...",
            "url": "https://example.com/article"
        }
        
        # Should not crash, should extract available fields
        source = Source.from_dict(research_output)
        assert source.title == "Example Research Article"
        assert source.url == "https://example.com/article"
        assert source.authors is None  # Not in research output

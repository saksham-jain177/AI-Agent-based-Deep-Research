"""Tests for citation_formatter module."""

import pytest
from datetime import date
from citation_formatter import Source, CitationFormatter, format_sources_as_citations


class TestSource:
    """Tests for Source dataclass."""
    
    def test_source_creation(self):
        """Source should be creatable with minimal fields."""
        src = Source(title="Test Article", url="https://example.com")
        assert src.title == "Test Article"
        assert src.url == "https://example.com"
        assert src.access_date == date.today()
    
    def test_source_normalizes_title(self):
        """Source should normalize whitespace in title."""
        src = Source(title="  Test Article  ", url="https://example.com")
        assert src.title == "Test Article"
    
    def test_source_handles_empty_title(self):
        """Source should default empty title to 'Untitled'."""
        src = Source(title="   ", url="https://example.com")
        assert src.title == "Untitled"
    
    def test_bibtex_key_generation(self):
        """BibTeX key should be generated from author and year."""
        src = Source(
            title="Test Article",
            url="https://example.com",
            authors=["John Smith"],
            publication_date=date(2024, 1, 15)
        )
        key = src.to_bibtex_key()
        assert "smith" in key
        assert "2024" in key
    
    def test_bibtex_key_without_author(self):
        """BibTeX key should handle missing author."""
        src = Source(title="Test Article", url="https://example.com")
        key = src.to_bibtex_key()
        assert "unknown" in key
    
    def test_from_dict(self, sample_sources):
        """Source should be creatable from dictionary."""
        src = Source.from_dict(sample_sources[0])
        assert src.title == "Climate Change Effects on Agriculture"
        assert src.url == "https://example.com/climate"
        assert src.authors == ["John Smith", "Jane Doe"]


class TestCitationFormatter:
    """Tests for CitationFormatter class."""
    
    def test_deterministic_ordering(self, sample_sources):
        """Output should be deterministic regardless of input order."""
        sources1 = [Source.from_dict(s) for s in sample_sources]
        sources2 = [Source.from_dict(s) for s in reversed(sample_sources)]
        
        formatter1 = CitationFormatter(sources1)
        formatter2 = CitationFormatter(sources2)
        
        # Both should produce identical output
        assert formatter1.format_apa() == formatter2.format_apa()
        assert formatter1.format_mla() == formatter2.format_mla()
        assert formatter1.format_ieee() == formatter2.format_ieee()
    
    def test_format_apa(self, sample_sources):
        """APA format should include required elements."""
        sources = [Source.from_dict(s) for s in sample_sources]
        formatter = CitationFormatter(sources)
        result = formatter.format_apa()
        
        assert "Climate Change" in result
        assert "https://" in result
        assert "[1]" in result
    
    def test_format_mla(self, sample_sources):
        """MLA format should include required elements."""
        sources = [Source.from_dict(s) for s in sample_sources]
        formatter = CitationFormatter(sources)
        result = formatter.format_mla()
        
        assert "Climate Change" in result
        assert result.count('"') >= 2  # Titles in quotes
    
    def test_format_ieee(self, sample_sources):
        """IEEE format should include required elements."""
        sources = [Source.from_dict(s) for s in sample_sources]
        formatter = CitationFormatter(sources)
        result = formatter.format_ieee()
        
        assert "[1]" in result
        assert "Available:" in result or "https://" in result


class TestBibTeX:
    """Tests for BibTeX generation and validation."""
    
    def test_bibtex_generation(self, sample_sources):
        """BibTeX should be generated for all sources."""
        sources = [Source.from_dict(s) for s in sample_sources]
        formatter = CitationFormatter(sources)
        result = formatter.format_bibtex()
        
        assert "@misc{" in result
        assert "title = {" in result
        assert "url = {" in result
    
    def test_bibtex_roundtrip(self, sample_sources):
        """BibTeX should be valid (parseable by bibtexparser)."""
        try:
            import bibtexparser
        except ImportError:
            pytest.skip("bibtexparser not installed")
        
        sources = [Source.from_dict(s) for s in sample_sources]
        formatter = CitationFormatter(sources)
        bibtex = formatter.format_bibtex()
        
        parsed = bibtexparser.loads(bibtex)
        assert len(parsed.entries) == len(sources)
    
    def test_no_duplicate_keys(self, sample_sources):
        """BibTeX keys should be unique."""
        # Create sources with same author/year to test collision handling
        sources = [
            Source(title="Article One", url="https://a.com", authors=["John Smith"], publication_date=date(2024, 1, 1)),
            Source(title="Article Two", url="https://b.com", authors=["John Smith"], publication_date=date(2024, 1, 1)),
        ]
        formatter = CitationFormatter(sources)
        bibtex = formatter.format_bibtex()
        
        # Extract keys
        import re
        keys = re.findall(r"@misc\{([^,]+),", bibtex)
        assert len(keys) == len(set(keys)), "Duplicate keys found"
    
    def test_special_characters(self):
        """Special characters should be handled."""
        sources = [
            Source(
                title="Analysis & Review: The 100% Solution",
                url="https://example.com",
                authors=["José García"]
            )
        ]
        formatter = CitationFormatter(sources)
        bibtex = formatter.format_bibtex()
        
        # Should not crash; special chars should be escaped or preserved
        assert "title = {" in bibtex
    
    def test_deterministic_bibtex(self, sample_sources):
        """BibTeX output should be identical across multiple runs."""
        sources = [Source.from_dict(s) for s in sample_sources]
        
        formatter1 = CitationFormatter(sources)
        formatter2 = CitationFormatter(sources)
        
        assert formatter1.format_bibtex() == formatter2.format_bibtex()


class TestConvenienceFunction:
    """Tests for format_sources_as_citations function."""
    
    def test_format_apa_style(self, sample_sources):
        """Should format as APA when specified."""
        result = format_sources_as_citations(sample_sources, style="apa")
        assert "[1]" in result
    
    def test_format_bibtex_style(self, sample_sources):
        """Should format as BibTeX when specified."""
        result = format_sources_as_citations(sample_sources, style="bibtex")
        assert "@misc{" in result
    
    def test_default_to_apa(self, sample_sources):
        """Unknown style should default to APA."""
        result = format_sources_as_citations(sample_sources, style="unknown")
        assert "[1]" in result

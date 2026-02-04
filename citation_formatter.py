"""
Citation Formatter Module - Unified Citation Engine with Validation

Provides deterministic citation formatting for APA, MLA, IEEE, and BibTeX.
Uses bibtexparser for BibTeX generation and validation.
"""

import re
import hashlib
from typing import Optional, List
from datetime import date
from dataclasses import dataclass, field


@dataclass
class Source:
    """
    Validated source for citation generation.
    
    All sources are normalized and validated on creation.
    """
    title: str
    url: str
    authors: Optional[List[str]] = None
    publication_date: Optional[date] = None
    publisher: Optional[str] = None
    access_date: date = field(default_factory=date.today)
    
    def __post_init__(self):
        # Normalize title
        self.title = self.title.strip()
        if not self.title:
            self.title = "Untitled"
        
        # Normalize authors
        if self.authors:
            self.authors = [a.strip() for a in self.authors if a.strip()]
        
        # Normalize URL
        self.url = self.url.strip()
    
    def to_bibtex_key(self) -> str:
        """Generate collision-resistant BibTeX key."""
        # Format: author_year_hash
        author_part = "unknown"
        if self.authors and len(self.authors) > 0:
            # Take first author's last name
            first_author = self.authors[0]
            parts = first_author.split()
            if parts:
                author_part = re.sub(r'[^a-zA-Z]', '', parts[-1].lower())
        
        year_part = "nd"  # no date
        if self.publication_date:
            year_part = str(self.publication_date.year)
        
        # Add hash for uniqueness (first 6 chars)
        content_hash = hashlib.md5(
            f"{self.title}{self.url}".encode()
        ).hexdigest()[:6]
        
        return f"{author_part}{year_part}_{content_hash}"
    
    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        """Create Source from dictionary (e.g., from research results)."""
        pub_date = None
        if data.get("publication_date"):
            try:
                if isinstance(data["publication_date"], date):
                    pub_date = data["publication_date"]
                elif isinstance(data["publication_date"], str):
                    # Try to parse ISO format
                    pub_date = date.fromisoformat(data["publication_date"][:10])
            except (ValueError, TypeError):
                pass
        
        return cls(
            title=data.get("title", "Untitled"),
            url=data.get("url", ""),
            authors=data.get("authors"),
            publication_date=pub_date,
            publisher=data.get("publisher"),
        )


class CitationFormatter:
    """
    Unified citation formatting with deterministic ordering and validation.
    
    Sources are sorted by title for deterministic output across runs.
    BibTeX entries are validated via round-trip parsing.
    """
    
    def __init__(self, sources: List[Source]):
        # Sort by title for deterministic output (critical for clean git diffs)
        self.sources = sorted(sources, key=lambda s: s.title.lower())
    
    def _escape_bibtex(self, text: str) -> str:
        """Escape special characters for BibTeX."""
        if not text:
            return ""
        # Basic escaping for common special chars
        # Full Unicode escaping is deferred per scope control
        replacements = [
            ("&", r"\&"),
            ("%", r"\%"),
            ("_", r"\_"),
            ("#", r"\#"),
            ("{", r"\{"),
            ("}", r"\}"),
        ]
        result = text
        for old, new in replacements:
            result = result.replace(old, new)
        return result
    
    def _format_authors_apa(self, authors: Optional[List[str]]) -> str:
        """Format authors for APA style."""
        if not authors or len(authors) == 0:
            return ""
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def _format_authors_mla(self, authors: Optional[List[str]]) -> str:
        """Format authors for MLA style."""
        if not authors or len(authors) == 0:
            return ""
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]}, and {authors[1]}"
        else:
            return f"{authors[0]}, et al."
    
    def _format_authors_ieee(self, authors: Optional[List[str]]) -> str:
        """Format authors for IEEE style."""
        if not authors or len(authors) == 0:
            return ""
        
        if len(authors) <= 3:
            return ", ".join(authors)
        else:
            return f"{authors[0]} et al."
    
    def format_apa(self) -> str:
        """
        Format citations in APA style.
        
        Format: Author(s). (Year). Title. Publisher. URL
        """
        citations = []
        for i, src in enumerate(self.sources, 1):
            parts = []
            
            # Authors
            if src.authors:
                parts.append(self._format_authors_apa(src.authors))
            
            # Year
            if src.publication_date:
                parts.append(f"({src.publication_date.year}).")
            else:
                parts.append("(n.d.).")
            
            # Title (italicized in actual rendering)
            parts.append(f"{src.title}.")
            
            # Publisher
            if src.publisher:
                parts.append(f"{src.publisher}.")
            
            # URL
            if src.url:
                parts.append(f"Retrieved from {src.url}")
            
            citations.append(f"[{i}] " + " ".join(parts))
        
        return "\n\n".join(citations)
    
    def format_mla(self) -> str:
        """
        Format citations in MLA style.
        
        Format: Author(s). "Title." Publisher, Date. URL.
        """
        citations = []
        for i, src in enumerate(self.sources, 1):
            parts = []
            
            # Authors
            if src.authors:
                parts.append(f"{self._format_authors_mla(src.authors)}.")
            
            # Title (in quotes for articles)
            parts.append(f'"{src.title}."')
            
            # Publisher
            if src.publisher:
                parts.append(f"{src.publisher},")
            
            # Date
            if src.publication_date:
                parts.append(f"{src.publication_date.strftime('%d %b. %Y')}.")
            
            # URL
            if src.url:
                parts.append(src.url)
            
            citations.append(f"[{i}] " + " ".join(parts))
        
        return "\n\n".join(citations)
    
    def format_ieee(self) -> str:
        """
        Format citations in IEEE style.
        
        Format: [N] Author(s), "Title," Publisher, Date. [Online]. Available: URL
        """
        citations = []
        for i, src in enumerate(self.sources, 1):
            parts = []
            
            # Authors
            if src.authors:
                parts.append(f"{self._format_authors_ieee(src.authors)},")
            
            # Title (in quotes)
            parts.append(f'"{src.title},"')
            
            # Publisher
            if src.publisher:
                parts.append(f"{src.publisher},")
            
            # Date
            if src.publication_date:
                parts.append(f"{src.publication_date.year}.")
            
            # URL
            if src.url:
                parts.append(f"[Online]. Available: {src.url}")
            
            citations.append(f"[{i}] " + " ".join(parts))
        
        return "\n\n".join(citations)
    
    def format_bibtex(self) -> str:
        """
        Generate validated BibTeX entries.
        
        Uses bibtexparser for generation; validates via round-trip parsing.
        Entries are sorted by key for deterministic output.
        """
        try:
            from bibtexparser.bwriter import BibTexWriter
            from bibtexparser.bibdatabase import BibDatabase
            import bibtexparser
            
            db = BibDatabase()
            used_keys = set()
            
            for src in self.sources:
                key = src.to_bibtex_key()
                
                # Handle key collisions
                original_key = key
                counter = 1
                while key in used_keys:
                    key = f"{original_key}_{counter}"
                    counter += 1
                used_keys.add(key)
                
                entry = {
                    "ID": key,
                    "ENTRYTYPE": "misc",
                    "title": self._escape_bibtex(src.title),
                    "url": src.url,
                    "note": f"Accessed: {src.access_date.isoformat()}",
                }
                
                if src.authors:
                    entry["author"] = " and ".join(src.authors)
                
                if src.publication_date:
                    entry["year"] = str(src.publication_date.year)
                
                if src.publisher:
                    entry["publisher"] = self._escape_bibtex(src.publisher)
                
                db.entries.append(entry)
            
            # Sort entries by key for deterministic output
            db.entries = sorted(db.entries, key=lambda e: e.get("ID", ""))
            
            writer = BibTexWriter()
            bibtex_str = writer.write(db)
            
            # Validate by re-parsing (fail fast on malformed output)
            parsed = bibtexparser.loads(bibtex_str)
            if len(parsed.entries) != len(self.sources):
                raise ValueError(
                    f"BibTeX validation failed: expected {len(self.sources)} entries, "
                    f"got {len(parsed.entries)}"
                )
            
            return bibtex_str
            
        except ImportError:
            # Fallback: generate basic BibTeX without validation
            return self._format_bibtex_fallback()
    
    def _format_bibtex_fallback(self) -> str:
        """Fallback BibTeX generation without bibtexparser."""
        entries = []
        used_keys = set()
        
        for src in self.sources:
            key = src.to_bibtex_key()
            
            # Handle collisions
            original_key = key
            counter = 1
            while key in used_keys:
                key = f"{original_key}_{counter}"
                counter += 1
            used_keys.add(key)
            
            lines = [f"@misc{{{key},"]
            lines.append(f'  title = {{{self._escape_bibtex(src.title)}}},')
            
            if src.authors:
                lines.append(f'  author = {{{" and ".join(src.authors)}}},')
            
            if src.publication_date:
                lines.append(f'  year = {{{src.publication_date.year}}},')
            
            lines.append(f'  url = {{{src.url}}},')
            lines.append(f'  note = {{Accessed: {src.access_date.isoformat()}}}')
            lines.append("}")
            
            entries.append("\n".join(lines))
        
        # Sort for deterministic output
        entries.sort()
        return "\n\n".join(entries)


def format_sources_as_citations(
    sources: List[dict],
    style: str = "apa"
) -> str:
    """
    Convenience function to format source dictionaries as citations.
    
    Args:
        sources: List of source dictionaries with title, url, etc.
        style: Citation style - "apa", "mla", "ieee", or "bibtex"
    
    Returns:
        Formatted citation string
    """
    source_objects = [Source.from_dict(s) for s in sources]
    formatter = CitationFormatter(source_objects)
    
    style_lower = style.lower()
    if style_lower == "apa":
        return formatter.format_apa()
    elif style_lower == "mla":
        return formatter.format_mla()
    elif style_lower == "ieee":
        return formatter.format_ieee()
    elif style_lower == "bibtex":
        return formatter.format_bibtex()
    else:
        return formatter.format_apa()  # Default to APA

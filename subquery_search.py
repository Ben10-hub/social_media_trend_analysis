"""
Subquery Search Module - Advanced searching with filters, boolean operators, and faceting
"""
import pandas as pd
import re
from collections import Counter
from datetime import datetime, timezone, timedelta


class SubquerySearch:
    """Advanced search with boolean operators, filters, and faceting."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with a dataframe containing 'text' and optionally 'timestamp', 'platform'."""
        self.df = df.copy() if df is not None else pd.DataFrame()
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data for searching."""
        if "text" not in self.df.columns:
            return
        
        # Clean text for searching
        self.df["_search_text"] = self.df["text"].fillna("").astype(str).str.lower()
        
        # Parse timestamps
        if "timestamp" in self.df.columns:
            try:
                self.df["_timestamp_parsed"] = pd.to_datetime(self.df["timestamp"], errors="coerce")
            except:
                self.df["_timestamp_parsed"] = pd.NaT
    
    def _parse_query(self, query: str) -> dict:
        """Parse complex query with boolean operators."""
        query = (query or "").strip()
        
        must_have = []
        must_not = []
        should_have = []
        
        # Parse: term1 term2 (required), -term3 (excluded), |term4 (optional)
        tokens = query.split()
        
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            if token.startswith("-"):
                # Exclusion
                must_not.append(token[1:].lower())
            elif token.startswith("|"):
                # Optional
                should_have.append(token[1:].lower())
            else:
                # Required
                must_have.append(token.lower())
        
        return {
            "must_have": must_have,
            "must_not": must_not,
            "should_have": should_have,
        }
    
    def search(
        self,
        query: str,
        platform_filter: str = None,
        date_range: tuple = None,
        case_sensitive: bool = False,
    ) -> pd.DataFrame:
        """
        Search with complex query and optional filters.
        
        Args:
            query: Search query with boolean operators (e.g., "AI -hype |trend")
            platform_filter: Filter by platform (e.g., "reddit" or None for all)
            date_range: Tuple of (start_date, end_date) as strings
            case_sensitive: Case sensitivity
        
        Returns:
            Filtered dataframe of matching results
        """
        if self.df.empty:
            return pd.DataFrame()
        
        result = self.df.copy()
        
        # Parse query
        parsed = self._parse_query(query)
        
        # Apply text filters
        search_col = "text" if case_sensitive else "_search_text"
        
        # Must have all terms
        for term in parsed["must_have"]:
            result = result[result[search_col].str.contains(
                re.escape(term),
                regex=True,
                na=False,
                case=case_sensitive
            )]
        
        # Must not have these terms
        for term in parsed["must_not"]:
            result = result[~result[search_col].str.contains(
                re.escape(term),
                regex=True,
                na=False,
                case=case_sensitive
            )]
        
        # Should have (at least one, adds score but not required)
        # We track this but don't filter unless all must_have fail
        
        # Platform filter
        if platform_filter and "platform" in result.columns:
            result = result[result["platform"].str.lower() == platform_filter.lower()]
        
        # Date range filter
        if date_range and "_timestamp_parsed" in result.columns:
            try:
                start = pd.to_datetime(date_range[0], errors="coerce")
                end = pd.to_datetime(date_range[1], errors="coerce")
                if start:
                    result = result[result["_timestamp_parsed"] >= start]
                if end:
                    result = result[result["_timestamp_parsed"] <= end]
            except:
                pass
        
        # Score and sort by should_have terms and recency
        if len(parsed["should_have"]) > 0 or "_timestamp_parsed" in result.columns:
            result["_score"] = 0.0
            
            # Score for should_have terms
            for term in parsed["should_have"]:
                match = result[search_col].str.contains(
                    re.escape(term),
                    regex=True,
                    na=False,
                    case=case_sensitive
                )
                result.loc[match, "_score"] += 1.0
            
            # Boost recent posts
            if "_timestamp_parsed" in result.columns:
                now = pd.Timestamp.utcnow()
                result["_recency"] = (now - result["_timestamp_parsed"]).dt.total_seconds()
                result.loc[result["_recency"] <= 3600, "_score"] += 2.0  # Recent boost
            
            result = result.sort_values("_score", ascending=False, na_position="last")
            result = result.drop(columns=["_score"], errors="ignore")
        
        return result.drop(columns=["_recency"], errors="ignore")
    
    def faceted_search(self, query: str, facet_by: str = "platform") -> dict:
        """
        Search and group results by a facet (platform, sentiment, etc).
        
        Args:
            query: Search query
            facet_by: Column to group by (default: platform)
        
        Returns:
            Dict with facets and counts
        """
        results = self.search(query)
        
        if results.empty or facet_by not in results.columns:
            return {}
        
        facets = results.groupby(facet_by).size().to_dict()
        return facets
    
    def search_and_analyze(
        self,
        query: str,
        top_keywords: int = 10,
        platform_filter: str = None,
    ) -> dict:
        """
        Search and return analysis of results.
        
        Args:
            query: Search query
            top_keywords: How many top keywords to extract
            platform_filter: Optional platform filter
        
        Returns:
            Dict with search stats and insights
        """
        results = self.search(query, platform_filter=platform_filter)
        
        if results.empty:
            return {
                "total_matches": 0,
                "query": query,
                "platforms": [],
                "keywords": [],
                "sentiment": {},
                "results": pd.DataFrame(),
            }
        
        # Extract keywords
        keywords = self._extract_keywords(results, top_k=top_keywords)
        
        # Platform breakdown
        platforms = {}
        if "platform" in results.columns:
            platforms = results["platform"].value_counts().to_dict()
        
        # Sentiment breakdown
        sentiment = {}
        if "sentiment" in results.columns:
            sentiment = results["sentiment"].value_counts().to_dict()
        
        return {
            "total_matches": len(results),
            "query": query,
            "platforms": platforms,
            "keywords": keywords,
            "sentiment": sentiment,
            "results": results.head(100),  # Top 100 results
        }
    
    def _extract_keywords(self, df: pd.DataFrame, top_k: int = 10) -> list[str]:
        """Extract top keywords from search results."""
        try:
            from nltk.corpus import stopwords
            stop = set(stopwords.words("english"))
        except:
            stop = set()
        
        keywords = Counter()
        
        for text in df["text"].fillna("").astype(str):
            words = re.findall(r"\b[a-z]{3,}\b", text.lower())
            for word in words:
                if not stop or word not in stop:
                    keywords[word] += 1
        
        return [kw for kw, _ in keywords.most_common(top_k)]
    
    def trending_subqueries(self, df: pd.DataFrame = None) -> list[str]:
        """Generate suggested subqueries based on top issues."""
        search_df = df if df is not None else self.df
        
        if search_df.empty:
            return []
        
        keywords = self._extract_keywords(search_df, top_k=20)
        
        # Suggest subqueries
        suggestions = []
        for i in range(0, min(len(keywords), 10), 2):
            if i + 1 < len(keywords):
                suggestions.append(f"{keywords[i]} OR {keywords[i+1]}")
        
        return suggestions


def global_search_demo(df: pd.DataFrame) -> dict:
    """Demo function showing search capabilities."""
    search = SubquerySearch(df)
    
    results = {
        "ai_related": search.search_and_analyze("AI -hype"),
        "trending_keywords": search.search_and_analyze("trending"),
        "reddit_tech": search.search_and_analyze("technology", platform_filter="reddit"),
    }
    
    return results

import React, { useState, useEffect } from 'react';
import { Search, FileText, Wrench, Layers, Sparkles, Filter, ExternalLink, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function HistoricalSearch({ initialQuery = '', onSelectReport }) {
  const [query, setQuery] = useState(initialQuery || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const sampleQueries = [
    'severe mud loss in Demo-Barail',
    'stuck pipe and jar overpull in Kopili shale',
    'shallow gas kick drilling break Tipam',
    'casing cement channeling CBL squeeze',
  ];

  const handleSearch = (searchQuery) => {
    const q = searchQuery !== undefined ? searchQuery : query;
    if (!q || q.trim().length < 2) return;

    setLoading(true);
    setError(null);
    setHasSearched(true);

    api.searchHistorical(q.trim(), 8)
      .then((data) => {
        setResults(data?.results || []);
      })
      .catch((err) => {
        setError(err.message || 'Error executing semantic search.');
        setResults([]);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      handleSearch(initialQuery);
    }
  }, [initialQuery]);

  const getScoreBadge = (score) => {
    const pct = Math.round((score || 0) * 100);
    if (pct >= 65) return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    if (pct >= 45) return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-gray-100 text-gray-700 border-gray-300';
  };

  return (
    <div className="bg-white rounded-xl border border-[#CBD5E1] p-6 shadow-xs space-y-6">
      {/* Search Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-1">
          <Sparkles className="w-4 h-4 text-[#E5A93C]" />
          <span>AI-Powered Historical Knowledge Search</span>
        </div>
        <p className="text-xs text-gray-500">
          Query past drilling experience across offset wells in natural language to discover how previous engineers handled subsurface problems.
        </p>
      </div>

      {/* Search Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSearch();
        }}
        className="flex gap-2"
      >
        <div className="relative flex-1">
          <Search className="w-5 h-5 text-gray-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search historical drilling intelligence (e.g., stuck pipe in Demo-Barail around 3000m, mud loss mitigation)..."
            className="w-full pl-11 pr-4 py-2.5 bg-[#F8F9F8] border border-[#CBD5E1] rounded-lg text-sm text-[#1E2E1E] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#E5A93C] focus:bg-white transition"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-5 py-2.5 rounded-lg bg-[#1E2E1E] hover:bg-[#2A3E2A] text-white text-sm font-bold transition flex items-center space-x-2 shadow-xs disabled:opacity-50"
        >
          <span>{loading ? 'Searching...' : 'Search'}</span>
          <ArrowRight className="w-4 h-4 text-[#E5A93C]" />
        </button>
      </form>

      {/* Suggested Quick Queries */}
      <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span className="text-gray-500 font-medium">Quick Queries:</span>
        {sampleQueries.map((sq, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setQuery(sq);
              handleSearch(sq);
            }}
            className="px-2.5 py-1 bg-[#F8F9F8] hover:bg-[#EBF0EB] text-gray-700 hover:text-[#1E2E1E] rounded-md border border-[#E2E8F0] transition font-medium text-[11px]"
          >
            "{sq}"
          </button>
        ))}
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs">
          {error}
        </div>
      )}

      {/* Results Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs text-gray-500 pb-2 border-b border-[#E2E8F0]">
          <span>
            {hasSearched ? `Found ${results.length} relevant historical report chunks` : 'Enter a question or choose an example query above'}
          </span>
          <span className="font-mono text-[11px] text-gray-500">AI Knowledge Retrieval</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-gray-500 italic">
            Searching historical drilling archives across offset wells...
          </div>
        ) : results.length === 0 && hasSearched ? (
          <div className="p-8 text-center bg-[#F8F9F8] rounded-lg border border-dashed border-[#CBD5E1] text-xs text-gray-500">
            No matching historical report excerpts found. Try broadening your search query terms.
          </div>
        ) : (
          <div className="space-y-3">
            {results.map((res, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-[#CBD5E1] bg-white hover:border-[#94A3B8] transition shadow-2xs space-y-3"
              >
                {/* Header row */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-sm text-[#1E2E1E]">{res.well_name}</span>
                    <span className="text-xs text-gray-500">
                      • {res.report_name} (Page {res.page})
                    </span>
                    {res.event_type && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#1E2E1E] text-[#E5A93C] uppercase">
                        {res.event_type.replace('_', ' ')}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {res.formation && (
                      <span className="text-[11px] font-mono text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                        {res.formation}
                      </span>
                    )}
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getScoreBadge(
                        res.score
                      )}`}
                    >
                      Relevance: {Math.round((res.score || 0) * 100)}%
                    </span>
                  </div>
                </div>

                {/* Report excerpt */}
                <div className="bg-[#F8F9F8] p-3 rounded-lg border border-[#E2E8F0] text-xs text-gray-800 leading-relaxed font-sans">
                  "{res.text}"
                </div>

                {/* Mitigation & Footer */}
                <div className="flex items-center justify-between text-xs pt-1">
                  <div className="text-[11px] text-gray-500 font-mono">
                    Depth: {res.depth ? `${Number(res.depth).toFixed(0)}m` : 'Interval Report'}
                    {res.severity && ` • Severity: ${res.severity}`}
                  </div>
                  {onSelectReport && (
                    <button
                      onClick={() => onSelectReport(res)}
                      className="text-xs font-semibold text-[#1E2E1E] hover:text-[#E5A93C] flex items-center space-x-1"
                    >
                      <span>View Full Document Excerpt</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

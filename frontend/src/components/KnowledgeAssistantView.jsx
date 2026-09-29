import React, { useState } from 'react';
import { Bot, Send, Search, Sparkles, FileText, ExternalLink, ShieldAlert, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function KnowledgeAssistantView({
  activeWell,
  currentDepth = 3020,
  currentFormation = 'Demo-Barail',
  onSelectReport,
}) {
  const [query, setQuery] = useState('What happened in nearby wells around 3000m in Demo-Barail?');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const sampleQueries = [
    'What happened in nearby wells around 3000m in Demo-Barail?',
    'High torque and stuck pipe events in Demo-Kopili Shale',
    'Any gas kicks or high pressure incidents in Demo-Tipam Sandstone?',
    'Severe mud losses near 3020m depth',
    'Cementing issues reported in offset wells',
  ];

  const handleAsk = (userQuery = query) => {
    if (!userQuery.trim()) return;
    setLoading(true);
    setError(null);
    setQuery(userQuery);

    const wellId = activeWell?.id || 1;
    api.askAssistant(userQuery, wellId, currentDepth, 20)
      .then((data) => {
        setResult(data);
      })
      .catch((err) => {
        setError(err.message || 'Failed to query assistant.');
      })
      .finally(() => setLoading(false));
  };

  return (
    <div className="space-y-4">
      {/* Title & Scope Header */}
      <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs">
        <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-1">
          <Bot className="w-4 h-4 text-[#E5A93C]" />
          <span>Source-Grounded Drilling Knowledge Assistant</span>
        </div>
        <h2 className="text-base sm:text-lg font-bold text-[#1E2E1E]">
          Ask natural-language questions across offset DDRs, WCRs, and incident records
        </h2>
        <p className="text-xs text-gray-500 mt-1">
          Every response is grounded in factual database events and operational reports with document page citations.
        </p>

        {/* Preset Prompt Chips */}
        <div className="mt-3 flex flex-wrap gap-2">
          {sampleQueries.map((sq, i) => (
            <button
              key={i}
              onClick={() => handleAsk(sq)}
              className="text-[11px] font-medium bg-[#F4F6F4] text-[#1E2E1E] hover:bg-[#E5A93C]/20 border border-[#CBD5E1] px-2.5 py-1 rounded-full transition flex items-center space-x-1"
            >
              <Sparkles className="w-3 h-3 text-[#E5A93C]" />
              <span>{sq}</span>
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="mt-4 flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="e.g., What happened in nearby wells around 3000m in Demo-Barail?"
              className="w-full pl-9 pr-4 py-2.5 bg-[#F8F9F8] border border-[#CBD5E1] rounded-lg text-xs font-medium text-[#1E2E1E] focus:outline-none focus:ring-2 focus:ring-[#1E2E1E]"
            />
          </div>
          <button
            onClick={() => handleAsk()}
            disabled={loading}
            className="px-4 py-2.5 bg-[#1E2E1E] text-white hover:bg-[#2C3E2C] rounded-lg text-xs font-bold flex items-center space-x-1.5 disabled:opacity-50 transition"
          >
            <span>{loading ? 'Consulting Records...' : 'Query'}</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Query Result Card */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className="bg-white p-12 rounded-xl border border-[#CBD5E1] text-center text-xs text-gray-500 space-y-2">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-[#1E2E1E]" />
          <p>Parsing stratigraphy, correlating offset well records, and extracting document citations...</p>
        </div>
      )}

      {!loading && result && (
        <div className="space-y-4">
          {/* Main Synthesized Grounded Answer */}
          <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-gray-100">
              <span className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Source-Grounded Synthesis ({result.cases_found} Cases Found)</span>
              </span>
              <span className="text-[10px] text-gray-400 font-mono">
                Query: "{result.query}"
              </span>
            </div>

            <p className="text-sm font-semibold text-[#1E2E1E] leading-relaxed">
              {result.answer_summary}
            </p>

            <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg text-[11px] text-amber-900 italic">
              {result.disclaimer}
            </div>
          </div>

          {/* Cases Details Grid */}
          {result.cases && result.cases.length > 0 && (
            <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-3">
              <h3 className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
                Correlated Historical Incident Records
              </h3>
              <div className="space-y-3">
                {result.cases.map((c, idx) => (
                  <div key={idx} className="p-3.5 rounded-lg border border-[#E2E8F0] bg-[#F8F9F8] space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <strong className="text-xs font-bold text-[#1E2E1E]">{c.well_name}</strong>
                        <span className="text-[11px] text-gray-500 font-mono">({c.distance_km} km offset)</span>
                        <span className="text-gray-300">•</span>
                        <span className="text-xs font-mono font-bold text-gray-700">{c.depth}m</span>
                        <span className="text-xs text-gray-500">({c.formation_name})</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-red-100 text-red-800">
                        {c.event_type.replace('_', ' ')}
                      </span>
                    </div>

                    <p className="text-xs text-gray-700 leading-relaxed">
                      {c.description}
                    </p>

                    {c.mitigation && (
                      <div className="pt-2 border-t border-gray-200 text-[11px] text-gray-600">
                        <strong className="text-[#1E2E1E]">Documented Action:</strong> {c.mitigation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Citations & Evidence Links */}
          {result.citations && result.citations.length > 0 && (
            <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-3">
              <h3 className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider flex items-center space-x-1.5">
                <FileText className="w-4 h-4 text-[#E5A93C]" />
                <span>Supporting Source Document Citations</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {result.citations.map((cit, idx) => (
                  <div key={idx} className="p-3 rounded-lg border border-[#CBD5E1] bg-white flex flex-col justify-between space-y-2">
                    <div>
                      <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider block">
                        Citation [{idx + 1}] • {cit.well_name}
                      </span>
                      <strong className="text-xs font-bold text-[#1E2E1E] block mt-0.5">
                        {cit.document_name}
                      </strong>
                      <p className="text-[11px] text-gray-600 mt-1 line-clamp-2 italic">
                        "{cit.excerpt}"
                      </p>
                    </div>

                    <div className="pt-2 border-t border-gray-100 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-gray-500">Page {cit.page_number}</span>
                      <a
                        href={`https://nwis-sih.onrender.com/reports_static/${cit.document_name.includes('.pdf') ? cit.document_name : 'NWIS-W007_Drilling_Report_Lost_Circulation.pdf'}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs font-bold text-[#1E2E1E] hover:underline flex items-center space-x-1"
                      >
                        <span>Open Source PDF</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

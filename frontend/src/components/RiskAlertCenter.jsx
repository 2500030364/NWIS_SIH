import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, ArrowRight, Info, CheckCircle2, ChevronRight } from 'lucide-react';
import RiskEvidenceModal from './RiskEvidenceModal';

export default function RiskAlertCenter({ risks = [], currentDepth, currentFormation, onSearchReport }) {
  const [selectedRisk, setSelectedRisk] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const getSeverityBadge = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'HIGH':
        return 'bg-amber-100 text-amber-900 border-amber-300';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  const filteredRisks = risks.filter((r) => {
    if (filterSeverity === 'ALL') return true;
    if (filterSeverity === 'ACTIONABLE') return r.level === 'CRITICAL' || r.level === 'HIGH';
    return r.level === filterSeverity;
  });

  return (
    <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-4">
      {/* Header & Filter Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#E2E8F0]">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-[#E5A93C]" />
          <div>
            <h3 className="text-sm font-bold text-[#1E2E1E] uppercase tracking-wider">
              Operational Risk & Alert Center
            </h3>
            <span className="text-[11px] text-gray-500">
              Explainable multi-factor hazard assessment for {currentFormation || 'Demo-Barail'} @ {currentDepth ? currentDepth.toFixed(0) : '3020'}m
            </span>
          </div>
        </div>

        {/* Severity Filters */}
        <div className="flex items-center space-x-1 text-xs">
          {['ALL', 'ACTIONABLE', 'CRITICAL', 'HIGH'].map((f) => (
            <button
              key={f}
              onClick={() => setFilterSeverity(f)}
              className={`px-2.5 py-1 rounded font-semibold transition ${
                filterSeverity === f
                  ? 'bg-[#1E2E1E] text-[#E5A93C] shadow-xs'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Risks Grid */}
      {filteredRisks.length === 0 ? (
        <div className="p-8 text-center bg-[#F8F9F8] rounded-lg border border-dashed border-[#CBD5E1] space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
          <div className="text-sm font-bold text-[#1E2E1E]">Safe Drilling Interval</div>
          <p className="text-xs text-gray-500 max-w-md mx-auto">
            No active hazards detected within the current depth neighborhood. Offset well records indicate safe operations at this depth.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredRisks.map((risk, idx) => {
            const isCriticalOrHigh = risk.level === 'CRITICAL' || risk.level === 'HIGH';
            return (
              <div
                key={idx}
                className={`p-4 rounded-xl border transition-all hover:shadow-md flex flex-col justify-between space-y-3 ${
                  isCriticalOrHigh
                    ? 'bg-amber-50/40 border-amber-200 hover:border-amber-400'
                    : 'bg-[#F8F9F8] border-[#E2E8F0] hover:border-gray-300'
                }`}
              >
                <div>
                  {/* Top line: Title & Badge */}
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div className="font-bold text-sm text-[#1E2E1E] flex items-center space-x-1.5">
                      {isCriticalOrHigh && <AlertTriangle className="w-4 h-4 text-[#D97706] shrink-0" />}
                      <span>{risk.title}</span>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase shrink-0 ${getSeverityBadge(
                        risk.level
                      )}`}
                    >
                      {risk.level} ({Math.round(risk.score * 100)}%)
                    </span>
                  </div>

                  {/* Depth Interval and Formation info */}
                  <div className="text-[11px] text-gray-600 flex items-center gap-2 mb-2 font-mono">
                    <span>{risk.current_formation}</span>
                    {risk.historical_depth_interval && (
                      <>
                        <span>•</span>
                        <span className="text-[#B45309] font-semibold">
                          Hazard: {risk.historical_depth_interval}
                        </span>
                      </>
                    )}
                  </div>

                  {/* Summary narrative excerpt */}
                  <p className="text-xs text-gray-700 line-clamp-3 leading-relaxed">
                    {risk.explanation.split('\n')[0]}
                  </p>

                  {/* Supporting Wells tags */}
                  {risk.supporting_wells?.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
                      <span className="text-[10px] text-gray-500 font-semibold uppercase">Offset Wells:</span>
                      {risk.supporting_wells.slice(0, 4).map((w, wIdx) => (
                        <span
                          key={wIdx}
                          className="px-1.5 py-0.5 bg-white border border-[#CBD5E1] rounded text-[10px] font-mono text-gray-800"
                        >
                          {w}
                        </span>
                      ))}
                      {risk.supporting_wells.length > 4 && (
                        <span className="text-[10px] text-gray-500">
                          +{risk.supporting_wells.length - 4} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Card Action Button */}
                <div className="pt-2 border-t border-gray-200/60 flex items-center justify-between">
                  <span className="text-[10px] text-gray-500 italic">
                    {risk.supporting_events?.length || 0} supporting events
                  </span>
                  <button
                    onClick={() => setSelectedRisk(risk)}
                    className="py-1 px-2.5 rounded bg-white hover:bg-gray-100 text-[#1E2E1E] text-xs font-bold border border-[#CBD5E1] shadow-2xs transition flex items-center space-x-1"
                  >
                    <span>View Historical Evidence</span>
                    <ChevronRight className="w-3.5 h-3.5 text-[#E5A93C]" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Detail Modal */}
      {selectedRisk && (
        <RiskEvidenceModal
          risk={selectedRisk}
          onClose={() => setSelectedRisk(null)}
          onSearchReport={onSearchReport}
        />
      )}
    </div>
  );
}

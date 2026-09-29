import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, ArrowRight, ShieldCheck, Wrench, ChevronRight, Layers, ExternalLink } from 'lucide-react';
import RiskEvidenceModal from './RiskEvidenceModal';

export default function PrimaryRiskHero({
  risks = [],
  primaryRisk = null,
  currentDepth,
  currentFormation,
  onSearchReport,
  onViewAllRisks,
}) {
  const [selectedEvidenceRisk, setSelectedEvidenceRisk] = useState(null);
  const [activeRiskIndex, setActiveRiskIndex] = useState(0);

  // Filter to actionable or top risks
  const candidateRisks = risks.length > 0 ? risks : (primaryRisk ? [primaryRisk] : []);
  const actionableRisks = candidateRisks.filter((r) => r.level === 'CRITICAL' || r.level === 'HIGH' || r.level === 'MEDIUM');
  const displayRisks = actionableRisks.length > 0 ? actionableRisks : candidateRisks;
  const currentRisk = displayRisks[activeRiskIndex] || displayRisks[0];

  const getSeverityStyle = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return {
          badge: 'bg-red-50 text-red-700 border-red-300',
          border: 'border-red-200',
          accent: 'text-red-700',
          bg: 'bg-red-50/40',
        };
      case 'HIGH':
        return {
          badge: 'bg-amber-50 text-amber-800 border-amber-300',
          border: 'border-amber-200',
          accent: 'text-amber-800',
          bg: 'bg-amber-50/40',
        };
      case 'MEDIUM':
        return {
          badge: 'bg-yellow-50 text-yellow-800 border-yellow-300',
          border: 'border-yellow-200',
          accent: 'text-yellow-800',
          bg: 'bg-yellow-50/40',
        };
      default:
        return {
          badge: 'bg-emerald-50 text-emerald-800 border-emerald-300',
          border: 'border-emerald-200',
          accent: 'text-emerald-800',
          bg: 'bg-emerald-50/40',
        };
    }
  };

  const style = currentRisk ? getSeverityStyle(currentRisk.level) : getSeverityStyle('LOW');

  // Parse explanation bullets cleanly for non-technical 5-second scan
  const getBullets = (explanation) => {
    if (!explanation) return [];
    return explanation
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => (line.startsWith('•') ? line.substring(1).trim() : line))
      .slice(0, 3);
  };

  if (!currentRisk) {
    return (
      <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs flex flex-col justify-between h-full">
        <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider pb-2 border-b border-[#E2E8F0]">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Current Subsurface Risk Evaluation</span>
        </div>
        <div className="p-6 text-center space-y-2 my-auto">
          <ShieldCheck className="w-10 h-10 text-emerald-600 mx-auto" />
          <div className="text-sm font-bold text-[#1E2E1E]">Normal Safe Interval</div>
          <p className="text-xs text-gray-500 max-w-xs mx-auto">
            No anomalous drilling hazards detected at {currentDepth?.toFixed(0)}m in {currentFormation}.
          </p>
        </div>
      </div>
    );
  }

  const bullets = getBullets(currentRisk.explanation);

  return (
    <>
      <div className={`bg-white rounded-xl border ${style.border} p-4 sm:p-5 shadow-xs flex flex-col justify-between h-full space-y-3`}>
        {/* Top Header */}
        <div>
          <div className="flex items-center justify-between pb-2.5 border-b border-[#E2E8F0]">
            <div className="flex items-center space-x-2">
              <ShieldAlert className={`w-4 h-4 ${style.accent}`} />
              <span className="text-[11px] font-bold text-[#1E2E1E] uppercase tracking-wider">
                Current Priority Hazard
              </span>
            </div>

            {/* Risk Carousel / Count Switcher */}
            {displayRisks.length > 1 && (
              <div className="flex items-center space-x-1.5 text-[11px]">
                <span className="text-gray-500 text-[10px]">
                  Alert {activeRiskIndex + 1} of {displayRisks.length}
                </span>
                <div className="flex items-center space-x-1">
                  {displayRisks.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActiveRiskIndex(idx)}
                      className={`w-2 h-2 rounded-full transition-all ${
                        idx === activeRiskIndex ? 'bg-[#1E2E1E] w-4' : 'bg-gray-300 hover:bg-gray-400'
                      }`}
                      title={`View alert ${idx + 1}`}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Hero Risk Title & Severity */}
          <div className="mt-3 flex items-start justify-between gap-2">
            <div>
              <div className="text-base sm:text-lg font-bold text-[#1E2E1E] leading-snug flex items-center gap-1.5">
                <AlertTriangle className={`w-5 h-5 shrink-0 ${style.accent}`} />
                <span>{currentRisk.title.replace('Potential ', '')}</span>
              </div>
              <div className="text-[11px] text-gray-500 font-mono mt-0.5">
                Stratigraphy: <span className="font-semibold text-gray-800">{currentRisk.current_formation}</span> @{' '}
                <span className="font-semibold text-[#1E2E1E]">{currentRisk.current_depth}m</span>
              </div>
            </div>

            <div className="text-right shrink-0">
              <span className={`px-2 py-0.5 rounded text-[11px] font-extrabold border uppercase tracking-wider ${style.badge}`}>
                {currentRisk.level}
              </span>
              <div className="text-xs font-mono font-bold text-gray-700 mt-1">
                {Math.round(currentRisk.score * 100)}% <span className="text-[10px] text-gray-500 font-normal">match</span>
              </div>
            </div>
          </div>

          {/* Why? - Explainability Box */}
          <div className="mt-3 p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0] space-y-1.5">
            <div className="text-[11px] font-extrabold uppercase tracking-wider text-gray-700">
              Why?
            </div>
            <ul className="space-y-1 text-xs text-gray-700 leading-relaxed">
              {bullets.map((b, i) => (
                <li key={i} className="flex items-start space-x-1.5">
                  <span className="text-[#E5A93C] font-bold shrink-0">•</span>
                  <span>{b}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommended Mitigation Summary */}
          {currentRisk.recommended_mitigation && (
            <div className="mt-2.5 p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80 text-[11px] text-emerald-950 flex items-start space-x-2">
              <Wrench className="w-3.5 h-3.5 text-emerald-700 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-emerald-900 uppercase text-[10px] block">Recommended Rig Action:</span>
                <span className="line-clamp-2">{currentRisk.recommended_mitigation}</span>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="pt-2.5 border-t border-[#E2E8F0] flex items-center justify-between gap-2">
          <button
            onClick={() => setSelectedEvidenceRisk(currentRisk)}
            className="px-3.5 py-1.5 bg-[#1E2E1E] hover:bg-[#2C3E2C] text-[#E5A93C] rounded-lg text-xs font-bold transition flex items-center space-x-1.5 shadow-xs uppercase tracking-wider"
          >
            <span>VIEW EVIDENCE</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          {onViewAllRisks && (
            <button
              onClick={onViewAllRisks}
              className="text-xs font-semibold text-gray-600 hover:text-[#1E2E1E] transition flex items-center space-x-1"
            >
              <span>All Risks ({risks.length})</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Evidence Modal */}
      {selectedEvidenceRisk && (
        <RiskEvidenceModal
          risk={selectedEvidenceRisk}
          onClose={() => setSelectedEvidenceRisk(null)}
          onSearchReport={onSearchReport}
        />
      )}
    </>
  );
}

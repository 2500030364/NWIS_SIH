import React from 'react';
import { X, AlertTriangle, ShieldCheck, MapPin, Wrench, Layers, Compass, ExternalLink } from 'lucide-react';

export default function RiskEvidenceModal({ risk, onClose, onSearchReport }) {
  if (!risk) return null;

  const getSeverityStyle = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'HIGH':
        return 'bg-amber-50 text-amber-900 border-amber-200';
      case 'MEDIUM':
        return 'bg-yellow-50 text-yellow-800 border-yellow-200';
      default:
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
    }
  };

  return (
    <div className="fixed inset-0 z-[3000] bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl border border-[#CBD5E1] w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="bg-[#1E2E1E] text-white p-5 flex items-center justify-between border-b border-[#2C3E2C]">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-[#E5A93C]/20 border border-[#E5A93C]/40 text-[#E5A93C]">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold tracking-wide">{risk.title}</h3>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${getSeverityStyle(risk.level)}`}>
                  {risk.level} ({Math.round(risk.score * 100)}%)
                </span>
              </div>
              <p className="text-xs text-gray-300 mt-0.5">
                Explainable Decision-Support Evidence • Measured Depth: {risk.current_depth}m • {risk.current_formation}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-gray-400 hover:text-white hover:bg-[#2C3E2C] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs text-gray-700">
          {/* 1. Why NWIS Raised This Alert */}
          <div className="p-4 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0] space-y-2">
            <div className="flex items-center space-x-2 font-bold text-[#1E2E1E] uppercase tracking-wider text-[11px]">
              <ShieldCheck className="w-4 h-4 text-[#4A604A]" />
              <span>Why Did NWIS Raise This Alert? (Institutional Memory)</span>
            </div>
            <div className="whitespace-pre-line text-xs text-gray-800 leading-relaxed font-sans pl-1">
              {risk.explanation}
            </div>
          </div>

          {/* 2. Key Metrics Comparison Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-gray-500 block mb-1">Current Depth</span>
              <span className="text-sm font-bold font-mono text-[#1E2E1E]">{risk.current_depth} m</span>
            </div>
            <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-gray-500 block mb-1">Hazard Interval</span>
              <span className="text-sm font-bold font-mono text-[#E5A93C]">
                {risk.historical_depth_interval || 'Adjacent'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-gray-500 block mb-1">Current Formation</span>
              <span className="text-xs font-bold text-[#1E2E1E] truncate block">{risk.current_formation}</span>
            </div>
            <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-gray-500 block mb-1">Supporting Wells</span>
              <span className="text-sm font-bold text-[#1E2E1E]">{risk.supporting_wells?.length || 0} wells</span>
            </div>
          </div>

          {/* 3. Supporting Offset Wells & Historical Incidents */}
          <div>
            <div className="flex items-center space-x-2 mb-3 font-bold text-[#1E2E1E] uppercase tracking-wider text-[11px]">
              <MapPin className="w-4 h-4 text-[#1E2E1E]" />
              <span>Offset Well Evidence Records ({risk.supporting_events?.length || 0} matching events)</span>
            </div>

            {(!risk.supporting_events || risk.supporting_events.length === 0) ? (
              <div className="text-gray-500 italic p-3 bg-gray-50 rounded-lg">
                No individual event records attached.
              </div>
            ) : (
              <div className="space-y-3">
                {risk.supporting_events.map((ev, idx) => (
                  <div key={idx} className="p-3.5 rounded-lg border border-[#E2E8F0] bg-white shadow-2xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-[#1E2E1E] text-xs">{ev.well_name}</span>
                        <span className="text-[10px] text-gray-500 font-mono">({ev.distance_km} km away)</span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold border uppercase ${getSeverityStyle(ev.severity)}`}>
                          {ev.severity}
                        </span>
                      </div>
                      <span className="font-mono text-xs font-bold text-[#E5A93C]">
                        @{Number(ev.depth).toFixed(0)}m
                      </span>
                    </div>

                    <p className="text-xs text-gray-700 leading-relaxed">{ev.description}</p>

                    {ev.cause && (
                      <div className="text-[11px] text-gray-600 bg-[#F8F9F8] p-2 rounded border border-[#E2E8F0]">
                        <span className="font-semibold text-gray-900">Engineering Root Cause:</span> {ev.cause}
                      </div>
                    )}

                    {ev.mitigation && (
                      <div className="text-[11px] text-emerald-800 bg-emerald-50/60 p-2 rounded border border-emerald-200/60 flex items-start space-x-1.5">
                        <Wrench className="w-3.5 h-3.5 text-emerald-700 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold text-emerald-900">Proven Mitigation in {ev.well_name}:</span> {ev.mitigation}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 4. Sensor Telemetry Evidence */}
          {risk.telemetry_evidence && (
            <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg text-xs space-y-1 text-amber-900">
              <span className="font-bold block text-[11px] uppercase tracking-wider text-amber-800">
                Active Sensor Telemetry Corroboration:
              </span>
              <p>{risk.telemetry_evidence}</p>
            </div>
          )}

          {/* 5. Recommended Operational Mitigation */}
          {risk.recommended_mitigation && (
            <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-lg text-xs space-y-1 text-emerald-900">
              <div className="flex items-center space-x-1.5 font-bold uppercase tracking-wider text-[11px] text-emerald-800">
                <Wrench className="w-4 h-4 text-emerald-700" />
                <span>Recommended Engineering Action:</span>
              </div>
              <p className="leading-relaxed pl-1">{risk.recommended_mitigation}</p>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-[#E2E8F0] bg-[#F8F9F8] flex items-center justify-between">
          <div className="text-[10px] text-gray-500 italic">
            * NWIS provides advisory decision-support based on offset well correlation.
          </div>
          <button
            onClick={() => {
              onClose();
              if (onSearchReport) {
                onSearchReport(`${risk.risk_type.replace('_', ' ').toLowerCase()} in ${risk.current_formation}`);
              }
            }}
            className="py-1.5 px-3 rounded-lg bg-[#1E2E1E] hover:bg-[#2A3E2A] text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-xs"
          >
            <span>Search Historical Reports for this Hazard</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

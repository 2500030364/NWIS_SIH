import React, { useState, useEffect } from 'react';
import { BrainCircuit, Layers, AlertTriangle, ShieldCheck, Wrench, ArrowRight, MapPin, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';

export default function DrillingIntelligenceView({
  activeWell,
  currentDepth,
  currentFormation,
  onSearchHistorical,
}) {
  const [formationEvents, setFormationEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDetailedLog, setShowDetailedLog] = useState(false);

  useEffect(() => {
    if (!currentFormation) return;
    setLoading(true);

    api.getAllEvents({ formation: currentFormation, limit: 100 })
      .then((data) => {
        setFormationEvents(data || []);
      })
      .catch(() => setFormationEvents([]))
      .finally(() => setLoading(false));
  }, [currentFormation]);

  // Group events by hazard type to compute concise patterns
  const hazardPatterns = React.useMemo(() => {
    const grouped = {};
    formationEvents.forEach((ev) => {
      const type = ev.event_type;
      if (!grouped[type]) {
        grouped[type] = {
          type,
          count: 0,
          wells: new Set(),
          depths: [],
          mitigations: [],
          severities: [],
        };
      }
      grouped[type].count += 1;
      grouped[type].wells.add(ev.well_id);
      grouped[type].depths.push(Number(ev.depth));
      if (ev.mitigation) grouped[type].mitigations.push(ev.mitigation);
      if (ev.severity) grouped[type].severities.push(ev.severity);
    });

    return Object.values(grouped).map((g) => {
      const minDepth = Math.min(...g.depths);
      const maxDepth = Math.max(...g.depths);
      const depthRangeStr = minDepth === maxDepth ? `~${minDepth.toFixed(0)} m` : `${minDepth.toFixed(0)}–${maxDepth.toFixed(0)} m`;
      const isCritical = g.severities.includes('CRITICAL');
      const isHigh = g.severities.includes('HIGH');

      return {
        type: g.type,
        eventCount: g.count,
        wellCount: g.wells.size,
        depthRange: depthRangeStr,
        sampleMitigation: g.mitigations[0] || 'Standard well control & circulation protocols.',
        severity: isCritical ? 'CRITICAL' : isHigh ? 'HIGH' : 'MEDIUM',
      };
    }).sort((a, b) => b.eventCount - a.eventCount);
  }, [formationEvents]);

  const getSeverityBadge = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'HIGH':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      default:
        return 'bg-yellow-50 text-yellow-800 border-yellow-200';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 sm:p-6 shadow-xs space-y-6">
      {/* Title & Core Value Proposition */}
      <div className="border-b border-[#E2E8F0] pb-4">
        <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-1">
          <BrainCircuit className="w-4 h-4 text-[#E5A93C]" />
          <span>Cross-Well Drilling Intelligence & Institutional Memory</span>
        </div>
        <h3 className="text-base font-bold text-[#1E2E1E]">
          What happened in nearby offset wells when they drilled through {currentFormation || 'Demo-Barail'}?
        </h3>
        <p className="text-xs text-gray-500 mt-0.5">
          Correlating offset drilling incidents, depths, root causes, and operational mitigations across neighboring wells.
        </p>
      </div>

      {/* Formation Profile Summary Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3.5 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-0.5">Target Stratigraphy</span>
          <span className="text-base font-bold text-[#1E2E1E] block">{currentFormation || 'Demo-Barail'}</span>
          <span className="text-xs font-mono text-gray-500 mt-0.5 block">Bit Depth: {currentDepth ? currentDepth.toFixed(1) : '3020'}m</span>
        </div>

        <div className="p-3.5 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-0.5">Penetrated Offset Wells</span>
          <span className="text-base font-bold text-[#1E2E1E] block">
            {new Set(formationEvents.map((e) => e.well_id)).size} wells
          </span>
          <span className="text-xs text-gray-500 mt-0.5 block">Recorded drilling through this zone</span>
        </div>

        <div className="p-3.5 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-0.5">Cataloged Offset Incidents</span>
          <span className="text-base font-bold text-[#E5A93C] font-mono block">{formationEvents.length} events</span>
          <span className="text-xs text-gray-500 mt-0.5 block">Documented in offset DDR/WCR reports</span>
        </div>
      </div>

      {/* Common Historical Patterns in this Formation */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
            Common Historical Patterns in {currentFormation || 'Demo-Barail'}
          </div>
          <span className="text-xs text-gray-500">Concise offset hazard summary</span>
        </div>

        {loading ? (
          <div className="p-6 text-center text-xs text-gray-500 italic">
            Analyzing offset well history logs for {currentFormation}...
          </div>
        ) : hazardPatterns.length === 0 ? (
          <div className="p-6 text-center bg-[#F8F9F8] rounded-lg text-xs text-gray-500">
            No historical hazards recorded in {currentFormation}.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {hazardPatterns.map((pat) => (
              <div
                key={pat.type}
                className="p-3.5 rounded-xl border border-[#CBD5E1] bg-[#F8F9F8] hover:border-[#94A3B8] transition flex flex-col justify-between space-y-2.5"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-[#1E2E1E] uppercase tracking-wide">
                      {pat.type.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-0.2 rounded text-[9px] font-extrabold border uppercase ${getSeverityBadge(pat.severity)}`}>
                      {pat.severity}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] font-mono bg-white p-2 rounded border border-[#E2E8F0]">
                    <div>
                      <span className="text-gray-500 text-[10px] block">Offset Wells:</span>
                      <span className="font-bold text-[#1E2E1E]">{pat.wellCount} wells ({pat.eventCount} incidents)</span>
                    </div>
                    <div>
                      <span className="text-gray-500 text-[10px] block">Hazard Depth:</span>
                      <span className="font-bold text-[#B45309]">{pat.depthRange}</span>
                    </div>
                  </div>

                  <div className="mt-2 text-[11px] text-emerald-950 bg-emerald-50/80 p-2 rounded border border-emerald-200/60 leading-snug">
                    <span className="font-bold text-emerald-900 block text-[10px] uppercase">Proven Offset Mitigation:</span>
                    <span className="line-clamp-2">{pat.sampleMitigation}</span>
                  </div>
                </div>

                <button
                  onClick={() => onSearchHistorical && onSearchHistorical(`${pat.type.replace('_', ' ')} in ${currentFormation}`)}
                  className="pt-2 border-t border-[#E2E8F0] text-[11px] font-bold text-[#1E2E1E] hover:text-[#E5A93C] flex items-center justify-between"
                >
                  <span>Search Offset DDR Reports</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Expandable Detailed Event Log */}
      <div className="pt-2 border-t border-[#E2E8F0]">
        <button
          onClick={() => setShowDetailedLog(!showDetailedLog)}
          className="w-full py-2.5 px-4 bg-[#F8F9F8] hover:bg-[#EBF0EB] border border-[#CBD5E1] rounded-lg text-xs font-bold text-[#1E2E1E] flex items-center justify-between transition"
        >
          <span>
            {showDetailedLog ? 'Hide Detailed Offset Incident Log' : `View All Detailed Offset Incident Records (${formationEvents.length} logs)`}
          </span>
          {showDetailedLog ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showDetailedLog && (
          <div className="mt-4 space-y-3">
            {formationEvents.map((ev, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg border border-[#CBD5E1] bg-white space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-[#1E2E1E]">
                      Well {ev.well_id ? `NWIS-W${String(ev.well_id).padStart(3, '0')}` : 'Offset'}
                    </span>
                    <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-[#1E2E1E] text-white uppercase">
                      {ev.event_type.replace('_', ' ')}
                    </span>
                    <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold border uppercase ${getSeverityBadge(ev.severity)}`}>
                      {ev.severity}
                    </span>
                  </div>
                  <span className="font-mono font-bold text-[#B45309]">@{Number(ev.depth).toFixed(0)}m</span>
                </div>

                <p className="text-gray-700 leading-relaxed">{ev.description}</p>

                {ev.cause && (
                  <div className="text-[11px] text-gray-600 bg-[#F8F9F8] p-2 rounded border border-[#E2E8F0]">
                    <span className="font-bold text-gray-800">Identified Root Cause:</span> {ev.cause}
                  </div>
                )}

                {ev.mitigation && (
                  <div className="text-[11px] text-emerald-800 bg-emerald-50/60 p-2 rounded border border-emerald-200/60 flex items-start space-x-1.5">
                    <Wrench className="w-3 h-3 text-emerald-700 shrink-0 mt-0.5" />
                    <span><span className="font-bold text-emerald-950">Applied Rig Mitigation:</span> {ev.mitigation}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

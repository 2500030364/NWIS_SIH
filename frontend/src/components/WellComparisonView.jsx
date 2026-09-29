import React, { useState, useEffect } from 'react';
import { GitCompare, Layers, Activity, AlertTriangle, ShieldCheck, Info, ChevronRight, FileText } from 'lucide-react';
import { api } from '../services/api';

export default function WellComparisonView({
  activeWell,
  wells = [],
  currentDepth = 3020,
  offsetWellId,
  onSelectEvidence,
  onOpenReport,
}) {
  const [selectedOffsetWellId, setSelectedOffsetWellId] = useState(offsetWellId || 7);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Offset candidate wells (all wells except active well)
  const offsetCandidates = wells.filter((w) => w.id !== (activeWell?.id || 1));

  useEffect(() => {
    if (offsetWellId) setSelectedOffsetWellId(offsetWellId);
    else if (offsetCandidates.length && !offsetCandidates.some((w) => w.id === selectedOffsetWellId)) {
      setSelectedOffsetWellId(offsetCandidates[0].id);
    }
  }, [offsetWellId, activeWell, wells]);

  useEffect(() => {
    if (!activeWell || !selectedOffsetWellId) return;
    setLoading(true);
    const activeId = activeWell.id || 1;

    api.compareWells(activeId, selectedOffsetWellId, currentDepth)
      .then((data) => setComparisonData(data))
      .catch(() => setComparisonData(null))
      .finally(() => setLoading(false));
  }, [activeWell, selectedOffsetWellId, currentDepth]);

  return (
    <div className="space-y-4">
      {/* Header with Well Selectors */}
      <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E2E8F0]">
          <div>
            <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-1">
              <GitCompare className="w-4 h-4 text-[#E5A93C]" />
              <span>Current vs. Historical Offset Well Comparison</span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-[#1E2E1E]">
              Side-by-side stratigraphic, sensor, and hazard comparison
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Compare active drilling conditions against documented parameters and events from past wells.
            </p>
          </div>

          {/* Offset Well Picker */}
          <div className="flex items-center space-x-2 self-start sm:self-auto">
            <span className="text-xs font-semibold text-gray-600">Compare with Offset:</span>
            <select
              value={selectedOffsetWellId}
              onChange={(e) => setSelectedOffsetWellId(Number(e.target.value))}
              className="bg-[#F8F9F8] border border-[#CBD5E1] rounded px-3 py-1.5 text-xs font-bold text-[#1E2E1E] focus:outline-none focus:ring-1 focus:ring-[#1E2E1E]"
            >
              {offsetCandidates.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.well_name} ({w.status} • {w.total_depth}m)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Prototype Disclaimer */}
        <div className="mt-3 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg flex items-center space-x-2 text-[11px] text-amber-900">
          <Info className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            <strong>Decision-Support Notice:</strong> Historical similarity highlights potential subsurface analogies. All operational drilling actions remain under engineer discretion.
          </span>
        </div>
      </div>

      {loading ? (
        <div className="bg-white p-12 rounded-xl border border-[#CBD5E1] text-center text-xs text-gray-500">
          Loading comparative well intelligence...
        </div>
      ) : !comparisonData ? (
        <div className="bg-white p-12 rounded-xl border border-[#CBD5E1] text-center text-xs text-gray-500">
          Unable to load comparative data for this well pair.
        </div>
      ) : (
        <div className="space-y-4">
          {/* Section 1: Side-by-Side Well Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Left: Active Well */}
            <div className="bg-white rounded-xl border-2 border-[#E5A93C] p-4 shadow-xs space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                <div>
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">CURRENT WELL</span>
                  <span className="text-lg font-extrabold text-[#1E2E1E]">{comparisonData.active_well.well_name}</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-100 text-amber-800">
                  {comparisonData.active_well.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">CURRENT DEPTH</span>
                  <strong className="text-[#1E2E1E] font-mono text-sm">{comparisonData.active_well.current_depth}m</strong>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">FORMATION</span>
                  <strong className="text-[#1E2E1E]">{comparisonData.active_well.current_formation}</strong>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">TOTAL DEPTH</span>
                  <strong className="text-[#1E2E1E] font-mono">{comparisonData.active_well.total_depth}m</strong>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">FIELD</span>
                  <strong className="text-[#1E2E1E]">Demo-Dihing Basin</strong>
                </div>
              </div>
            </div>

            {/* Right: Offset Well */}
            <div className="bg-white rounded-xl border border-[#CBD5E1] p-4 shadow-xs space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                <div>
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">HISTORICAL OFFSET WELL</span>
                  <span className="text-lg font-extrabold text-[#1E2E1E]">{comparisonData.offset_well.well_name}</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-gray-100 text-gray-700">
                  {comparisonData.offset_well.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">OFFSET DISTANCE</span>
                  <strong className="text-[#1E2E1E] font-mono text-sm">{comparisonData.offset_well.distance_km} km</strong>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">FORMATION AT DEPTH</span>
                  <strong className="text-[#1E2E1E]">{comparisonData.offset_well.formation_at_depth}</strong>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">TOTAL DEPTH</span>
                  <strong className="text-[#1E2E1E] font-mono">{comparisonData.offset_well.total_depth}m</strong>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-400 block text-[10px]">STRATIGRAPHIC MATCH</span>
                  <strong className={comparisonData.formation_comparison.is_matched ? 'text-emerald-700' : 'text-gray-700'}>
                    {comparisonData.formation_comparison.is_matched ? '✓ Matching Formation' : 'Differing Tops'}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Sensor Telemetry Parameter Comparison Table */}
          <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
              <Activity className="w-4 h-4 text-[#E5A93C]" />
              <span>Drilling Sensor Parameters at ~{currentDepth.toFixed(0)}m Interval</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-[#F8F9F8] border-b border-[#CBD5E1] text-[10px] text-gray-500 uppercase">
                  <tr>
                    <th className="py-2.5 px-3">Parameter Channel</th>
                    <th className="py-2.5 px-3">{comparisonData.active_well.well_name} (Current)</th>
                    <th className="py-2.5 px-3">{comparisonData.offset_well.well_name} (Historical)</th>
                    <th className="py-2.5 px-3">Variance / Correlation Note</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 font-mono">
                  <tr>
                    <td className="py-2.5 px-3 font-sans font-semibold text-gray-700">Torque (kNm)</td>
                    <td className="py-2.5 px-3 font-bold text-[#1E2E1E]">{comparisonData.active_well.telemetry?.torque} kNm</td>
                    <td className="py-2.5 px-3 text-gray-600">{comparisonData.offset_well.telemetry?.torque} kNm</td>
                    <td className="py-2.5 px-3 font-sans text-gray-500">Δ {comparisonData.telemetry_comparison?.torque_variance} kNm</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-sans font-semibold text-gray-700">Standpipe Pressure (psi)</td>
                    <td className="py-2.5 px-3 font-bold text-[#1E2E1E]">{comparisonData.active_well.telemetry?.standpipe_pressure} psi</td>
                    <td className="py-2.5 px-3 text-gray-600">{comparisonData.offset_well.telemetry?.standpipe_pressure} psi</td>
                    <td className="py-2.5 px-3 font-sans text-gray-500">Δ {comparisonData.telemetry_comparison?.pressure_variance} psi</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-sans font-semibold text-gray-700">Mud Flow Rate (L/min)</td>
                    <td className="py-2.5 px-3 font-bold text-[#1E2E1E]">{comparisonData.active_well.telemetry?.mud_flow} L/min</td>
                    <td className="py-2.5 px-3 text-gray-600">{comparisonData.offset_well.telemetry?.mud_flow} L/min</td>
                    <td className="py-2.5 px-3 font-sans text-gray-500">Comparable circulation velocity</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-sans font-semibold text-gray-700">Weight on Bit (WOB, klbf)</td>
                    <td className="py-2.5 px-3 font-bold text-[#1E2E1E]">{comparisonData.active_well.telemetry?.wob} klbf</td>
                    <td className="py-2.5 px-3 text-gray-600">{comparisonData.offset_well.telemetry?.wob} klbf</td>
                    <td className="py-2.5 px-3 font-sans text-gray-500">Normal bit loading</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-sans font-semibold text-gray-700">Rate of Penetration (m/hr)</td>
                    <td className="py-2.5 px-3 font-bold text-[#1E2E1E]">{comparisonData.active_well.telemetry?.rop} m/hr</td>
                    <td className="py-2.5 px-3 text-gray-600">{comparisonData.offset_well.telemetry?.rop} m/hr</td>
                    <td className="py-2.5 px-3 font-sans text-gray-500">Drilling speed correlation</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 3: Documented Historical Incidents & Mitigation Reference */}
          <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0]">
              <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <span>Historical Incidents in {comparisonData.offset_well.well_name} at Comparable Interval</span>
              </div>
              <span className="text-xs text-gray-500">
                {comparisonData.historical_events.length} event(s) recorded (±150m)
              </span>
            </div>

            {comparisonData.historical_events.length === 0 ? (
              <div className="py-6 text-center text-xs text-gray-500 flex flex-col items-center space-y-1">
                <ShieldCheck className="w-6 h-6 text-emerald-500" />
                <span>No historical hazards recorded in this specific offset well around this depth.</span>
              </div>
            ) : (
              <div className="space-y-3">
                {comparisonData.historical_events.map((ev) => (
                  <div key={ev.id} className="p-4 rounded-lg border border-red-200 bg-red-50/50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-red-900">
                        {ev.event_type.replace('_', ' ')} at {ev.depth}m in {ev.formation}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-red-100 text-red-800">
                        {ev.severity}
                      </span>
                    </div>

                    <p className="text-xs text-gray-700 leading-relaxed">
                      <strong>Incident Description:</strong> {ev.description}
                    </p>

                    {ev.cause && (
                      <p className="text-xs text-gray-600">
                        <strong>Root Cause:</strong> {ev.cause}
                      </p>
                    )}

                    {/* Historical Mitigation Box */}
                    {ev.mitigation && (
                      <div className="p-3 bg-white border border-amber-200 rounded-md text-xs space-y-1 mt-2">
                        <strong className="text-[#1E2E1E] block">Historical Action Documented:</strong>
                        <p className="text-gray-700 italic">{ev.mitigation}</p>
                        <div className="text-[10px] text-gray-400 pt-1 border-t border-gray-100">
                          NOTE: This is historical information extracted from operational reports, not an autonomous operational recommendation.
                        </div>
                      </div>
                    )}

                    <div className="pt-2 flex items-center justify-between text-[11px]">
                      <span className="text-gray-500 font-mono">
                        Source Document: DDR_{comparisonData.offset_well.well_name}_Final.pdf
                      </span>
                      <button
                        onClick={() => onSelectEvidence && onSelectEvidence(ev)}
                        className="text-[#1E2E1E] font-bold hover:underline flex items-center space-x-1"
                      >
                        <span>Inspect Evidence Chain</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

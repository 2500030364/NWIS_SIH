import React, { useState, useEffect } from 'react';
import { Telescope, AlertTriangle, ShieldCheck, Eye, Layers, ChevronRight, Info, Compass } from 'lucide-react';
import { api } from '../services/api';

export default function DrillAheadTimeline({
  activeWell,
  currentDepth = 3020,
  currentFormation = 'Demo-Barail',
  onSelectEvidence,
  onInspectWell,
}) {
  const [drillAheadData, setDrillAheadData] = useState(null);
  const [lookaheadM, setLookaheadM] = useState(400);
  const [selectedZone, setSelectedZone] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeWell) return;
    setLoading(true);
    const wellId = activeWell.id || 1;

    api.getDrillAhead(wellId, currentDepth, lookaheadM, 20)
      .then((data) => {
        setDrillAheadData(data);
        if (data && data.zones && data.zones.length > 0) {
          // Default select the first hazard or watch zone, or current bit
          const firstHazard = data.zones.find((z) => z.status === 'HAZARD_ZONE' || z.status === 'CURRENT_BIT') || data.zones[0];
          setSelectedZone(firstHazard);
        }
      })
      .catch(() => setDrillAheadData(null))
      .finally(() => setLoading(false));
  }, [activeWell, currentDepth, lookaheadM]);

  const getStatusBadge = (status, concentration) => {
    if (status === 'CURRENT_BIT') {
      return {
        bg: 'bg-amber-500 text-white font-extrabold shadow-xs',
        border: 'border-amber-400',
        dot: 'bg-white animate-pulse',
        label: 'ACTIVE BIT',
      };
    }
    if (concentration === 'CONCENTRATED' || status === 'HAZARD_ZONE') {
      return {
        bg: 'bg-red-50 text-red-700 border-red-300 font-bold',
        border: 'border-red-500',
        dot: 'bg-red-600',
        label: 'HISTORICAL HAZARD CLUSTER',
      };
    }
    if (concentration === 'MODERATE' || status === 'WATCH') {
      return {
        bg: 'bg-amber-50 text-amber-800 border-amber-300 font-medium',
        border: 'border-amber-400',
        dot: 'bg-amber-500',
        label: 'HISTORICAL WATCH ZONE',
      };
    }
    return {
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      border: 'border-emerald-300',
      dot: 'bg-emerald-500',
      label: 'NO HISTORICAL EVENTS REPORTED',
    };
  };

  return (
    <div className="space-y-4">
      {/* Title & Lookahead Controls Header */}
      <div className="bg-white rounded-xl border border-[#CBD5E1] p-4 sm:p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E2E8F0]">
          <div>
            <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-1">
              <Telescope className="w-4 h-4 text-[#E5A93C]" />
              <span>Drill-Ahead Historical Look-Ahead Timeline</span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-[#1E2E1E]">
              What historical experience exists ahead of the active bit?
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Correlating upcoming depth intervals with past offset incidents within 20 km.
            </p>
          </div>

          {/* Lookahead Range Buttons */}
          <div className="flex items-center space-x-2 self-start sm:self-auto">
            <span className="text-xs font-semibold text-gray-500">Lookahead Window:</span>
            {[200, 400, 600].map((m) => (
              <button
                key={m}
                onClick={() => setLookaheadM(m)}
                className={`px-2.5 py-1 rounded text-xs font-bold transition ${
                  lookaheadM === m
                    ? 'bg-[#1E2E1E] text-white shadow-xs'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                +{m}m
              </button>
            ))}
          </div>
        </div>

        {/* Prototype & Decision Support Banner */}
        <div className="mt-3 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg flex items-center space-x-2 text-[11px] text-amber-900">
          <Info className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            <strong>Historical Event Concentration:</strong> Color indicators represent the historical density of recorded offset incidents in this interval — <em>not a guaranteed prediction of future downhole events</em>.
          </span>
        </div>
      </div>

      {/* Main 2-Column Split: Timeline on Left, Selected Zone Detail on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Left Column: Visual Depth Track (7 columns) */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-[#CBD5E1] p-4 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-gray-500 uppercase pb-2 border-b border-gray-100">
            <span>Interval Depth (MD)</span>
            <span>Formation & Historical Events Ahead</span>
          </div>

          {loading ? (
            <div className="py-12 text-center text-xs text-gray-500">
              Scanning offset well records across upcoming depth intervals...
            </div>
          ) : !drillAheadData || !drillAheadData.zones || drillAheadData.zones.length === 0 ? (
            <div className="py-12 text-center text-xs text-gray-500">
              No historical data available for this lookahead interval.
            </div>
          ) : (
            <div className="space-y-2.5 max-h-[520px] overflow-y-auto pr-1">
              {drillAheadData.zones.map((zone, idx) => {
                const badge = getStatusBadge(zone.status, zone.concentration);
                const isSelected = selectedZone?.depth_start === zone.depth_start;
                const isCurrent = zone.status === 'CURRENT_BIT';

                return (
                  <div
                    key={idx}
                    onClick={() => setSelectedZone(zone)}
                    className={`cursor-pointer rounded-lg border p-3 transition-all flex items-center justify-between ${
                      isSelected
                        ? 'border-[#1E2E1E] bg-[#F4F6F4] shadow-xs ring-1 ring-[#1E2E1E]'
                        : isCurrent
                        ? 'border-amber-400 bg-amber-50/60'
                        : 'border-[#E2E8F0] hover:bg-gray-50'
                    }`}
                  >
                    {/* Left: Depth Track Marker */}
                    <div className="flex items-center space-x-3">
                      <div className="flex flex-col items-center">
                        <span className={`w-3.5 h-3.5 rounded-full ${badge.dot} flex items-center justify-center`} />
                        <span className="h-6 w-0.5 bg-gray-200 mt-1" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-1.5 font-mono text-sm font-bold text-[#1E2E1E]">
                          <span>{zone.depth_start.toFixed(0)}m</span>
                          <span className="text-gray-400 text-xs">to</span>
                          <span className="text-gray-500 text-xs">{zone.depth_end.toFixed(0)}m</span>
                        </div>
                        <span className="text-[11px] text-gray-500 font-medium">
                          {zone.formation_name}
                        </span>
                      </div>
                    </div>

                    {/* Right: Event Status Tag & Summary */}
                    <div className="text-right space-y-1">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] uppercase tracking-wider ${badge.bg}`}>
                        {badge.label}
                      </span>
                      <div className="text-xs font-semibold text-gray-700">
                        {zone.event_count > 0 ? (
                          <span className="text-red-700 font-bold">{zone.event_count} offset incident(s)</span>
                        ) : (
                          <span className="text-emerald-700">Clear Interval</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Detailed Evidence & Mitigation for Selected Zone (5 columns) */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-4">
          <div className="border-b border-[#E2E8F0] pb-3">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-0.5">
              Selected Depth Interval Details
            </span>
            {selectedZone ? (
              <div>
                <div className="text-base font-bold text-[#1E2E1E] flex items-center space-x-2">
                  <span>{selectedZone.depth_start.toFixed(0)}m – {selectedZone.depth_end.toFixed(0)}m</span>
                  <span className="text-xs font-normal text-gray-500">({selectedZone.formation_name})</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">{selectedZone.summary}</p>
              </div>
            ) : (
              <span className="text-xs text-gray-400">Select a depth zone to inspect historical records</span>
            )}
          </div>

          {/* Historical Events List inside Selected Zone */}
          {selectedZone && selectedZone.events && selectedZone.events.length > 0 ? (
            <div className="space-y-3">
              <span className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider block">
                Recorded Offset Incidents ({selectedZone.events.length})
              </span>
              <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
                {selectedZone.events.map((ev, i) => (
                  <div key={i} className="p-3 rounded-lg border border-red-200 bg-red-50/40 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
                        <span className="text-xs font-bold text-[#1E2E1E]">{ev.event_type.replace('_', ' ')}</span>
                      </div>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-red-100 text-red-800">
                        {ev.severity}
                      </span>
                    </div>

                    <div className="text-[11px] text-gray-600 font-mono">
                      Well: <strong className="text-[#1E2E1E]">{ev.well_name}</strong> • Depth: <strong>{ev.depth}m</strong> • Offset: <strong>{ev.distance_km ? ev.distance_km.toFixed(1) : 0} km</strong>
                    </div>

                    <p className="text-xs text-gray-700 leading-relaxed">
                      {ev.description}
                    </p>

                    {/* Historical Mitigation */}
                    {ev.mitigation && (
                      <div className="pt-2 border-t border-red-100 text-[11px] text-gray-600">
                        <strong className="text-[#1E2E1E] block mb-0.5">Historical Action Documented:</strong>
                        <p className="italic text-gray-700">{ev.mitigation}</p>
                        <span className="text-[10px] text-gray-400 mt-1 block">
                          NOTE: Historical record only, not an operational drilling instruction.
                        </span>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="pt-2 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-gray-500">
                        Source: {ev.source_document || 'DDR Report'}
                      </span>
                      <button
                        onClick={() => onSelectEvidence && onSelectEvidence(ev)}
                        className="px-2 py-1 bg-[#1E2E1E] text-white hover:bg-[#2C3E2C] rounded text-[11px] font-semibold flex items-center space-x-1"
                      >
                        <span>View Evidence</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-gray-500 space-y-2">
              <ShieldCheck className="w-8 h-8 text-emerald-500 mx-auto" />
              <p>No historical hazards or incidents were documented by offset wells within this interval.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

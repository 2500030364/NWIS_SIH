import React, { useEffect, useState } from 'react';
import { X, Layers, AlertCircle, MapPin, Calendar, ShieldAlert, Wrench, CheckCircle } from 'lucide-react';
import { api } from '../services/api';

export default function WellDetailDrawer({ well, onClose, onInspectOffsetIntelligence }) {
  const [formations, setFormations] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!well) return;

    const wellId = well.well_id || well.id;
    setLoading(true);

    Promise.all([
      api.getWellFormations(wellId).catch(() => []),
      api.getWellHistory(wellId).catch(() => []),
    ])
      .then(([forms, hist]) => {
        setFormations(forms || []);
        setHistory(hist || []);
      })
      .finally(() => setLoading(false));
  }, [well]);

  if (!well) return null;

  const getSeverityStyle = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'HIGH':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'MEDIUM':
        return 'bg-yellow-50 text-yellow-800 border-yellow-200';
      default:
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[460px] bg-white border-l border-[#CBD5E1] shadow-2xl z-[2000] flex flex-col transform transition-transform duration-300 ease-in-out">
      {/* Header */}
      <div className="bg-[#1E2E1E] text-white px-5 py-4 flex items-center justify-between border-b border-[#2C3E2C]">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-base font-bold tracking-wide">{well.well_name}</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-[#E5A93C] text-[#1E2E1E] uppercase">
              {well.status || 'COMPLETED'}
            </span>
          </div>
          <div className="text-[11px] text-gray-300 mt-0.5">
            {well.distance_km !== undefined ? `Offset: ${well.distance_km} km away • ` : ''}
            Field: {well.field_name || 'Demo-Dihing Basin'}
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-md text-gray-300 hover:text-white hover:bg-[#2C3E2C] transition-colors"
          title="Close drawer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* Basic Stats Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
            <span className="text-gray-500 font-medium uppercase text-[10px] block mb-1">Total Measured Depth</span>
            <span className="text-sm font-bold text-[#1E2E1E] font-mono">{well.total_depth} m</span>
          </div>
          <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
            <span className="text-gray-500 font-medium uppercase text-[10px] block mb-1">Geographic Coordinates</span>
            <span className="text-[11px] font-mono text-[#1E2E1E] block">
              {Number(well.latitude).toFixed(4)}° N, {Number(well.longitude).toFixed(4)}° E
            </span>
          </div>
        </div>

        {/* Stratigraphic Formations Column */}
        <div>
          <div className="flex items-center space-x-2 mb-3 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
            <Layers className="w-4 h-4 text-[#4A604A]" />
            <span>Stratigraphic Column ({formations.length} intervals)</span>
          </div>

          {loading ? (
            <div className="text-xs text-gray-500 italic py-2">Loading geological layers...</div>
          ) : formations.length === 0 ? (
            <div className="text-xs text-gray-500 italic py-2">No formation intervals cataloged.</div>
          ) : (
            <div className="space-y-1.5">
              {formations.map((f, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 rounded-md bg-[#F8F9F8] border border-[#E2E8F0] text-xs"
                >
                  <span className="font-semibold text-[#1E2E1E]">{f.formation_name}</span>
                  <span className="font-mono text-[11px] text-gray-500">
                    {Number(f.top_depth).toFixed(0)}m – {Number(f.bottom_depth).toFixed(0)}m
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Historical Events & Hazards Timeline */}
        <div>
          <div className="flex items-center space-x-2 mb-3 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4 text-[#E5A93C]" />
            <span>Historical Incidents ({history.length} logged)</span>
          </div>

          {loading ? (
            <div className="text-xs text-gray-500 italic py-2">Loading historical events...</div>
          ) : history.length === 0 ? (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-lg flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Clean operational record. No major drilling hazards or NPT logged for this well.</span>
            </div>
          ) : (
            <div className="relative border-l-2 border-gray-200 ml-3 pl-4 space-y-4">
              {history.map((ev, idx) => (
                <div key={idx} className="relative group">
                  {/* Timeline dot */}
                  <div className="absolute -left-[23px] top-1.5 w-3 h-3 rounded-full bg-white border-2 border-[#1E2E1E] group-hover:bg-[#E5A93C] transition-colors" />

                  <div className={`p-3 rounded-lg border ${getSeverityStyle(ev.severity)} space-y-2`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-xs uppercase tracking-wide">
                          {ev.event_type.replace('_', ' ')}
                        </span>
                        <span className="px-1.5 py-0.2 rounded text-[10px] font-bold border">
                          {ev.severity}
                        </span>
                      </div>
                      <span className="font-mono text-xs font-semibold text-gray-700">
                        @{Number(ev.depth).toFixed(0)}m
                      </span>
                    </div>

                    <p className="text-xs text-gray-700 leading-relaxed">{ev.description}</p>

                    {ev.cause && (
                      <div className="text-[11px] text-gray-600 pt-1 border-t border-gray-200/60">
                        <span className="font-semibold text-gray-800">Root Cause:</span> {ev.cause}
                      </div>
                    )}

                    {ev.mitigation && (
                      <div className="text-[11px] text-emerald-800 pt-1 flex items-start space-x-1.5">
                        <Wrench className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold">Mitigation:</span> {ev.mitigation}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Drawer Footer Actions */}
      <div className="p-4 border-t border-[#E2E8F0] bg-[#F8F9F8] flex items-center justify-between">
        <button
          onClick={() => {
            onClose();
            if (onInspectOffsetIntelligence) onInspectOffsetIntelligence(well);
          }}
          className="w-full py-2 px-4 rounded-lg bg-[#1E2E1E] hover:bg-[#2A3E2A] text-white text-xs font-bold transition flex items-center justify-center space-x-2 shadow-xs"
        >
          <span>Correlate with Active Well Intelligence</span>
          <span>→</span>
        </button>
      </div>
    </div>
  );
}

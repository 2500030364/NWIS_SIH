import React, { useState, useEffect } from 'react';
import { History, Filter, AlertTriangle, ShieldCheck, ChevronRight, Search, FileText } from 'lucide-react';
import { api } from '../services/api';

export default function HistoricalEventExplorer({
  wells = [],
  onSelectEvidence,
  onOpenReport,
}) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [eventTypeFilter, setEventTypeFilter] = useState('');
  const [wellFilter, setWellFilter] = useState('');
  const [formationFilter, setFormationFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [minDepth, setMinDepth] = useState('');
  const [maxDepth, setMaxDepth] = useState('');

  const eventTypes = [
    'MUD_LOSS',
    'STUCK_PIPE',
    'KICK',
    'TORQUE_SPIKE',
    'CEMENTING_ISSUE',
    'LOST_CIRCULATION',
    'HIGH_PRESSURE',
    'NPT',
  ];

  const formations = [
    'Demo-Alluvium',
    'Demo-Girujan Clay',
    'Demo-Tipam Sandstone',
    'Demo-Bokabil',
    'Demo-Barail',
    'Demo-Kopili Shale',
    'Demo-Sylhet Limestone',
  ];

  useEffect(() => {
    setLoading(true);
    const params = { limit: 150 };
    if (eventTypeFilter) params.event_type = eventTypeFilter;
    if (wellFilter) params.well_id = wellFilter;
    if (formationFilter) params.formation = formationFilter;
    if (severityFilter) params.severity = severityFilter;

    api.getAllEvents(params)
      .then((data) => {
        let filtered = data || [];
        if (minDepth) filtered = filtered.filter((e) => Number(e.depth) >= Number(minDepth));
        if (maxDepth) filtered = filtered.filter((e) => Number(e.depth) <= Number(maxDepth));
        setEvents(filtered);
      })
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, [eventTypeFilter, wellFilter, formationFilter, severityFilter, minDepth, maxDepth]);

  const clearFilters = () => {
    setEventTypeFilter('');
    setWellFilter('');
    setFormationFilter('');
    setSeverityFilter('');
    setMinDepth('');
    setMaxDepth('');
  };

  const getSeverityBadge = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-300 font-extrabold';
      case 'HIGH':
        return 'bg-amber-100 text-amber-800 border-amber-300 font-bold';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  return (
    <div className="space-y-4">
      {/* Title & Filter Bar */}
      <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E2E8F0]">
          <div>
            <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-1">
              <History className="w-4 h-4 text-[#E5A93C]" />
              <span>Historical Drilling Incident Explorer</span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-[#1E2E1E]">
              Catalog of 122 documented subsurface events & root causes
            </h2>
          </div>
          <button
            onClick={clearFilters}
            className="text-xs text-gray-500 hover:text-[#1E2E1E] underline self-start sm:self-auto font-medium"
          >
            Reset Filters
          </button>
        </div>

        {/* Filter Controls Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {/* Event Type Filter */}
          <div>
            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-1">Hazard Type</label>
            <select
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
              className="w-full bg-[#F8F9F8] border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1E2E1E] font-medium"
            >
              <option value="">All Hazard Types</option>
              {eventTypes.map((t) => (
                <option key={t} value={t}>{t.replace('_', ' ')}</option>
              ))}
            </select>
          </div>

          {/* Formation Filter */}
          <div>
            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-1">Stratigraphy</label>
            <select
              value={formationFilter}
              onChange={(e) => setFormationFilter(e.target.value)}
              className="w-full bg-[#F8F9F8] border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1E2E1E] font-medium"
            >
              <option value="">All Formations</option>
              {formations.map((f) => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>

          {/* Well Filter */}
          <div>
            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-1">Well Source</label>
            <select
              value={wellFilter}
              onChange={(e) => setWellFilter(e.target.value)}
              className="w-full bg-[#F8F9F8] border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1E2E1E] font-medium"
            >
              <option value="">All Offset Wells</option>
              {wells.map((w) => (
                <option key={w.id} value={w.id}>{w.well_name}</option>
              ))}
            </select>
          </div>

          {/* Severity Filter */}
          <div>
            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-1">Severity</label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full bg-[#F8F9F8] border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1E2E1E] font-medium"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          {/* Depth Min */}
          <div>
            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-1">Min Depth (m)</label>
            <input
              type="number"
              placeholder="e.g. 2800"
              value={minDepth}
              onChange={(e) => setMinDepth(e.target.value)}
              className="w-full bg-[#F8F9F8] border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1E2E1E] font-medium"
            />
          </div>

          {/* Depth Max */}
          <div>
            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-1">Max Depth (m)</label>
            <input
              type="number"
              placeholder="e.g. 3400"
              value={maxDepth}
              onChange={(e) => setMaxDepth(e.target.value)}
              className="w-full bg-[#F8F9F8] border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1E2E1E] font-medium"
            />
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-3">
        <div className="flex items-center justify-between text-xs pb-2 border-b border-[#E2E8F0]">
          <span className="font-bold text-[#1E2E1E] uppercase tracking-wider">
            Matching Historical Incidents ({events.length})
          </span>
          <span className="text-gray-400">Click any row to inspect historical evidence</span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-gray-500">Querying historical database...</div>
        ) : events.length === 0 ? (
          <div className="py-12 text-center text-xs text-gray-500">
            No historical drilling events matched the selected filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#F8F9F8] border-b border-[#CBD5E1] text-[10px] text-gray-500 uppercase">
                <tr>
                  <th className="py-2.5 px-3">Hazard Type</th>
                  <th className="py-2.5 px-3">Well</th>
                  <th className="py-2.5 px-3">Depth</th>
                  <th className="py-2.5 px-3">Formation</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Description & Cause</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {events.map((ev) => (
                  <tr key={ev.id} className="hover:bg-[#F8F9F8] transition">
                    <td className="py-3 px-3 font-bold text-[#1E2E1E]">
                      {ev.event_type?.replace('_', ' ')}
                    </td>
                    <td className="py-3 px-3 font-semibold text-gray-700">
                      {ev.well_name || `NWIS-W${String(ev.well_id).padStart(3, '0')}`}
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-[#1E2E1E]">
                      {Number(ev.depth).toFixed(1)}m
                    </td>
                    <td className="py-3 px-3 text-gray-600">
                      {ev.formation || 'Demo-Barail'}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] border ${getSeverityBadge(ev.severity)}`}>
                        {ev.severity}
                      </span>
                    </td>
                    <td className="py-3 px-3 max-w-xs text-gray-700 truncate" title={ev.description}>
                      {ev.description}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => onSelectEvidence && onSelectEvidence(ev)}
                        className="px-2.5 py-1 bg-[#1E2E1E] text-white hover:bg-[#2C3E2C] rounded text-xs font-semibold"
                      >
                        Evidence
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

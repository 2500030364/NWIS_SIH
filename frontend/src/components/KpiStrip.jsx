import React from 'react';
import { Compass, AlertTriangle, History, ArrowDownToLine, MapPin, Layers } from 'lucide-react';

export default function KpiStrip({
  activeWell,
  currentDepth,
  currentFormation,
  nearbyWellsCount,
  activeRisksCount,
  highestRiskSeverity,
  historicalEventsCount,
  searchRadiusKm,
}) {
  const getSeverityBadge = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'HIGH':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'MEDIUM':
        return 'bg-yellow-50 text-yellow-800 border-yellow-200';
      default:
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
    }
  };

  return (
    <div className="nwis-kpis grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 px-5 py-3 bg-white border-b border-[#E2E8F0] shadow-2xs">
      {/* 1. Active Well */}
      <div className="nwis-kpi-card bg-[#F8F9F8] p-2.5 rounded-lg border border-[#E2E8F0] flex flex-col justify-between">
        <div className="flex items-center justify-between text-gray-500 mb-0.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Active Well</span>
          <Compass className="w-3.5 h-3.5 text-[#1E2E1E]" />
        </div>
        <div className="text-base font-bold text-[#1E2E1E] truncate">
          {activeWell?.well_name || 'NWIS-W001'}
        </div>
        <div className="text-[10px] text-gray-500 flex items-center gap-1 mt-0.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span className="font-semibold text-emerald-700">{activeWell?.status || 'DRILLING'}</span>
          <span>•</span>
          <span className="truncate">{activeWell?.field_name?.split('(')[0] || 'Demo-Dihing'}</span>
        </div>
      </div>

      {/* 2. Current Depth */}
      <div className="nwis-kpi-card bg-[#F8F9F8] p-2.5 rounded-lg border border-[#E2E8F0] flex flex-col justify-between">
        <div className="flex items-center justify-between text-gray-500 mb-0.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Current Depth</span>
          <ArrowDownToLine className="w-3.5 h-3.5 text-[#E5A93C]" />
        </div>
        <div className="text-base font-bold text-[#1E2E1E] font-mono">
          {currentDepth ? currentDepth.toFixed(1) : '3020.0'} <span className="text-xs font-normal text-gray-500">m</span>
        </div>
        <div className="text-[10px] text-gray-500 mt-0.5">
          Target: {activeWell?.total_depth ? Number(activeWell.total_depth).toFixed(0) : '3562'} m
        </div>
      </div>

      {/* 3. Current Formation */}
      <div className="nwis-kpi-card nwis-kpi-formation bg-[#F8F9F8] p-2.5 rounded-lg border border-[#E2E8F0] flex flex-col justify-between">
        <div className="flex items-center justify-between text-gray-500 mb-0.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Formation</span>
          <Layers className="w-3.5 h-3.5 text-[#E5A93C]" />
        </div>
        <div className="text-base font-bold text-[#1E2E1E] truncate">
          {currentFormation || '—'}
        </div>
        <div className="text-[10px] text-gray-500 mt-0.5">At current bit depth</div>
      </div>

      {/* 4. Nearby Offset Wells */}
      <div className="nwis-kpi-card bg-[#F8F9F8] p-2.5 rounded-lg border border-[#E2E8F0] flex flex-col justify-between">
        <div className="flex items-center justify-between text-gray-500 mb-0.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Nearby Wells</span>
          <MapPin className="w-3.5 h-3.5 text-[#1E2E1E]" />
        </div>
        <div className="text-base font-bold text-[#1E2E1E] font-mono">
          {nearbyWellsCount !== undefined ? nearbyWellsCount : '—'} <span className="text-xs font-normal text-gray-500">offset wells</span>
        </div>
        <div className="text-[10px] text-gray-500 mt-0.5">
          Within {searchRadiusKm || 20} km perimeter
        </div>
      </div>

      {/* 5. Active Risks */}
      <div className="nwis-kpi-card bg-[#F8F9F8] p-2.5 rounded-lg border border-[#E2E8F0] flex flex-col justify-between">
        <div className="flex items-center justify-between text-gray-500 mb-0.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Active Risks</span>
          <AlertTriangle className="w-3.5 h-3.5 text-[#E5A93C]" />
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-base font-bold text-[#1E2E1E] font-mono">
            {activeRisksCount || 0}
          </span>
          {highestRiskSeverity && (
            <span className={`px-1.5 py-0.2 rounded text-[9px] font-extrabold border uppercase ${getSeverityBadge(highestRiskSeverity)}`}>
              {highestRiskSeverity}
            </span>
          )}
        </div>
        <div className="text-[10px] text-gray-500 mt-0.5">
          Active Decision Alerts
        </div>
      </div>

      {/* 6. Historical Events (Real database count) */}
      <div className="nwis-kpi-card nwis-kpi-history bg-[#F8F9F8] p-2.5 rounded-lg border border-[#E2E8F0] flex flex-col justify-between">
        <div className="flex items-center justify-between text-gray-500 mb-0.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Historical Events</span>
          <History className="w-3.5 h-3.5 text-[#4A604A]" />
        </div>
        <div className="text-base font-bold text-[#1E2E1E] font-mono">
          {historicalEventsCount !== undefined && historicalEventsCount !== null ? historicalEventsCount : '...'} <span className="text-xs font-normal text-gray-500">incidents</span>
        </div>
        <div className="text-[10px] text-gray-500 mt-0.5">
          Offset Basin Institutional Memory
        </div>
      </div>
    </div>
  );
}

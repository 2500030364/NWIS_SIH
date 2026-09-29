import React from 'react';
import { Activity, Gauge, ArrowRight, Play, Pause, ChevronRight } from 'lucide-react';

export default function CompactDrillingStatus({
  telemetry = null,
  currentDepth,
  onStepDepth,
  onViewDetailedTelemetry,
}) {
  const data = telemetry || {
    torque: 16.8,
    wob: 14.2,
    rop: 8.5,
    rpm: 95.0,
    mud_flow: 1620.0,
    mud_weight: 1.25,
    standpipe_pressure: 2450.0,
    measured_depth: currentDepth || 3020.0,
  };

  const isMudLossRisk = Number(data.mud_flow) < 1750;
  const isStuckPipeRisk = Number(data.torque) > 26;
  const isKickRisk = Number(data.standpipe_pressure) > 2700;

  return (
    <div className="nwis-status-panel bg-white rounded-xl border border-[#CBD5E1] p-4 sm:p-5 shadow-xs space-y-3.5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-[#E2E8F0]">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-[#E5A93C]" />
          <div>
            <h4 className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
              Live Drilling Sensor Telemetry @ {currentDepth ? currentDepth.toFixed(1) : '3020.0'} m
            </h4>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Depth Step Controls */}
          <div className="flex items-center space-x-1 bg-[#F1F5F1] p-1 rounded-md border border-[#E2E8F0]">
            <span className="text-[10px] text-gray-500 font-medium px-1 uppercase">Bit Progress:</span>
            <button
              onClick={() => onStepDepth && onStepDepth(-10)}
              className="px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-white hover:bg-gray-100 text-gray-700 border border-[#CBD5E1] transition active:scale-95"
              title="Step depth back 10m"
            >
              -10m
            </button>
            <button
              onClick={() => onStepDepth && onStepDepth(5)}
              className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-[#E5A93C] hover:bg-[#D8992E] text-[#1E2E1E] transition active:scale-95"
              title="Advance drilling 5m"
            >
              +5m
            </button>
            <button
              onClick={() => onStepDepth && onStepDepth(10)}
              className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-[#E5A93C] hover:bg-[#D8992E] text-[#1E2E1E] transition active:scale-95"
              title="Advance drilling 10m"
            >
              +10m
            </button>
          </div>

          {onViewDetailedTelemetry && (
            <button
              onClick={onViewDetailedTelemetry}
              className="text-xs font-bold text-[#1E2E1E] hover:text-[#B45309] transition flex items-center space-x-1"
            >
              <span>Detailed Telemetry View</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* 4 Essential Telemetry Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* 1. Mud Flow */}
        <div className={`p-3 rounded-lg border ${isMudLossRisk ? 'bg-amber-50/70 border-amber-300' : 'bg-[#F8F9F8] border-[#E2E8F0]'}`}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-gray-500">Mud Circulation</span>
            <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${isMudLossRisk ? 'bg-amber-200 text-amber-900' : 'bg-emerald-100 text-emerald-800'}`}>
              {isMudLossRisk ? '⚠ Sub-nominal' : 'Normal'}
            </span>
          </div>
          <div className={`text-lg font-bold font-mono mt-1 ${isMudLossRisk ? 'text-amber-900' : 'text-[#1E2E1E]'}`}>
            {Number(data.mud_flow).toFixed(0)} <span className="text-xs font-normal text-gray-500">L/min</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">
            {isMudLossRisk ? 'Nominal baseline: 2100 L/min' : 'Safe circulation rate'}
          </div>
        </div>

        {/* 2. Surface Torque */}
        <div className={`p-3 rounded-lg border ${isStuckPipeRisk ? 'bg-amber-50/70 border-amber-300' : 'bg-[#F8F9F8] border-[#E2E8F0]'}`}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-gray-500">Surface Torque</span>
            <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${isStuckPipeRisk ? 'bg-amber-200 text-amber-900' : 'bg-emerald-100 text-emerald-800'}`}>
              {isStuckPipeRisk ? '⚠ Elevated' : 'Normal'}
            </span>
          </div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-1">
            {Number(data.torque).toFixed(1)} <span className="text-xs font-normal text-gray-500">kNm</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">
            Nominal envelope: 12.0–22.0 kNm
          </div>
        </div>

        {/* 3. Rate of Penetration (ROP) */}
        <div className="p-3 rounded-lg border bg-[#F8F9F8] border-[#E2E8F0]">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-gray-500">Drilling ROP</span>
            <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800">
              Normal
            </span>
          </div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-1">
            {Number(data.rop).toFixed(1)} <span className="text-xs font-normal text-gray-500">m/hr</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">
            Steady rotary penetration
          </div>
        </div>

        {/* 4. Standpipe Pressure (SPP) */}
        <div className={`p-3 rounded-lg border ${isKickRisk ? 'bg-red-50/70 border-red-300' : 'bg-[#F8F9F8] border-[#E2E8F0]'}`}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-gray-500">Standpipe Pressure</span>
            <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${isKickRisk ? 'bg-red-200 text-red-900' : 'bg-emerald-100 text-emerald-800'}`}>
              {isKickRisk ? '⚠ Pressure Surge' : 'Normal'}
            </span>
          </div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-1">
            {Number(data.standpipe_pressure).toFixed(0)} <span className="text-xs font-normal text-gray-500">psi</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">
            Normal range: 2100–2600 psi
          </div>
        </div>
      </div>
    </div>
  );
}

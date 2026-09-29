import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Activity, Gauge, AlertTriangle, ArrowRight, Play, Pause, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function TelemetryPanel({ activeWell, currentDepth, onStepDepth }) {
  const [telemetryData, setTelemetryData] = useState([]);
  const [activeTelemetry, setActiveTelemetry] = useState(null);
  const [autoPoll, setAutoPoll] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch telemetry around current depth
  const fetchTelemetry = () => {
    if (!activeWell) return;
    const wellId = activeWell.well_id || activeWell.id;
    const startDepth = Math.max(0, (currentDepth || 3020) - 150);
    const endDepth = (currentDepth || 3020) + 20;

    api.getWellTelemetry(wellId, startDepth, endDepth, 50)
      .then((data) => {
        if (data && data.length > 0) {
          // Format for chart
          const formatted = data.map((d) => ({
            depth: Number(d.measured_depth).toFixed(1),
            torque: Number(d.torque),
            mud_flow: Number(d.mud_flow),
            spp: Number(d.standpipe_pressure),
            rop: Number(d.rop),
            wob: Number(d.wob),
            rpm: Number(d.rpm),
            mud_weight: Number(d.mud_weight),
          }));
          setTelemetryData(formatted);
          setActiveTelemetry(data[data.length - 1]);
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    fetchTelemetry();
  }, [activeWell, currentDepth]);

  // Auto-polling simulation for live demo
  useEffect(() => {
    if (!autoPoll) return;
    const interval = setInterval(() => {
      onStepDepth(5);
    }, 4000);
    return () => clearInterval(interval);
  }, [autoPoll, onStepDepth]);

  const latest = activeTelemetry || {
    torque: 16.8,
    wob: 14.2,
    rop: 8.5,
    rpm: 95.0,
    mud_flow: 1620.0,
    mud_weight: 1.25,
    standpipe_pressure: 2450.0,
    measured_depth: currentDepth || 3020.0,
  };

  const isMudLossRisk = Number(latest.mud_flow) < 1750;
  const isStuckPipeRisk = Number(latest.torque) > 26;
  const isKickRisk = Number(latest.standpipe_pressure) > 2700;

  return (
    <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs space-y-5">
      {/* Header with Live Status & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#E2E8F0]">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-[#E5A93C]" />
          <div>
            <h3 className="text-sm font-bold text-[#1E2E1E] uppercase tracking-wider">
              Live Drilling Telemetry & Sensor Signatures
            </h3>
            <span className="text-[11px] text-gray-500">
              Depth-indexed real-time surface and MWD sensors
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setAutoPoll(!autoPoll)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition ${
              autoPoll
                ? 'bg-emerald-600 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
            }`}
          >
            {autoPoll ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{autoPoll ? 'Auto-Drilling Active' : 'Start Auto-Drilling'}</span>
          </button>

          <button
            onClick={() => onStepDepth(5)}
            className="px-3 py-1.5 rounded-lg bg-[#E5A93C] hover:bg-[#D69628] text-[#1E2E1E] text-xs font-bold flex items-center space-x-1 transition shadow-xs"
          >
            <span>+5m Step</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Real-Time Parameter Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {/* Torque */}
        <div className={`p-3 rounded-lg border ${isStuckPipeRisk ? 'bg-amber-50 border-amber-300' : 'bg-[#F8F9F8] border-[#E2E8F0]'}`}>
          <div className="text-[10px] uppercase font-bold text-gray-500">Torque</div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-0.5">
            {Number(latest.torque).toFixed(1)} <span className="text-xs font-normal text-gray-500">kNm</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Normal: 12–22</div>
        </div>

        {/* Mud Flow */}
        <div className={`p-3 rounded-lg border ${isMudLossRisk ? 'bg-amber-50 border-amber-300' : 'bg-[#F8F9F8] border-[#E2E8F0]'}`}>
          <div className="text-[10px] uppercase font-bold text-gray-500">Mud Flow</div>
          <div className={`text-lg font-bold font-mono mt-0.5 ${isMudLossRisk ? 'text-amber-800' : 'text-[#1E2E1E]'}`}>
            {Number(latest.mud_flow).toFixed(0)} <span className="text-xs font-normal text-gray-500">L/min</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">{isMudLossRisk ? '⚠ Sub-nominal loss' : 'Normal: >2100'}</div>
        </div>

        {/* Standpipe Pressure */}
        <div className={`p-3 rounded-lg border ${isKickRisk ? 'bg-red-50 border-red-300' : 'bg-[#F8F9F8] border-[#E2E8F0]'}`}>
          <div className="text-[10px] uppercase font-bold text-gray-500">SPP Pressure</div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-0.5">
            {Number(latest.standpipe_pressure).toFixed(0)} <span className="text-xs font-normal text-gray-500">psi</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Normal: 2100–2500</div>
        </div>

        {/* WOB */}
        <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
          <div className="text-[10px] uppercase font-bold text-gray-500">Weight on Bit</div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-0.5">
            {Number(latest.wob).toFixed(1)} <span className="text-xs font-normal text-gray-500">tonnes</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Set: 10–18 t</div>
        </div>

        {/* ROP */}
        <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
          <div className="text-[10px] uppercase font-bold text-gray-500">Rate of Penetration</div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-0.5">
            {Number(latest.rop).toFixed(1)} <span className="text-xs font-normal text-gray-500">m/hr</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Avg: 8.5 m/hr</div>
        </div>

        {/* RPM */}
        <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
          <div className="text-[10px] uppercase font-bold text-gray-500">Rotary Speed</div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-0.5">
            {Number(latest.rpm).toFixed(0)} <span className="text-xs font-normal text-gray-500">RPM</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Top Drive Speed</div>
        </div>

        {/* Mud Weight */}
        <div className="p-3 rounded-lg bg-[#F8F9F8] border border-[#E2E8F0]">
          <div className="text-[10px] uppercase font-bold text-gray-500">Mud Weight</div>
          <div className="text-lg font-bold font-mono text-[#1E2E1E] mt-0.5">
            {Number(latest.mud_weight).toFixed(2)} <span className="text-xs font-normal text-gray-500">SG</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Active Mud System</div>
        </div>
      </div>

      {/* Sensor Trend Anomaly Alert Banner */}
      {(isMudLossRisk || isStuckPipeRisk || isKickRisk) && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center space-x-3 text-xs text-amber-900">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
          <div className="leading-snug">
            <span className="font-bold">Active Sensor Signature Anomaly:</span>{' '}
            {isMudLossRisk && 'Mud pump flow rate dropped to sub-normal levels, indicating dynamic fluid loss to thief zone.'}
            {isStuckPipeRisk && 'Surface rotary torque escalating above 26 kNm threshold, indicating reactive shale tight hole.'}
            {isKickRisk && 'Standpipe pressure surging above 2700 psi, indicating formation pore pressure influx.'}
          </div>
        </div>
      )}

      {/* Depth vs Telemetry Multi-Line Chart */}
      <div className="h-64 w-full pt-2">
        <div className="text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">
          Drilling Parameter Log (Depth vs Mud Flow, Torque & Pressure)
        </div>
        {telemetryData.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-gray-400 italic">
            Connecting to telemetry sensor stream...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={telemetryData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis
                dataKey="depth"
                tick={{ fontSize: 10, fill: '#64748B' }}
                label={{ value: 'Measured Depth (m)', position: 'insideBottom', offset: -5, fontSize: 10 }}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 10, fill: '#64748B' }}
                domain={['auto', 'auto']}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 10, fill: '#64748B' }}
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderColor: '#CBD5E1',
                  borderRadius: '8px',
                  fontSize: '11px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="mud_flow"
                name="Mud Flow (L/min)"
                stroke="#2563EB"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="torque"
                name="Torque (kNm)"
                stroke="#D97706"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="spp"
                name="SPP (psi)"
                stroke="#10B981"
                strokeWidth={1.5}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

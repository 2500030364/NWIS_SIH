import React, { useState } from 'react';
import { Activity, ChevronDown, Compass } from 'lucide-react';

const primaryItems = [
  { id: 'dashboard', label: 'Overview' },
  { id: 'nearby', label: 'Nearby Wells' },
  { id: 'telemetry', label: 'Telemetry' },
  { id: 'memory', label: 'Well Events' },
];

const moreItems = [
  { id: 'intelligence', label: 'Formation Intel' },
  { id: 'drill-ahead', label: 'Drill Ahead' },
  { id: 'compare', label: 'Compare Wells' },
  { id: 'assistant', label: 'Knowledge Search' },
  { id: 'evidence', label: 'Risks & Reports' },
];

export default function Header({
  activeWell,
  wells,
  onSelectWell,
  onStepDepth,
  isStepping,
  backendConnected,
  activeTab,
  onSelectTab,
  alertCount = 0,
  onHome,
}) {
  const [moreOpen, setMoreOpen] = useState(false);
  const currentMore = moreItems.find((item) => item.id === activeTab);

  const selectTab = (id) => {
    onSelectTab(id);
    setMoreOpen(false);
  };

  return (
    <header className="nwis-header">
      <button type="button" className="nwis-topbar-brand nwis-topbar-home" onClick={onHome} aria-label="NWIS home — return to landing page">
        <div className="nwis-brand-mark">NWIS</div>
        <div className="nwis-brand-copy">
          <strong>Nearby Wells Intelligence System</strong>
          <span>SIH prototype · Drilling intelligence</span>
        </div>
      </button>

      <nav className="nwis-topnav" aria-label="Main navigation">
        {primaryItems.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => selectTab(item.id)}
            aria-current={activeTab === item.id ? 'page' : undefined}
            className={`nwis-topnav-link ${activeTab === item.id ? 'is-active' : ''}`}
          >
            {item.label}
          </button>
        ))}
        <div className="nwis-more-wrap">
          <button
            type="button"
            className={`nwis-topnav-link nwis-more-trigger ${currentMore ? 'is-active' : ''}`}
            aria-expanded={moreOpen}
            onClick={() => setMoreOpen((open) => !open)}
          >
            {currentMore?.label || 'More'} <ChevronDown size={13} />
          </button>
          {moreOpen && (
            <div className="nwis-more-menu">
              {moreItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => selectTab(item.id)}
                  className={activeTab === item.id ? 'is-active' : ''}
                >
                  <span>{item.label}</span>
                  {item.id === 'evidence' && alertCount > 0 && <span className="nwis-nav-count">{alertCount}</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      </nav>

      <div className="nwis-topbar-ops">
        <div className={`nwis-system-status ${backendConnected ? 'is-online' : 'is-offline'}`} title={backendConnected ? 'Backend connected; telemetry is simulated' : 'Backend unavailable; showing fallback state'}>
          <Activity size={14} />
          <span>{backendConnected ? 'Simulated telemetry' : 'System offline'}</span>
        </div>
        <label className="nwis-active-well">
          <Compass size={15} aria-hidden="true" />
          <span>Active well</span>
          <select
            aria-label="Active well"
            value={activeWell?.id || 1}
            onChange={(e) => {
              const selectedId = Number(e.target.value);
              const found = wells.find((w) => w.id === selectedId);
              if (found) onSelectWell(found);
            }}
          >
            {wells.map((w) => (
              <option key={w.id} value={w.id}>{w.well_name} ({w.status})</option>
            ))}
          </select>
        </label>
        <div className="nwis-header-stepper" aria-label="Depth simulation controls">
          <button type="button" onClick={() => onStepDepth(-10)} disabled={isStepping} title="Step depth back 10m">−10m</button>
          <button type="button" onClick={() => onStepDepth(5)} disabled={isStepping} title="Advance drilling 5m">+5m</button>
          <button type="button" onClick={() => onStepDepth(10)} disabled={isStepping} title="Advance drilling 10m">+10m</button>
        </div>
      </div>
    </header>
  );
}

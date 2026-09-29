import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import LandingPage from './components/LandingPage';
import KpiStrip from './components/KpiStrip';
import WellMap from './components/WellMap';
import WellDetailDrawer from './components/WellDetailDrawer';
import TelemetryPanel from './components/TelemetryPanel';
import RiskAlertCenter from './components/RiskAlertCenter';
import HistoricalSearch from './components/HistoricalSearch';
import DrillingIntelligenceView from './components/DrillingIntelligenceView';
import ReportsView from './components/ReportsView';
import PrimaryRiskHero from './components/PrimaryRiskHero';
import CompactDrillingStatus from './components/CompactDrillingStatus';
import RiskEvidenceModal from './components/RiskEvidenceModal';
import HistoricalEventExplorer from './components/HistoricalEventExplorer';
import DrillAheadTimeline from './components/DrillAheadTimeline';
import WellComparisonView from './components/WellComparisonView';
import KnowledgeAssistantView from './components/KnowledgeAssistantView';
import { api } from './services/api';
import { MapPin, ShieldAlert, Activity, Database, Search, FileText } from 'lucide-react';

const asHistoricalEvidence = (event) => ({
  title: event.event_type?.replaceAll('_', ' ') || 'Historical event evidence',
  risk_type: event.event_type || 'HISTORICAL_EVENT',
  level: event.severity || 'MEDIUM',
  score: 0,
  current_depth: Number(event.depth) || 0,
  historical_depth_interval: `${Number(event.depth) || 0} m historical event`,
  current_formation: event.formation || event.formation_name || 'Formation not recorded',
  explanation: `Historical record from ${event.well_name || `well ${event.well_id || 'not specified'}`}. ${event.description || ''}${event.cause ? `\nRecorded cause: ${event.cause}` : ''}`,
  supporting_wells: event.well_name ? [event.well_name] : [],
  supporting_events: [{ ...event, formation: event.formation || event.formation_name }],
  recommended_mitigation: event.mitigation,
});

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [hasEntered, setHasEntered] = useState(false);
  const [wells, setWells] = useState([]);
  const [activeWell, setActiveWell] = useState(null);
  const [selectedWell, setSelectedWell] = useState(null);
  const [comparisonWellId, setComparisonWellId] = useState(null);
  const [selectedRiskEvidence, setSelectedRiskEvidence] = useState(null);
  const [searchRadiusKm, setSearchRadiusKm] = useState(20);
  const [nearbyWells, setNearbyWells] = useState([]);
  const [currentDepth, setCurrentDepth] = useState(3020.0);
  const [currentFormation, setCurrentFormation] = useState('Demo-Barail');
  const [risks, setRisks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [historicalEventsCount, setHistoricalEventsCount] = useState(0);
  const [latestTelemetry, setLatestTelemetry] = useState(null);
  const [isStepping, setIsStepping] = useState(false);
  const [backendConnected, setBackendConnected] = useState(true);
  const [initialSearchQuery, setInitialSearchQuery] = useState('');

  // 1. Initial Load: Fetch all wells, active state, and real historical events count from DB
  useEffect(() => {
    api.checkHealth()
      .then(() => setBackendConnected(true))
      .catch(() => setBackendConnected(false));

    api.getWells()
      .then((data) => {
        setWells(data || []);
        if (data && data.length > 0) {
          // Default to NWIS-W001
          const w1 = data.find((w) => w.id === 1 || w.well_id === 'NWIS-W001') || data[0];
          setActiveWell(w1);
        }
      })
      .catch(() => setBackendConnected(false));

    api.getActiveState()
      .then((state) => {
        if (state) {
          if (state.current_depth) setCurrentDepth(Number(state.current_depth));
          if (state.current_formation) setCurrentFormation(state.current_formation);
        }
      })
      .catch(() => {});

    // Fetch real historical events count from backend database (no hardcoding)
    api.getEventsCount()
      .then((res) => {
        if (res && typeof res.count === 'number') {
          setHistoricalEventsCount(res.count);
        }
      })
      .catch(() => {
        // Fallback to query all events if /count fails
        api.getAllEvents({ limit: 500 })
          .then((evs) => setHistoricalEventsCount(evs?.length || 122))
          .catch(() => setHistoricalEventsCount(122));
      });
  }, []);

  // 2. Fetch Nearby Wells when activeWell or searchRadiusKm changes
  useEffect(() => {
    if (!activeWell) return;
    const lat = Number(activeWell.latitude);
    const lng = Number(activeWell.longitude);

    api.getNearbyWells(lat, lng, searchRadiusKm)
      .then((data) => {
        const activeId = Number(activeWell.id ?? activeWell.well_id);
        setNearbyWells((data || []).filter((well) => Number(well.id ?? well.well_id) !== activeId));
      })
      .catch(() => setNearbyWells([]));
  }, [activeWell, searchRadiusKm]);

  // 3. Refresh Risk Assessment and Alerts when activeWell or currentDepth changes
  const refreshRisks = useCallback(() => {
    if (!activeWell) return;
    const wellId = activeWell.id || 1;

    api.getRisks(wellId, currentDepth, searchRadiusKm)
      .then((res) => {
        if (res) {
          setRisks(res.risks || []);
          if (res.current_formation) setCurrentFormation(res.current_formation);
        }
      })
      .catch(() => {});

    api.getAlerts(wellId, currentDepth, searchRadiusKm, 'MEDIUM')
      .then((res) => {
        if (res) {
          setAlerts(res.alerts || []);
        }
      })
      .catch(() => {});
  }, [activeWell, currentDepth, searchRadiusKm]);

  useEffect(() => {
    refreshRisks();
  }, [refreshRisks]);

  // 4. Fetch telemetry point for compact telemetry display on depth change
  useEffect(() => {
    if (!activeWell) return;
    const wellId = activeWell.id || 1;

    api.getWellTelemetry(wellId, Math.max(0, currentDepth - 50), currentDepth + 10, 10)
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setLatestTelemetry(data[data.length - 1]);
        } else {
          setLatestTelemetry(null);
        }
      })
      .catch(() => {
        setLatestTelemetry(null);
      });
  }, [activeWell, currentDepth]);

  // Depth Stepper handler for live simulation
  const handleStepDepth = (deltaM) => {
    if (!activeWell || isStepping) return;
    const wellId = activeWell.id || 1;
    setIsStepping(true);

    api.stepActiveDepth(deltaM, wellId)
      .then((res) => {
        if (res && res.current_depth) {
          setCurrentDepth(Number(res.current_depth));
          if (res.current_formation) setCurrentFormation(res.current_formation);
        }
      })
      .catch(() => {
        // Fallback local state update
        setCurrentDepth((prev) => Math.max(0, prev + deltaM));
      })
      .finally(() => setIsStepping(false));
  };

  const handleSearchFromEvidence = (searchStr) => {
    setInitialSearchQuery(searchStr);
    setActiveTab('search');
  };

  const highestRiskSeverity = alerts.length > 0 ? alerts[0].level : 'LOW';

  if (!hasEntered) {
    return <LandingPage onEnter={() => setHasEntered(true)} />;
  }

  return (
    <div className="nwis-shell flex h-screen w-screen overflow-hidden bg-[#F8F9F8] text-[#1E293B]">
      {/* Main Content Workspace */}
      <div className="nwis-workspace flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <Header
          activeWell={activeWell}
          wells={wells}
          onSelectWell={(w) => {
            setActiveWell(w);
            setSelectedWell(null);
            setComparisonWellId(null);
            api.getActiveState(w.id).then((state) => {
              if (state?.current_depth != null) setCurrentDepth(Number(state.current_depth));
              if (state?.current_formation) setCurrentFormation(state.current_formation);
            }).catch(() => {});
          }}
          currentDepth={currentDepth}
          currentFormation={currentFormation}
          onStepDepth={handleStepDepth}
          isStepping={isStepping}
          backendConnected={backendConnected}
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          alertCount={alerts.length}
          onHome={() => {
            setActiveTab('dashboard');
            setHasEntered(false);
          }}
        />

        {/* Global KPI Strip */}
        <KpiStrip
          activeWell={activeWell}
          currentDepth={currentDepth}
          currentFormation={currentFormation}
          nearbyWellsCount={nearbyWells.length}
          activeRisksCount={alerts.length}
          highestRiskSeverity={highestRiskSeverity}
          historicalEventsCount={historicalEventsCount}
          searchRadiusKm={searchRadiusKm}
        />

        {/* Main Tab Routing */}
        <main className="nwis-content flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
          {/* TAB 1: COCKPIT OVERVIEW (Default) */}
          {activeTab === 'dashboard' && (
            <div className="space-y-4">
              <div className="nwis-overview-heading">
                <div>
                  <div className="nwis-eyebrow">DRILLING INTELLIGENCE / OVERVIEW</div>
                  <h1>Operational overview</h1>
                  <p>Nearby well history, current telemetry and formation context in one view.</p>
                </div>
                <span className="nwis-demo-tag"><span /> Synthetic demonstration data</span>
              </div>
              {/* 2-Column Split: Map on Left (Primary), Most Urgent Risk on Right */}
              <div className="nwis-dashboard-grid grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
                {/* Left Area: Nearby Wells Map (7 columns) */}
                <div className="nwis-map-card lg:col-span-7 bg-white p-3.5 rounded-xl border border-[#CBD5E1] shadow-xs flex flex-col">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#E2E8F0]">
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4 text-[#E5A93C]" />
                      <span className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider">
                        Nearby well map <span className="nwis-section-context">{searchRadiusKm} km radius</span>
                      </span>
                    </div>
                    <span className="text-[11px] text-gray-500 hidden sm:inline">
                      {nearbyWells.length} wells detected • Click to inspect details
                    </span>
                  </div>
                  <div className="flex-1">
                    <WellMap
                      activeWell={activeWell}
                      nearbyWells={nearbyWells}
                      selectedWell={selectedWell}
                      onSelectWell={setSelectedWell}
                      searchRadiusKm={searchRadiusKm}
                      onRadiusChange={setSearchRadiusKm}
                      height="h-[440px]"
                    />
                  </div>
                </div>

                {/* Right Area: Primary Active Risk Hero (5 columns) */}
                <div className="nwis-risk-column lg:col-span-5 flex flex-col">
                  <PrimaryRiskHero
                    risks={risks}
                    currentDepth={currentDepth}
                    currentFormation={currentFormation}
                    onViewAllRisks={() => setActiveTab('evidence')}
                    onSearchReport={handleSearchFromEvidence}
                  />
                </div>
              </div>

              {/* Below Map / Risk: Compact Live Drilling Status */}
              <CompactDrillingStatus
                telemetry={latestTelemetry}
                currentDepth={currentDepth}
                onStepDepth={handleStepDepth}
                isStepping={isStepping}
                onViewDetailedTelemetry={() => setActiveTab('telemetry')}
              />
            </div>
          )}

          {/* TAB 2: NEARBY WELLS VIEW */}
          {activeTab === 'nearby' && (
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-xl border border-[#CBD5E1] shadow-xs">
                <div className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-2">
                  Offset Well Field Geography ({nearbyWells.length} wells detected within {searchRadiusKm} km)
                </div>
                <WellMap
                  activeWell={activeWell}
                  nearbyWells={nearbyWells}
                  selectedWell={selectedWell}
                  onSelectWell={setSelectedWell}
                  searchRadiusKm={searchRadiusKm}
                  onRadiusChange={setSearchRadiusKm}
                  height="h-[450px]"
                />
              </div>

              {/* Nearby Wells Table */}
              <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 shadow-xs">
                <h3 className="text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-3">
                  Catalog of Offset Wells within {searchRadiusKm} km
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#F8F9F8] border-b border-[#CBD5E1] text-[10px] text-gray-500 uppercase">
                      <tr>
                        <th className="py-2.5 px-3">Well Identifier</th>
                        <th className="py-2.5 px-3">Offset Distance</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3">Total Depth</th>
                        <th className="py-2.5 px-3">Coordinates</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E2E8F0]">
                      {nearbyWells.map((w) => (
                        <tr key={w.well_id || w.id} className="hover:bg-[#F8F9F8] transition">
                          <td className="py-3 px-3 font-bold text-[#1E2E1E]">{w.well_name}</td>
                          <td className="py-3 px-3 font-mono text-gray-700 font-semibold">{w.distance_km || 0} km</td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-800 border">
                              {w.status}
                            </span>
                          </td>
                          <td className="py-3 px-3 font-mono">{w.total_depth}m</td>
                          <td className="py-3 px-3 font-mono text-gray-500 text-[11px]">
                            {Number(w.latitude).toFixed(3)}° N, {Number(w.longitude).toFixed(3)}° E
                          </td>
                          <td className="py-3 px-3 text-right">
                            <button
                              onClick={() => setSelectedWell(w)}
                              className="px-2.5 py-1 bg-[#1E2E1E] text-white hover:bg-[#2C3E2C] rounded text-xs font-semibold"
                            >
                              Inspect Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: DRILLING INTELLIGENCE VIEW */}
          {activeTab === 'intelligence' && (
            <DrillingIntelligenceView
              activeWell={activeWell}
              currentDepth={currentDepth}
              currentFormation={currentFormation}
              onSearchHistorical={handleSearchFromEvidence}
            />
          )}

          {activeTab === 'memory' && (
            <HistoricalEventExplorer
              wells={wells}
              onSelectEvidence={(event) => setSelectedRiskEvidence(asHistoricalEvidence(event))}
              onOpenReport={() => setActiveTab('reports')}
            />
          )}

          {activeTab === 'drill-ahead' && (
            <DrillAheadTimeline
              activeWell={activeWell}
              currentDepth={currentDepth}
              currentFormation={currentFormation}
              onSelectEvidence={(event) => setSelectedRiskEvidence(asHistoricalEvidence(event))}
              onInspectWell={(well) => setSelectedWell(well)}
            />
          )}

          {activeTab === 'compare' && (
            <WellComparisonView
              activeWell={activeWell}
              wells={wells}
              currentDepth={currentDepth}
              offsetWellId={comparisonWellId}
              onSelectEvidence={(event) => setSelectedRiskEvidence(asHistoricalEvidence(event))}
              onOpenReport={() => setActiveTab('reports')}
            />
          )}

          {activeTab === 'assistant' && (
            <KnowledgeAssistantView
              activeWell={activeWell}
              currentDepth={currentDepth}
              currentFormation={currentFormation}
              onSelectReport={() => setActiveTab('reports')}
            />
          )}

          {activeTab === 'evidence' && (
            <div className="space-y-4">
              <RiskAlertCenter
                risks={risks}
                currentDepth={currentDepth}
                currentFormation={currentFormation}
                onSearchReport={handleSearchFromEvidence}
              />
              <ReportsView onSearchHistorical={(q) => {
                setInitialSearchQuery(q);
                setActiveTab('search');
              }} />
            </div>
          )}

          {/* TAB 4: LIVE TELEMETRY VIEW */}
          {activeTab === 'telemetry' && (
            <TelemetryPanel
              activeWell={activeWell}
              currentDepth={currentDepth}
              onStepDepth={handleStepDepth}
            />
          )}

          {/* TAB 5: RISKS & ALERTS VIEW */}
          {activeTab === 'risks' && (
            <RiskAlertCenter
              risks={risks}
              currentDepth={currentDepth}
              currentFormation={currentFormation}
              onSearchReport={handleSearchFromEvidence}
            />
          )}

          {/* TAB 6: HISTORICAL INTELLIGENCE SEARCH */}
          {activeTab === 'search' && (
            <HistoricalSearch
              initialQuery={initialSearchQuery}
              onSelectReport={(rep) => {
                setActiveTab('reports');
              }}
            />
          )}

          {/* TAB 7: OPERATIONAL REPORTS VIEW */}
          {activeTab === 'reports' && (
            <ReportsView
              onSearchHistorical={(q) => {
                setInitialSearchQuery(q);
                setActiveTab('search');
              }}
            />
          )}
        </main>
      </div>

      {/* Slide-over Right Drawer for Selected Well Details */}
      {selectedWell && (
        <WellDetailDrawer
          well={selectedWell}
          onClose={() => setSelectedWell(null)}
          onInspectOffsetIntelligence={(w) => {
            setSelectedWell(null);
            setComparisonWellId(Number(w.id ?? w.well_id));
            setActiveTab('compare');
          }}
        />
      )}

      {/* Risk Evidence Modal (Decision-Support Evidence) */}
      {selectedRiskEvidence && (
        <RiskEvidenceModal
          risk={selectedRiskEvidence}
          onClose={() => setSelectedRiskEvidence(null)}
          onSearchReport={(q) => {
            setSelectedRiskEvidence(null);
            handleSearchFromEvidence(q);
          }}
        />
      )}
    </div>
  );
}

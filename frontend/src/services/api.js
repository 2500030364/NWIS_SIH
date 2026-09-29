/**
 * NWIS Frontend API Service
 * Connects React frontend to FastAPI backend endpoints.
 */

const API_BASE = '/api';

async function handleResponse(res) {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch (_) {}
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Health
  checkHealth: () => fetch(`${API_BASE}/health`).then(handleResponse),
  checkDbHealth: () => fetch(`${API_BASE}/health/db`).then(handleResponse),

  // Active Well State
  getActiveState: (wellId) => {
    const url = wellId ? `${API_BASE}/wells/active/state?well_id=${wellId}` : `${API_BASE}/wells/active/state`;
    return fetch(url).then(handleResponse);
  },

  setActiveDepth: (depth, wellId) => {
    const url = wellId 
      ? `${API_BASE}/wells/active/set_depth?depth=${depth}&well_id=${wellId}`
      : `${API_BASE}/wells/active/set_depth?depth=${depth}`;
    return fetch(url, { method: 'POST' }).then(handleResponse);
  },

  stepActiveDepth: (deltaM = 5.0, wellId) => {
    const url = wellId
      ? `${API_BASE}/wells/active/step?delta_m=${deltaM}&well_id=${wellId}`
      : `${API_BASE}/wells/active/step?delta_m=${deltaM}`;
    return fetch(url, { method: 'POST' }).then(handleResponse);
  },

  // Wells
  getWells: (statusFilter, fieldName) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    if (fieldName) params.append('field_name', fieldName);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetch(`${API_BASE}/wells${query}`).then(handleResponse);
  },

  getWell: (wellId) => fetch(`${API_BASE}/wells/${wellId}`).then(handleResponse),

  getNearbyWells: (lat, long, radiusKm = 20) =>
    fetch(`${API_BASE}/wells/nearby?lat=${lat}&long=${long}&radius=${radiusKm}`).then(handleResponse),

  getWellHistory: (wellId, formation, eventType, severity) => {
    const params = new URLSearchParams();
    if (formation) params.append('formation', formation);
    if (eventType) params.append('event_type', eventType);
    if (severity) params.append('severity', severity);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetch(`${API_BASE}/wells/${wellId}/history${query}`).then(handleResponse);
  },

  getWellFormations: (wellId) => fetch(`${API_BASE}/wells/${wellId}/formations`).then(handleResponse),
  getFormationsSummary: () => fetch(`${API_BASE}/formations`).then(handleResponse),

  // Events
  getAllEvents: (params = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.append(k, v);
    });
    return fetch(`${API_BASE}/events?${q.toString()}`).then(handleResponse);
  },
  getEventsCount: () => fetch(`${API_BASE}/events/count`).then(handleResponse),

  // Telemetry
  getActiveTelemetry: () => fetch(`${API_BASE}/wells/active/telemetry`).then(handleResponse),

  getWellTelemetry: (wellId, startDepth, endDepth, limit = 100) => {
    const params = new URLSearchParams({ limit });
    if (startDepth !== undefined && startDepth !== null) params.append('start_depth', startDepth);
    if (endDepth !== undefined && endDepth !== null) params.append('end_depth', endDepth);
    return fetch(`${API_BASE}/wells/${wellId}/telemetry?${params.toString()}`).then(handleResponse);
  },

  // Risks & Alerts (Phase 4)
  getRisks: (wellId, depth, radiusKm = 25) => {
    const params = new URLSearchParams({ radius_km: radiusKm });
    if (depth !== undefined && depth !== null) params.append('depth', depth);
    return fetch(`${API_BASE}/risks/${wellId}?${params.toString()}`).then(handleResponse);
  },

  getAlerts: (wellId, depth, radiusKm = 25, minLevel = 'MEDIUM') => {
    const params = new URLSearchParams({ radius_km: radiusKm, min_level: minLevel });
    if (depth !== undefined && depth !== null) params.append('depth', depth);
    return fetch(`${API_BASE}/alerts/${wellId}?${params.toString()}`).then(handleResponse);
  },

  // Semantic Document Search (Phase 3)
  searchHistorical: (query, topK = 5) => {
    const params = new URLSearchParams({ query, top_k: topK });
    return fetch(`${API_BASE}/search?${params.toString()}`).then(handleResponse);
  },

  // Operational Reports
  getReports: (params = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.append(k, v);
    });
    return fetch(`${API_BASE}/reports?${q.toString()}`).then(handleResponse);
  },

  getReport: (reportId) => fetch(`${API_BASE}/reports/${reportId}`).then(handleResponse),

  // Offset Well Relevance (Prototype Scoring)
  getOffsetRelevance: (wellId = 1, depth = 3020, radiusKm = 20) => {
    return fetch(`${API_BASE}/wells/${wellId}/relevance?current_depth=${depth}&radius_km=${radiusKm}`).then(handleResponse);
  },

  // Drill-Ahead Look-Ahead Timeline
  getDrillAhead: (wellId = 1, depth = 3020, lookaheadM = 400, radiusKm = 20) => {
    return fetch(`${API_BASE}/wells/${wellId}/drill-ahead?current_depth=${depth}&lookahead_m=${lookaheadM}&radius_km=${radiusKm}`).then(handleResponse);
  },

  // Current vs Offset Well Comparison
  compareWells: (activeWellId = 1, offsetWellId = 7, depth = 3020) => {
    return fetch(`${API_BASE}/wells/compare?active_well_id=${activeWellId}&offset_well_id=${offsetWellId}&current_depth=${depth}`).then(handleResponse);
  },

  // Knowledge Assistant
  askAssistant: (query, activeWellId = 1, depth = 3020, radiusKm = 20) => {
    return fetch(`${API_BASE}/assistant/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        active_well_id: activeWellId,
        current_depth: depth,
        radius_km: radiusKm,
      }),
    }).then(handleResponse);
  },
};


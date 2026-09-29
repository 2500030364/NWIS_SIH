import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { Layers, ZoomIn, ZoomOut, Compass } from 'lucide-react';

export default function WellMap({
  activeWell,
  nearbyWells = [],
  selectedWell,
  onSelectWell,
  searchRadiusKm = 20,
  onRadiusChange,
  height = 'h-[360px]',
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersGroupRef = useRef(null);
  const circleLayerRef = useRef(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const defaultCenter = [
        activeWell?.latitude ? Number(activeWell.latitude) : 27.35,
        activeWell?.longitude ? Number(activeWell.longitude) : 95.38,
      ];

      const map = L.map(mapContainerRef.current, {
        center: defaultCenter,
        zoom: 12,
        zoomControl: false,
      });

      // Clean OpenStreetMap tiles with no watermark or API key requirement
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      // Add custom positioned zoom controls
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      markersGroupRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Markers and Radius Overlay whenever activeWell or nearbyWells change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !markersGroupRef.current) return;

    markersGroupRef.current.clearLayers();

    if (!activeWell) return;

    const activeLat = Number(activeWell.latitude);
    const activeLng = Number(activeWell.longitude);

    // 1. Draw Search Radius Circle around active well
    if (circleLayerRef.current) {
      map.removeLayer(circleLayerRef.current);
    }
    const radiusMeters = (searchRadiusKm || 20) * 1000;
    circleLayerRef.current = L.circle([activeLat, activeLng], {
      radius: radiusMeters,
      color: '#4A604A',
      fillColor: '#E5A93C',
      fillOpacity: 0.07,
      weight: 1.5,
      dashArray: '5, 5',
    }).addTo(map);

    // 2. Active Well Marker (Mustard Yellow with pulsating ring)
    const activeIconHtml = `
      <div style="position: relative; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 32px; height: 32px; border-radius: 50%; background: rgba(229, 169, 60, 0.35); animation: pulse-ring 2s infinite;"></div>
        <div style="width: 18px; height: 18px; border-radius: 50%; background: #E5A93C; border: 3px solid #1E2E1E; box-shadow: 0 2px 6px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;">
          <div style="width: 4px; height: 4px; border-radius: 50%; background: #1E2E1E;"></div>
        </div>
      </div>
    `;

    const activeIcon = L.divIcon({
      html: activeIconHtml,
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });

    const activeMarker = L.marker([activeLat, activeLng], { icon: activeIcon })
      .bindPopup(
        `<div style="font-family: inherit; font-size: 12px;">
          <div style="font-weight: bold; color: #1E2E1E; font-size: 14px;">${activeWell.well_name}</div>
          <div style="color: #E5A93C; font-weight: 600; text-transform: uppercase; font-size: 10px;">★ Current Active Well</div>
          <div style="margin-top: 4px; color: #64748B;">Total Depth: ${activeWell.total_depth}m</div>
          <div style="color: #64748B;">Field: ${activeWell.field_name || 'Demo-Dihing'}</div>
        </div>`
      )
      .addTo(markersGroupRef.current);

    activeMarker.on('click', () => onSelectWell(activeWell));

    // 3. Offset Well Markers
    nearbyWells.forEach((w) => {
      if (w.well_id === activeWell.id || w.id === activeWell.id) return;

      const isSelected = selectedWell && (selectedWell.id === w.well_id || selectedWell.id === w.id);
      const isDrilling = w.status === 'DRILLING';

      const offsetColor = isSelected ? '#E5A93C' : '#1E2E1E';
      const offsetBorder = isSelected ? '#1E2E1E' : '#FFFFFF';

      const offsetIconHtml = `
        <div style="width: 22px; height: 22px; border-radius: 50%; background: ${offsetColor}; border: 2.5px solid ${offsetBorder}; box-shadow: 0 2px 5px rgba(0,0,0,0.25); display: flex; align-items: center; justify-content: center; cursor: pointer;">
          <div style="width: 6px; height: 6px; border-radius: 50%; background: ${isDrilling ? '#10B981' : '#CBD5E1'};"></div>
        </div>
      `;

      const offsetIcon = L.divIcon({
        html: offsetIconHtml,
        className: '',
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });

      const marker = L.marker([Number(w.latitude), Number(w.longitude)], { icon: offsetIcon })
        .bindPopup(
          `<div style="font-family: inherit; font-size: 12px;">
            <div style="font-weight: bold; color: #1E2E1E; font-size: 13px;">${w.well_name}</div>
            <div style="color: #64748B; font-size: 11px;">Offset Distance: <span style="font-weight: bold; color: #1E2E1E;">${w.distance_km || 0} km</span></div>
            <div style="color: #64748B; font-size: 11px;">Status: <span style="color: ${isDrilling ? '#059669' : '#475569'}; font-weight: 600;">${w.status}</span></div>
            <div style="color: #64748B; font-size: 11px;">Total Depth: ${w.total_depth}m</div>
            <div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid #E2E8F0; font-size: 10px; color: #2563EB; font-weight: 600;">
              Click marker to inspect historical events & formations →
            </div>
          </div>`
        )
        .addTo(markersGroupRef.current);

      marker.on('click', () => onSelectWell(w));
    });

    // Pan smoothly to active well
    map.setView([activeLat, activeLng], map.getZoom() || 12);
  }, [activeWell, nearbyWells, selectedWell, searchRadiusKm]);

  return (
    <div className={`relative w-full ${height} bg-gray-100 rounded-xl overflow-hidden border border-[#CBD5E1] shadow-xs`}>
      {/* Map Container */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Top Floating Map Controls: Radius Selection */}
      <div className="absolute top-3 left-3 z-[1000] bg-white/95 backdrop-blur-xs px-3 py-2 rounded-lg border border-[#CBD5E1] shadow-md flex items-center space-x-3 text-xs">
        <div className="flex items-center space-x-1.5 font-semibold text-[#1E2E1E]">
          <Compass className="w-3.5 h-3.5 text-[#E5A93C]" />
          <span>Offset Radius:</span>
        </div>
        <div className="flex items-center space-x-1">
          {[5, 10, 20].map((r) => (
            <button
              key={r}
              onClick={() => onRadiusChange && onRadiusChange(r)}
              className={`px-2.5 py-1 rounded font-bold transition-all ${
                searchRadiusKm === r
                  ? 'bg-[#1E2E1E] text-[#E5A93C] shadow-xs'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {r} km
            </button>
          ))}
        </div>
      </div>

      {/* Floating Legend */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-white/95 backdrop-blur-xs px-3 py-2 rounded-lg border border-[#CBD5E1] shadow-md text-[11px] text-gray-700 space-y-1">
        <div className="font-bold text-[#1E2E1E] uppercase tracking-wider text-[10px] mb-1">
          Map Legend
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-[#E5A93C] border border-[#1E2E1E]" />
          <span>Active Drilling Well</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-[#1E2E1E] border border-white" />
          <span>Offset Nearby Wells</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-0.5 border-t border-dashed border-[#4A604A]" />
          <span>Offset Perimeter ({searchRadiusKm} km)</span>
        </div>
      </div>
    </div>
  );
}

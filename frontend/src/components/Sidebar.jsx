import React from 'react';
import {
  LayoutDashboard,
  MapPin,
  Activity,
  History,
  Telescope,
  GitCompare,
  Bot,
  FileCheck,
  Layers,
  ShieldCheck,
} from 'lucide-react';

export default function Sidebar({ activeTab, onSelectTab, alertCount = 0 }) {
  const navActiveTab = ['risks', 'search', 'reports'].includes(activeTab) ? 'evidence' : activeTab;
  const navItems = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
    { id: 'nearby', label: 'Nearby Wells', icon: MapPin },
    { id: 'telemetry', label: 'Telemetry', icon: Activity },
    { id: 'memory', label: 'Well Events', icon: History },
    { id: 'intelligence', label: 'Formation Intel', icon: Layers },
    { id: 'drill-ahead', label: 'Drill Ahead', icon: Telescope },
    { id: 'compare', label: 'Compare Wells', icon: GitCompare },
    { id: 'assistant', label: 'Knowledge Search', icon: Bot },
    { id: 'evidence', label: 'Risks & Reports', icon: FileCheck, badge: alertCount },
  ];

  return (
    <aside className="nwis-sidebar w-64 bg-[#1E2E1E] text-gray-300 flex flex-col justify-between shrink-0 border-r border-[#2A3F2A]">
      {/* Navigation Links */}
      <div className="py-4">
        <div className="px-4 mb-3 text-[11px] font-bold uppercase tracking-wider text-gray-400">
          Decision Support Cockpit
        </div>
        <nav className="space-y-1 px-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = navActiveTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                aria-label={item.label}
                title={item.label}
                className={`nwis-nav-item w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[#E5A93C] text-[#1E2E1E] font-bold shadow-xs'
                    : 'text-gray-300 hover:bg-[#283D28] hover:text-white'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#1E2E1E]' : 'text-gray-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge > 0 && (
                  <span
                    className={`px-1.5 py-0.5 rounded-full text-[10px] font-extrabold ${
                      isActive ? 'bg-[#1E2E1E] text-white' : 'bg-[#E5A93C] text-[#1E2E1E]'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Industrial Footer Note */}
      <div className="p-4 border-t border-[#2A3F2A] bg-[#172417] text-[11px] text-gray-400">
        <div className="flex items-center space-x-2 text-gray-300 font-semibold mb-1">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Decision Support System</span>
        </div>
        <p className="leading-relaxed text-gray-400">
          Oil India Limited SIH Prototype • Synthetic demonstration data.
        </p>
      </div>
    </aside>
  );
}

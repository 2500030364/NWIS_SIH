import React, { useState, useEffect } from 'react';
import { FileText, Eye, Calendar, Filter, Search, X, Compass, ExternalLink, Download } from 'lucide-react';
import { api } from '../services/api';

export default function ReportsView({ onSearchHistorical }) {
  const [reports, setReports] = useState([]);
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);

  const fetchReports = () => {
    setLoading(true);
    const params = {
      limit: 60,
    };
    if (filterType !== 'ALL') {
      params.report_type = filterType;
    }
    if (searchQuery.trim()) {
      params.search = searchQuery.trim();
    }

    api.getReports(params)
      .then((data) => {
        setReports(data || []);
      })
      .catch((err) => {
        console.error('Error fetching reports:', err);
        setReports([]);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchReports();
  }, [filterType]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchReports();
  };

  const getReportTypeBadge = (type) => {
    switch (type?.toUpperCase()) {
      case 'DDR':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'WCR':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'MUD_LOG':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'COMPLETION_REPORT':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'DRILLING_REPORT':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-[#CBD5E1] p-5 sm:p-6 shadow-xs space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#E2E8F0]">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-[#1E2E1E] uppercase tracking-wider mb-0.5">
            <FileText className="w-4 h-4 text-[#E5A93C]" />
            <span>Operational Drilling Reports Database</span>
          </div>
          <p className="text-xs text-gray-500">
            Real documents extracted and indexed from offset wells (Daily Drilling Reports, Completion Reports, Mud Logs).
          </p>
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap items-center gap-1 text-xs">
          {['ALL', 'DDR', 'WCR', 'MUD_LOG', 'COMPLETION_REPORT', 'DRILLING_REPORT'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-2.5 py-1 rounded-md font-bold transition text-[11px] ${
                filterType === t
                  ? 'bg-[#1E2E1E] text-[#E5A93C] shadow-xs'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
            >
              {t.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearchSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search report name or text contents (e.g. mud loss, stuck pipe, Barail, casing)..."
            className="w-full pl-10 pr-4 py-2 bg-[#F8F9F8] border border-[#CBD5E1] rounded-lg text-xs text-[#1E2E1E] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#E5A93C] focus:bg-white"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-[#1E2E1E] hover:bg-[#2A3E2A] text-white text-xs font-bold rounded-lg transition"
        >
          Search
        </button>
      </form>

      {/* Reports Count & Status */}
      <div className="flex items-center justify-between text-xs text-gray-500 pb-1 border-b border-[#E2E8F0]">
        <span>
          Showing {reports.length} operational reports from PostgreSQL database
        </span>
        <span className="font-mono text-[11px] text-gray-600">Database Table: reports</span>
      </div>

      {/* Reports Grid */}
      {loading ? (
        <div className="p-8 text-center text-xs text-gray-500 italic">
          Loading operational reports from database...
        </div>
      ) : reports.length === 0 ? (
        <div className="p-8 text-center bg-[#F8F9F8] rounded-lg border border-dashed border-[#CBD5E1] text-xs text-gray-500">
          No reports found matching your criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="p-4 rounded-xl border border-[#CBD5E1] bg-white hover:border-[#94A3B8] transition shadow-2xs flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="font-bold text-sm text-[#1E2E1E] line-clamp-1">
                    {report.report_name}
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-extrabold border uppercase shrink-0 ${getReportTypeBadge(
                      report.report_type
                    )}`}
                  >
                    {report.report_type.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-[11px] text-gray-500 font-mono mb-2">
                  <span className="flex items-center gap-1 font-semibold text-gray-800">
                    <Compass className="w-3.5 h-3.5 text-[#E5A93C]" />
                    {report.well_name || `Well #${report.well_id}`}
                  </span>
                  <span className="flex items-center gap-1 text-gray-500">
                    <Calendar className="w-3.5 h-3.5" />
                    {report.report_date}
                  </span>
                </div>

                <p className="text-xs text-gray-700 line-clamp-3 leading-relaxed">
                  {report.excerpt || 'Operational drilling log extracted and processed for subsurface risk correlation.'}
                </p>
              </div>

              <div className="pt-2 border-t border-[#E2E8F0] flex items-center justify-between">
                <span className="text-[10px] font-mono text-gray-500 truncate max-w-[200px]">
                  {report.file_path}
                </span>

                <button
                  onClick={() => setSelectedReport(report)}
                  className="px-2.5 py-1 bg-[#F8F9F8] hover:bg-[#E2E8F0] text-[#1E2E1E] border border-[#CBD5E1] rounded text-xs font-bold transition flex items-center space-x-1"
                >
                  <Eye className="w-3.5 h-3.5 text-[#E5A93C]" />
                  <span>Inspect Document</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Selected Report Inspection Modal */}
      {selectedReport && (
        <div className="fixed inset-0 z-[3000] bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-[#CBD5E1] w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="bg-[#1E2E1E] text-white p-4 flex items-center justify-between border-b border-[#2C3E2C]">
              <div>
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-[#E5A93C]" />
                  <h3 className="text-sm font-bold tracking-wide truncate max-w-md">
                    {selectedReport.report_name}
                  </h3>
                  <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold border uppercase ${getReportTypeBadge(selectedReport.report_type)}`}>
                    {selectedReport.report_type}
                  </span>
                </div>
                <div className="text-[11px] text-gray-300 mt-0.5">
                  Well: {selectedReport.well_name} • Date: {selectedReport.report_date}
                </div>
              </div>
              <button
                onClick={() => setSelectedReport(null)}
                className="p-1 rounded-md text-gray-400 hover:text-white hover:bg-[#2C3E2C]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs text-gray-700">
              <div className="p-3 bg-[#F8F9F8] rounded-lg border border-[#E2E8F0] text-[11px] font-mono space-y-1">
                <div><span className="font-bold text-gray-700">File Path:</span> {selectedReport.file_path}</div>
                <div><span className="font-bold text-gray-700">Database Record ID:</span> #{selectedReport.id}</div>
              </div>

              <div>
                <span className="text-[11px] font-bold text-[#1E2E1E] uppercase tracking-wider block mb-2">
                  Extracted Operational Text Content:
                </span>
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg font-mono text-[11px] leading-relaxed text-gray-800 whitespace-pre-wrap max-h-[350px] overflow-y-auto">
                  {selectedReport.extracted_text || 'No text extracted for this record.'}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-3 border-t border-[#E2E8F0] bg-[#F8F9F8] flex items-center justify-between">
              <button
                onClick={() => {
                  setSelectedReport(null);
                  if (onSearchHistorical) onSearchHistorical(selectedReport.report_name);
                }}
                className="text-xs font-bold text-[#1E2E1E] hover:text-[#E5A93C] flex items-center space-x-1"
              >
                <span>Search in Semantic Knowledge Base →</span>
              </button>

              <button
                onClick={() => setSelectedReport(null)}
                className="px-4 py-1.5 bg-[#1E2E1E] hover:bg-[#2C3E2C] text-white rounded text-xs font-bold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React from 'react';
import { Search, Filter, Calendar } from 'lucide-react';

interface FilterBarProps {
  onSearch: (query: string) => void;
  onStatusChange: (status: string) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({ onSearch, onStatusChange }) => {
  return (
    <div className="flex flex-col md:flex-row gap-4 w-full bg-white/5 p-4 rounded-xl border border-white/10 items-center justify-between shadow-[0_0_15px_rgba(0,0,0,0.2)]">
      
      {/* Search Input */}
      <div className="relative w-full md:w-96 group">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-slate-400 group-focus-within:text-sky-400 transition-colors" />
        </div>
        <input
          type="text"
          onChange={(e) => onSearch(e.target.value)}
          placeholder="Search encrypted files..."
          className="w-full bg-black/40 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500/50 transition-all shadow-inner"
        />
      </div>

      {/* Filters */}
      <div className="flex w-full md:w-auto items-center gap-3">
        
        {/* Status Dropdown */}
        <div className="relative flex-1 md:flex-none group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Filter className="h-4 w-4 text-slate-400 group-hover:text-sky-400 transition-colors" />
          </div>
          <select 
            onChange={(e) => onStatusChange(e.target.value)}
            className="w-full md:w-44 appearance-none bg-black/40 hover:bg-black/60 border border-white/10 rounded-lg pl-9 pr-8 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500/50 transition-all cursor-pointer shadow-inner"
          >
            <option value="all" className="bg-slate-900">All Statuses</option>
            <option value="encrypted" className="bg-slate-900">Encrypted (Secured)</option>
            <option value="decrypted" className="bg-slate-900">Decrypted (Unlocked)</option>
            <option value="failed" className="bg-slate-900">Failed / Blocked</option>
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg className="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Date Range Button */}
        <button className="flex items-center justify-center gap-2 px-4 py-2.5 bg-black/40 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium text-slate-300 hover:text-sky-400 transition-all shadow-inner hover:shadow-[0_0_10px_rgba(14,165,233,0.2)]">
          <Calendar className="w-4 h-4" />
          <span className="hidden sm:inline">Date Range</span>
        </button>
      </div>

    </div>
  );
};

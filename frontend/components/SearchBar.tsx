"use client";
import { useState } from "react";
import { Search } from "lucide-react";

export default function SearchBar({
  onSearch,
  loading,
}: {
  onSearch: (ticker: string) => void;
  loading: boolean;
}) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const t = value.trim().toUpperCase();
    if (t) onSearch(t);
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          className="bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 w-52"
          placeholder="Enter ticker (e.g. AAPL)"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={loading}
        />
      </div>
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
      >
        {loading ? "..." : "Analyze"}
      </button>
    </form>
  );
}

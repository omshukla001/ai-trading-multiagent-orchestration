"use client";
import { useState, useRef, useEffect } from "react";
import { Search } from "lucide-react";

// Popular tickers with display names grouped by market
const SUGGESTIONS = [
  // Indian Indices
  { ticker: "^NSEI",    name: "Nifty 50",          group: "🇮🇳 Indian Indices" },
  { ticker: "^BSESN",   name: "BSE Sensex",         group: "🇮🇳 Indian Indices" },
  { ticker: "^NSEBANK", name: "Nifty Bank",          group: "🇮🇳 Indian Indices" },
  { ticker: "^CNXIT",   name: "Nifty IT",            group: "🇮🇳 Indian Indices" },
  // Indian Stocks
  { ticker: "RELIANCE.NS", name: "Reliance Industries", group: "🇮🇳 NSE Stocks" },
  { ticker: "INFY.NS",     name: "Infosys",              group: "🇮🇳 NSE Stocks" },
  { ticker: "TCS.NS",      name: "TCS",                  group: "🇮🇳 NSE Stocks" },
  { ticker: "HDFCBANK.NS", name: "HDFC Bank",             group: "🇮🇳 NSE Stocks" },
  { ticker: "WIPRO.NS",    name: "Wipro",                 group: "🇮🇳 NSE Stocks" },
  { ticker: "ICICIBANK.NS",name: "ICICI Bank",            group: "🇮🇳 NSE Stocks" },
  { ticker: "SBIN.NS",     name: "State Bank of India",   group: "🇮🇳 NSE Stocks" },
  { ticker: "ADANIENT.NS", name: "Adani Enterprises",     group: "🇮🇳 NSE Stocks" },
  { ticker: "ADANIPOWER.NS", name: "Adani Power",         group: "🇮🇳 NSE Stocks" },
  { ticker: "ADANIPORTS.NS", name: "Adani Ports",         group: "🇮🇳 NSE Stocks" },
  { ticker: "ADANIGREEN.NS", name: "Adani Green Energy",  group: "🇮🇳 NSE Stocks" },
  { ticker: "TATAMOTORS.NS",name: "Tata Motors",          group: "🇮🇳 NSE Stocks" },
  { ticker: "TATASTEEL.NS", name: "Tata Steel",           group: "🇮🇳 NSE Stocks" },
  { ticker: "TATAPOWER.NS", name: "Tata Power",           group: "🇮🇳 NSE Stocks" },
  { ticker: "BAJFINANCE.NS",name: "Bajaj Finance",        group: "🇮🇳 NSE Stocks" },
  { ticker: "HINDUNILVR.NS",name: "Hindustan Unilever",   group: "🇮🇳 NSE Stocks" },
  { ticker: "ITC.NS",       name: "ITC",                  group: "🇮🇳 NSE Stocks" },
  { ticker: "LT.NS",        name: "Larsen & Toubro",      group: "🇮🇳 NSE Stocks" },
  { ticker: "HCLTECH.NS",   name: "HCL Technologies",    group: "🇮🇳 NSE Stocks" },
  { ticker: "BEL.NS",      name: "Bharat Electronics",    group: "🇮🇳 NSE Stocks" },
  // US Indices
  { ticker: "^GSPC",  name: "S&P 500",              group: "🇺🇸 US Indices" },
  { ticker: "^DJI",   name: "Dow Jones",             group: "🇺🇸 US Indices" },
  { ticker: "^IXIC",  name: "NASDAQ Composite",      group: "🇺🇸 US Indices" },
  { ticker: "^VIX",   name: "VIX Volatility Index",  group: "🇺🇸 US Indices" },
  // US Stocks
  { ticker: "AAPL",  name: "Apple",                  group: "🇺🇸 US Stocks" },
  { ticker: "NVDA",  name: "NVIDIA",                 group: "🇺🇸 US Stocks" },
  { ticker: "MSFT",  name: "Microsoft",              group: "🇺🇸 US Stocks" },
  { ticker: "GOOGL", name: "Alphabet (Google)",      group: "🇺🇸 US Stocks" },
  { ticker: "AMZN",  name: "Amazon",                 group: "🇺🇸 US Stocks" },
  { ticker: "TSLA",  name: "Tesla",                  group: "🇺🇸 US Stocks" },
  { ticker: "META",  name: "Meta (Facebook)",        group: "🇺🇸 US Stocks" },
  { ticker: "NFLX",  name: "Netflix",                group: "🇺🇸 US Stocks" },
  { ticker: "AMD",   name: "AMD",                    group: "🇺🇸 US Stocks" },
  { ticker: "SPY",   name: "S&P 500 ETF (SPY)",      group: "🇺🇸 US Stocks" },
  // Crypto
  { ticker: "BTC-USD", name: "Bitcoin",              group: "₿ Crypto" },
  { ticker: "ETH-USD", name: "Ethereum",             group: "₿ Crypto" },
  { ticker: "SOL-USD", name: "Solana",               group: "₿ Crypto" },
  { ticker: "BNB-USD", name: "BNB",                  group: "₿ Crypto" },
  // Global
  { ticker: "0700.HK", name: "Tencent (HK)",         group: "🌍 Global" },
  { ticker: "9984.T",  name: "SoftBank (Tokyo)",      group: "🌍 Global" },
  { ticker: "AZN.L",   name: "AstraZeneca (London)",  group: "🌍 Global" },
];

export default function SearchBar({
  onSearch,
  loading,
}: {
  onSearch: (ticker: string) => void;
  loading: boolean;
}) {
  const [value, setValue]     = useState("");
  const [open, setOpen]       = useState(false);
  const [focused, setFocused] = useState(false);
  const containerRef          = useRef<HTMLDivElement>(null);

  // Filter suggestions based on input
  const filtered = value.trim().length === 0
    ? SUGGESTIONS.slice(0, 12)          // show top 12 when empty
    : SUGGESTIONS.filter((s) =>
        s.ticker.toLowerCase().includes(value.toLowerCase()) ||
        s.name.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 10);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSelect = (ticker: string) => {
    setValue(ticker);
    setOpen(false);
    onSearch(ticker);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const t = value.trim().toUpperCase();
    if (t) {
      setOpen(false);
      onSearch(t);
    }
  };

  // Group filtered results
  const groups = filtered.reduce<Record<string, typeof SUGGESTIONS>>((acc, s) => {
    if (!acc[s.group]) acc[s.group] = [];
    acc[s.group].push(s);
    return acc;
  }, {});

  return (
    <div ref={containerRef} className="relative">
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
          <input
            className="bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 w-60 transition-colors"
            placeholder="Search ticker or name..."
            value={value}
            onChange={(e) => { setValue(e.target.value); setOpen(true); }}
            onFocus={() => { setFocused(true); setOpen(true); }}
            onBlur={() => setFocused(false)}
            disabled={loading}
            autoComplete="off"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !value.trim()}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {loading ? (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin inline-block" />
              Loading
            </span>
          ) : "Analyze"}
        </button>
      </form>

      {/* Dropdown */}
      {open && filtered.length > 0 && (
        <div className="absolute right-0 top-full mt-1 w-72 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl z-50 max-h-80 overflow-y-auto">
          {value.trim().length === 0 && (
            <p className="text-xs text-gray-500 px-3 pt-2.5 pb-1">Popular tickers</p>
          )}
          {Object.entries(groups).map(([group, items]) => (
            <div key={group}>
              <p className="text-xs text-gray-500 px-3 pt-2 pb-1 sticky top-0 bg-gray-900">{group}</p>
              {items.map((s) => (
                <button
                  key={s.ticker}
                  onMouseDown={() => handleSelect(s.ticker)}
                  className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-800 transition-colors text-left"
                >
                  <span className="text-white text-sm">{s.name}</span>
                  <span className="text-blue-400 text-xs font-mono ml-2 shrink-0">{s.ticker}</span>
                </button>
              ))}
            </div>
          ))}
          {/* Custom ticker hint */}
          {value.trim().length > 0 && filtered.length < 10 && (
            <div className="border-t border-gray-800 px-3 py-2">
              <button
                onMouseDown={() => handleSelect(value.trim().toUpperCase())}
                className="w-full flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <Search className="w-3.5 h-3.5" />
                Search for <span className="font-mono text-blue-400 ml-1">{value.trim().toUpperCase()}</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

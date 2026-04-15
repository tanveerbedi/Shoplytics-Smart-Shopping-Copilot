import { Link, useLocation } from "react-router-dom";
import { Zap, Search, CircleDot } from "lucide-react";
import useShoplyticsStore from "../../store/useShoplyticsStore";

export default function Navbar() {
  const location = useLocation();
  const isDashboard = location.pathname === "/dashboard";
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);

  return (
    <nav className="fixed top-0 w-full h-16 z-50 bg-white/80 backdrop-blur-xl border-b border-border shadow-sm transition-all">
      <div className="max-w-[1600px] w-full mx-auto px-6 h-full flex items-center justify-between">
        
        {/* Left: Logo */}
        <Link to="/" className="flex items-center gap-2.5 group shrink-0">
          <div className="bg-gradient-to-br from-primary to-primary-dark p-1.5 rounded-lg shadow-soft group-hover:shadow-[0_0_15px_rgba(37,99,235,0.4)] transition-all">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold text-2xl tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-text-primary via-text-primary to-primary-dark select-none">
            SHOPLYTICS
          </span>
        </Link>

        {/* Center: Search (if on dashboard) */}
        {isDashboard && (
          <div className="hidden md:flex flex-1 max-w-xl mx-8">
            <div className="w-full relative flex items-center bg-bg-muted border border-border/60 focus-within:border-primary/50 focus-within:bg-white rounded-full px-4 py-1.5 transition-all shadow-sm focus-within:shadow-[0_0_0_3px_rgba(37,99,235,0.08)]">
              <Search className="w-4 h-4 text-text-dim" />
              <input
                type="text"
                readOnly
                value={useShoplyticsStore.getState().query || "Search active..."}
                onClick={() => {
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                className="flex-1 bg-transparent border-none outline-none text-sm text-text-primary px-3 py-1 truncate cursor-pointer"
              />
            </div>
          </div>
        )}

        {/* Right: Actions */}
        <div className="flex items-center gap-5 shrink-0">
          {/* Status Badge */}
          {isDashboard ? (
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border border-border shadow-sm bg-white/50
              ${pipelineStatus === "running" ? "shadow-[0_0_10px_rgba(37,99,235,0.1)] border-primary/20" : ""}
            `}>
              <CircleDot className={`w-3.5 h-3.5 ${
                pipelineStatus === "running" ? "text-primary animate-pulse" : 
                pipelineStatus === "failed" ? "text-error" : "text-success"
              }`} />
              <span className="text-[11px] font-bold tracking-widest uppercase font-mono text-text-primary">
                {pipelineStatus === "running" ? "Analyzing" : pipelineStatus === "failed" ? "Failed" : "Online"}
              </span>
            </div>
          ) : (
            <div className="hidden sm:block px-2.5 py-1 rounded-md text-[10px] font-mono font-bold tracking-widest uppercase bg-bg-muted text-text-muted border border-border">
              v2.0 Beta
            </div>
          )}

          {!isDashboard && (
            <Link
              to="/dashboard"
              className="text-sm font-semibold text-text-primary hover:text-primary transition-colors flex items-center gap-1.5 bg-bg-muted hover:bg-primary/5 px-4 py-2 rounded-full border border-border hover:border-primary/30"
            >
              Enter Dashboard <span className="text-lg leading-none">→</span>
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

import { useState } from "react";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import usePipeline from "../../hooks/usePipeline";
import { Edit2, RotateCcw, CheckCircle2, CircleDashed, TerminalSquare, Search, Filter, Globe, Database, Copy, Brain, HandCoins, BarChart3, FileText, Bot } from "lucide-react";

const iconMap = {
  planning: Brain,
  searching: Search,
  filtering: Filter,
  browsing: Globe,
  extracting: Database,
  deduplicating: Copy,
  sentiment: Bot,
  deal_detection: HandCoins,
  ranking: BarChart3,
  summarizing: FileText,
};

export default function CommandPanel() {
  const query = useShoplyticsStore((s) => s.query);
  const setQuery = useShoplyticsStore((s) => s.setQuery);
  const agents = useShoplyticsStore((s) => s.agents);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const { launch } = usePipeline();

  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(query);

  const isRunning = pipelineStatus === "running";

  const handleRun = () => {
    if (!isRunning && editValue.trim()) {
      setQuery(editValue);
      launch(editValue);
      setIsEditing(false);
    }
  };

  return (
    <div className="flex flex-col h-full z-10 w-full min-h-0 min-w-0 font-sans">
      {/* Header & Status */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-bold text-text-primary uppercase tracking-wide">
          Command Info
        </h2>
        <div className="flex items-center justify-between px-2 py-0.5 rounded-full border border-border bg-bg-muted/50">
          <div className="flex items-center gap-1.5">
            <div
              className={`w-2 h-2 rounded-full ${
                isRunning ? "bg-primary animate-pulse" : pipelineStatus === "error" ? "bg-error" : "bg-success"
              }`}
            />
            <span className="text-[10px] font-mono font-medium tracking-wider text-text-primary uppercase">
              {isRunning ? "Running" : pipelineStatus === "failed" ? "Error" : "System Online"}
            </span>
          </div>
        </div>
      </div>

      {/* Query Box */}
      <div className="bg-bg-muted border border-border rounded-lg p-3 mb-6 relative">
        {isEditing ? (
          <textarea
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="w-full text-sm bg-white border border-primary/40 rounded p-2 focus:outline-none focus:ring-2 focus:ring-primary/20 text-text-primary resize-none"
            rows={3}
            autoFocus
            onBlur={() => {
              if (editValue.trim() !== query) {
                setQuery(editValue);
              }
              setIsEditing(false);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleRun();
              }
            }}
          />
        ) : (
          <div className="text-sm font-medium text-text-primary leading-snug line-clamp-3">
            {query || "Enter a query from the landing page"}
          </div>
        )}

        <div className="mt-3 flex gap-2">
          {!isEditing && (
            <button
              onClick={() => {
                setEditValue(query);
                setIsEditing(true);
              }}
              className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold text-text-muted hover:text-primary hover:bg-primary/5 rounded transition-colors"
            >
              <Edit2 className="w-3 h-3" /> Edit
            </button>
          )}
          <button
            onClick={handleRun}
            disabled={isRunning || !editValue.trim()}
            className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold text-text-muted hover:text-primary hover:bg-primary/5 rounded transition-colors disabled:opacity-50"
          >
            <RotateCcw className={`w-3 h-3 ${isRunning ? "animate-spin" : ""}`} /> 
            Run Again
          </button>
        </div>
      </div>

      <h2 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-3">
        Pipeline
      </h2>
      <div className="flex-1 overflow-y-auto space-y-1 w-full relative h-[400px]">
        {agents.map((agent) => {
          const Icon = iconMap[agent.key] || TerminalSquare;
          const isActive = agent.status === "running";
          const isDone = agent.status === "done";
          const isError = agent.status === "error";

          return (
            <div
              key={agent.key}
              className={`flex items-center justify-between p-2 rounded-lg transition-all ${
                isActive ? "bg-primary/5 border-l-2 border-primary" : "border-l-2 border-transparent"
              } ${isDone ? "opacity-60" : ""}`}
            >
              <div className="flex items-center gap-2.5">
                <Icon
                  className={`w-4 h-4 ${
                    isActive ? "text-primary" : isDone ? "text-success" : isError ? "text-error" : "text-text-muted"
                  }`}
                />
                <span
                  className={`text-sm font-semibold ${
                    isActive ? "text-primary" : "text-text-primary"
                  }`}
                >
                  {agent.name}
                </span>
              </div>
              <div className="w-4 h-4 rounded-full flex items-center justify-center">
                {isDone && <CheckCircle2 className="w-4 h-4 text-success" />}
                {isError && <div className="w-3 h-3 rounded-full bg-error" />}
                {isActive && <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />}
                {!isDone && !isError && !isActive && <CircleDashed className="w-4 h-4 text-border" />}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

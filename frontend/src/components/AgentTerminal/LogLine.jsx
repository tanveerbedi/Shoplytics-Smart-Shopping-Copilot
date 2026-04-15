const SOURCE_COLORS = {
  planner: "text-accent-purple",
  search: "text-accent-amber",
  domain_filter: "text-accent-amber",
  browser: "text-accent-cyan",
  extractor: "text-accent-green",
  deduplicator: "text-blue-400",
  sentiment: "text-pink-400",
  deal: "text-accent-amber",
  ranker: "text-violet-400",
  analyst: "text-violet-400",
  summarizer: "text-emerald-400",
  system: "text-text-dim",
};

const LEVEL_COLORS = {
  info: "text-text-muted",
  warn: "text-accent-amber",
  error: "text-accent-red",
};

export default function LogLine({ log, index }) {
  const agentName = (log.agent || "system").toUpperCase();
  const agentColor = SOURCE_COLORS[log.agent?.toLowerCase()] || SOURCE_COLORS.system;
  const contentColor = LEVEL_COLORS[log.level] || LEVEL_COLORS.info;

  const time = log.timestamp
    ? new Date(log.timestamp).toLocaleTimeString("en-IN", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "";

  return (
    <div className="flex gap-2 py-0.5 hover:bg-white/[0.02] px-1 rounded group transition-colors">
      {/* Timestamp */}
      <span className="text-text-dim text-[10px] w-16 flex-shrink-0 opacity-50 group-hover:opacity-100 transition-opacity tabular-nums">
        {time}
      </span>

      {/* Agent tag */}
      <span
        className={`text-[10px] font-semibold w-20 flex-shrink-0 tracking-wider ${agentColor}`}
      >
        [{agentName}]
      </span>

      {/* Content */}
      <span className={`text-[11px] leading-relaxed break-all ${contentColor}`}>
        {log.content}
      </span>
    </div>
  );
}

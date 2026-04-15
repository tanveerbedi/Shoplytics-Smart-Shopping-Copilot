import { useEffect, useRef } from "react";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import { Terminal } from "lucide-react";

export default function AgentTerminal() {
  const logs = useShoplyticsStore((s) => s.logs);
  const bottomRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs.length]);

  return (
    <div className="flex flex-col h-full bg-terminal overflow-hidden text-white font-mono z-10 w-full min-h-0 min-w-0 rounded-xl max-h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-white/[0.04]">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-white/50" />
          <div className="text-[10px] font-bold tracking-widest uppercase text-white/50">
            Agent Terminal
          </div>
        </div>
        <div className="text-[10px] text-white/40 bg-white/5 px-2 py-0.5 rounded-full">{logs.length} Lines</div>
      </div>

      {/* Log Area */}
      <div className="flex-1 overflow-y-auto p-4 terminal-scrollbar text-[11px] leading-relaxed break-words break-all">
        {logs.length === 0 ? (
          <div className="text-white/30 h-full flex items-center justify-center font-sans text-sm">
            Awaiting commands...
          </div>
        ) : (
          <div className="space-y-1.5">
            {logs.map((log, i) => {
              const agentName = (log.agent || "system").toUpperCase();
              let tagColor = "text-white/30";
              if (agentName.includes("BROWSER")) tagColor = "text-[#22d3ee]"; // cyan-400
              else if (agentName.includes("EXTRACTOR")) tagColor = "text-[#4ade80]"; // green-400
              else if (agentName.includes("PLANNER")) tagColor = "text-[#60a5fa]"; // blue-400
              else if (agentName.includes("ERROR") || log.level === "error") tagColor = "text-[#f87171]"; // red-400

              return (
                <div key={i} className="flex gap-2.5 font-mono break-words whitespace-pre-wrap hover:bg-white/[0.02] px-1 -mx-1 rounded transition-colors group">
                  <span className={`w-[85px] flex-shrink-0 font-bold ${tagColor}`}>
                    [{agentName}]
                  </span>
                  <span className="text-white/80 group-hover:text-white transition-colors">{log.content}</span>
                </div>
              );
            })}
            <div className="flex gap-2 font-mono mt-2">
              <span className="w-[85px] flex-shrink-0" />
              <span className="animate-blink text-white/60">█</span>
            </div>
            <div ref={bottomRef} className="h-1" />
          </div>
        )}
      </div>
    </div>
  );
}

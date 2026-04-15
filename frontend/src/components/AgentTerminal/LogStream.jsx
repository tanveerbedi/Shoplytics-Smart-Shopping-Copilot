import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import LogLine from "./LogLine";

export default function LogStream() {
  const logs = useShoplyticsStore((s) => s.logs);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const bottomRef = useRef(null);
  const containerRef = useRef(null);

  // Auto-scroll to bottom on new logs
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs.length]);

  const isIdle = pipelineStatus === "idle";
  const isActive = pipelineStatus === "running";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15, duration: 0.4 }}
      className="flex flex-col h-full"
    >
      {/* Terminal header bar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-bg-border bg-bg-card/50">
        <div className="flex items-center gap-2">
          <span className="text-accent-cyan text-xs font-mono">▸</span>
          <h2 className="text-xs font-mono font-semibold tracking-widest uppercase text-text-muted">
            Agent Terminal
          </h2>
        </div>
        <div className="flex items-center gap-3">
          {isActive && (
            <span className="text-[9px] font-mono text-accent-green animate-pulse">
              ● LIVE
            </span>
          )}
          <span className="text-[9px] font-mono text-text-dim">
            {logs.length} lines
          </span>
        </div>
      </div>

      {/* Log area */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto terminal-gradient scanline p-3 font-mono min-h-0"
      >
        {isIdle && logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-text-dim">
            <div className="text-3xl mb-3 opacity-20">⚡</div>
            <span className="text-[11px] font-mono tracking-wider">
              AWAITING COMMANDS
            </span>
            <span className="text-[9px] font-mono mt-1 text-text-dim/50">
              Enter a query and launch agents to begin
            </span>
          </div>
        ) : (
          <>
            <AnimatePresence mode="popLayout">
              {logs.map((log, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -4 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <LogLine log={log} index={i} />
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Blinking cursor at bottom */}
            {isActive && (
              <div className="flex items-center gap-1 mt-1 px-1">
                <span className="text-accent-cyan text-[10px] font-mono">❯</span>
                <span className="cursor-blink" />
              </div>
            )}

            <div ref={bottomRef} />
          </>
        )}
      </div>
    </motion.div>
  );
}

import { useState } from "react";
import { motion } from "framer-motion";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import usePipeline from "../../hooks/usePipeline";
import GlowButton from "../shared/GlowButton";

export default function QueryInput() {
  const query = useShoplyticsStore((s) => s.query);
  const setQuery = useShoplyticsStore((s) => s.setQuery);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const resetTask = useShoplyticsStore((s) => s.resetTask);
  const { launch } = usePipeline();

  const [isFocused, setIsFocused] = useState(false);
  const isRunning = pipelineStatus === "running";

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isRunning) {
      launch(query);
    }
  };

  const handleReset = () => {
    resetTask();
    setQuery("");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1, duration: 0.4 }}
    >
      <div className="mb-3 flex items-center gap-2">
        <span className="text-accent-cyan text-xs font-mono">▸</span>
        <h2 className="text-xs font-mono font-semibold tracking-widest uppercase text-text-muted">
          Command Input
        </h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div
          className={`relative rounded border transition-all duration-300 ${
            isFocused
              ? "border-accent-cyan/60 shadow-glow-cyan"
              : "border-bg-border"
          }`}
        >
          <textarea
            id="query-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Find best 4K TVs under ₹40,000 across Amazon, Flipkart, Croma..."
            disabled={isRunning}
            rows={3}
            className="w-full bg-bg/80 text-text-primary placeholder-text-dim
              text-sm font-mono p-3 rounded resize-none
              focus:outline-none disabled:opacity-50"
          />
          {/* Typing indicator */}
          {isFocused && (
            <div className="absolute bottom-2 right-3 flex items-center gap-1">
              <span className="text-[9px] text-text-dim font-mono">
                SHIFT+ENTER for newline
              </span>
            </div>
          )}
        </div>

        <div className="mt-3 flex gap-2">
          <GlowButton
            onClick={() => handleSubmit({ preventDefault: () => {} })}
            disabled={!query.trim() || isRunning}
            variant="cyan"
          >
            {isRunning ? (
              <>
                <span className="inline-block w-3 h-3 border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full animate-spin" />
                AGENTS RUNNING
              </>
            ) : (
              <>
                <span>⚡</span>
                LAUNCH AGENTS
              </>
            )}
          </GlowButton>

          {(pipelineStatus === "completed" || pipelineStatus === "failed") && (
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={handleReset}
              className="px-3 py-2 text-[10px] font-mono text-text-muted border border-bg-border
                rounded hover:border-text-dim hover:text-text-primary transition-all cursor-pointer"
            >
              RESET
            </motion.button>
          )}
        </div>
      </form>
    </motion.div>
  );
}

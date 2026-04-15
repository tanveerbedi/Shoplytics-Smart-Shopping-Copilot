import { motion } from "framer-motion";
import useShoplyticsStore from "../../store/useShoplyticsStore";

const SUGGESTIONS = [
  "Compare iPhone 15 prices across Amazon and Flipkart",
  "Best noise cancelling headphones under ₹15,000",
  "Find cheapest MacBook Air M2 deals in India",
  "Samsung Galaxy S24 price comparison across stores",
  "Best 4K Smart TVs under ₹40,000",
  "Gaming laptop deals under ₹80,000",
];

export default function SuggestedQueries() {
  const setQuery = useShoplyticsStore((s) => s.setQuery);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const isRunning = pipelineStatus === "running";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3, duration: 0.4 }}
      className="mt-4"
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] font-mono text-text-dim tracking-widest uppercase">
          Suggested
        </span>
        <div className="flex-1 h-px bg-bg-border" />
      </div>

      <div className="flex flex-col gap-1">
        {SUGGESTIONS.map((s, i) => (
          <motion.button
            key={s}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.35 + i * 0.05 }}
            onClick={() => !isRunning && setQuery(s)}
            disabled={isRunning}
            className={`
              text-left text-[11px] font-mono px-2.5 py-1.5
              rounded border border-transparent
              transition-all duration-200
              ${
                isRunning
                  ? "text-text-dim cursor-not-allowed"
                  : "text-text-muted hover:text-accent-cyan hover:border-bg-border hover:bg-bg-card cursor-pointer"
              }
            `}
          >
            <span className="text-text-dim mr-1.5">›</span>
            {s}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

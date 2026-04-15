import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import useShoplyticsStore from "../../store/useShoplyticsStore";

export default function AIDecisionBox() {
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const recommendation = useShoplyticsStore((s) => s.recommendation);
  const summary = useShoplyticsStore((s) => s.summary);

  const isIdle = pipelineStatus === "idle";
  const isRunning = pipelineStatus === "running";
  const isComplete = pipelineStatus === "completed";
  const isFailed = pipelineStatus === "failed";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3, duration: 0.4 }}
      className="flex flex-col border-t border-bg-border"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 bg-bg-card/30">
        <span className="text-accent-green text-xs font-mono">▸</span>
        <h3 className="text-xs font-mono font-semibold tracking-widest uppercase text-text-muted">
          AI Decision Intelligence
        </h3>
      </div>

      {/* Content */}
      <div className="px-3 py-3 overflow-y-auto max-h-48 font-mono text-[11px]">
        {isIdle && (
          <p className="text-text-dim text-center py-4">
            AI reasoning will appear here after analysis
          </p>
        )}

        {isRunning && (
          <div className="flex flex-col items-center gap-3 py-4">
            <div className="flex gap-1">
              {[0, 1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="w-1 h-4 bg-accent-cyan/40 rounded-full wave-bar"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
            <span className="text-text-dim text-[10px] tracking-wider">
              AI ANALYZING MARKET DATA...
            </span>
          </div>
        )}

        {isFailed && (
          <div className="text-accent-red text-center py-4">
            <span className="text-lg block mb-1">✗</span>
            Pipeline encountered an error. Check terminal logs above.
          </div>
        )}

        {isComplete && (recommendation || summary) && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {summary && (
              <div className="mb-3 text-text-muted leading-relaxed text-[11px]">
                <ReactMarkdown className="recommendation-md">
                  {summary}
                </ReactMarkdown>
              </div>
            )}
            {recommendation && (
              <div className="border-t border-bg-border pt-3">
                <div className="text-[9px] text-accent-green tracking-widest uppercase mb-2 font-semibold">
                  ⚡ Recommendation
                </div>
                <ReactMarkdown className="recommendation-md">
                  {recommendation}
                </ReactMarkdown>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

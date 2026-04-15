import { motion } from "framer-motion";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import StatusDot from "../shared/StatusDot";

export default function ExecutionPipeline() {
  const agents = useShoplyticsStore((s) => s.agents);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);

  const statusText = {
    idle: "",
    running: "ACTIVE",
    done: "DONE",
    error: "FAIL",
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.4, duration: 0.4 }}
      className="mt-5"
    >
      <div className="flex items-center gap-2 mb-3">
        <span className="text-accent-cyan text-xs font-mono">▸</span>
        <h2 className="text-xs font-mono font-semibold tracking-widest uppercase text-text-muted">
          Pipeline
        </h2>
        {pipelineStatus === "running" && (
          <span className="ml-auto text-[9px] font-mono text-accent-cyan animate-pulse tracking-wider">
            EXECUTING
          </span>
        )}
      </div>

      <div className="border border-bg-border rounded bg-bg/50 p-2 space-y-0.5">
        {agents.map((agent, idx) => {
          const isActive = agent.status === "running";
          const isDone = agent.status === "done";
          const isError = agent.status === "error";

          return (
            <motion.div
              key={agent.key}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.45 + idx * 0.04 }}
              className={`
                flex items-center gap-2.5 px-2.5 py-1.5 rounded text-xs font-mono
                transition-all duration-300
                ${isActive ? "bg-accent-cyan/8 border border-accent-cyan/20 text-accent-cyan" : ""}
                ${isDone ? "text-text-muted" : ""}
                ${isError ? "text-accent-red" : ""}
                ${!isActive && !isDone && !isError ? "text-text-dim" : ""}
              `}
            >
              {/* Icon */}
              <span className="text-sm w-5 text-center flex-shrink-0">
                {isDone ? (
                  <span className="text-accent-green">✓</span>
                ) : isError ? (
                  <span className="text-accent-red">✗</span>
                ) : (
                  agent.icon
                )}
              </span>

              {/* Name */}
              <span className={`flex-1 text-[11px] ${isActive ? "font-semibold" : ""}`}>
                {agent.name}
              </span>

              {/* Status dot */}
              <StatusDot status={agent.status} size="sm" />

              {/* Status label for active/done/error */}
              {agent.status !== "idle" && (
                <span
                  className={`text-[9px] tracking-wider font-semibold w-10 text-right ${
                    isActive ? "text-accent-cyan" : isDone ? "text-accent-green/60" : "text-accent-red/60"
                  }`}
                >
                  {statusText[agent.status] || ""}
                </span>
              )}
            </motion.div>
          );
        })}

        {/* Connecting line decoration */}
        {pipelineStatus !== "idle" && (
          <div className="mt-2 pt-2 border-t border-bg-border flex items-center justify-between px-2">
            <span className="text-[9px] font-mono text-text-dim">
              {agents.filter((a) => a.status === "done").length}/{agents.length} COMPLETE
            </span>
            <div className="w-20 h-1 bg-bg-border rounded overflow-hidden">
              <motion.div
                className="h-full bg-accent-cyan rounded"
                initial={{ width: "0%" }}
                animate={{
                  width: `${(agents.filter((a) => a.status === "done").length / agents.length) * 100}%`,
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

import { motion } from "framer-motion";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import StatusDot from "./StatusDot";

export default function Header() {
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const taskId = useShoplyticsStore((s) => s.taskId);

  const statusLabel = {
    idle: "STANDBY",
    running: "ACTIVE",
    completed: "COMPLETE",
    failed: "ERROR",
  };

  const statusColor = {
    idle: "text-text-muted",
    running: "text-accent-cyan",
    completed: "text-accent-green",
    failed: "text-accent-red",
  };

  return (
    <motion.header
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="relative z-20 flex items-center justify-between px-6 py-3 border-b border-bg-border bg-bg-panel/60 backdrop-blur-md"
    >
      {/* Left: Logo */}
      <div className="flex items-center gap-3">
        <span className="text-xl">⚡</span>
        <div className="flex flex-col leading-tight">
          <span className="text-base font-display font-bold tracking-tight text-text-primary">
            SHOPLYTICS
          </span>
          <span className="text-[10px] font-mono text-text-dim tracking-widest uppercase">
            AI Product Intelligence
          </span>
        </div>
      </div>

      {/* Center: Version + pipeline indicator */}
      <div className="hidden md:flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1 border border-bg-border rounded bg-bg/50">
          <span className="text-[10px] text-text-dim font-mono">SYS</span>
          <span className="text-[10px] text-accent-cyan font-mono">v2.0</span>
        </div>
        {taskId && (
          <div className="flex items-center gap-2 px-3 py-1 border border-bg-border rounded bg-bg/50">
            <span className="text-[10px] text-text-dim font-mono">TASK</span>
            <span className="text-[10px] text-accent-amber font-mono">
              {taskId}
            </span>
          </div>
        )}
      </div>

      {/* Right: Status */}
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center gap-2 px-3 py-1.5 border border-bg-border rounded ${statusColor[pipelineStatus]}`}
        >
          <StatusDot
            status={
              pipelineStatus === "running"
                ? "running"
                : pipelineStatus === "completed"
                ? "done"
                : pipelineStatus === "failed"
                ? "error"
                : "idle"
            }
            size="sm"
          />
          <span className="text-[11px] font-mono font-semibold tracking-widest">
            {statusLabel[pipelineStatus] || "STANDBY"}
          </span>
        </div>
      </div>
    </motion.header>
  );
}

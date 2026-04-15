import { motion } from "framer-motion";

const colorMap = {
  idle: "bg-text-dim",
  running: "bg-accent-cyan",
  done: "bg-accent-green",
  error: "bg-accent-red",
  processing: "bg-accent-amber",
};

const glowMap = {
  running: "shadow-glow-cyan",
  done: "",
  error: "shadow-glow-red",
  processing: "shadow-glow-amber",
};

export default function StatusDot({ status = "idle", size = "sm" }) {
  const sizeClass = size === "lg" ? "w-3 h-3" : "w-2 h-2";
  const color = colorMap[status] || colorMap.idle;
  const glow = glowMap[status] || "";
  const shouldPulse = status === "running" || status === "processing";

  return (
    <motion.span
      className={`inline-block rounded-full ${sizeClass} ${color} ${glow} ${
        shouldPulse ? "dot-pulse" : ""
      }`}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
    />
  );
}

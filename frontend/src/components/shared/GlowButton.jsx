import { motion } from "framer-motion";

export default function GlowButton({
  children,
  onClick,
  disabled = false,
  variant = "cyan",
  className = "",
}) {
  const variants = {
    cyan: {
      base: "border-accent-cyan/30 text-accent-cyan",
      hover: "hover:border-accent-cyan hover:shadow-glow-cyan",
      bg: "bg-accent-cyan/5",
      activeBg: "hover:bg-accent-cyan/10",
    },
    green: {
      base: "border-accent-green/30 text-accent-green",
      hover: "hover:border-accent-green hover:shadow-glow-green",
      bg: "bg-accent-green/5",
      activeBg: "hover:bg-accent-green/10",
    },
  };

  const v = variants[variant] || variants.cyan;

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`
        glow-btn relative w-full px-5 py-3 font-mono text-sm font-semibold
        tracking-wider uppercase border rounded
        transition-all duration-300
        ${v.base} ${v.bg} ${v.activeBg}
        ${disabled ? "opacity-40 cursor-not-allowed" : `cursor-pointer ${v.hover}`}
        ${className}
      `}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </motion.button>
  );
}

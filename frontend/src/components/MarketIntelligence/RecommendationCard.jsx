import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";

export default function RecommendationCard({ recommendation, products }) {
  if (!recommendation && (!products || products.length === 0)) return null;

  // Find the best deal product
  const bestDeal =
    products?.find((p) => p.deal_tag === "Best Value") ||
    products?.reduce(
      (min, p) =>
        p.price_numeric && (!min || p.price_numeric < min.price_numeric)
          ? p
          : min,
      null
    );

  // Calculate stats
  const totalProducts = products?.length || 0;
  const avgPrice =
    products && products.length > 0
      ? products.reduce((sum, p) => sum + (p.price_numeric || 0), 0) /
        products.filter((p) => p.price_numeric).length
      : 0;
  const storesSet = new Set(
    products
      ?.map(
        (p) =>
          p.source_site ||
          p.source_url?.match(/\/\/(?:www\.)?([^/]+)/)?.[1] ||
          ""
      )
      .filter(Boolean)
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.5 }}
      className="space-y-3"
    >
      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2">
        <div className="border border-bg-border rounded p-3 bg-bg-card/50 text-center">
          <div className="text-lg font-display font-bold text-text-primary">
            {totalProducts}
          </div>
          <div className="text-[8px] font-mono text-text-dim tracking-widest uppercase mt-0.5">
            Products
          </div>
        </div>
        <div className="border border-bg-border rounded p-3 bg-bg-card/50 text-center">
          <div className="text-lg font-display font-bold text-text-primary">
            {avgPrice > 0 ? `₹${Math.round(avgPrice).toLocaleString("en-IN")}` : "—"}
          </div>
          <div className="text-[8px] font-mono text-text-dim tracking-widest uppercase mt-0.5">
            Avg Price
          </div>
        </div>
        <div className="border border-bg-border rounded p-3 bg-bg-card/50 text-center">
          <div className="text-lg font-display font-bold text-text-primary">
            {storesSet.size}
          </div>
          <div className="text-[8px] font-mono text-text-dim tracking-widest uppercase mt-0.5">
            Stores
          </div>
        </div>
      </div>

      {/* Best deal highlight */}
      {bestDeal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="relative overflow-hidden border border-accent-green/20 rounded bg-accent-green/[0.03] p-4"
        >
          {/* Top accent line */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-accent-green via-accent-cyan to-accent-green" />

          <div className="flex items-center gap-2 mb-2">
            <span className="text-[9px] font-mono font-bold text-accent-green tracking-widest uppercase">
              🏆 Top Pick
            </span>
          </div>
          <div className="text-sm font-mono text-text-primary font-semibold leading-snug mb-1 line-clamp-2">
            {bestDeal.name}
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-xl font-display font-bold text-accent-green text-glow-green">
              {bestDeal.price_numeric
                ? `₹${bestDeal.price_numeric.toLocaleString("en-IN")}`
                : bestDeal.price || "—"}
            </span>
            <span className="text-[10px] font-mono text-text-dim">
              {bestDeal.source_site ||
                bestDeal.source_url?.match(/\/\/(?:www\.)?([^/]+)/)?.[1] ||
                ""}
            </span>
            {bestDeal.rating && (
              <span className="text-[10px] font-mono text-accent-amber">
                {bestDeal.rating}★
              </span>
            )}
          </div>
          {bestDeal.product_url && (
            <a
              href={bestDeal.product_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 mt-3 px-4 py-1.5 text-[10px] font-mono font-semibold
                tracking-wider uppercase border border-accent-green/30 text-accent-green rounded
                hover:bg-accent-green/10 hover:border-accent-green/60 transition-all"
            >
              BUY NOW →
            </a>
          )}
        </motion.div>
      )}

      {/* Full recommendation text */}
      {recommendation && (
        <div className="border border-bg-border rounded p-3 bg-bg-card/30">
          <div className="text-[9px] font-mono text-accent-cyan tracking-widest uppercase mb-2 font-semibold">
            AI Analysis
          </div>
          <div className="text-[11px] font-mono leading-relaxed">
            <ReactMarkdown className="recommendation-md">
              {recommendation}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </motion.div>
  );
}

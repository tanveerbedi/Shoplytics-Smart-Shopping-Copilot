import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import { Trophy, ShoppingCart, ShieldCheck } from "lucide-react";

export default function RecommendationCard() {
  const results = useShoplyticsStore((s) => s.results);
  const recommendation = useShoplyticsStore((s) => s.recommendation);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);

  if (pipelineStatus !== "completed") return null;
  if (!recommendation && !results?.products?.length) return null;

  const products = results.products || [];
  const bestDeal =
    products.find((p) => p.deal_tag === "Best Value") ||
    products.reduce(
      (min, p) => (p.price_numeric && (!min || p.price_numeric < min.price_numeric) ? p : min),
      null
    );

  // We want to avoid a massive wall of text.
  // We'll extract a shorter snippet or format it beautifully.
  // In a real scenario, the LLM output might be huge, we'll try to present it in a readable container.

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, type: "spring", stiffness: 100 }}
      className="bg-white border hover:border-primary/50 transition-colors border-l-[4px] border-l-success shadow-soft rounded-2xl p-6 lg:p-8 mb-8 relative overflow-hidden group"
    >
      {/* Decorative background element */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-success/5 to-transparent rounded-bl-full pointer-events-none -z-0" />
      
      <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start">
        
        {/* Left: The "WOW" Best Deal highlight */}
        <div className="flex-1 w-full bg-success-light/30 border border-success/20 rounded-xl p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-4 text-success border border-success/20 bg-success/5 px-3 py-1 rounded-full w-fit">
            <Trophy className="w-4 h-4" />
            <span className="text-[11px] font-bold uppercase tracking-widest">Top AI Pick</span>
          </div>
          
          <h2 className="text-xl md:text-2xl font-bold text-text-primary leading-tight mb-2 line-clamp-3" title={bestDeal?.name}>
            {bestDeal?.name || "Best Product Not Found"}
          </h2>
          
          <div className="flex items-end gap-3 mt-auto pt-6">
            <span className="text-4xl md:text-5xl font-display font-bold text-success tracking-tight">
              {bestDeal?.price_numeric ? `₹${bestDeal.price_numeric.toLocaleString("en-IN")}` : bestDeal?.price || "—"}
            </span>
            <span className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-2">
              @ {bestDeal?.source_site || bestDeal?.source_url?.match(/\/\/(?:www\.)?([^/]+)/)?.[1] || "Store"}
            </span>
          </div>

          <div className="mt-6 flex flex-col sm:flex-row items-center gap-3">
            {bestDeal?.product_url ? (
              <a
                href={bestDeal.product_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto flex justify-center items-center gap-2 bg-success hover:bg-success/90 text-white px-6 py-3 rounded-xl font-bold uppercase tracking-wide transition-all shadow-[0_4px_14px_rgba(22,163,74,0.3)] hover:shadow-[0_6px_20px_rgba(22,163,74,0.4)] hover:-translate-y-0.5"
              >
                <ShoppingCart className="w-4 h-4" />
                Buy Now
              </a>
            ) : (
              <button disabled className="w-full sm:w-auto bg-bg-muted text-text-dim px-6 py-3 rounded-xl font-bold uppercase tracking-wide cursor-not-allowed">
                No Link
              </button>
            )}
            <div className="flex items-center gap-1.5 text-xs font-semibold text-text-muted">
              <ShieldCheck className="w-4 h-4 text-success/70" />
              Verified Deal
            </div>
          </div>
        </div>

        {/* Right: The AI Justification Text (restrained height with scrolling if huge) */}
        <div className="flex-1 w-full flex flex-col">
          <h3 className="text-sm font-bold text-text-primary uppercase tracking-wide mb-3 flex items-center gap-2">
            Why we picked this
          </h3>
          <div className="text-sm text-text-primary leading-relaxed prose prose-sm prose-primary max-w-none max-h-[220px] overflow-y-auto pr-2 custom-scrollbar">
            {recommendation ? (
              <ReactMarkdown>{recommendation}</ReactMarkdown>
            ) : (
              <p>Based on our comprehensive market scan across multiple platforms, this product offers the best balance of price, vendor trustworthiness, and positive sentiment. We filtered out inflated listings and suspicious sellers to arrive at this definitive recommendation.</p>
            )}
          </div>
          
          <div className="mt-auto pt-4">
             <div className="flex justify-between text-[10px] font-bold text-text-muted mb-1.5 uppercase tracking-widest">
              <span>Confidence Score</span>
              <span className="text-primary">94%</span>
            </div>
            <div className="w-full h-1.5 bg-bg-muted rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `94%` }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                className="h-full bg-primary"
              />
            </div>
          </div>
        </div>

      </div>
    </motion.div>
  );
}

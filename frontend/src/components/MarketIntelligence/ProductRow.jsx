import { motion } from "framer-motion";

export default function ProductRow({ product, index, isBestDeal }) {
  const price = product.price_numeric || product.price || "—";
  const priceDisplay =
    typeof price === "number" ? `₹${price.toLocaleString("en-IN")}` : price;
  const rating = product.rating ? `${product.rating}★` : "—";
  const site = product.source_site || product.source_url?.match(/\/\/(?:www\.)?([^/]+)/)?.[1] || "—";
  const dealTag = product.deal_tag || "";
  const sentiment = product.sentiment_indicator || "";

  const dealColors = {
    "Best Value": "text-accent-green border-accent-green/30 bg-accent-green/5",
    Premium: "text-accent-amber border-accent-amber/30 bg-accent-amber/5",
    Average: "text-text-muted border-bg-border bg-bg-card",
    Overpriced: "text-accent-red border-accent-red/30 bg-accent-red/5",
  };

  return (
    <motion.tr
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.05 * index, duration: 0.3 }}
      className={`
        group border-b border-bg-border/50 transition-all duration-200
        hover:bg-accent-cyan/[0.03]
        ${isBestDeal ? "bg-accent-green/[0.04]" : ""}
      `}
    >
      {/* Rank */}
      <td className="py-2.5 px-2 text-center">
        <span
          className={`text-[10px] font-mono font-bold ${
            isBestDeal ? "text-accent-green" : "text-text-dim"
          }`}
        >
          {String(index + 1).padStart(2, "0")}
        </span>
      </td>

      {/* Product Name */}
      <td className="py-2.5 px-2 max-w-[220px]">
        <div className="flex flex-col gap-0.5">
          {product.product_url ? (
            <a
              href={product.product_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] font-mono text-text-primary hover:text-accent-cyan transition-colors truncate block"
              title={product.name}
            >
              {product.name}
            </a>
          ) : (
            <span
              className="text-[11px] font-mono text-text-primary truncate block"
              title={product.name}
            >
              {product.name}
            </span>
          )}
          {product.brand && (
            <span className="text-[9px] text-text-dim">{product.brand}</span>
          )}
        </div>
      </td>

      {/* Price */}
      <td className="py-2.5 px-2">
        <span
          className={`text-xs font-mono font-semibold ${
            isBestDeal ? "text-accent-green text-glow-green" : "text-text-primary"
          }`}
        >
          {priceDisplay}
        </span>
      </td>

      {/* Store */}
      <td className="py-2.5 px-2">
        <span className="text-[10px] font-mono text-text-muted">{site}</span>
      </td>

      {/* Rating */}
      <td className="py-2.5 px-2">
        <span className="text-[10px] font-mono text-accent-amber">{rating}</span>
      </td>

      {/* Deal Tag */}
      <td className="py-2.5 px-2">
        {dealTag && (
          <span
            className={`inline-block text-[8px] font-mono font-bold tracking-wider uppercase px-1.5 py-0.5 rounded border ${
              dealColors[dealTag] || dealColors.Average
            }`}
          >
            {dealTag}
          </span>
        )}
      </td>

      {/* Sentiment */}
      <td className="py-2.5 px-2">
        {sentiment && (
          <span className="text-[9px] font-mono text-text-muted">{sentiment}</span>
        )}
      </td>

      {/* Link */}
      <td className="py-2.5 px-2">
        {product.product_url && (
          <a
            href={product.product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[9px] font-mono text-accent-cyan/60 hover:text-accent-cyan transition-colors tracking-wider"
          >
            VIEW →
          </a>
        )}
      </td>

      {/* Best deal indicator line */}
      {isBestDeal && (
        <td className="absolute left-0 top-0 bottom-0 w-[2px] bg-accent-green" />
      )}
    </motion.tr>
  );
}

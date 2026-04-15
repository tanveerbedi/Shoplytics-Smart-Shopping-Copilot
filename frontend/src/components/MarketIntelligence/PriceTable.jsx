import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import ProductRow from "./ProductRow";

export default function PriceTable({ products }) {
  const [sortKey, setSortKey] = useState("price_numeric");
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  const sorted = useMemo(() => {
    if (!products || products.length === 0) return [];
    return [...products].sort((a, b) => {
      let va = a[sortKey];
      let vb = b[sortKey];

      // Handle nulls
      if (va == null) va = sortAsc ? Infinity : -Infinity;
      if (vb == null) vb = sortAsc ? Infinity : -Infinity;

      // String comparison
      if (typeof va === "string" && typeof vb === "string") {
        return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
      }

      return sortAsc ? va - vb : vb - va;
    });
  }, [products, sortKey, sortAsc]);

  // Best deal = product with deal_tag "Best Value" or lowest price
  const bestDealName = useMemo(() => {
    const bv = products?.find((p) => p.deal_tag === "Best Value");
    if (bv) return bv.name;
    const cheapest = products?.reduce(
      (min, p) =>
        p.price_numeric && (!min || p.price_numeric < min.price_numeric) ? p : min,
      null
    );
    return cheapest?.name || null;
  }, [products]);

  const columns = [
    { key: "index", label: "#", sortable: false },
    { key: "name", label: "PRODUCT", sortable: true },
    { key: "price_numeric", label: "PRICE", sortable: true },
    { key: "source_site", label: "STORE", sortable: true },
    { key: "rating", label: "RATING", sortable: true },
    { key: "deal_tag", label: "DEAL", sortable: true },
    { key: "sentiment_indicator", label: "SENTIMENT", sortable: false },
    { key: "link", label: "", sortable: false },
  ];

  if (!products || products.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.4 }}
      className="border border-bg-border rounded overflow-hidden"
    >
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-bg-card/80 border-b border-bg-border">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => col.sortable && handleSort(col.key)}
                  className={`
                    text-left text-[9px] font-mono font-semibold tracking-widest uppercase
                    px-2 py-2 text-text-dim
                    ${col.sortable ? "cursor-pointer hover:text-accent-cyan transition-colors" : ""}
                  `}
                >
                  <span className="flex items-center gap-1">
                    {col.label}
                    {col.sortable && sortKey === col.key && (
                      <span className="text-accent-cyan text-[8px]">
                        {sortAsc ? "▲" : "▼"}
                      </span>
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((product, i) => (
              <ProductRow
                key={product.name + i}
                product={product}
                index={i}
                isBestDeal={product.name === bestDealName}
              />
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

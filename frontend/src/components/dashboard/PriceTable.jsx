import { useState, useMemo } from "react";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import { ArrowUpDown, ShoppingCart } from "lucide-react";

export default function PriceTable() {
  const results = useShoplyticsStore((s) => s.results);
  const products = results?.products || [];

  const [sortKey, setSortKey] = useState("price_numeric");
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = (key) => {
    if (sortKey === key) setSortAsc(!sortAsc);
    else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  const sorted = useMemo(() => {
    if (!products.length) return [];
    return [...products].sort((a, b) => {
      let va = a[sortKey];
      let vb = b[sortKey];
      if (va == null) va = sortAsc ? Infinity : -Infinity;
      if (vb == null) vb = sortAsc ? Infinity : -Infinity;
      if (typeof va === "string" && typeof vb === "string") {
        return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
      }
      return sortAsc ? va - vb : vb - va;
    });
  }, [products, sortKey, sortAsc]);

  const bestDealName = useMemo(() => {
    const bv = products.find((p) => p.deal_tag === "Best Value");
    if (bv) return bv.name;
    const cheapest = products.reduce(
      (min, p) => (p.price_numeric && (!min || p.price_numeric < min.price_numeric) ? p : min),
      null
    );
    return cheapest?.name;
  }, [products]);

  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);

  if (pipelineStatus === "idle") {
    return null;
  }

  if (pipelineStatus === "running" && !products.length) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-text-muted">Gathering market data...</span>
        </div>
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-10 bg-bg-muted rounded animate-pulse w-full" style={{ animationDelay: `${i * 0.1}s` }} />
        ))}
      </div>
    );
  }

  if (!products.length) return null;

  const Th = ({ label, sortableKey }) => (
    <th
      onClick={() => handleSort(sortableKey)}
      className="text-left py-2 px-3 text-xs font-semibold text-text-muted uppercase tracking-wide border-b border-border cursor-pointer hover:bg-bg-muted/50 transition-colors select-none"
    >
      <div className="flex items-center gap-1">
        {label}
        <ArrowUpDown className={`w-3 h-3 ${sortKey === sortableKey ? "text-primary text-opacity-100" : "text-opacity-0"} transition-opacity`} />
      </div>
    </th>
  );

  return (
    <div className="w-full">
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr>
              <Th label="Product" sortableKey="name" />
              <Th label="Platform" sortableKey="source_site" />
              <Th label="Price" sortableKey="price_numeric" />
              <Th label="Rating" sortableKey="rating" />
            </tr>
          </thead>
          <tbody>
            {sorted.map((p, i) => {
              const isBest = p.name === bestDealName;
              return (
                <tr
                  key={i}
                  className={`border-b border-border/50 transition-colors group ${
                    isBest ? "bg-[#F0FDF4] hover:bg-[#dcfce7]" : "hover:bg-bg-muted"
                  }`}
                >
                  <td className="py-2.5 px-3 max-w-[160px]">
                    {p.product_url ? (
                      <a 
                        href={p.product_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="font-medium text-text-primary hover:text-primary transition-colors truncate block" 
                        title={p.name}
                      >
                        {p.name}
                      </a>
                    ) : (
                      <div className="font-medium text-text-primary truncate" title={p.name}>
                        {p.name}
                      </div>
                    )}
                    {isBest && (
                      <span className="inline-block mt-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold tracking-wider text-success bg-success-light uppercase border border-success/20">
                        🏆 Best Deal
                      </span>
                    )}
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                        p.source_site?.toLowerCase().includes("amazon")
                          ? "bg-orange-50 text-orange-600 border-orange-200"
                          : p.source_site?.toLowerCase().includes("flipkart")
                          ? "bg-blue-50 text-blue-600 border-blue-200"
                          : p.source_site?.toLowerCase().includes("croma")
                          ? "bg-red-50 text-red-600 border-red-200"
                          : "bg-bg-muted text-text-muted border-border"
                      }`}
                    >
                      {p.source_site || p.source_url?.match(/\/\/(?:www\.)?([^/]+)/)?.[1] || "Store"}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <div className={`font-semibold ${isBest ? "text-success" : "text-text-primary"}`}>
                      {p.price_numeric ? `₹${p.price_numeric.toLocaleString("en-IN")}` : p.price || "—"}
                    </div>
                  </td>
                  <td className="py-2.5 px-3">
                    <div className="text-warning font-medium">{p.rating ? `${p.rating}★` : "—"}</div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell, PieChart, Pie, Legend } from "recharts";
import { format } from "d3-format";

export default function MarketCharts({ products }) {
  if (!products || products.length === 0) return null;

  // Filter products that have valid numeric prices
  const pricedProducts = products
    .filter((p) => p.price_numeric != null && p.price_numeric > 0)
    .sort((a, b) => a.price_numeric - b.price_numeric)
    .slice(0, 10); // Show max 10 products for clarity

  // Find the cheapest for highlighting
  const minPrice = Math.min(...pricedProducts.map((p) => p.price_numeric));

  // Determine colors based on platform
  const getPlatformColor = (url = "") => {
    const lUrl = url.toLowerCase();
    if (lUrl.includes("amazon")) return "#F97316"; // orange
    if (lUrl.includes("flipkart")) return "#2563EB"; // blue
    if (lUrl.includes("croma")) return "#DC2626"; // red
    if (lUrl.includes("reliance")) return "#0D9488"; // teal
    return "#64748B"; // slate
  };

  // Aggregate data for Platform Distribution Donut Chart
  const platformCounts = products.reduce((acc, p) => {
    let site = p.source_site || p.source_url?.match(/\/\/(?:www\.)?([^/]+)/)?.[1] || "Other";
    site = site.toLowerCase();
    let label = "Other";
    if (site.includes("amazon")) label = "Amazon";
    else if (site.includes("flipkart")) label = "Flipkart";
    else if (site.includes("croma")) label = "Croma";
    else if (site.includes("reliance")) label = "Reliance";
    
    acc[label] = (acc[label] || 0) + 1;
    return acc;
  }, {});

  const platformData = Object.keys(platformCounts).map(key => ({
    name: key,
    value: platformCounts[key],
  }));

  // Format currency
  const formatINR = (val) => `₹${val.toLocaleString("en-IN")}`;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white/95 backdrop-blur border border-border shadow-panel p-3 rounded-lg max-w-[200px]">
          <p className="text-xs font-bold text-text-primary line-clamp-2 mb-1">{data.name}</p>
          <p className="text-lg font-display text-primary">{formatINR(data.price_numeric)}</p>
          <p className="text-[10px] text-text-muted mt-1 uppercase tracking-wider">{data.source_site}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      {/* Chart 1: Price Comparison Bar Chart */}
      <div className="bg-white rounded-xl border border-border shadow-panel p-5">
        <h3 className="text-sm font-bold text-text-primary mb-4 flex items-center gap-2">
          💰 Price Breakdown
        </h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={pricedProducts} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis 
                dataKey="source_site" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: "#64748B", fontWeight: 600 }}
                dy={10}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tickFormatter={(val) => `₹${val/1000}k`}
                tick={{ fontSize: 10, fill: "#94A3B8" }}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: "#F1F5F9" }} />
              <Bar dataKey="price_numeric" radius={[4, 4, 0, 0]} maxBarSize={40}>
                {pricedProducts.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.price_numeric === minPrice ? "#16A34A" : getPlatformColor(entry.source_site)} 
                    style={{ filter: entry.price_numeric === minPrice ? "drop-shadow(0px 4px 8px rgba(22, 163, 74, 0.4))" : "none" }}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 2: Platform Distribution */}
      <div className="bg-white rounded-xl border border-border shadow-panel p-5">
        <h3 className="text-sm font-bold text-text-primary mb-4 flex items-center gap-2">
          🏪 Platform Distribution
        </h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={platformData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {platformData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getPlatformColor(entry.name)} />
                ))}
              </Pie>
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white/95 backdrop-blur border border-border shadow-panel p-3 rounded-lg">
                        <p className="text-xs font-bold text-text-primary mb-1">{data.name}</p>
                        <p className="text-sm font-display text-primary">{data.value} listings</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '11px', fontWeight: 600, color: '#64748B' }}/>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

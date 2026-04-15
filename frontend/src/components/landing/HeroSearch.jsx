import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Zap, Search } from "lucide-react";

const SUGGESTIONS = [
  "iPhone 15",
  "Best 4K TVs under ₹40,000",
  "Sony WH-1000XM5 headphones",
  "MacBook Air M2",
  "Samsung Galaxy S24 Ultra",
  "Gaming laptops below ₹80k",
];

export default function HeroSearch() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e?.preventDefault();
    if (query.trim()) {
      navigate(`/dashboard?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <section className="relative pt-32 pb-20 px-4 flex flex-col items-center text-center">
      {/* Background flare */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[100px] pointer-events-none -z-10" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.6 }}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 text-primary-dark text-xs font-semibold tracking-wide uppercase mb-6"
      >
        <Zap className="w-3.5 h-3.5" />
        AI-Powered Shopping Intelligence
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.16, duration: 0.6 }}
        className="font-display text-5xl md:text-7xl !leading-[1.1] text-text-primary tracking-tight max-w-4xl max-w-[800px]"
      >
        Find the Best Price. <br className="hidden md:block" />
        Every Time. Instantly.
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.22, duration: 0.6 }}
        className="mt-6 text-lg text-text-muted max-w-2xl"
      >
        Shoplytics unleashes multi-agent AI to scour Amazon, Flipkart, and Croma in real-time.
        We do the digging, you get the absolute best deal.
      </motion.p>

      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.28, duration: 0.6 }}
        className="w-full max-w-3xl mt-10"
      >
        <form
          onSubmit={handleSearch}
          className="relative flex items-center p-2 bg-white rounded-full shadow-soft border border-border/50 focus-within:border-primary/40 focus-within:shadow-[0_0_0_4px_rgba(37,99,235,0.1)] transition-all"
        >
          <Search className="w-5 h-5 text-text-dim ml-4" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Compare iPhone 15 prices across Amazon, Flipkart, Croma..."
            className="flex-1 bg-transparent border-none outline-none text-base text-text-primary placeholder:text-text-dim px-4 py-3"
          />
          <button
            type="submit"
            disabled={!query.trim()}
            className="bg-primary hover:bg-primary-dark disabled:bg-primary/50 text-white px-6 py-3 rounded-full font-medium transition-colors flex items-center gap-2"
          >
            <Zap className="w-4 h-4" />
            Launch Agents
          </button>
        </form>
      </motion.div>

      {/* Suggestions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.34, duration: 0.6 }}
        className="mt-8"
      >
        <div className="flex flex-wrap justify-center gap-2 max-w-3xl">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => {
                setQuery(s);
              }}
              className="px-4 py-2 rounded-full text-sm font-medium text-text-muted bg-white border border-border hover:border-primary/30 hover:text-primary transition-all cursor-pointer shadow-sm hover:shadow"
            >
              {s}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Trust line */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.6 }}
        className="mt-12 flex items-center gap-2 justify-center text-[11px] font-mono font-medium text-text-dim tracking-widest uppercase"
      >
        <span>Trusted by smart shoppers</span>
        <span className="w-1 h-1 rounded-full bg-text-dim/50" />
        <span>Real-time data</span>
        <span className="w-1 h-1 rounded-full bg-text-dim/50" />
        <span>AI-powered</span>
      </motion.div>
    </section>
  );
}

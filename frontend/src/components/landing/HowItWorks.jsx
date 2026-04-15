import { motion } from "framer-motion";
import { BrainCircuit, Search, Database, Lightbulb } from "lucide-react";

const STEPS = [
  {
    icon: BrainCircuit,
    title: "1. Plan",
    desc: "AI intelligently breaks down your search query into specific extraction targets.",
  },
  {
    icon: Search,
    title: "2. Scour",
    desc: "Browser agents stealthily navigate Amazon, Flipkart, and Croma simultaneously.",
  },
  {
    icon: Database,
    title: "3. Extract",
    desc: "CSS selectors and LLM fallback extract prices, ratings, and stock status.",
  },
  {
    icon: Lightbulb,
    title: "4. Recommend",
    desc: "We analyze the data and present the absolute best deal for you to buy.",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-24 bg-white border-y border-border">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <span className="text-xs font-mono font-bold tracking-widest text-primary uppercase">
            How It Works
          </span>
          <h2 className="mt-4 text-3xl md:text-5xl font-display text-text-primary tracking-tight">
            The Multi-Agent Pipeline
          </h2>
        </div>

        <div className="relative mt-12 grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Connecting line (desktop only) */}
          <div className="hidden md:block absolute top-[28px] left-[10%] right-[10%] h-[2px] bg-bg border-t-2 border-dashed border-border z-0" />

          {STEPS.map((step, idx) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ delay: idx * 0.1, duration: 0.5 }}
                className="relative z-10 flex flex-col items-center text-center p-6 bg-white rounded-xl border border-border shadow-sm hover:shadow-panel hover:-translate-y-1 transition-all group"
              >
                <div className="w-14 h-14 rounded-xl bg-bg-muted flex items-center justify-center text-primary mb-6 group-hover:bg-primary group-hover:text-white transition-colors shadow-soft">
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-text-primary mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-text-muted leading-relaxed">
                  {step.desc}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

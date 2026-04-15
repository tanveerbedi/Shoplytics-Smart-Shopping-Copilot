import { motion } from "framer-motion";
import { Zap, Clock, ShieldCheck } from "lucide-react";

const FEATURES = [
  {
    icon: Zap,
    title: "Multi-Agent AI Architecture",
    desc: "A swarm of agents orchestrate your search: Planners, Extractors, Rankers, and Summarizers working in concert.",
  },
  {
    icon: Clock,
    title: "Real-Time Price Scraping",
    desc: "We don't use stale cached data. Agents spin up headless browsers to fetch the live price at the moment you ask.",
  },
  {
    icon: ShieldCheck,
    title: "Intelligent Deal Detection",
    desc: "Advanced logic identifies overpriced items, filters out scam listings, and tags the true 'Best Value' product.",
  },
];

export default function FeatureCards() {
  return (
    <section className="py-24 bg-bg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {FEATURES.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <motion.div
                key={feat.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ delay: idx * 0.1, duration: 0.5 }}
                className="bg-white p-8 rounded-2xl border border-border shadow-sm hover:shadow-[0_0_30px_rgba(37,99,235,0.08)] hover:border-primary/20 transition-all"
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-6">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-xl font-bold text-text-primary mb-3">
                  {feat.title}
                </h3>
                <p className="text-text-muted leading-relaxed">
                  {feat.desc}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

import HeroSearch from "../components/landing/HeroSearch";
import HowItWorks from "../components/landing/HowItWorks";
import FeatureCards from "../components/landing/FeatureCards";
import { Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col w-full min-h-screen">
      <HeroSearch />
      <HowItWorks />
      <FeatureCards />
      
      {/* Footer */}
      <footer className="py-8 border-t border-border bg-white text-center flex flex-col items-center gap-2">
        <div className="flex items-center gap-1.5 text-text-primary font-display text-lg">
          <Zap className="w-4 h-4 text-primary fill-primary/20" />
          SHOPLYTICS
        </div>
        <div className="text-sm font-mono text-text-muted">
          Built with ⚡ by Shoplytics
        </div>
        <a 
          href="#" 
          className="text-xs font-medium text-text-dim hover:text-primary transition-colors mt-2"
        >
          GitHub →
        </a>
      </footer>
    </div>
  );
}

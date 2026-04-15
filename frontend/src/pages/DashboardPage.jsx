import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import useShoplyticsStore from "../store/useShoplyticsStore";
import usePipeline from "../hooks/usePipeline";

import CommandPanel from "../components/dashboard/CommandPanel";
import AgentTerminal from "../components/dashboard/AgentTerminal";
import AIDecisionBox from "../components/dashboard/AIDecisionBox";
import PriceTable from "../components/dashboard/PriceTable";
import RecommendationCard from "../components/dashboard/RecommendationCard";
import MarketCharts from "../components/dashboard/MarketCharts";

export default function DashboardPage() {
  const [searchParams] = useSearchParams();
  const rawQuery = searchParams.get("q");

  const query = useShoplyticsStore((s) => s.query);
  const setQuery = useShoplyticsStore((s) => s.setQuery);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const results = useShoplyticsStore((s) => s.results);
  const { launch } = usePipeline();

  // If we arrive with a ?q= param, populate the store and auto-run if idle
  useEffect(() => {
    if (rawQuery && rawQuery !== query && pipelineStatus === "idle") {
      setQuery(rawQuery);
      launch(rawQuery);
    }
  }, [rawQuery, query, pipelineStatus, setQuery, launch]);

  return (
    <div className="min-h-screen bg-bg-muted/30 pt-6 pb-20 px-4 md:px-8">
      {/* Scrollable Layout Context */}
      <div className="max-w-[1600px] mx-auto flex flex-col lg:flex-row gap-6 items-start">
        
        {/* ── LEFT PANEL (Brain / Pipeline) - 30% ── */}
        {/* Make it sticky so it stays visible while scrolling the long data side */}
        <aside className="w-full lg:w-[350px] xl:w-[400px] shrink-0 flex flex-col gap-6 lg:sticky lg:top-[88px]">
          {/* Centralized the search into the header, so this is just pipeline status */}
          <div className="bg-white rounded-xl border border-border shadow-panel p-5">
            <CommandPanel />
          </div>

          <div className="bg-white rounded-xl border border-border shadow-panel flex flex-col overflow-hidden max-h-[400px] xl:max-h-[500px]">
            <AgentTerminal />
          </div>

          <div className="bg-white rounded-xl border border-border shadow-panel flex flex-col overflow-hidden max-h-[300px]">
            <AIDecisionBox />
          </div>
        </aside>

        {/* ── RIGHT PANEL (Market Intelligence Data) - 70% ── */}
        <main className="flex-1 w-full flex flex-col min-w-0">
          
          {/* AI Top Pick / Recommendation Hero Card */}
          <RecommendationCard />

          {/* Graphical Analysis */}
          {pipelineStatus === "completed" && results?.products && (
            <MarketCharts products={results.products} />
          )}

          {/* Deep Data Table */}
          <div className="bg-white rounded-xl border border-border shadow-panel p-5">
            <h3 className="text-sm font-bold text-text-primary mb-4 uppercase tracking-wide">
              Data Matrix
            </h3>
            <PriceTable />
          </div>

        </main>
      </div>
    </div>
  );
}

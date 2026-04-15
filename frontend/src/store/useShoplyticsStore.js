import { create } from "zustand";

const PIPELINE_AGENTS = [
  { name: "Planner", key: "planning", icon: "📋" },
  { name: "Search", key: "searching", icon: "🔍" },
  { name: "Filter", key: "filtering", icon: "🔗" },
  { name: "Browser", key: "browsing", icon: "🌐" },
  { name: "Extractor", key: "extracting", icon: "🔬" },
  { name: "Dedup", key: "deduplicating", icon: "🧬" },
  { name: "Sentiment", key: "sentiment", icon: "🤖" },
  { name: "Deal Detect", key: "deal_detection", icon: "⚖️" },
  { name: "Ranking", key: "ranking", icon: "📈" },
  { name: "Summary", key: "summarizing", icon: "📝" },
];

const useShoplyticsStore = create((set, get) => ({
  // ── Query ───────────────────────────────────
  query: "",
  setQuery: (q) => set({ query: q }),

  // ── Task ────────────────────────────────────
  taskId: null,
  pipelineStatus: "idle", // idle | running | completed | failed
  currentStep: null,

  // ── Pipeline agents ─────────────────────────
  agents: PIPELINE_AGENTS.map((a) => ({ ...a, status: "idle" })),

  // ── Logs ────────────────────────────────────
  logs: [],
  addLog: (log) =>
    set((s) => {
      const newLogs = [...s.logs, log];
      // Infer which pipeline step is active from log content
      let stepUpdate = {};
      const content = (log.content || "").toLowerCase();
      const agent = (log.agent || "").toLowerCase();
      for (const a of PIPELINE_AGENTS) {
        if (content.includes(a.key) || agent === a.key || agent === a.name.toLowerCase()) {
          stepUpdate = { currentStep: a.key };
          break;
        }
      }
      // Update agent statuses based on current step
      let agentUpdate = {};
      if (stepUpdate.currentStep) {
        const stepKey = stepUpdate.currentStep;
        const idx = PIPELINE_AGENTS.findIndex((a) => a.key === stepKey);
        if (idx >= 0) {
          agentUpdate = {
            agents: PIPELINE_AGENTS.map((a, i) => ({
              ...a,
              status: i < idx ? "done" : i === idx ? "running" : "idle",
            })),
          };
        }
      }
      return { logs: newLogs, ...stepUpdate, ...agentUpdate };
    }),
  clearLogs: () => set({ logs: [] }),

  // ── Results ─────────────────────────────────
  results: null,
  recommendation: "",
  summary: "",

  // ── AI Thinking ─────────────────────────────
  aiThinking: "",
  setAiThinking: (t) => set({ aiThinking: t }),

  // ── WebSocket ref ───────────────────────────
  ws: null,
  setWs: (ws) => set({ ws }),

  // ── Actions ─────────────────────────────────
  startTask: (taskId) =>
    set({
      taskId,
      pipelineStatus: "running",
      currentStep: null,
      logs: [],
      results: null,
      recommendation: "",
      summary: "",
      aiThinking: "",
      agents: PIPELINE_AGENTS.map((a) => ({ ...a, status: "idle" })),
    }),

  completeTask: (result) =>
    set({
      pipelineStatus: "completed",
      results: result,
      recommendation: result?.recommendation || "",
      summary: result?.summary || "",
      agents: PIPELINE_AGENTS.map((a) => ({ ...a, status: "done" })),
    }),

  failTask: (error) =>
    set((s) => ({
      pipelineStatus: "failed",
      aiThinking: `Error: ${error}`,
      agents: s.agents.map((a) =>
        a.status === "running" ? { ...a, status: "error" } : a
      ),
    })),

  resetTask: () =>
    set({
      taskId: null,
      pipelineStatus: "idle",
      currentStep: null,
      logs: [],
      results: null,
      recommendation: "",
      summary: "",
      aiThinking: "",
      agents: PIPELINE_AGENTS.map((a) => ({ ...a, status: "idle" })),
    }),
}));

export { PIPELINE_AGENTS };
export default useShoplyticsStore;

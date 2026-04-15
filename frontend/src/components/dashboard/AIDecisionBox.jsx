import ReactMarkdown from "react-markdown";
import useShoplyticsStore from "../../store/useShoplyticsStore";
import { Sparkles } from "lucide-react";

export default function AIDecisionBox() {
  const aiThinking = useShoplyticsStore((s) => s.aiThinking);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const recommendation = useShoplyticsStore((s) => s.recommendation);
  const summary = useShoplyticsStore((s) => s.summary);

  const isRunning = pipelineStatus === "running";
  
  // Either show the thinking stream or the final summary/recommendation
  const content = summary || recommendation || aiThinking;

  return (
    <div className="flex flex-col h-full bg-white z-10 w-full min-h-0 min-w-0 font-sans">
      <div className="px-4 py-3 border-b border-border flex items-center gap-2 bg-bg-muted/30">
        <Sparkles className="w-4 h-4 text-primary" />
        <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide">
          ► AI Decision Intelligence
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto p-4 text-sm text-text-primary leading-relaxed relative">
        {!content && !isRunning && (
          <div className="text-text-dim/80 h-full flex flex-col items-center justify-center font-medium">
            AI reasoning will appear here
          </div>
        )}
        
        {isRunning && !content && (
          <div className="flex flex-col items-center justify-center h-full gap-2">
            <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <div className="text-xs font-medium text-text-muted">Analyzing context...</div>
          </div>
        )}

        {content && (
          <div className="prose prose-sm prose-primary max-w-none">
            <ReactMarkdown>{content}</ReactMarkdown>
            {isRunning && <span className="inline-block w-1.5 h-3 ml-1 bg-primary animate-blink" />}
          </div>
        )}
      </div>
    </div>
  );
}

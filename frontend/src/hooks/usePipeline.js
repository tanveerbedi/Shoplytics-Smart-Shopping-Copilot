import { useCallback, useRef, useEffect } from "react";
import useShoplyticsStore from "../store/useShoplyticsStore";
import { createTask, getTaskStatus } from "../api/client";

export default function usePipeline() {
  const pollRef = useRef(null);

  const query = useShoplyticsStore((s) => s.query);
  const taskId = useShoplyticsStore((s) => s.taskId);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const startTask = useShoplyticsStore((s) => s.startTask);
  const completeTask = useShoplyticsStore((s) => s.completeTask);
  const failTask = useShoplyticsStore((s) => s.failTask);
  const addLog = useShoplyticsStore((s) => s.addLog);

  const launch = useCallback(
    async (q) => {
      const queryText = q || query;
      if (!queryText.trim()) return;

      try {
        const data = await createTask(queryText.trim());
        startTask(data.task_id);
      } catch (err) {
        failTask(err.message || "Failed to start task");
      }
    },
    [query, startTask, failTask]
  );

  // Polling fallback: if WebSocket fails, poll REST endpoint
  useEffect(() => {
    if (!taskId || pipelineStatus !== "running") return;

    const poll = async () => {
      try {
        const data = await getTaskStatus(taskId);

        // Sync new messages
        const storeState = useShoplyticsStore.getState();
        const existingCount = storeState.logs.length;
        const serverMsgs = data.messages || [];

        if (serverMsgs.length > existingCount) {
          const newMsgs = serverMsgs.slice(existingCount);
          for (const msg of newMsgs) {
            // Only add if we don't have a WS connection
            if (!storeState.ws || storeState.ws.readyState !== WebSocket.OPEN) {
              addLog({
                agent: msg.agent || "system",
                content: msg.content || "",
                level: msg.level || "info",
                timestamp: msg.timestamp || new Date().toISOString(),
              });
            }
          }
        }

        if (data.status === "completed" && data.result) {
          completeTask(data.result);
          clearInterval(pollRef.current);
        } else if (data.status === "failed") {
          failTask(data.error || "Pipeline failed");
          clearInterval(pollRef.current);
        }
      } catch {
        // Polling error, will retry
      }
    };

    pollRef.current = setInterval(poll, 2000);
    return () => clearInterval(pollRef.current);
  }, [taskId, pipelineStatus, addLog, completeTask, failTask]);

  return { launch };
}

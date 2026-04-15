import { useEffect, useRef, useCallback } from "react";
import useShoplyticsStore from "../store/useShoplyticsStore";
import { getWebSocketUrl } from "../api/client";

export default function useLogStream() {
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);

  const taskId = useShoplyticsStore((s) => s.taskId);
  const pipelineStatus = useShoplyticsStore((s) => s.pipelineStatus);
  const addLog = useShoplyticsStore((s) => s.addLog);
  const completeTask = useShoplyticsStore((s) => s.completeTask);
  const failTask = useShoplyticsStore((s) => s.failTask);
  const setWs = useShoplyticsStore((s) => s.setWs);

  const connect = useCallback(() => {
    if (!taskId || pipelineStatus !== "running") return;

    const url = getWebSocketUrl(taskId);
    const ws = new WebSocket(url);
    wsRef.current = ws;
    setWs(ws);

    ws.onopen = () => {
      addLog({
        agent: "system",
        content: "WebSocket connected — streaming live agent logs",
        level: "info",
        timestamp: new Date().toISOString(),
      });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "message") {
          addLog({
            agent: data.agent || "system",
            content: data.content || "",
            level: data.level || "info",
            timestamp: data.timestamp || new Date().toISOString(),
          });
        } else if (data.type === "status") {
          // Status heartbeats — no action needed, store updates via logs
        } else if (data.type === "result") {
          completeTask(data.data);
        } else if (data.type === "error") {
          failTask(data.error || "Unknown pipeline error");
        }
      } catch {
        // Non-JSON message, ignore
      }
    };

    ws.onerror = () => {
      addLog({
        agent: "system",
        content: "WebSocket error — connection lost",
        level: "error",
        timestamp: new Date().toISOString(),
      });
    };

    ws.onclose = (e) => {
      setWs(null);
      // If the pipeline is still running, try polling fallback
      const currentStatus = useShoplyticsStore.getState().pipelineStatus;
      if (currentStatus === "running") {
        reconnectTimerRef.current = setTimeout(connect, 3000);
      }
    };
  }, [taskId, pipelineStatus, addLog, completeTask, failTask, setWs]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
  }, [connect]);
}

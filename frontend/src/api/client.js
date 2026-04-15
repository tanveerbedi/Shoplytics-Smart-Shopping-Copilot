import axios from "axios";

const API_BASE = "";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

export async function createTask(query) {
  const { data } = await client.post("/api/task", { query });
  return data;
}

export async function getTaskStatus(taskId) {
  const { data } = await client.get(`/api/task/${taskId}`);
  return data;
}

export async function healthCheck() {
  const { data } = await client.get("/health");
  return data;
}

export function getWebSocketUrl(taskId) {
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${window.location.host}/ws/task/${taskId}`;
}

export default client;

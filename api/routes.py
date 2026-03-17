"""
API routes – REST and WebSocket endpoints for the Universal AI Web Agent.
"""

from __future__ import annotations
import asyncio
import uuid
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from models.schemas import TaskRequest, TaskStatus, FinalReport, AgentMessage
from orchestrator.graph import agent_graph

logger = logging.getLogger(__name__)
router = APIRouter()

# ── In-memory task store ─────────────────────────────────
# In production, replace with Redis or a database.
_tasks: dict[str, TaskStatus] = {}
_task_locks: dict[str, asyncio.Lock] = {}


# ── Helper ───────────────────────────────────────────────

async def _run_pipeline(task_id: str, query: str) -> None:
    """Execute the agent pipeline in the background."""
    _tasks[task_id].status = "running"

    initial_state = {
        "query": query,
        "plan": None,
        "search_results": [],
        "raw_pages": [],
        "extracted_products": [],
        "analysis": None,
        "final_report": None,
        "messages": [],
        "current_step": "starting",
        "error": None,
    }

    try:
        # Run the compiled LangGraph pipeline
        final_state = await agent_graph.ainvoke(initial_state)

        _tasks[task_id].status = "completed"
        _tasks[task_id].messages = final_state.get("messages", [])
        _tasks[task_id].result = final_state.get("final_report")

    except Exception as exc:
        logger.exception("Pipeline failed for task %s", task_id)
        _tasks[task_id].status = "failed"
        _tasks[task_id].error = str(exc)
        _tasks[task_id].messages.append(
            AgentMessage(agent="system", content=f"Pipeline error: {exc}", level="error")
        )


# ── Endpoints ────────────────────────────────────────────

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Universal AI Web Agent"}


@router.post("/api/task")
async def create_task(request: TaskRequest):
    """
    Submit a new research task. Returns a task ID immediately.
    The pipeline runs asynchronously in the background.
    """
    task_id = str(uuid.uuid4())[:8]

    _tasks[task_id] = TaskStatus(task_id=task_id, status="pending")
    _task_locks[task_id] = asyncio.Lock()

    # Launch pipeline in background
    asyncio.create_task(_run_pipeline(task_id, request.query))

    return {"task_id": task_id, "status": "pending"}


@router.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the current status, messages, and result of a task."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = _tasks[task_id]
    return {
        "task_id": task.task_id,
        "status": task.status,
        "messages": [m.model_dump() for m in task.messages],
        "result": task.result.model_dump() if task.result else None,
        "error": task.error,
    }


@router.websocket("/ws/task/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for streaming agent messages in real-time.
    Polls the task status and pushes new messages to the client.
    """
    await websocket.accept()

    if task_id not in _tasks:
        await websocket.send_json({"error": "Task not found"})
        await websocket.close()
        return

    last_msg_count = 0

    try:
        while True:
            task = _tasks[task_id]
            current_messages = task.messages

            # Send any new messages
            if len(current_messages) > last_msg_count:
                new_msgs = current_messages[last_msg_count:]
                for msg in new_msgs:
                    await websocket.send_json({
                        "type": "message",
                        "agent": msg.agent,
                        "content": msg.content,
                        "level": msg.level,
                        "timestamp": msg.timestamp.isoformat(),
                    })
                last_msg_count = len(current_messages)

            # Send status update
            await websocket.send_json({
                "type": "status",
                "status": task.status,
                "current_step": task.task_id,
            })

            # If task is done, send result and close
            if task.status in ("completed", "failed"):
                if task.result:
                    await websocket.send_json({
                        "type": "result",
                        "data": task.result.model_dump(),
                    })
                if task.error:
                    await websocket.send_json({
                        "type": "error",
                        "error": task.error,
                    })
                await websocket.close()
                break

            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for task %s", task_id)
    except Exception as exc:
        logger.error("WebSocket error for task %s: %s", task_id, exc)

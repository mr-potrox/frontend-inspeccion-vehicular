from typing import Dict, Set
from fastapi import WebSocket
from asyncio import Lock
from .logging_utils import log_event

class WSManager:
    def __init__(self):
        self._sessions: Dict[str, Set[WebSocket]] = {}
        self._lock = Lock()

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._sessions.setdefault(session_id, set()).add(ws)
        log_event("ws_connect", session_id=session_id)

    async def disconnect(self, session_id: str, ws: WebSocket):
        async with self._lock:
            conns = self._sessions.get(session_id, set())
            if ws in conns:
                conns.remove(ws)
            if not conns and session_id in self._sessions:
                self._sessions.pop(session_id, None)
        log_event("ws_disconnect", session_id=session_id)

    async def broadcast(self, session_id: str, payload: dict):
        async with self._lock:
            conns = list(self._sessions.get(session_id, []))
        dead = []
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for d in dead:
                    self._sessions.get(session_id, set()).discard(d)
        if payload.get("event"):
            log_event("ws_event", session_id=session_id, event=payload["event"])

manager = WSManager()
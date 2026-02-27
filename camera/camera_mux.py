#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["opencv-python-headless"]
# ///
"""Persistent MJPEG relay for IP cameras that sleep when idle.

Keeps the camera connection alive and serves frames locally on demand.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import cv2

INDEX_HTML = b"""\
<!DOCTYPE html>
<html><head><title>Camera Mux</title>
<style>body{margin:0;background:#111;display:flex;justify-content:center;align-items:center;height:100vh}
img{max-width:100%;max-height:100vh}</style>
</head><body><img src="/stream"></body></html>
"""


class FrameBuffer:
    """Thread-safe container for the latest camera frame."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.frame: bytes | None = None
        self.timestamp: float = 0.0

    def update(self, jpeg: bytes) -> None:
        with self.lock:
            self.frame = jpeg
            self.timestamp = time.monotonic()

    def get(self) -> tuple[bytes | None, float]:
        with self.lock:
            return self.frame, self.timestamp


class CameraReader(threading.Thread):
    """Continuously reads frames from the IP camera, reconnecting on failure."""

    def __init__(self, source: str, buf: FrameBuffer) -> None:
        super().__init__(daemon=True)
        self.source = source
        self.buf = buf
        self.connected = False
        self._backoff = 2.0
        self._max_backoff = 10.0

    def run(self) -> None:
        while True:
            cap = cv2.VideoCapture(self.source)
            if not cap.isOpened():
                self.connected = False
                print(f"[reader] failed to open {self.source}, retrying in {self._backoff:.1f}s")
                time.sleep(self._backoff)
                self._backoff = min(self._backoff * 1.5, self._max_backoff)
                continue

            self.connected = True
            self._backoff = 2.0
            print(f"[reader] connected to {self.source}")

            while True:
                ok, frame = cap.read()
                if not ok:
                    print("[reader] read failed, reconnecting")
                    self.connected = False
                    cap.release()
                    break
                ok, jpeg = cv2.imencode(".jpg", frame)
                if ok:
                    self.buf.update(jpeg.tobytes())

            time.sleep(self._backoff)


class MuxHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    buf: FrameBuffer
    reader: CameraReader
    start_time: float
    source: str

    def log_message(self, format: str, *args: object) -> None:
        # Suppress per-request logs
        pass

    def do_GET(self) -> None:
        if self.path == "/":
            self._serve_index()
        elif self.path == "/frame":
            self._serve_frame()
        elif self.path == "/stream":
            self._serve_stream()
        elif self.path == "/health":
            self._serve_health()
        else:
            self.send_error(404)

    def _serve_index(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(INDEX_HTML)

    def _serve_frame(self) -> None:
        frame, _ = self.buf.get()
        if frame is None:
            self.send_error(503, "No frame available")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(frame)))
        self.end_headers()
        self.wfile.write(frame)

    def _serve_stream(self) -> None:
        boundary = b"--frame"
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            while True:
                frame, _ = self.buf.get()
                if frame is None:
                    time.sleep(0.1)
                    continue
                self.wfile.write(boundary + b"\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n")
                self.wfile.write(f"Content-Length: {len(frame)}\r\n".encode())
                self.wfile.write(b"\r\n")
                self.wfile.write(frame)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
                time.sleep(1 / 30)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _serve_health(self) -> None:
        frame, ts = self.buf.get()
        now = time.monotonic()
        data = {
            "connected": self.reader.connected,
            "frame_age_s": round(now - ts, 2) if frame else None,
            "uptime_s": round(now - self.start_time, 1),
            "source": self.source,
        }
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Persistent MJPEG camera relay")
    parser.add_argument(
        "--source",
        default="http://10.0.44.199:4747/video?640x480",
        help="IP camera URL",
    )
    parser.add_argument("--port", type=int, default=8100, help="HTTP server port")
    args = parser.parse_args()

    buf = FrameBuffer()
    reader = CameraReader(args.source, buf)
    reader.start()

    MuxHandler.buf = buf
    MuxHandler.reader = reader
    MuxHandler.start_time = time.monotonic()
    MuxHandler.source = args.source

    server = ThreadingHTTPServer(("0.0.0.0", args.port), MuxHandler)
    print(f"[mux] serving on http://0.0.0.0:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[mux] shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()

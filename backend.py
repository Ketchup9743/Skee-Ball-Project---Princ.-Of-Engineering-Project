import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None


HOST = "0.0.0.0"
PORT = 8000
SERIAL_BAUD_RATE = 115200
PROJECT_DIR = Path(__file__).parent

state = {
    "score": 0,
    "sensor_scores": {"1": 0, "2": 0, "3": 0},
    "events": 0,
}
state_lock = threading.Lock()


def reset_state():
    with state_lock:
        state["score"] = 0
        state["sensor_scores"] = {"1": 0, "2": 0, "3": 0}
        state["events"] = 0


def handle_serial_message(message):
    parts = message.strip().split(",")
    if parts[0] == "RESET":
        reset_state()
    elif len(parts) == 3 and parts[0] == "SCORE_EVENT":
        sensor, points = parts[1], int(parts[2])
        with state_lock:
            state["score"] += points
            state["sensor_scores"][sensor] = state["sensor_scores"].get(sensor, 0) + points
            state["events"] += 1


def find_serial_port():
    if serial is None:
        return None
    configured_port = os.getenv("MICROBIT_PORT")
    if configured_port:
        return configured_port
    ports = list(list_ports.comports())
    return ports[0].device if ports else None


def serial_reader():
    if serial is None:
        print("pyserial is not installed; the webpage is running without micro:bit input.")
        return
    serial_port = find_serial_port()
    if serial_port is None:
        print("No micro:bit found. Set MICROBIT_PORT if it is not detected automatically.")
        return
    print("Listening for the micro:bit on {}".format(serial_port))
    with serial.Serial(serial_port, SERIAL_BAUD_RATE, timeout=1) as connection:
        while True:
            message = connection.readline().decode("utf-8", errors="ignore")
            if message:
                try:
                    handle_serial_message(message)
                except (ValueError, IndexError):
                    print("Ignored serial message: {}".format(message.strip()))


class RequestHandler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            body = (PROJECT_DIR / "scoreboard.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/styles.css":
            body = (PROJECT_DIR / "styles.css").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/score":
            with state_lock:
                self.send_json(state.copy())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/reset":
            reset_state()
            self.send_json({"ok": True})
        else:
            self.send_error(404)

    def log_message(self, format_string, *args):
        return


if __name__ == "__main__":
    threading.Thread(target=serial_reader, daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), RequestHandler)
    print("Scoreboard available at http://localhost:{}".format(PORT))
    server.serve_forever()
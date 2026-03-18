import socket
import subprocess
import time
from typing import Optional

class DevServer:
    def __init__(self, command: str, port: int = 0, working_dir: str = "."):
        self.command = command
        self.port = port
        self.working_dir = working_dir
        self.process: Optional[subprocess.Popen] = None
        
        if self.port == 0:
            self.port = self._find_free_port()

    def _find_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def start(self):
        env = {"PORT": str(self.port), "VITE_PORT": str(self.port)}
        # Replace template placeholders if any
        cmd = self.command.replace("{port}", str(self.port))
        
        self.process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=self.working_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Wait for self._health_check() in an async/polling manner

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def is_healthy(self, timeout: int = 30) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", self.port)) == 0:
                    return True
            time.sleep(1)
        return False

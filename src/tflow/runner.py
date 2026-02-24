import subprocess
import json
from pathlib import Path
from typing import Dict, Any

class TestRunner:
    def __init__(self, project_dir: Path, output_dir: Path):
        self.project_dir = project_dir
        self.output_dir = output_dir

    def run_tests(self, test_files: list[str], headed: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Execute playwright tests."""
        if dry_run:
            return {"status": "dry_run", "passed": True, "results": []}
            
        cmd = ["npx", "playwright", "test"]
        cmd.extend(test_files)
        if headed:
            cmd.append("--headed")
        cmd.extend(["--reporter=json"])
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            # Parse Playwright JSON output
            try:
                report = json.loads(result.stdout)
                passed = result.returncode == 0
                return {"status": "completed", "passed": passed, "report": report}
            except json.JSONDecodeError:
                return {"status": "error", "passed": False, "error": "Failed to parse playwright output."}
        except Exception as e:
            return {"status": "error", "passed": False, "error": str(e)}

    def analyze_failure(self, report: Dict[str, Any]) -> str:
        """Stub for failure analysis."""
        return "Unknown failure"

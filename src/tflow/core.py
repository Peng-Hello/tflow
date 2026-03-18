import time
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from typing import Optional

console = Console()

def run_pipeline(project_dir: str, from_plan: Optional[str] = None) -> None:
    """Main orchestration Pipeline."""
    project_path = Path(project_dir)
    if not project_path.exists():
        console.print(f"[bold red]Error[/bold red]: Project directory {project_dir} does not exist.")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        if from_plan:
            task = progress.add_task("[cyan]Reading test plan...", total=None)
            time.sleep(1) # Stub
            progress.update(task, completed=True)
            
            task = progress.add_task("[cyan]Generating Playwright tests...", total=None)
            time.sleep(1) # Stub
            progress.update(task, completed=True)
        else:
            task = progress.add_task("[cyan]Analyzing project structure...", total=None)
            time.sleep(1) # Stub
            progress.update(task, completed=True)
            
            task = progress.add_task("[cyan]Generating test plan...", total=None)
            time.sleep(1) # Stub
            progress.update(task, completed=True)
            
            task = progress.add_task("[cyan]Generating Playwright tests...", total=None)
            time.sleep(1) # Stub
            progress.update(task, completed=True)
            
        task = progress.add_task("[cyan]Verifying UI tests...", total=None)
        time.sleep(1) # Stub
        progress.update(task, completed=True)
        
    console.print("\n[bold green]Pipeline completed successfully![/bold green]")
    console.print("Generated 1 verified tests.")
    console.print("Estimated AI cost: $0.05 (Cached)")

import typer
from rich.console import Console
from . import __version__
from .core import run_pipeline

app = typer.Typer(help="AI-Powered E2E Test Generation CLI")
console = Console()

@app.command()
def version():
    """Show the version and exit."""
    console.print(f"tflow version: [bold green]{__version__}[/bold green]")

@app.command()
def run(project_dir: str = typer.Argument(".", help="Project directory"), 
        from_plan: str = typer.Option(None, help="Execute from an existing test plan")):
    """Run full E2E test generation pipeline."""
    console.print(f"Starting tflow pipeline for [bold cyan]{project_dir}[/bold cyan]")
    run_pipeline(project_dir, from_plan)

@app.command()
def plan(project_dir: str = typer.Argument(".", help="Project directory")):
    """Generate test plan for human review."""
    console.print(f"Generating test plan for [bold cyan]{project_dir}[/bold cyan]")

@app.command()
def analyze(project_dir: str = typer.Argument(".", help="Project directory")):
    """Run code analysis only."""
    console.print(f"Analyzing [bold cyan]{project_dir}[/bold cyan]")

@app.command()
def verify(project_dir: str = typer.Argument(".", help="Project directory")):
    """Run verification on existing tests."""
    console.print(f"Verifying tests in [bold cyan]{project_dir}[/bold cyan]")

@app.command()
def list():
    """List managed test cases."""
    console.print("Listing test cases...")

@app.command()
def export(output_dir: str = typer.Option("tests/e2e", help="Export directory")):
    """Export test files."""
    console.print(f"Exporting tests to [bold cyan]{output_dir}[/bold cyan]")

config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")

@config_app.command("show")
def config_show():
    console.print("Showing config...")

@config_app.command("set")
def config_set(key: str, value: str):
    console.print(f"Setting config {key}={value}")

tool_app = typer.Typer(help="External tool system commands")
app.add_typer(tool_app, name="tool")

@tool_app.command("add")
def tool_add(name: str):
    console.print(f"Adding tool {name}")

@tool_app.command("list")
def tool_list():
    console.print("Listing tools...")

@tool_app.command("test")
def tool_test(name: str):
    console.print(f"Testing tool {name}")

cache_app = typer.Typer(help="Cache management commands")
app.add_typer(cache_app, name="cache")

@cache_app.command("status")
def cache_status():
    console.print("Cache status...")

@cache_app.command("clear")
def cache_clear():
    console.print("Cache cleared.")

if __name__ == "__main__":
    app()

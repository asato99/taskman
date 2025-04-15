"""
Main CLI application entry point
"""
import typer
from rich.console import Console
from rich.panel import Panel

from taskman.commands import db

app = typer.Typer(
    name="taskman",
    help="Task Management System CLI",
    add_completion=False,
)

# Add database commands
app.add_typer(db.app, name="db", help="Database management commands")

console = Console()

@app.callback()
def main():
    """
    Task Management System CLI
    """
    pass

@app.command()
def version():
    """
    Show the version of the application
    """
    from taskman import __version__
    console.print(Panel(f"Task Management System CLI v{__version__}", title="Version"))

if __name__ == "__main__":
    app() 
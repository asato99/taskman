"""
Main CLI application entry point
"""
import typer
from rich.console import Console
from rich.panel import Panel

from taskman.commands import db, objective, task, process, workflow, process_instance, task_instance, task_step

app = typer.Typer(
    name="taskman",
    help="Task Management System CLI",
    add_completion=False,
)

# Add database commands
app.add_typer(db.app, name="db", help="Database management commands")

# Add objective commands
app.add_typer(objective.app, name="objective", help="Objective management commands")

# Add task commands
app.add_typer(task.app, name="task", help="Task management commands")

# Add process commands
app.add_typer(process.app, name="process", help="Process management commands")

# Add workflow commands
app.add_typer(workflow.app, name="workflow", help="Workflow management commands")

# Add process instance commands
app.add_typer(process_instance.app, name="instance", help="Process instance management commands")

# Add task instance commands
app.add_typer(task_instance.app, name="task-instance", help="Task instance management commands")

# Add task step commands
app.add_typer(task_step.app, name="step", help="Task step management commands")

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
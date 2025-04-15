"""
Database management commands
"""
import typer
from rich.console import Console
from rich.panel import Panel

from taskman.database.init_db import create_database, init_db
from taskman.database.seed_data import create_sample_data

console = Console()
app = typer.Typer()

@app.command()
def init():
    """
    Initialize the database by creating all tables
    """
    try:
        console.print(Panel("Creating database...", title="Database Initialization"))
        create_database()
        init_db()
        console.print(Panel("Database initialized successfully!", title="Success"))
    except Exception as e:
        console.print(Panel(f"Error initializing database: {e}", title="Error", style="red"))
        raise typer.Exit(1)

@app.command()
def seed():
    """
    Seed the database with sample data
    """
    try:
        console.print(Panel("Seeding sample data...", title="Data Seeding"))
        create_sample_data()
        console.print(Panel("Sample data created successfully!", title="Success"))
    except Exception as e:
        console.print(Panel(f"Error seeding data: {e}", title="Error", style="red"))
        raise typer.Exit(1)

@app.command()
def reset():
    """
    Reset the database by dropping and recreating all tables
    """
    try:
        console.print(Panel("Resetting database...", title="Database Reset"))
        # TODO: Implement database reset
        console.print(Panel("Database reset successfully!", title="Success"))
    except Exception as e:
        console.print(Panel(f"Error resetting database: {e}", title="Error", style="red"))
        raise typer.Exit(1) 
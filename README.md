# Task Management System

A command-line based task management system that helps organize and track objectives, processes, and tasks.

## Features

- Objective management
- Process management
- Task management
- Workflow management
- Database operations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task-management
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Database Management

Initialize the database:
```bash
python -m taskman db init
```

Seed sample data:
```bash
python -m taskman db seed
```

### Objective Management

List objectives:
```bash
python -m taskman objective list
```

Create an objective:
```bash
python -m taskman objective create --title="New Objective" --measure="Measure" --target=100
```

### Process Management

List processes:
```bash
python -m taskman process list
```

Create a process:
```bash
python -m taskman process create --name="New Process" --description="Process description"
```

### Task Management

List tasks:
```bash
python -m taskman task list
```

Create a task:
```bash
python -m taskman task create --process=<process_id> --name="New Task" --priority=高
```

## Development

### Project Structure

```
task-management/
├── taskman/
│   ├── commands/         # CLI commands
│   ├── database/         # Database related code
│   ├── models/           # Data models
│   ├── cli.py            # CLI application
│   └── __main__.py       # Entry point
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── README.md            # This file
```

### Running Tests

```bash
python -m pytest
```

## License

MIT License 
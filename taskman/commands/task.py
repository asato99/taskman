"""
Task management commands
"""
import typer
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from taskman.database.connection import get_db
from taskman.models.task import Task

console = Console()
app = typer.Typer()


@app.command()
def list(
    status: str = typer.Option(None, "--status", "-s", help="Filter by status (未着手, 進行中, 完了, 保留)"),
    priority: str = typer.Option(None, "--priority", "-p", help="Filter by priority (低, 中, 高, 緊急)"),
    assigned_to: str = typer.Option(None, "--assigned", "-a", help="Filter by assignee")
):
    """
    List all tasks
    """
    try:
        db = next(get_db())
        query = db.query(Task)
        
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
            
        tasks = query.all()
        
        if not tasks:
            console.print(Panel("タスクが見つかりませんでした。", title="情報"))
            return
        
        table = Table(title="タスク一覧")
        table.add_column("ID", style="dim")
        table.add_column("タスク名")
        table.add_column("状態")
        table.add_column("優先度")
        table.add_column("担当者")
        table.add_column("期限")
        
        for task in tasks:
            table.add_row(
                str(task.id),
                task.name,
                task.status,
                task.priority,
                task.assigned_to or "-",
                task.due_date.strftime("%Y-%m-%d") if task.due_date else "-"
            )
        
        console.print(table)
    except Exception as e:
        console.print(Panel(f"タスク一覧の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="タスク名"),
    description: str = typer.Option("", "--description", "-d", help="タスクの説明"),
    process_id: int = typer.Option(..., "--process", "-p", help="所属プロセスID"),
    estimated_duration: Optional[int] = typer.Option(None, "--duration", help="予想所要時間（分）"),
    priority: str = typer.Option("中", "--priority", help="優先度（低, 中, 高, 緊急）"),
    assigned_to: Optional[str] = typer.Option(None, "--assign", "-a", help="担当者"),
    due_date: Optional[str] = typer.Option(None, "--due-date", help="期限（YYYY-MM-DD形式）")
):
    """
    Create a new task
    """
    try:
        db = next(get_db())
        
        # 優先度の検証
        if priority not in ["低", "中", "高", "緊急"]:
            console.print(Panel("無効な優先度です。'低', '中', '高', '緊急'のいずれかを指定してください。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 日付の変換
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                console.print(Panel("無効な日付形式です。YYYY-MM-DD形式で指定してください。", 
                                  title="エラー", style="red"))
                raise typer.Exit(1)
        
        # プロセスの存在確認（実装されたらコメントアウトを外す）
        # process = db.query(Process).filter(Process.id == process_id).first()
        # if not process:
        #     console.print(Panel(f"プロセス（ID: {process_id}）が見つかりません", title="エラー", style="red"))
        #     raise typer.Exit(1)
        
        # 新しいタスクの作成
        new_task = Task(
            name=name,
            description=description,
            process_id=process_id,
            estimated_duration=estimated_duration,
            status="未着手",
            priority=priority,
            assigned_to=assigned_to,
            due_date=parsed_due_date
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        console.print(Panel(f"タスク「{name}」が作成されました（ID: {new_task.id}）", title="成功"))
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスク作成中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def show(
    task_id: int = typer.Argument(..., help="タスクのID")
):
    """
    Show details of a task
    """
    try:
        db = next(get_db())
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            console.print(Panel(f"タスク（ID: {task_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 詳細情報の表示
        console.print(Panel(f"[bold]タスク詳細（ID: {task.id}）[/bold]", title="情報"))
        console.print(f"[bold]タスク名:[/bold] {task.name}")
        console.print(f"[bold]説明:[/bold] {task.description or '未設定'}")
        console.print(f"[bold]プロセスID:[/bold] {task.process_id}")
        console.print(f"[bold]予想所要時間:[/bold] {task.estimated_duration or '未設定'} 分")
        console.print(f"[bold]状態:[/bold] {task.status}")
        console.print(f"[bold]優先度:[/bold] {task.priority}")
        console.print(f"[bold]担当者:[/bold] {task.assigned_to or '未設定'}")
        console.print(f"[bold]期限:[/bold] {task.due_date.strftime('%Y-%m-%d') if task.due_date else '未設定'}")
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスク情報の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def update(
    task_id: int = typer.Argument(..., help="タスクのID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="タスク名"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="タスクの説明"),
    estimated_duration: Optional[int] = typer.Option(None, "--duration", help="予想所要時間（分）"),
    priority: Optional[str] = typer.Option(None, "--priority", help="優先度（低, 中, 高, 緊急）"),
    assigned_to: Optional[str] = typer.Option(None, "--assign", "-a", help="担当者"),
    due_date: Optional[str] = typer.Option(None, "--due-date", help="期限（YYYY-MM-DD形式）"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="状態（未着手, 進行中, 完了, 保留）")
):
    """
    Update a task
    """
    try:
        db = next(get_db())
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            console.print(Panel(f"タスク（ID: {task_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 優先度の検証
        if priority is not None and priority not in ["低", "中", "高", "緊急"]:
            console.print(Panel("無効な優先度です。'低', '中', '高', '緊急'のいずれかを指定してください。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 状態の検証
        if status is not None and status not in ["未着手", "進行中", "完了", "保留"]:
            console.print(Panel("無効な状態です。'未着手', '進行中', '完了', '保留'のいずれかを指定してください。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 日付の変換
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                console.print(Panel("無効な日付形式です。YYYY-MM-DD形式で指定してください。", 
                                  title="エラー", style="red"))
                raise typer.Exit(1)
        
        # 変更がある場合のみ更新
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if estimated_duration is not None:
            task.estimated_duration = estimated_duration
        if priority is not None:
            task.priority = priority
        if assigned_to is not None:
            task.assigned_to = assigned_to
        if parsed_due_date is not None:
            task.due_date = parsed_due_date
        if status is not None:
            task.status = status
        
        db.commit()
        console.print(Panel(f"タスク（ID: {task_id}）を更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスク更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def status(
    task_id: int = typer.Argument(..., help="タスクのID"),
    new_status: str = typer.Argument(..., help="新しい状態（未着手, 進行中, 完了, 保留）")
):
    """
    Update the status of a task
    """
    try:
        if new_status not in ["未着手", "進行中", "完了", "保留"]:
            console.print(Panel("無効な状態です。'未着手', '進行中', '完了', '保留'のいずれかを指定してください。", 
                              title="エラー", style="red"))
            raise typer.Exit(1)
        
        db = next(get_db())
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            console.print(Panel(f"タスク（ID: {task_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        old_status = task.status
        task.status = new_status
        db.commit()
        
        console.print(Panel(f"タスク（ID: {task_id}）の状態を「{old_status}」から「{new_status}」に更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"状態更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def delete(
    task_id: int = typer.Argument(..., help="タスクのID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除")
):
    """
    Delete a task
    """
    try:
        db = next(get_db())
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            console.print(Panel(f"タスク（ID: {task_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 削除確認（forceが指定されていない場合）
        if not force:
            confirm = typer.confirm(f"タスク「{task.name}」（ID: {task_id}）を削除しますか？")
            if not confirm:
                console.print(Panel("削除をキャンセルしました。", title="情報"))
                return
        
        # 関連するデータの確認（必要に応じて実装）
        # 例：task_instances = db.query(TaskInstance).filter(TaskInstance.task_id == task_id).all()
        # if task_instances and not force:
        #     console.print(Panel(f"このタスクには{len(task_instances)}個のインスタンスがあります。削除するには --force オプションを使用してください。", 
        #                       title="警告", style="yellow"))
        #     raise typer.Exit(1)
        
        # タスクの削除
        db.delete(task)
        db.commit()
        
        console.print(Panel(f"タスク「{task.name}」（ID: {task_id}）を削除しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスク削除中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1) 
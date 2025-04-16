"""
Task instance management commands
"""
import typer
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from taskman.database.connection import get_db
from taskman.models.task import Task
from taskman.models.process_instance import ProcessInstance
from taskman.models.task_instance import TaskInstance

console = Console()
app = typer.Typer()


@app.command()
def list(
    process_instance_id: Optional[int] = typer.Option(None, "--instance", "-i", help="プロセスインスタンスIDでフィルタリング"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="ステータスでフィルタリング（未着手, 実行中, 完了, 中断, 失敗）"),
    assigned_to: Optional[str] = typer.Option(None, "--assigned", "-a", help="担当者でフィルタリング")
):
    """
    タスクインスタンス一覧を表示
    """
    try:
        db = next(get_db())
        query = db.query(TaskInstance)
        
        if process_instance_id:
            query = query.filter(TaskInstance.process_instance_id == process_instance_id)
        if status:
            if status not in ["未着手", "実行中", "完了", "中断", "失敗"]:
                console.print(Panel("無効なステータスです。'未着手', '実行中', '完了', '中断', '失敗'のいずれかを指定してください。", 
                                   title="エラー", style="red"))
                raise typer.Exit(1)
            query = query.filter(TaskInstance.status == status)
        if assigned_to:
            query = query.filter(TaskInstance.assigned_to == assigned_to)
            
        task_instances = query.all()
        
        if not task_instances:
            message = "タスクインスタンスが見つかりませんでした。"
            if process_instance_id:
                message = f"プロセスインスタンス（ID: {process_instance_id}）に関連するタスクインスタンスが見つかりませんでした。"
            console.print(Panel(message, title="情報"))
            return
        
        table = Table(title="タスクインスタンス一覧")
        table.add_column("ID", style="dim")
        table.add_column("タスク名")
        table.add_column("プロセスインスタンス")
        table.add_column("ステータス")
        table.add_column("担当者")
        table.add_column("開始日時")
        table.add_column("終了日時")
        
        for task_instance in task_instances:
            # タスク名を取得
            task = db.query(Task).filter(Task.id == task_instance.task_id).first()
            task_name = task.name if task else f"不明 (ID: {task_instance.task_id})"
            
            # プロセスインスタンス情報を取得
            process_instance = db.query(ProcessInstance).filter(
                ProcessInstance.id == task_instance.process_instance_id
            ).first()
            process_instance_info = f"ID: {task_instance.process_instance_id}"
            if process_instance:
                process_instance_info = f"{process_instance.process.name} (ID: {task_instance.process_instance_id})"
            
            # 日時のフォーマット
            started_at = task_instance.started_at.strftime("%Y-%m-%d %H:%M") if task_instance.started_at else "-"
            completed_at = task_instance.completed_at.strftime("%Y-%m-%d %H:%M") if task_instance.completed_at else "-"
            
            table.add_row(
                str(task_instance.id),
                task_name,
                process_instance_info,
                task_instance.status,
                task_instance.assigned_to or "-",
                started_at,
                completed_at
            )
        
        console.print(table)
    except Exception as e:
        console.print(Panel(f"タスクインスタンス一覧の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def show(
    task_instance_id: int = typer.Argument(..., help="タスクインスタンスのID")
):
    """
    タスクインスタンスの詳細を表示
    """
    try:
        db = next(get_db())
        task_instance = db.query(TaskInstance).filter(TaskInstance.id == task_instance_id).first()
        
        if not task_instance:
            console.print(Panel(f"タスクインスタンス（ID: {task_instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # タスク情報を取得
        task = db.query(Task).filter(Task.id == task_instance.task_id).first()
        task_name = task.name if task else f"不明 (ID: {task_instance.task_id})"
        
        # プロセスインスタンス情報を取得
        process_instance = db.query(ProcessInstance).filter(
            ProcessInstance.id == task_instance.process_instance_id
        ).first()
        process_info = "不明"
        if process_instance and hasattr(process_instance, 'process') and process_instance.process:
            process_info = f"{process_instance.process.name} (ID: {process_instance.process.id})"
        
        # 詳細情報の表示
        console.print(Panel(f"[bold]タスクインスタンス詳細（ID: {task_instance.id}）[/bold]", title="情報"))
        console.print(f"[bold]タスク:[/bold] {task_name} (ID: {task_instance.task_id})")
        console.print(f"[bold]プロセスインスタンス:[/bold] ID: {task_instance.process_instance_id} ({process_info})")
        console.print(f"[bold]ステータス:[/bold] {task_instance.status}")
        console.print(f"[bold]担当者:[/bold] {task_instance.assigned_to or '未割り当て'}")
        console.print(f"[bold]開始日時:[/bold] {task_instance.started_at.strftime('%Y-%m-%d %H:%M:%S') if task_instance.started_at else '未開始'}")
        console.print(f"[bold]終了日時:[/bold] {task_instance.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task_instance.completed_at else '未完了'}")
        console.print(f"[bold]メモ:[/bold] {task_instance.notes or 'なし'}")
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクインスタンス情報の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def create(
    process_instance_id: int = typer.Option(..., "--instance", "-i", help="プロセスインスタンスID"),
    task_id: int = typer.Option(..., "--task", "-t", help="タスクID"),
    assigned_to: Optional[str] = typer.Option(None, "--assigned", "-a", help="担当者"),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="メモ")
):
    """
    新しいタスクインスタンスを作成
    """
    try:
        db = next(get_db())
        
        # プロセスインスタンスの存在確認
        process_instance = db.query(ProcessInstance).filter(ProcessInstance.id == process_instance_id).first()
        if not process_instance:
            console.print(Panel(f"プロセスインスタンス（ID: {process_instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # タスクの存在確認
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            console.print(Panel(f"タスク（ID: {task_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # プロセスインスタンスとタスクの関連性を確認（タスクがプロセスのものであること）
        if hasattr(process_instance, 'process') and hasattr(task, 'process_id') and task.process_id != process_instance.process.id:
            console.print(Panel(
                f"タスク（ID: {task_id}）はプロセスインスタンス（ID: {process_instance_id}）のプロセスに所属していません", 
                title="エラー", style="red"
            ))
            raise typer.Exit(1)
        
        # 新しいタスクインスタンスの作成
        new_task_instance = TaskInstance(
            process_instance_id=process_instance_id,
            task_id=task_id,
            status="未着手",
            assigned_to=assigned_to,
            notes=notes
        )
        
        db.add(new_task_instance)
        db.commit()
        db.refresh(new_task_instance)
        
        console.print(Panel(
            f"タスクインスタンスが作成されました（ID: {new_task_instance.id}）\n"
            f"タスク: {task.name} (ID: {task_id})\n"
            f"プロセスインスタンス: ID: {process_instance_id}",
            title="成功"
        ))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクインスタンス作成中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def update(
    task_instance_id: int = typer.Argument(..., help="タスクインスタンスのID"),
    assigned_to: Optional[str] = typer.Option(None, "--assigned", "-a", help="担当者"),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="メモ")
):
    """
    タスクインスタンスを更新
    """
    try:
        db = next(get_db())
        task_instance = db.query(TaskInstance).filter(TaskInstance.id == task_instance_id).first()
        
        if not task_instance:
            console.print(Panel(f"タスクインスタンス（ID: {task_instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 変更がある場合のみ更新
        if assigned_to is not None:
            task_instance.assigned_to = assigned_to
        if notes is not None:
            task_instance.notes = notes
        
        db.commit()
        console.print(Panel(f"タスクインスタンス（ID: {task_instance_id}）を更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクインスタンス更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def status(
    task_instance_id: int = typer.Argument(..., help="タスクインスタンスのID"),
    new_status: str = typer.Argument(..., help="新しいステータス（未着手, 実行中, 完了, 中断, 失敗）")
):
    """
    タスクインスタンスのステータスを更新
    """
    try:
        if new_status not in ["未着手", "実行中", "完了", "中断", "失敗"]:
            console.print(Panel("無効なステータスです。'未着手', '実行中', '完了', '中断', '失敗'のいずれかを指定してください。", 
                              title="エラー", style="red"))
            raise typer.Exit(1)
        
        db = next(get_db())
        task_instance = db.query(TaskInstance).filter(TaskInstance.id == task_instance_id).first()
        
        if not task_instance:
            console.print(Panel(f"タスクインスタンス（ID: {task_instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        old_status = task_instance.status
        task_instance.status = new_status
        
        # ステータスに応じて開始・終了日時を更新
        if new_status == "実行中" and not task_instance.started_at:
            task_instance.started_at = datetime.now()
        
        if new_status in ["完了", "中断", "失敗"] and not task_instance.completed_at:
            task_instance.completed_at = datetime.now()
        
        db.commit()
        
        console.print(Panel(f"タスクインスタンス（ID: {task_instance_id}）のステータスを「{old_status}」から「{new_status}」に更新しました", 
                          title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ステータス更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def delete(
    task_instance_id: int = typer.Argument(..., help="タスクインスタンスのID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除")
):
    """
    タスクインスタンスを削除
    """
    try:
        db = next(get_db())
        task_instance = db.query(TaskInstance).filter(TaskInstance.id == task_instance_id).first()
        
        if not task_instance:
            console.print(Panel(f"タスクインスタンス（ID: {task_instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # ステータスによる削除制限（実行中のタスクは削除不可など）
        if task_instance.status == "実行中" and not force:
            console.print(Panel(
                f"実行中のタスクインスタンス（ID: {task_instance_id}）は削除できません。\n"
                "強制的に削除するには --force オプションを使用してください。", 
                title="警告", style="yellow"
            ))
            raise typer.Exit(1)
        
        # 削除確認（forceが指定されていない場合）
        if not force:
            # タスク名を取得
            task = db.query(Task).filter(Task.id == task_instance.task_id).first()
            task_name = task.name if task else f"不明 (ID: {task_instance.task_id})"
            
            confirm = typer.confirm(f"タスクインスタンス（ID: {task_instance_id}、タスク: {task_name}）を削除しますか？")
            if not confirm:
                console.print(Panel("削除をキャンセルしました。", title="情報"))
                return
        
        # タスクインスタンスの削除
        db.delete(task_instance)
        db.commit()
        
        console.print(Panel(f"タスクインスタンス（ID: {task_instance_id}）を削除しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクインスタンス削除中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1) 
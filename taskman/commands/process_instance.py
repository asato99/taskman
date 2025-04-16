"""
Process instance management commands
"""
import typer
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from taskman.database.connection import get_db
from taskman.models.process import Process
from taskman.models.process_instance import ProcessInstance
from taskman.models.task_instance import TaskInstance

console = Console()
app = typer.Typer()


@app.command()
def list(
    process_id: Optional[int] = typer.Option(None, "--process", "-p", help="プロセスIDでフィルタリング"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="ステータスでフィルタリング（実行中, 完了, 中断, 失敗）"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="作成者でフィルタリング")
):
    """
    プロセスインスタンス一覧を表示
    """
    try:
        db = next(get_db())
        query = db.query(ProcessInstance)
        
        if process_id:
            query = query.filter(ProcessInstance.process_id == process_id)
        if status:
            if status not in ["実行中", "完了", "中断", "失敗"]:
                console.print(Panel("無効なステータスです。'実行中', '完了', '中断', '失敗'のいずれかを指定してください。", 
                                   title="エラー", style="red"))
                raise typer.Exit(1)
            query = query.filter(ProcessInstance.status == status)
        if user:
            query = query.filter(ProcessInstance.created_by == user)
            
        instances = query.all()
        
        if not instances:
            message = "プロセスインスタンスが見つかりませんでした。"
            if process_id:
                message = f"プロセス（ID: {process_id}）に関連するインスタンスが見つかりませんでした。"
            console.print(Panel(message, title="情報"))
            return
        
        table = Table(title="プロセスインスタンス一覧")
        table.add_column("ID", style="dim")
        table.add_column("プロセス名")
        table.add_column("ステータス")
        table.add_column("開始日時")
        table.add_column("終了日時")
        table.add_column("作成者")
        table.add_column("タスク数")
        
        for instance in instances:
            # プロセス名を取得
            process = db.query(Process).filter(Process.id == instance.process_id).first()
            process_name = process.name if process else f"不明 (ID: {instance.process_id})"
            
            # 関連するタスクインスタンス数
            task_count = db.query(TaskInstance).filter(TaskInstance.process_instance_id == instance.id).count()
            
            # 日時のフォーマット
            started_at = instance.started_at.strftime("%Y-%m-%d %H:%M") if instance.started_at else "-"
            completed_at = instance.completed_at.strftime("%Y-%m-%d %H:%M") if instance.completed_at else "-"
            
            table.add_row(
                str(instance.id),
                process_name,
                instance.status,
                started_at,
                completed_at,
                instance.created_by or "-",
                str(task_count)
            )
        
        console.print(table)
    except Exception as e:
        console.print(Panel(f"プロセスインスタンス一覧の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def show(
    instance_id: int = typer.Argument(..., help="プロセスインスタンスのID")
):
    """
    プロセスインスタンスの詳細を表示
    """
    try:
        db = next(get_db())
        instance = db.query(ProcessInstance).filter(ProcessInstance.id == instance_id).first()
        
        if not instance:
            console.print(Panel(f"プロセスインスタンス（ID: {instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # プロセス情報を取得
        process = db.query(Process).filter(Process.id == instance.process_id).first()
        process_name = process.name if process else f"不明 (ID: {instance.process_id})"
        
        # 関連するタスクインスタンスを取得
        task_instances = db.query(TaskInstance).filter(
            TaskInstance.process_instance_id == instance.id
        ).all()
        
        # 詳細情報の表示
        console.print(Panel(f"[bold]プロセスインスタンス詳細（ID: {instance.id}）[/bold]", title="情報"))
        console.print(f"[bold]プロセス:[/bold] {process_name} (ID: {instance.process_id})")
        console.print(f"[bold]ステータス:[/bold] {instance.status}")
        console.print(f"[bold]開始日時:[/bold] {instance.started_at.strftime('%Y-%m-%d %H:%M:%S') if instance.started_at else '-'}")
        console.print(f"[bold]終了日時:[/bold] {instance.completed_at.strftime('%Y-%m-%d %H:%M:%S') if instance.completed_at else '-'}")
        console.print(f"[bold]作成者:[/bold] {instance.created_by or '未設定'}")
        
        # タスクインスタンス情報を表示
        if task_instances:
            console.print("\n[bold]タスクインスタンス:[/bold]")
            task_table = Table()
            task_table.add_column("ID", style="dim")
            task_table.add_column("タスク名")
            task_table.add_column("ステータス")
            task_table.add_column("担当者")
            task_table.add_column("開始日時")
            task_table.add_column("終了日時")
            
            for task_instance in task_instances:
                # タスク名を取得（必要に応じて実装）
                task_name = task_instance.task.name if hasattr(task_instance, 'task') and task_instance.task else f"不明 (ID: {task_instance.task_id})"
                
                # 日時のフォーマット
                ti_started_at = task_instance.started_at.strftime("%Y-%m-%d %H:%M") if task_instance.started_at else "-"
                ti_completed_at = task_instance.completed_at.strftime("%Y-%m-%d %H:%M") if task_instance.completed_at else "-"
                
                task_table.add_row(
                    str(task_instance.id),
                    task_name,
                    task_instance.status,
                    task_instance.assigned_to or "-",
                    ti_started_at,
                    ti_completed_at
                )
            
            console.print(task_table)
        else:
            console.print("\n[italic]このプロセスインスタンスには関連するタスクインスタンスがありません。[/italic]")
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"プロセスインスタンス情報の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def create(
    process_id: int = typer.Option(..., "--process", "-p", help="プロセスID"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="作成者")
):
    """
    新しいプロセスインスタンスを作成
    """
    try:
        db = next(get_db())
        
        # プロセスの存在確認
        process = db.query(Process).filter(Process.id == process_id).first()
        if not process:
            console.print(Panel(f"プロセス（ID: {process_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # プロセスのステータスがアクティブであることを確認
        if process.status != "アクティブ":
            console.print(Panel(f"プロセス（ID: {process_id}）はアクティブではありません。アクティブなプロセスのみインスタンス化できます。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 新しいプロセスインスタンスの作成
        new_instance = ProcessInstance(
            process_id=process_id,
            status="実行中",
            started_at=datetime.now(),
            created_by=user
        )
        
        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        
        console.print(Panel(
            f"プロセスインスタンスが作成されました（ID: {new_instance.id}）\n"
            f"プロセス: {process.name} (ID: {process_id})",
            title="成功"
        ))
        
        # ワークフロー情報を使ってタスクインスタンスを作成（必要に応じて実装）
        # この部分は、プロセスのワークフローに基づいて最初のタスクインスタンスを作成する処理など
        # ここでは簡略化のため省略
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"プロセスインスタンス作成中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def status(
    instance_id: int = typer.Argument(..., help="プロセスインスタンスのID"),
    new_status: str = typer.Argument(..., help="新しいステータス（実行中, 完了, 中断, 失敗）")
):
    """
    プロセスインスタンスのステータスを更新
    """
    try:
        if new_status not in ["実行中", "完了", "中断", "失敗"]:
            console.print(Panel("無効なステータスです。'実行中', '完了', '中断', '失敗'のいずれかを指定してください。", 
                              title="エラー", style="red"))
            raise typer.Exit(1)
        
        db = next(get_db())
        instance = db.query(ProcessInstance).filter(ProcessInstance.id == instance_id).first()
        
        if not instance:
            console.print(Panel(f"プロセスインスタンス（ID: {instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        old_status = instance.status
        instance.status = new_status
        
        # 完了または中断の場合は終了日時を設定
        if new_status in ["完了", "中断", "失敗"] and not instance.completed_at:
            instance.completed_at = datetime.now()
        
        db.commit()
        
        console.print(Panel(f"プロセスインスタンス（ID: {instance_id}）のステータスを「{old_status}」から「{new_status}」に更新しました", 
                          title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ステータス更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def delete(
    instance_id: int = typer.Argument(..., help="プロセスインスタンスのID"),
    force: bool = typer.Option(False, "--force", "-f", help="関連オブジェクトを含めて強制削除")
):
    """
    プロセスインスタンスを削除
    """
    try:
        db = next(get_db())
        instance = db.query(ProcessInstance).filter(ProcessInstance.id == instance_id).first()
        
        if not instance:
            console.print(Panel(f"プロセスインスタンス（ID: {instance_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 関連するタスクインスタンスのチェック
        task_instances = db.query(TaskInstance).filter(
            TaskInstance.process_instance_id == instance_id
        ).all()
        
        if task_instances and not force:
            console.print(Panel(
                f"プロセスインスタンス（ID: {instance_id}）には{len(task_instances)}個のタスクインスタンスがあります。\n"
                "関連するタスクインスタンスも含めて削除するには --force オプションを使用してください。", 
                title="警告", style="yellow"
            ))
            raise typer.Exit(1)
        
        # 削除確認
        confirm = typer.confirm(f"プロセスインスタンス（ID: {instance_id}）を削除しますか？")
        if not confirm:
            console.print(Panel("削除をキャンセルしました。", title="情報"))
            return
        
        # forceオプションが指定されている場合は関連するタスクインスタンスも削除
        if force and task_instances:
            for task_instance in task_instances:
                db.delete(task_instance)
            console.print(Panel(f"{len(task_instances)}個の関連タスクインスタンスを削除しました。", title="情報"))
        
        # プロセスインスタンスの削除
        db.delete(instance)
        db.commit()
        
        console.print(Panel(f"プロセスインスタンス（ID: {instance_id}）を削除しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"プロセスインスタンス削除中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1) 
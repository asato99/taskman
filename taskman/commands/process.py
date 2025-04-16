"""
Process management commands
"""
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from taskman.database.connection import get_db
from taskman.models.process import Process

console = Console()
app = typer.Typer()


@app.command()
def list():
    """
    プロセス一覧を表示
    """
    try:
        db = next(get_db())
        processes = db.query(Process).all()
        
        if not processes:
            console.print(Panel("プロセスが見つかりませんでした。", title="情報"))
            return
        
        table = Table(title="プロセス一覧")
        table.add_column("ID", style="dim")
        table.add_column("プロセス名")
        table.add_column("バージョン")
        table.add_column("ステータス")
        
        for process in processes:
            table.add_row(
                str(process.id),
                process.name,
                str(process.version),
                process.status
            )
        
        console.print(table)
    except Exception as e:
        console.print(Panel(f"プロセス一覧の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def show(
    process_id: int = typer.Argument(..., help="プロセスのID")
):
    """
    プロセスの詳細を表示
    """
    try:
        db = next(get_db())
        process = db.query(Process).filter(Process.id == process_id).first()
        
        if not process:
            console.print(Panel(f"プロセス（ID: {process_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 詳細情報の表示
        console.print(Panel(f"[bold]プロセス詳細（ID: {process.id}）[/bold]", title="情報"))
        console.print(f"[bold]プロセス名:[/bold] {process.name}")
        console.print(f"[bold]説明:[/bold] {process.description or '未設定'}")
        console.print(f"[bold]バージョン:[/bold] {process.version}")
        console.print(f"[bold]ステータス:[/bold] {process.status}")
        
        # 関連する目標を表示
        objectives = process.objectives
        if objectives:
            console.print(f"\n[bold]関連する目標:[/bold]")
            for obj in objectives:
                console.print(f"  - {obj.title} (ID: {obj.id})")
        
        # 関連するタスクを表示
        tasks = process.tasks
        if tasks:
            console.print(f"\n[bold]関連するタスク:[/bold]")
            for task in tasks:
                console.print(f"  - {task.name} (ID: {task.id})")
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"プロセス情報の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="プロセス名"),
    description: str = typer.Option("", "--description", "-d", help="プロセスの説明"),
    status: str = typer.Option("ドラフト", "--status", "-s", 
                              help="ステータス（アクティブ, 非アクティブ, ドラフト）")
):
    """
    新しいプロセスを作成
    """
    try:
        db = next(get_db())
        
        # ステータスの検証
        if status not in ["アクティブ", "非アクティブ", "ドラフト"]:
            console.print(Panel("無効なステータスです。'アクティブ', '非アクティブ', 'ドラフト'のいずれかを指定してください。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 新しいプロセスの作成
        new_process = Process(
            name=name,
            description=description,
            status=status
        )
        
        db.add(new_process)
        db.commit()
        db.refresh(new_process)
        
        console.print(Panel(f"プロセス「{name}」が作成されました（ID: {new_process.id}）", title="成功"))
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"プロセス作成中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def update(
    process_id: int = typer.Argument(..., help="プロセスのID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="プロセス名"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="プロセスの説明"),
    status: Optional[str] = typer.Option(None, "--status", "-s", 
                                       help="ステータス（アクティブ, 非アクティブ, ドラフト）"),
    increment_version: bool = typer.Option(False, "--increment-version", "-i", help="バージョンを増加させる")
):
    """
    プロセスを更新
    """
    try:
        db = next(get_db())
        process = db.query(Process).filter(Process.id == process_id).first()
        
        if not process:
            console.print(Panel(f"プロセス（ID: {process_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # ステータスの検証
        if status is not None and status not in ["アクティブ", "非アクティブ", "ドラフト"]:
            console.print(Panel("無効なステータスです。'アクティブ', '非アクティブ', 'ドラフト'のいずれかを指定してください。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 変更がある場合のみ更新
        if name is not None:
            process.name = name
        if description is not None:
            process.description = description
        if status is not None:
            process.status = status
        if increment_version:
            process.version += 1
        
        db.commit()
        console.print(Panel(f"プロセス（ID: {process_id}）を更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"プロセス更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def status(
    process_id: int = typer.Argument(..., help="プロセスのID"),
    new_status: str = typer.Argument(..., help="新しいステータス（アクティブ, 非アクティブ, ドラフト）")
):
    """
    プロセスのステータスを更新
    """
    try:
        if new_status not in ["アクティブ", "非アクティブ", "ドラフト"]:
            console.print(Panel("無効なステータスです。'アクティブ', '非アクティブ', 'ドラフト'のいずれかを指定してください。", 
                              title="エラー", style="red"))
            raise typer.Exit(1)
        
        db = next(get_db())
        process = db.query(Process).filter(Process.id == process_id).first()
        
        if not process:
            console.print(Panel(f"プロセス（ID: {process_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        old_status = process.status
        process.status = new_status
        db.commit()
        
        console.print(Panel(f"プロセス（ID: {process_id}）のステータスを「{old_status}」から「{new_status}」に更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ステータス更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def delete(
    process_id: int = typer.Argument(..., help="プロセスのID"),
    force: bool = typer.Option(False, "--force", "-f", help="関連オブジェクトを無視して強制削除")
):
    """
    プロセスを削除
    """
    try:
        db = next(get_db())
        process = db.query(Process).filter(Process.id == process_id).first()
        
        if not process:
            console.print(Panel(f"プロセス（ID: {process_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 関連オブジェクトのチェック
        if not force:
            has_related_objects = False
            error_message = "以下の関連オブジェクトが存在するため削除できません：\n"
            
            if process.tasks:
                has_related_objects = True
                error_message += f"- タスク: {len(process.tasks)}個\n"
            
            if process.instances:
                has_related_objects = True
                error_message += f"- プロセスインスタンス: {len(process.instances)}個\n"
            
            if has_related_objects:
                error_message += "\n--force オプションを使用して強制的に削除することができます。"
                console.print(Panel(error_message, title="警告", style="yellow"))
                raise typer.Exit(1)
        
        # 削除確認
        confirm = typer.confirm(f"プロセス「{process.name}」（ID: {process_id}）を削除しますか？")
        if not confirm:
            console.print(Panel("削除をキャンセルしました。", title="情報"))
            return
        
        # プロセスの削除
        db.delete(process)
        db.commit()
        
        console.print(Panel(f"プロセス「{process.name}」（ID: {process_id}）を削除しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"プロセス削除中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1) 
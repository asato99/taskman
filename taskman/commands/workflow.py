"""
Workflow management commands
"""
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from taskman.database.connection import get_db
from taskman.models.workflow import Workflow
from taskman.models.process import Process
from taskman.models.task import Task

console = Console()
app = typer.Typer()

@app.command()
def list(
    process_id: Optional[int] = typer.Option(None, "--process", "-p", help="プロセスIDでフィルタリング")
):
    """
    ワークフロー一覧を表示
    """
    try:
        db = next(get_db())
        query = db.query(Workflow)
        
        if process_id:
            query = query.filter(Workflow.process_id == process_id)
            
        workflows = query.all()
        
        if not workflows:
            message = "ワークフローが見つかりませんでした。"
            if process_id:
                message = f"プロセス（ID: {process_id}）に関連するワークフローが見つかりませんでした。"
            console.print(Panel(message, title="情報"))
            return
        
        table = Table(title="ワークフロー一覧")
        table.add_column("ID", style="dim")
        table.add_column("プロセスID")
        table.add_column("開始タスク")
        table.add_column("終了タスク")
        table.add_column("条件タイプ")
        table.add_column("順序")
        
        for workflow in workflows:
            from_task_name = workflow.from_task.name if workflow.from_task else "開始点"
            to_task_name = workflow.to_task.name if workflow.to_task else "終了点"
            
            table.add_row(
                str(workflow.id),
                str(workflow.process_id),
                f"{from_task_name} (ID: {workflow.from_task_id or 'なし'})",
                f"{to_task_name} (ID: {workflow.to_task_id or 'なし'})",
                workflow.condition_type,
                str(workflow.sequence_number or "-")
            )
        
        console.print(table)
    except Exception as e:
        console.print(Panel(f"ワークフロー一覧の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def show(
    workflow_id: int = typer.Argument(..., help="ワークフローのID")
):
    """
    ワークフローの詳細を表示
    """
    try:
        db = next(get_db())
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            console.print(Panel(f"ワークフロー（ID: {workflow_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # プロセス情報を取得
        process = db.query(Process).filter(Process.id == workflow.process_id).first()
        process_name = process.name if process else "不明なプロセス"
        
        # タスク情報を取得
        from_task = db.query(Task).filter(Task.id == workflow.from_task_id).first() if workflow.from_task_id else None
        to_task = db.query(Task).filter(Task.id == workflow.to_task_id).first() if workflow.to_task_id else None
        
        # 詳細情報の表示
        console.print(Panel(f"[bold]ワークフロー詳細（ID: {workflow.id}）[/bold]", title="情報"))
        console.print(f"[bold]プロセス:[/bold] {process_name} (ID: {workflow.process_id})")
        console.print(f"[bold]開始タスク:[/bold] {from_task.name if from_task else '開始点'} (ID: {workflow.from_task_id or 'なし'})")
        console.print(f"[bold]終了タスク:[/bold] {to_task.name if to_task else '終了点'} (ID: {workflow.to_task_id or 'なし'})")
        console.print(f"[bold]条件タイプ:[/bold] {workflow.condition_type}")
        console.print(f"[bold]条件式:[/bold] {workflow.condition_expression or 'なし'}")
        console.print(f"[bold]順序番号:[/bold] {workflow.sequence_number or 'なし'}")
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ワークフロー情報の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def create(
    process_id: int = typer.Option(..., "--process", "-p", help="プロセスID"),
    from_task_id: Optional[int] = typer.Option(None, "--from", help="開始タスクID (なしの場合はプロセス開始点)"),
    to_task_id: Optional[int] = typer.Option(None, "--to", help="終了タスクID (なしの場合はプロセス終了点)"),
    condition_type: str = typer.Option("常時", "--condition-type", "-c", 
                                     help="条件タイプ (常時, 条件付き, 並列)"),
    condition_expression: Optional[str] = typer.Option(None, "--condition", 
                                                    help="条件式 (条件付きの場合に必要)"),
    sequence: Optional[int] = typer.Option(None, "--sequence", "-s", 
                                        help="順序番号 (並列の場合に使用)")
):
    """
    新しいワークフローを作成
    """
    try:
        db = next(get_db())
        
        # プロセスの存在確認
        process = db.query(Process).filter(Process.id == process_id).first()
        if not process:
            console.print(Panel(f"プロセス（ID: {process_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 開始タスクの存在確認（指定されている場合）
        if from_task_id:
            from_task = db.query(Task).filter(Task.id == from_task_id).first()
            if not from_task:
                console.print(Panel(f"開始タスク（ID: {from_task_id}）が見つかりません", title="エラー", style="red"))
                raise typer.Exit(1)
            # タスクがプロセスに所属しているか確認
            if from_task.process_id != process_id:
                console.print(Panel(f"開始タスク（ID: {from_task_id}）はプロセス（ID: {process_id}）に所属していません", 
                                  title="エラー", style="red"))
                raise typer.Exit(1)
        
        # 終了タスクの存在確認（指定されている場合）
        if to_task_id:
            to_task = db.query(Task).filter(Task.id == to_task_id).first()
            if not to_task:
                console.print(Panel(f"終了タスク（ID: {to_task_id}）が見つかりません", title="エラー", style="red"))
                raise typer.Exit(1)
            # タスクがプロセスに所属しているか確認
            if to_task.process_id != process_id:
                console.print(Panel(f"終了タスク（ID: {to_task_id}）はプロセス（ID: {process_id}）に所属していません", 
                                  title="エラー", style="red"))
                raise typer.Exit(1)
        
        # 条件タイプの検証
        if condition_type not in ["常時", "条件付き", "並列"]:
            console.print(Panel("無効な条件タイプです。'常時', '条件付き', '並列'のいずれかを指定してください。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 条件付きタイプの場合、条件式が必要
        if condition_type == "条件付き" and not condition_expression:
            console.print(Panel("条件付きタイプの場合、条件式を指定する必要があります。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 新しいワークフローの作成
        new_workflow = Workflow(
            process_id=process_id,
            from_task_id=from_task_id,
            to_task_id=to_task_id,
            condition_type=condition_type,
            condition_expression=condition_expression,
            sequence_number=sequence
        )
        
        db.add(new_workflow)
        db.commit()
        db.refresh(new_workflow)
        
        from_task_name = "開始点" if from_task_id is None else f"タスク（ID: {from_task_id}）"
        to_task_name = "終了点" if to_task_id is None else f"タスク（ID: {to_task_id}）"
        
        console.print(Panel(
            f"ワークフローが作成されました（ID: {new_workflow.id}）\n"
            f"プロセス: {process.name} (ID: {process_id})\n"
            f"経路: {from_task_name} → {to_task_name}",
            title="成功"
        ))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ワークフロー作成中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def update(
    workflow_id: int = typer.Argument(..., help="ワークフローのID"),
    from_task_id: Optional[int] = typer.Option(None, "--from", help="開始タスクID"),
    to_task_id: Optional[int] = typer.Option(None, "--to", help="終了タスクID"),
    condition_type: Optional[str] = typer.Option(None, "--condition-type", "-c", 
                                              help="条件タイプ (常時, 条件付き, 並列)"),
    condition_expression: Optional[str] = typer.Option(None, "--condition", 
                                                    help="条件式"),
    sequence: Optional[int] = typer.Option(None, "--sequence", "-s", 
                                        help="順序番号")
):
    """
    ワークフローを更新
    """
    try:
        db = next(get_db())
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            console.print(Panel(f"ワークフロー（ID: {workflow_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 開始タスクの存在確認（指定されている場合）
        if from_task_id is not None:
            if from_task_id == 0:
                # 0を指定した場合は開始点を表す（NULLに設定）
                workflow.from_task_id = None
            else:
                from_task = db.query(Task).filter(Task.id == from_task_id).first()
                if not from_task:
                    console.print(Panel(f"開始タスク（ID: {from_task_id}）が見つかりません", title="エラー", style="red"))
                    raise typer.Exit(1)
                # タスクがプロセスに所属しているか確認
                if from_task.process_id != workflow.process_id:
                    console.print(Panel(f"開始タスク（ID: {from_task_id}）はプロセス（ID: {workflow.process_id}）に所属していません", 
                                      title="エラー", style="red"))
                    raise typer.Exit(1)
                workflow.from_task_id = from_task_id
        
        # 終了タスクの存在確認（指定されている場合）
        if to_task_id is not None:
            if to_task_id == 0:
                # 0を指定した場合は終了点を表す（NULLに設定）
                workflow.to_task_id = None
            else:
                to_task = db.query(Task).filter(Task.id == to_task_id).first()
                if not to_task:
                    console.print(Panel(f"終了タスク（ID: {to_task_id}）が見つかりません", title="エラー", style="red"))
                    raise typer.Exit(1)
                # タスクがプロセスに所属しているか確認
                if to_task.process_id != workflow.process_id:
                    console.print(Panel(f"終了タスク（ID: {to_task_id}）はプロセス（ID: {workflow.process_id}）に所属していません", 
                                      title="エラー", style="red"))
                    raise typer.Exit(1)
                workflow.to_task_id = to_task_id
        
        # 条件タイプの検証と更新
        if condition_type is not None:
            if condition_type not in ["常時", "条件付き", "並列"]:
                console.print(Panel("無効な条件タイプです。'常時', '条件付き', '並列'のいずれかを指定してください。", 
                                   title="エラー", style="red"))
                raise typer.Exit(1)
            workflow.condition_type = condition_type
        
        # 条件式の更新
        if condition_expression is not None:
            workflow.condition_expression = condition_expression
        
        # 順序番号の更新
        if sequence is not None:
            workflow.sequence_number = sequence
        
        # 更新後の検証
        if workflow.condition_type == "条件付き" and not workflow.condition_expression:
            console.print(Panel("条件付きタイプの場合、条件式を指定する必要があります。", 
                               title="エラー", style="red"))
            raise typer.Exit(1)
        
        db.commit()
        console.print(Panel(f"ワークフロー（ID: {workflow_id}）を更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ワークフロー更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def delete(
    workflow_id: int = typer.Argument(..., help="ワークフローのID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除")
):
    """
    ワークフローを削除
    """
    try:
        db = next(get_db())
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            console.print(Panel(f"ワークフロー（ID: {workflow_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 削除確認（forceが指定されていない場合）
        if not force:
            from_task_name = "開始点" if workflow.from_task_id is None else f"タスク（ID: {workflow.from_task_id}）"
            to_task_name = "終了点" if workflow.to_task_id is None else f"タスク（ID: {workflow.to_task_id}）"
            
            confirm = typer.confirm(
                f"ワークフロー（ID: {workflow_id}、{from_task_name} → {to_task_name}）を削除しますか？"
            )
            if not confirm:
                console.print(Panel("削除をキャンセルしました。", title="情報"))
                return
        
        # ワークフローの削除
        db.delete(workflow)
        db.commit()
        
        console.print(Panel(f"ワークフロー（ID: {workflow_id}）を削除しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ワークフロー削除中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1) 
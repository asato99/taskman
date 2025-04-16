"""
Task step management commands
"""
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from taskman.database.connection import get_db
from taskman.models.task import Task
from taskman.models.task_step import TaskStep

console = Console()
app = typer.Typer()


@app.command()
def list(
    task_id: Optional[int] = typer.Option(None, "--task", "-t", help="タスクIDでフィルタリング")
):
    """
    タスクステップ一覧を表示
    """
    try:
        db = next(get_db())
        query = db.query(TaskStep)
        
        if task_id:
            query = query.filter(TaskStep.task_id == task_id)
            
        steps = query.all()
        
        if not steps:
            message = "タスクステップが見つかりませんでした。"
            if task_id:
                message = f"タスク（ID: {task_id}）に関連するステップが見つかりませんでした。"
            console.print(Panel(message, title="情報"))
            return
        
        # タスク名を表示するためのテーブルヘッダーを設定
        if task_id:
            task = db.query(Task).filter(Task.id == task_id).first()
            task_name = task.name if task else f"不明 (ID: {task_id})"
            title = f"タスク「{task_name}」のステップ一覧"
        else:
            title = "全タスクステップ一覧"
        
        table = Table(title=title)
        table.add_column("ID", style="dim")
        table.add_column("タスク名")
        table.add_column("ステップ番号")
        table.add_column("ステップ名")
        table.add_column("予想所要時間")
        
        for step in steps:
            # タスク名を取得
            if hasattr(step, 'task') and step.task:
                task_name = step.task.name
            else:
                task = db.query(Task).filter(Task.id == step.task_id).first()
                task_name = task.name if task else f"不明 (ID: {step.task_id})"
            
            # 所要時間の表示形式を整える
            duration = f"{step.expected_duration}分" if step.expected_duration else "-"
            
            table.add_row(
                str(step.id),
                task_name,
                str(step.step_number),
                step.name,
                duration
            )
        
        console.print(table)
    except Exception as e:
        console.print(Panel(f"タスクステップ一覧の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def show(
    step_id: int = typer.Argument(..., help="タスクステップのID")
):
    """
    タスクステップの詳細を表示
    """
    try:
        db = next(get_db())
        step = db.query(TaskStep).filter(TaskStep.id == step_id).first()
        
        if not step:
            console.print(Panel(f"タスクステップ（ID: {step_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # タスク情報を取得
        task = db.query(Task).filter(Task.id == step.task_id).first()
        task_name = task.name if task else f"不明 (ID: {step.task_id})"
        
        # 詳細情報の表示
        console.print(Panel(f"[bold]タスクステップ詳細（ID: {step.id}）[/bold]", title="情報"))
        console.print(f"[bold]タスク:[/bold] {task_name} (ID: {step.task_id})")
        console.print(f"[bold]ステップ番号:[/bold] {step.step_number}")
        console.print(f"[bold]ステップ名:[/bold] {step.name}")
        console.print(f"[bold]説明:[/bold] {step.description or '未設定'}")
        console.print(f"[bold]予想所要時間:[/bold] {f'{step.expected_duration}分' if step.expected_duration else '未設定'}")
        console.print(f"[bold]必要なリソース:[/bold] {step.required_resources or '未設定'}")
        console.print(f"[bold]検証方法:[/bold] {step.verification_method or '未設定'}")
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクステップ情報の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def create(
    task_id: int = typer.Option(..., "--task", "-t", help="タスクID"),
    name: str = typer.Option(..., "--name", "-n", help="ステップ名"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="説明"),
    duration: Optional[int] = typer.Option(None, "--duration", help="予想所要時間（分）"),
    resources: Optional[str] = typer.Option(None, "--resources", "-r", help="必要なリソース"),
    verification: Optional[str] = typer.Option(None, "--verification", "-v", help="検証方法"),
    step_number: Optional[int] = typer.Option(None, "--step-number", "-s", help="ステップ番号（省略時は自動設定）")
):
    """
    新しいタスクステップを作成
    """
    try:
        db = next(get_db())
        
        # タスクの存在確認
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            console.print(Panel(f"タスク（ID: {task_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # ステップ番号の自動設定（省略時）
        if step_number is None:
            # 現在の最大ステップ番号を取得
            max_step_query = db.query(TaskStep).filter(TaskStep.task_id == task_id).order_by(TaskStep.step_number.desc()).first()
            if max_step_query:
                step_number = max_step_query.step_number + 1
            else:
                step_number = 1
        else:
            # 指定されたステップ番号が既に使用されていないか確認
            existing_step = db.query(TaskStep).filter(
                TaskStep.task_id == task_id,
                TaskStep.step_number == step_number
            ).first()
            
            if existing_step:
                console.print(Panel(
                    f"ステップ番号 {step_number} は既にタスク（ID: {task_id}）で使用されています。"
                    "別のステップ番号を指定するか、省略して自動設定を使用してください。", 
                    title="エラー", style="red"
                ))
                raise typer.Exit(1)
        
        # 新しいタスクステップの作成
        new_step = TaskStep(
            task_id=task_id,
            step_number=step_number,
            name=name,
            description=description,
            expected_duration=duration,
            required_resources=resources,
            verification_method=verification
        )
        
        db.add(new_step)
        db.commit()
        db.refresh(new_step)
        
        console.print(Panel(
            f"タスクステップが作成されました（ID: {new_step.id}）\n"
            f"タスク: {task.name} (ID: {task_id})\n"
            f"ステップ番号: {step_number}, 名前: {name}",
            title="成功"
        ))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクステップ作成中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def update(
    step_id: int = typer.Argument(..., help="タスクステップのID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="ステップ名"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="説明"),
    duration: Optional[int] = typer.Option(None, "--duration", help="予想所要時間（分）"),
    resources: Optional[str] = typer.Option(None, "--resources", "-r", help="必要なリソース"),
    verification: Optional[str] = typer.Option(None, "--verification", "-v", help="検証方法"),
    step_number: Optional[int] = typer.Option(None, "--step-number", "-s", help="ステップ番号")
):
    """
    タスクステップを更新
    """
    try:
        db = next(get_db())
        step = db.query(TaskStep).filter(TaskStep.id == step_id).first()
        
        if not step:
            console.print(Panel(f"タスクステップ（ID: {step_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # ステップ番号の変更時、同じタスク内で既に使用されていないか確認
        if step_number is not None and step_number != step.step_number:
            existing_step = db.query(TaskStep).filter(
                TaskStep.task_id == step.task_id,
                TaskStep.step_number == step_number,
                TaskStep.id != step_id
            ).first()
            
            if existing_step:
                console.print(Panel(
                    f"ステップ番号 {step_number} は既にタスク（ID: {step.task_id}）で使用されています。", 
                    title="エラー", style="red"
                ))
                raise typer.Exit(1)
            
            step.step_number = step_number
        
        # 変更がある場合のみ更新
        if name is not None:
            step.name = name
        if description is not None:
            step.description = description
        if duration is not None:
            step.expected_duration = duration
        if resources is not None:
            step.required_resources = resources
        if verification is not None:
            step.verification_method = verification
        
        db.commit()
        console.print(Panel(f"タスクステップ（ID: {step_id}）を更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクステップ更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def delete(
    step_id: int = typer.Argument(..., help="タスクステップのID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除"),
    reorder: bool = typer.Option(False, "--reorder", "-r", help="ステップ番号を自動的に振り直す")
):
    """
    タスクステップを削除
    """
    try:
        db = next(get_db())
        step = db.query(TaskStep).filter(TaskStep.id == step_id).first()
        
        if not step:
            console.print(Panel(f"タスクステップ（ID: {step_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # タスク情報を取得
        task = db.query(Task).filter(Task.id == step.task_id).first()
        task_name = task.name if task else f"不明 (ID: {step.task_id})"
        
        # 削除確認（forceが指定されていない場合）
        if not force:
            confirm = typer.confirm(
                f"タスクステップ（ID: {step_id}、タスク: {task_name}、ステップ番号: {step.step_number}）を削除しますか？"
            )
            if not confirm:
                console.print(Panel("削除をキャンセルしました。", title="情報"))
                return
        
        # タスクステップの削除
        deleted_step_number = step.step_number
        task_id = step.task_id
        
        db.delete(step)
        
        # ステップ番号の振り直し
        if reorder:
            # 同じタスクの削除対象より後のステップを取得
            subsequent_steps = db.query(TaskStep).filter(
                TaskStep.task_id == task_id,
                TaskStep.step_number > deleted_step_number
            ).order_by(TaskStep.step_number).all()
            
            # ステップ番号を1つずつ減らす
            for s in subsequent_steps:
                s.step_number -= 1
        
        db.commit()
        
        message = f"タスクステップ（ID: {step_id}）を削除しました"
        if reorder:
            message += f"\n{len(subsequent_steps)}個のステップ番号を自動的に更新しました"
        
        console.print(Panel(message, title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"タスクステップ削除中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def reorder(
    task_id: int = typer.Argument(..., help="タスクID")
):
    """
    タスクのステップ番号を連続した番号に振り直す
    """
    try:
        db = next(get_db())
        
        # タスクの存在確認
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            console.print(Panel(f"タスク（ID: {task_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # タスクのステップを取得
        steps = db.query(TaskStep).filter(
            TaskStep.task_id == task_id
        ).order_by(TaskStep.step_number).all()
        
        if not steps:
            console.print(Panel(f"タスク（ID: {task_id}）にはステップがありません", title="情報"))
            return
        
        # ステップ番号を1から連続して振り直す
        for i, step in enumerate(steps, 1):
            if step.step_number != i:
                step.step_number = i
        
        db.commit()
        
        console.print(Panel(
            f"タスク「{task.name}」（ID: {task_id}）の{len(steps)}個のステップ番号を振り直しました",
            title="成功"
        ))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"ステップ番号の振り直し中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1) 
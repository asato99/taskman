"""
Objective management commands
"""
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from taskman.database.connection import get_db
from taskman.models import Objective

console = Console()
app = typer.Typer()


@app.command()
def list(
    status: str = typer.Option(None, "--status", "-s", help="Filter by status (進行中, 達成, 未達成, 中止)")
):
    """
    List all objectives
    """
    try:
        db = next(get_db())
        query = db.query(Objective)
        
        if status:
            query = query.filter(Objective.status == status)
            
        objectives = query.all()
        
        if not objectives:
            console.print(Panel("目標が見つかりませんでした。", title="情報"))
            return
        
        table = Table(title="目標一覧")
        table.add_column("ID", style="dim")
        table.add_column("タイトル")
        table.add_column("測定指標")
        table.add_column("目標値")
        table.add_column("現在値")
        table.add_column("期限")
        table.add_column("状態")
        
        for obj in objectives:
            table.add_row(
                str(obj.id),
                obj.title,
                obj.measure or "-",
                str(obj.target_value) if obj.target_value is not None else "-",
                str(obj.current_value) if obj.current_value is not None else "0",
                obj.time_frame or "-",
                obj.status
            )
        
        console.print(table)
    except Exception as e:
        console.print(Panel(f"目標一覧の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def create(
    title: str = typer.Option(..., "--title", "-t", help="目標のタイトル"),
    description: str = typer.Option("", "--description", "-d", help="目標の説明"),
    measure: str = typer.Option(None, "--measure", "-m", help="測定指標"),
    target: float = typer.Option(None, "--target", help="目標値"),
    time_frame: str = typer.Option(None, "--time-frame", help="期限"),
    parent_id: int = typer.Option(None, "--parent", "-p", help="親目標のID")
):
    """
    Create a new objective
    """
    try:
        db = next(get_db())
        
        # 親目標の存在確認
        if parent_id:
            parent = db.query(Objective).filter(Objective.id == parent_id).first()
            if not parent:
                console.print(Panel(f"親目標（ID: {parent_id}）が見つかりません", title="エラー", style="red"))
                raise typer.Exit(1)
        
        # 新しい目標の作成
        new_objective = Objective(
            title=title,
            description=description,
            measure=measure,
            target_value=target,
            time_frame=time_frame,
            status="進行中",
            parent_id=parent_id
        )
        
        db.add(new_objective)
        db.commit()
        db.refresh(new_objective)
        
        console.print(Panel(f"目標「{title}」が作成されました（ID: {new_objective.id}）", title="成功"))
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"目標作成中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def show(
    objective_id: int = typer.Argument(..., help="目標のID")
):
    """
    Show details of an objective
    """
    try:
        db = next(get_db())
        objective = db.query(Objective).filter(Objective.id == objective_id).first()
        
        if not objective:
            console.print(Panel(f"目標（ID: {objective_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 親目標情報の取得
        parent = None
        if objective.parent_id:
            parent = db.query(Objective).filter(Objective.id == objective.parent_id).first()
        
        # 子目標の取得
        children = db.query(Objective).filter(Objective.parent_id == objective_id).all()
        
        # 詳細情報の表示
        console.print(Panel(f"[bold]目標詳細（ID: {objective.id}）[/bold]", title="情報"))
        console.print(f"[bold]タイトル:[/bold] {objective.title}")
        console.print(f"[bold]説明:[/bold] {objective.description or '未設定'}")
        console.print(f"[bold]測定指標:[/bold] {objective.measure or '未設定'}")
        console.print(f"[bold]目標値:[/bold] {objective.target_value if objective.target_value is not None else '未設定'}")
        console.print(f"[bold]現在値:[/bold] {objective.current_value if objective.current_value is not None else '0'}")
        console.print(f"[bold]期限:[/bold] {objective.time_frame or '未設定'}")
        console.print(f"[bold]状態:[/bold] {objective.status}")
        console.print(f"[bold]作成日時:[/bold] {objective.created_at}")
        console.print(f"[bold]更新日時:[/bold] {objective.updated_at}")
        
        if parent:
            console.print(f"[bold]親目標:[/bold] {parent.title} (ID: {parent.id})")
        
        if children:
            console.print("\n[bold]子目標:[/bold]")
            child_table = Table()
            child_table.add_column("ID")
            child_table.add_column("タイトル")
            child_table.add_column("状態")
            
            for child in children:
                child_table.add_row(str(child.id), child.title, child.status)
            
            console.print(child_table)
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"目標情報の取得中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def update(
    objective_id: int = typer.Argument(..., help="目標のID"),
    title: str = typer.Option(None, "--title", "-t", help="目標のタイトル"),
    description: str = typer.Option(None, "--description", "-d", help="目標の説明"),
    measure: str = typer.Option(None, "--measure", "-m", help="測定指標"),
    target: float = typer.Option(None, "--target", help="目標値"),
    current: float = typer.Option(None, "--current", "-c", help="現在値"),
    time_frame: str = typer.Option(None, "--time-frame", help="期限"),
    status: str = typer.Option(None, "--status", "-s", 
                              help="状態（進行中, 達成, 未達成, 中止）")
):
    """
    Update an objective
    """
    try:
        db = next(get_db())
        objective = db.query(Objective).filter(Objective.id == objective_id).first()
        
        if not objective:
            console.print(Panel(f"目標（ID: {objective_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 変更がある場合のみ更新
        if title is not None:
            objective.title = title
        if description is not None:
            objective.description = description
        if measure is not None:
            objective.measure = measure
        if target is not None:
            objective.target_value = target
        if current is not None:
            objective.current_value = current
        if time_frame is not None:
            objective.time_frame = time_frame
        if status is not None:
            if status not in ["進行中", "達成", "未達成", "中止"]:
                console.print(Panel("無効な状態です。'進行中', '達成', '未達成', '中止'のいずれかを指定してください。", 
                                  title="エラー", style="red"))
                raise typer.Exit(1)
            objective.status = status
        
        db.commit()
        console.print(Panel(f"目標（ID: {objective_id}）を更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"目標更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def delete(
    objective_id: int = typer.Argument(..., help="目標のID"),
    force: bool = typer.Option(False, "--force", "-f", help="子目標も含めて強制的に削除")
):
    """
    Delete an objective
    """
    try:
        db = next(get_db())
        objective = db.query(Objective).filter(Objective.id == objective_id).first()
        
        if not objective:
            console.print(Panel(f"目標（ID: {objective_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        # 子目標の確認
        children = db.query(Objective).filter(Objective.parent_id == objective_id).all()
        if children and not force:
            console.print(Panel(f"この目標には{len(children)}個の子目標があります。削除するには --force オプションを使用してください。", 
                              title="警告", style="yellow"))
            raise typer.Exit(1)
        
        # 子目標の削除（forceが指定された場合）
        if children and force:
            for child in children:
                db.delete(child)
        
        # 目標の削除
        db.delete(objective)
        db.commit()
        
        if children and force:
            console.print(Panel(f"目標（ID: {objective_id}）とその子目標（{len(children)}個）を削除しました", title="成功"))
        else:
            console.print(Panel(f"目標（ID: {objective_id}）を削除しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"目標削除中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1)


@app.command()
def status(
    objective_id: int = typer.Argument(..., help="目標のID"),
    new_status: str = typer.Argument(..., help="新しい状態（進行中, 達成, 未達成, 中止）")
):
    """
    Update the status of an objective
    """
    try:
        if new_status not in ["進行中", "達成", "未達成", "中止"]:
            console.print(Panel("無効な状態です。'進行中', '達成', '未達成', '中止'のいずれかを指定してください。", 
                              title="エラー", style="red"))
            raise typer.Exit(1)
        
        db = next(get_db())
        objective = db.query(Objective).filter(Objective.id == objective_id).first()
        
        if not objective:
            console.print(Panel(f"目標（ID: {objective_id}）が見つかりません", title="エラー", style="red"))
            raise typer.Exit(1)
        
        old_status = objective.status
        objective.status = new_status
        db.commit()
        
        console.print(Panel(f"目標（ID: {objective_id}）の状態を「{old_status}」から「{new_status}」に更新しました", title="成功"))
        
    except SQLAlchemyError as e:
        console.print(Panel(f"データベースエラー: {e}", title="エラー", style="red"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"状態更新中にエラーが発生しました: {e}", title="エラー", style="red"))
        raise typer.Exit(1) 
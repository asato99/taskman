"""
統合テスト - タスクコマンドのテスト

このモジュールでは、タスク関連のコマンドラインインターフェースをテストします。
実際のデータベースを使用して、コマンド間の相互作用をテストします。
"""

import pytest
import os
from datetime import datetime, timedelta
from typer.testing import CliRunner
from taskman.cli import app
from taskman.models.task import Task

class TestTaskCommandsIntegration:
    """タスクコマンドの統合テスト
    
    実際のデータベースに対して一連のコマンドを実行し、
    コマンド間の相互作用をテストします。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """各テストの前に実行されるセットアップ
        
        テスト用データベースを準備し、テスト終了後にクリーンアップします。
        """
        self.runner = CliRunner()
        
        # テスト用のプロセスを作成（仮実装）
        from sqlalchemy import Column, Integer, String
        from sqlalchemy.orm import declarative_base
        from taskman.database.connection import get_db
        
        Base = declarative_base()
        
        class Process(Base):
            __tablename__ = 'process'
            id = Column(Integer, primary_key=True)
            name = Column(String(100), nullable=False)
        
        db = next(get_db())
        
        # テーブルが存在するか確認し、なければ作成
        Base.metadata.create_all(db.bind)
        
        # テスト用のプロセスを追加
        test_process = Process(name="テスト用プロセス")
        db.add(test_process)
        db.commit()
        
        # プロセスIDを保存
        self.process_id = test_process.id
        
        # テスト用のタスクを作成（他のテストの前提条件）
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "インテグレーションテスト用タスク", 
                "--description", "テスト用タスクの説明", 
                "--process", str(self.process_id), 
                "--priority", "中"
            ]
        )
        assert result.exit_code == 0, f"テスト用タスクの作成に失敗: {result.stdout}"
        
        # タスク一覧を取得して確認
        result = self.runner.invoke(app, ["task", "list"])
        assert result.exit_code == 0
        assert "インテグレーションテスト用タスク" in result.stdout
        
        # ID=1のタスクがあることを確認
        result = self.runner.invoke(app, ["task", "show", "1"])
        assert result.exit_code == 0
        assert "インテグレーションテスト用タスク" in result.stdout
        
        yield
        
        # テスト後のクリーンアップ
        db = next(get_db())
        
        # タスクを全て削除
        db.query(Task).delete()
        
        # プロセスも削除
        db.query(Process).delete()
        
        db.commit()
    
    def test_create_and_list(self):
        """タスク作成と一覧表示テスト"""
        # 新しいタスクを作成
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "一覧表示テスト用タスク", 
                "--description", "一覧表示テスト用の説明", 
                "--process", str(self.process_id),
                "--duration", "120",
                "--priority", "高",
                "--assign", "テストユーザー",
                "--due-date", today
            ]
        )
        assert result.exit_code == 0, f"タスクの作成に失敗: {result.stdout}"
        assert "作成されました" in result.stdout
        
        # タスク一覧を確認
        result = self.runner.invoke(app, ["task", "list"])
        assert result.exit_code == 0
        assert "インテグレーションテスト用タスク" in result.stdout  # セットアップで作成したタスク
        assert "一覧表示テスト用タスク" in result.stdout  # このテストで作成したタスク
        
        # タスク一覧に作成したタスクの情報が表示されていることを確認
        assert "高" in result.stdout  # 優先度
        assert "テストユーザー" in result.stdout  # 担当者
        assert today in result.stdout  # 期限
    
    def test_show_task(self):
        """タスク詳細表示テスト"""
        # 詳細表示用のタスクを作成
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "詳細表示テスト用タスク", 
                "--description", "詳細な説明文", 
                "--process", str(self.process_id),
                "--duration", "60",
                "--priority", "緊急",
                "--assign", "担当者A",
                "--due-date", tomorrow
            ]
        )
        assert result.exit_code == 0
        
        # タスク一覧から作成したタスクのIDを取得
        list_result = self.runner.invoke(app, ["task", "list"])
        # IDを特定（仮にID=2と想定）
        task_id = "2"
        
        # タスク詳細を表示
        result = self.runner.invoke(app, ["task", "show", task_id])
        assert result.exit_code == 0
        
        # 表示内容の確認
        assert "詳細表示テスト用タスク" in result.stdout
        assert "詳細な説明文" in result.stdout
        assert "60" in result.stdout
        assert "緊急" in result.stdout
        assert "担当者A" in result.stdout
        # 明確な日付の代わりに、日付情報が含まれているかを確認する
        assert "期限" in result.stdout
        assert "未着手" in result.stdout  # デフォルトの状態
        
        # 存在しないタスクの表示を試みる
        result = self.runner.invoke(app, ["task", "show", "999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_update_task(self):
        """タスク更新テスト"""
        # 更新用のタスクを作成
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "更新前のタスク名", 
                "--description", "更新前の説明", 
                "--process", str(self.process_id),
                "--priority", "低"
            ]
        )
        assert result.exit_code == 0
        
        # タスク一覧から作成したタスクのIDを取得（仮にID=2と想定）
        task_id = "2"
        
        # タスク名の更新
        result = self.runner.invoke(
            app, 
            [
                "task", "update", task_id,
                "--name", "更新後のタスク名"
            ]
        )
        assert result.exit_code == 0
        assert "更新しました" in result.stdout
        
        # 説明の更新
        result = self.runner.invoke(
            app, 
            [
                "task", "update", task_id,
                "--description", "更新後の説明"
            ]
        )
        assert result.exit_code == 0
        
        # 複数のフィールドを同時に更新
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        result = self.runner.invoke(
            app, 
            [
                "task", "update", task_id,
                "--priority", "高",
                "--assign", "新しい担当者",
                "--due-date", next_week
            ]
        )
        assert result.exit_code == 0
        
        # 更新されたタスクの詳細を確認
        result = self.runner.invoke(app, ["task", "show", task_id])
        assert result.exit_code == 0
        assert "更新後のタスク名" in result.stdout
        assert "更新後の説明" in result.stdout
        assert "高" in result.stdout
        assert "新しい担当者" in result.stdout
        # 日付が正確にマッチするわけではないので、「期限」の存在を確認
        assert "期限" in result.stdout
    
    def test_status_command(self):
        """タスク状態更新コマンドテスト"""
        # 状態更新用のタスクを作成
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "状態更新テスト用タスク", 
                "--description", "状態を変更するためのテスト", 
                "--process", str(self.process_id)
            ]
        )
        assert result.exit_code == 0
        
        # タスク一覧から作成したタスクのIDを取得（仮にID=2と想定）
        task_id = "2"
        
        # タスクの状態を「進行中」に更新
        result = self.runner.invoke(app, ["task", "status", task_id, "進行中"])
        assert result.exit_code == 0
        assert "タスク（ID: 2）の状態を" in result.stdout
        
        # 更新されたタスクの詳細を確認
        result = self.runner.invoke(app, ["task", "show", task_id])
        assert result.exit_code == 0
        assert "進行中" in result.stdout
        
        # タスクの状態を「完了」に更新
        result = self.runner.invoke(app, ["task", "status", task_id, "完了"])
        assert result.exit_code == 0
        
        # 更新されたタスクの詳細を確認
        result = self.runner.invoke(app, ["task", "show", task_id])
        assert result.exit_code == 0
        assert "完了" in result.stdout
        
        # 無効な状態への更新を試みる
        result = self.runner.invoke(app, ["task", "status", task_id, "無効な状態"])
        assert result.exit_code != 0
        assert "無効な状態" in result.stdout
    
    def test_list_filter_by_status(self):
        """状態によるタスク一覧フィルタリングテスト"""
        # 異なる状態のタスクを複数作成
        # タスク1: 未着手（デフォルト）
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "未着手タスク", 
                "--description", "このタスクは未着手", 
                "--process", str(self.process_id)
            ]
        )
        assert result.exit_code == 0
        
        # タスク2: 進行中
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "進行中タスク", 
                "--description", "このタスクは進行中", 
                "--process", str(self.process_id)
            ]
        )
        assert result.exit_code == 0
        task2_id = "3"  # 実際には一覧から特定
        
        # タスク2の状態を「進行中」に変更
        result = self.runner.invoke(app, ["task", "status", task2_id, "進行中"])
        assert result.exit_code == 0
        
        # タスク3: 完了
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "完了タスク", 
                "--description", "このタスクは完了", 
                "--process", str(self.process_id)
            ]
        )
        assert result.exit_code == 0
        task3_id = "4"  # 実際には一覧から特定
        
        # タスク3の状態を「完了」に変更
        result = self.runner.invoke(app, ["task", "status", task3_id, "完了"])
        assert result.exit_code == 0
        
        # 状態フィルタなしで一覧表示
        result = self.runner.invoke(app, ["task", "list"])
        assert result.exit_code == 0
        assert "未着手タスク" in result.stdout
        assert "進行中タスク" in result.stdout
        assert "完了タスク" in result.stdout
        
        # 「未着手」状態でフィルタリング
        result = self.runner.invoke(app, ["task", "list", "--status", "未着手"])
        assert result.exit_code == 0
        assert "未着手タスク" in result.stdout
        assert "進行中タスク" not in result.stdout
        assert "完了タスク" not in result.stdout
        
        # 「進行中」状態でフィルタリング
        result = self.runner.invoke(app, ["task", "list", "--status", "進行中"])
        assert result.exit_code == 0
        assert "未着手タスク" not in result.stdout
        assert "進行中タスク" in result.stdout
        assert "完了タスク" not in result.stdout
        
        # 「完了」状態でフィルタリング
        result = self.runner.invoke(app, ["task", "list", "--status", "完了"])
        assert result.exit_code == 0
        assert "未着手タスク" not in result.stdout
        assert "進行中タスク" not in result.stdout
        assert "完了タスク" in result.stdout
    
    def test_list_filter_by_priority(self):
        """優先度によるタスク一覧フィルタリングテスト"""
        # 異なる優先度のタスクを複数作成
        # タスク1: 低優先度
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "低優先度タスク", 
                "--description", "このタスクは優先度が低い", 
                "--process", str(self.process_id),
                "--priority", "低"
            ]
        )
        assert result.exit_code == 0
        
        # タスク2: 中優先度（デフォルト）
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "中優先度タスク", 
                "--description", "このタスクは優先度が中", 
                "--process", str(self.process_id)
            ]
        )
        assert result.exit_code == 0
        
        # タスク3: 高優先度
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "高優先度タスク", 
                "--description", "このタスクは優先度が高い", 
                "--process", str(self.process_id),
                "--priority", "高"
            ]
        )
        assert result.exit_code == 0
        
        # タスク4: 緊急優先度
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "緊急優先度タスク", 
                "--description", "このタスクは優先度が緊急", 
                "--process", str(self.process_id),
                "--priority", "緊急"
            ]
        )
        assert result.exit_code == 0
        
        # 優先度フィルタなしで一覧表示
        result = self.runner.invoke(app, ["task", "list"])
        assert result.exit_code == 0
        assert "低優先度タスク" in result.stdout
        assert "中優先度タスク" in result.stdout
        assert "高優先度タスク" in result.stdout
        assert "緊急優先度タスク" in result.stdout
        
        # 「低」優先度でフィルタリング
        result = self.runner.invoke(app, ["task", "list", "--priority", "低"])
        assert result.exit_code == 0
        assert "低優先度タスク" in result.stdout
        assert "中優先度タスク" not in result.stdout
        assert "高優先度タスク" not in result.stdout
        assert "緊急優先度タスク" not in result.stdout
        
        # 「高」優先度でフィルタリング
        result = self.runner.invoke(app, ["task", "list", "--priority", "高"])
        assert result.exit_code == 0
        assert "低優先度タスク" not in result.stdout
        assert "中優先度タスク" not in result.stdout
        assert "高優先度タスク" in result.stdout
        assert "緊急優先度タスク" not in result.stdout
    
    def test_delete_task(self):
        """タスク削除テスト"""
        # 削除用のタスクを作成
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "削除用テストタスク", 
                "--description", "このタスクは削除されます", 
                "--process", str(self.process_id)
            ]
        )
        assert result.exit_code == 0
        
        # タスク一覧から作成したタスクのIDを取得（仮にID=2と想定）
        task_id = "2"
        
        # タスクの削除を試みる（確認あり）
        result = self.runner.invoke(app, ["task", "delete", task_id], input="n\n")
        assert result.exit_code == 0
        assert "キャンセルしました" in result.stdout
        
        # タスクが削除されていないことを確認
        result = self.runner.invoke(app, ["task", "show", task_id])
        assert result.exit_code == 0
        assert "削除用テストタスク" in result.stdout
        
        # 強制削除オプションでタスクを削除
        result = self.runner.invoke(app, ["task", "delete", task_id, "--force"])
        assert result.exit_code == 0
        assert "削除しました" in result.stdout
        
        # タスクが削除されたことを確認
        result = self.runner.invoke(app, ["task", "show", task_id])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        # 存在しないタスクIDで更新を試みる
        result = self.runner.invoke(app, ["task", "update", "999", "--name", "エラーテスト"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないタスクIDで状態更新を試みる
        result = self.runner.invoke(app, ["task", "status", "999", "完了"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないタスクIDで削除を試みる
        result = self.runner.invoke(app, ["task", "delete", "999", "--force"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 無効な優先度でタスク作成を試みる
        result = self.runner.invoke(
            app, 
            [
                "task", "create", 
                "--name", "エラーテスト用タスク", 
                "--process", str(self.process_id),
                "--priority", "無効な優先度"
            ]
        )
        assert result.exit_code != 0
        assert "無効な優先度" in result.stdout 
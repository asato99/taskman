"""
タスクインスタンスコマンドの統合テスト
"""
import os
import sys
import pytest
from typer.testing import CliRunner
from datetime import datetime

# プロジェクトルートをインポートパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from taskman.models.task import Task
from taskman.models.process import Process
from taskman.models.process_instance import ProcessInstance
from taskman.models.task_instance import TaskInstance
from taskman.database.connection import get_db
from taskman.cli import app


class TestTaskInstanceCommandsIntegration:
    """タスクインスタンスコマンドの統合テスト
    
    すべてのテストは独立して実行できます。
    各テストはセットアップでテスト環境を準備し、テアダウンで環境をクリーンアップします。
    """
    
    runner = CliRunner()
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """テスト前のセットアップ
        
        プロセス、タスク、プロセスインスタンスを作成します。
        """
        # 前提条件の作成
        db = next(get_db())
        
        # プロセスの作成
        test_process = Process(name="テスト用プロセス", description="テスト用プロセスの説明")
        db.add(test_process)
        db.commit()
        db.refresh(test_process)
        self.process_id = test_process.id
        
        # タスクの作成
        test_task = Task(
            process_id=self.process_id,
            name="テスト用タスク",
            description="テスト用タスクの説明",
            priority="中"
        )
        db.add(test_task)
        db.commit()
        db.refresh(test_task)
        self.task_id = test_task.id
        
        # プロセスインスタンスの作成
        test_process_instance = ProcessInstance(
            process_id=self.process_id,
            status="実行中",
            created_by="テストユーザー"
        )
        db.add(test_process_instance)
        db.commit()
        db.refresh(test_process_instance)
        self.process_instance_id = test_process_instance.id
        
        yield
        
        # クリーンアップ
        db = next(get_db())
        db.query(TaskInstance).delete()
        db.query(ProcessInstance).delete()
        db.query(Task).delete()
        db.query(Process).delete()
        db.commit()
    
    def test_create_and_list(self):
        """タスクインスタンスの作成と一覧表示のテスト"""
        # タスクインスタンスの作成
        result = self.runner.invoke(
            app,
            [
                "task-instance", "create",
                "--instance", str(self.process_instance_id),
                "--task", str(self.task_id),
                "--assigned", "テスト担当者",
                "--notes", "テスト用メモ"
            ]
        )
        assert result.exit_code == 0, f"タスクインスタンスの作成に失敗: {result.stdout}"
        assert "タスクインスタンスが作成されました" in result.stdout
        
        # 一覧表示の確認
        result = self.runner.invoke(app, ["task-instance", "list"])
        assert result.exit_code == 0
        assert "テスト用タスク" in result.stdout
        assert "テスト担当者" in result.stdout
        assert "未着手" in result.stdout  # デフォルトのステータス
        
        # フィルタリングのテスト
        result = self.runner.invoke(
            app, 
            [
                "task-instance", "list",
                "--instance", str(self.process_instance_id)
            ]
        )
        assert result.exit_code == 0
        assert "テスト用タスク" in result.stdout
        
        result = self.runner.invoke(
            app, 
            [
                "task-instance", "list",
                "--status", "未着手"
            ]
        )
        assert result.exit_code == 0
        assert "テスト用タスク" in result.stdout
        
        result = self.runner.invoke(
            app, 
            [
                "task-instance", "list",
                "--assigned", "テスト担当者"
            ]
        )
        assert result.exit_code == 0
        assert "テスト用タスク" in result.stdout
    
    def test_show_task_instance(self):
        """タスクインスタンスの詳細表示のテスト"""
        # タスクインスタンスの作成
        create_result = self.runner.invoke(
            app,
            [
                "task-instance", "create",
                "--instance", str(self.process_instance_id),
                "--task", str(self.task_id),
                "--notes", "詳細表示テスト用メモ"
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したタスクインスタンスのIDを抽出
        db = next(get_db())
        task_instance = db.query(TaskInstance).first()
        task_instance_id = task_instance.id
        
        # 詳細表示
        result = self.runner.invoke(
            app,
            ["task-instance", "show", str(task_instance_id)]
        )
        assert result.exit_code == 0
        assert "タスクインスタンス詳細" in result.stdout
        assert "テスト用タスク" in result.stdout
        assert "詳細表示テスト用メモ" in result.stdout
        assert "未着手" in result.stdout
        
        # 存在しないIDの場合
        result = self.runner.invoke(
            app,
            ["task-instance", "show", "999"]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_status_changes(self):
        """タスクインスタンスのステータス変更テスト"""
        # タスクインスタンスの作成
        create_result = self.runner.invoke(
            app,
            [
                "task-instance", "create",
                "--instance", str(self.process_instance_id),
                "--task", str(self.task_id)
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したタスクインスタンスのIDを抽出
        db = next(get_db())
        task_instance = db.query(TaskInstance).first()
        task_instance_id = task_instance.id
        
        # 初期状態の確認
        show_result = self.runner.invoke(
            app,
            ["task-instance", "show", str(task_instance_id)]
        )
        assert "未着手" in show_result.stdout
        assert "未開始" in show_result.stdout  # 開始日時
        
        # 「実行中」に変更
        result = self.runner.invoke(
            app,
            ["task-instance", "status", str(task_instance_id), "実行中"]
        )
        assert result.exit_code == 0
        assert "ステータスを「未着手」から「実行中」に更新しました" in result.stdout
        
        # 変更後の確認
        show_result = self.runner.invoke(
            app,
            ["task-instance", "show", str(task_instance_id)]
        )
        assert "実行中" in show_result.stdout
        assert "未開始" not in show_result.stdout  # 開始日時が設定された
        
        # 「完了」に変更
        result = self.runner.invoke(
            app,
            ["task-instance", "status", str(task_instance_id), "完了"]
        )
        assert result.exit_code == 0
        
        # 変更後の確認
        show_result = self.runner.invoke(
            app,
            ["task-instance", "show", str(task_instance_id)]
        )
        assert "完了" in show_result.stdout
        assert "未完了" not in show_result.stdout  # 終了日時が設定された
        
        # 無効なステータスのテスト
        result = self.runner.invoke(
            app,
            ["task-instance", "status", str(task_instance_id), "無効なステータス"]
        )
        assert result.exit_code != 0
        assert "無効なステータスです" in result.stdout
    
    def test_update(self):
        """タスクインスタンスの更新テスト"""
        # タスクインスタンスの作成
        create_result = self.runner.invoke(
            app,
            [
                "task-instance", "create",
                "--instance", str(self.process_instance_id),
                "--task", str(self.task_id),
                "--assigned", "更新前担当者",
                "--notes", "更新前メモ"
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したタスクインスタンスのIDを抽出
        db = next(get_db())
        task_instance = db.query(TaskInstance).first()
        task_instance_id = task_instance.id
        
        # 担当者の更新
        result = self.runner.invoke(
            app,
            [
                "task-instance", "update", str(task_instance_id),
                "--assigned", "更新後担当者"
            ]
        )
        assert result.exit_code == 0
        assert "更新しました" in result.stdout
        
        # メモの更新
        result = self.runner.invoke(
            app,
            [
                "task-instance", "update", str(task_instance_id),
                "--notes", "更新後メモ"
            ]
        )
        assert result.exit_code == 0
        
        # 更新後の確認
        show_result = self.runner.invoke(
            app,
            ["task-instance", "show", str(task_instance_id)]
        )
        assert "更新後担当者" in show_result.stdout
        assert "更新後メモ" in show_result.stdout
    
    def test_delete(self):
        """タスクインスタンスの削除テスト"""
        # タスクインスタンスの作成
        create_result = self.runner.invoke(
            app,
            [
                "task-instance", "create",
                "--instance", str(self.process_instance_id),
                "--task", str(self.task_id)
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したタスクインスタンスのIDを抽出
        db = next(get_db())
        task_instance = db.query(TaskInstance).first()
        task_instance_id = task_instance.id
        
        # 削除（強制削除オプション付き）
        result = self.runner.invoke(
            app,
            ["task-instance", "delete", str(task_instance_id), "--force"]
        )
        assert result.exit_code == 0
        assert "削除しました" in result.stdout
        
        # 削除後の確認
        show_result = self.runner.invoke(
            app,
            ["task-instance", "show", str(task_instance_id)]
        )
        assert show_result.exit_code != 0
        assert "見つかりません" in show_result.stdout
    
    def test_delete_running_instance(self):
        """実行中のタスクインスタンス削除テスト"""
        # タスクインスタンスの作成
        create_result = self.runner.invoke(
            app,
            [
                "task-instance", "create",
                "--instance", str(self.process_instance_id),
                "--task", str(self.task_id)
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したタスクインスタンスのIDを抽出
        db = next(get_db())
        task_instance = db.query(TaskInstance).first()
        task_instance_id = task_instance.id
        
        # ステータスを「実行中」に変更
        status_result = self.runner.invoke(
            app,
            ["task-instance", "status", str(task_instance_id), "実行中"]
        )
        assert status_result.exit_code == 0
        
        # 通常の削除コマンドでは削除できないことを確認
        result = self.runner.invoke(
            app,
            ["task-instance", "delete", str(task_instance_id)]
        )
        assert result.exit_code != 0
        assert "実行中のタスクインスタンス" in result.stdout
        assert "--force オプション" in result.stdout
        
        # force オプション付きでは削除できることを確認
        result = self.runner.invoke(
            app,
            ["task-instance", "delete", str(task_instance_id), "--force"]
        )
        assert result.exit_code == 0
        assert "削除しました" in result.stdout 
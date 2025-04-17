"""
統合テスト - プロセスインスタンスコマンドのテスト

このモジュールでは、プロセスインスタンス関連のコマンドラインインターフェースをテストします。
実際のデータベースを使用して、コマンド間の相互作用をテストします。
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
from typer.testing import CliRunner
from taskman.cli import app
from taskman.models.process import Process
from taskman.models.process_instance import ProcessInstance
from taskman.models.task import Task
from taskman.models.task_instance import TaskInstance

class TestProcessInstanceCommandsIntegration:
    """プロセスインスタンスコマンドの統合テスト
    
    実際のデータベースに対して一連のコマンドを実行し、
    コマンド間の相互作用をテストします。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """各テストの前に実行されるセットアップ
        
        テスト用データベースを準備し、テスト終了後にクリーンアップします。
        """
        from taskman.database.connection import get_db
        
        self.runner = CliRunner()
        
        # 基本テスト用プロセスの作成
        result = self.runner.invoke(
            app,
            [
                "process", "create",
                "--name", "インテグレーションテスト用プロセス",
                "--description", "テスト用プロセスの説明"
            ]
        )
        assert result.exit_code == 0, f"テスト用プロセスの作成に失敗: {result.stdout}"
        
        # プロセスIDを保存（最初に作成したプロセスなのでID=1と想定）
        self.process_id = "1"
        
        # プロセスをアクティブ状態に設定
        status_result = self.runner.invoke(
            app,
            [
                "process", "status",
                self.process_id, "アクティブ"
            ]
        )
        assert status_result.exit_code == 0, f"プロセスのステータス設定に失敗: {status_result.stdout}"
        
        yield
        
        # テスト後のクリーンアップ
        db = next(get_db())
        db.query(TaskInstance).delete()
        db.query(ProcessInstance).delete()
        db.query(Task).delete()
        db.query(Process).delete()
        db.commit()
    
    def test_create_and_list(self):
        """プロセスインスタンスの作成と一覧表示テスト"""
        # プロセスインスタンスを作成
        result = self.runner.invoke(
            app,
            [
                "instance", "create",
                "--process", self.process_id,
                "--user", "テストユーザー"
            ]
        )
        # エラーメッセージを出力
        print(f"Exit code: {result.exit_code}")
        print(f"Output: {result.stdout}")
        if result.exception:
            print(f"Exception: {result.exception}")
        
        assert result.exit_code == 0, f"プロセスインスタンス作成失敗: {result.stdout}"
        assert "インスタンスが作成されました" in result.stdout or "作成されました" in result.stdout
        
        # もう1つプロセスインスタンスを作成
        result = self.runner.invoke(
            app,
            [
                "instance", "create",
                "--process", self.process_id,
                "--user", "テストユーザー2"
            ]
        )
        assert result.exit_code == 0
        
        # 一覧表示のテスト
        result = self.runner.invoke(app, ["instance", "list"])
        assert result.exit_code == 0
        assert "テストユーザー" in result.stdout
        assert "実行中" in result.stdout  # デフォルトステータス
        
        # フィルタリングのテスト（プロセスID）
        result = self.runner.invoke(
            app, 
            [
                "instance", "list",
                "--process", self.process_id
            ]
        )
        assert result.exit_code == 0
        assert "テストユーザー" in result.stdout
        
        # フィルタリングのテスト（ステータス）
        result = self.runner.invoke(
            app, 
            [
                "instance", "list",
                "--status", "実行中"
            ]
        )
        assert result.exit_code == 0
        assert "テストユーザー" in result.stdout
        
        # フィルタリングのテスト（ユーザー）
        result = self.runner.invoke(
            app, 
            [
                "instance", "list",
                "--user", "テストユーザー2"
            ]
        )
        assert result.exit_code == 0
        assert "テストユーザー2" in result.stdout
    
    def test_show_instance(self):
        """プロセスインスタンスの詳細表示テスト"""
        # インスタンスを作成
        create_result = self.runner.invoke(
            app,
            [
                "instance", "create",
                "--process", self.process_id,
                "--user", "詳細表示テスト"
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したインスタンスのIDを取得（仮にID=1と想定）
        from taskman.database.connection import get_db
        db = next(get_db())
        instance = db.query(ProcessInstance).first()
        instance_id = str(instance.id)
        
        # 詳細表示
        result = self.runner.invoke(
            app,
            ["instance", "show", instance_id]
        )
        assert result.exit_code == 0
        assert "インスタンス詳細" in result.stdout or "詳細" in result.stdout
        assert "テスト用プロセス" in result.stdout
        assert "詳細表示テスト" in result.stdout
        assert "実行中" in result.stdout  # デフォルトのステータス
        
        # 存在しないIDのテスト
        result = self.runner.invoke(
            app,
            ["instance", "show", "999"]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_status_changes(self):
        """プロセスインスタンスのステータス変更テスト"""
        # インスタンスを作成
        create_result = self.runner.invoke(
            app,
            [
                "instance", "create",
                "--process", self.process_id,
                "--user", "ステータス変更テスト"
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したインスタンスのIDを取得
        from taskman.database.connection import get_db
        db = next(get_db())
        instance = db.query(ProcessInstance).first()
        instance_id = str(instance.id)
        
        # 初期状態の確認
        show_result = self.runner.invoke(
            app,
            ["instance", "show", instance_id]
        )
        assert "実行中" in show_result.stdout  # デフォルトは「実行中」
        
        # 完了に変更
        result = self.runner.invoke(
            app,
            ["instance", "status", instance_id, "完了"]
        )
        assert result.exit_code == 0
        assert "ステータスを更新しました" in result.stdout or "更新しました" in result.stdout
        
        # 変更後の状態確認
        show_result = self.runner.invoke(
            app,
            ["instance", "show", instance_id]
        )
        assert "完了" in show_result.stdout
        
        # 無効なステータスに変更を試みる
        result = self.runner.invoke(
            app,
            ["instance", "status", instance_id, "無効な値"]
        )
        assert result.exit_code != 0
        assert "無効なステータス" in result.stdout
    
    def test_delete_instance(self):
        """プロセスインスタンス削除テスト"""
        # インスタンスを作成
        create_result = self.runner.invoke(
            app,
            [
                "instance", "create",
                "--process", self.process_id,
                "--user", "削除テスト"
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したインスタンスのIDを取得
        from taskman.database.connection import get_db
        db = next(get_db())
        instance = db.query(ProcessInstance).first()
        instance_id = str(instance.id)
        
        # インスタンスを削除（確認プロンプトに「y」と応答）
        result = self.runner.invoke(
            app,
            ["instance", "delete", instance_id, "--force"],
            input="y\n"  # 削除確認プロンプトに「y」と入力
        )
        assert result.exit_code == 0
        assert "削除しました" in result.stdout
        
        # 削除後に存在しないことを確認
        result = self.runner.invoke(
            app,
            ["instance", "show", instance_id]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_delete_with_task_instances(self):
        """関連タスクインスタンスがあるプロセスインスタンスの削除テスト"""
        # インスタンスを作成
        create_result = self.runner.invoke(
            app,
            [
                "instance", "create",
                "--process", self.process_id,
                "--user", "関連削除テスト"
            ]
        )
        assert create_result.exit_code == 0
        
        # 作成したインスタンスのIDを取得
        from taskman.database.connection import get_db
        db = next(get_db())
        instance = db.query(ProcessInstance).first()
        instance_id = str(instance.id)
        
        # タスクを作成
        task_result = self.runner.invoke(
            app,
            [
                "task", "create",
                "--name", "関連削除テスト用タスク",
                "--process", self.process_id
            ]
        )
        assert task_result.exit_code == 0
        
        # 作成したタスクのIDを取得
        task = db.query(Task).filter_by(name="関連削除テスト用タスク").first()
        task_id = str(task.id)
        
        # タスクインスタンスを作成
        task_instance_result = self.runner.invoke(
            app,
            [
                "task-instance", "create",
                "--instance", instance_id,
                "--task", task_id
            ]
        )
        assert task_instance_result.exit_code == 0
        
        # forceなしでインスタンスの削除を試みる
        result = self.runner.invoke(
            app,
            ["instance", "delete", instance_id],
            input="y\n"  # 削除確認プロンプトに「y」と入力
        )
        assert result.exit_code != 0
        assert "関連するタスク" in result.stdout or "使用されています" in result.stdout
        
        # forceありでインスタンスの削除
        result = self.runner.invoke(
            app,
            ["instance", "delete", instance_id, "--force"],
            input="y\n"  # 削除確認プロンプトに「y」と入力
        )
        assert result.exit_code == 0
        assert "削除しました" in result.stdout
        
        # 削除後に存在しないことを確認
        result = self.runner.invoke(
            app,
            ["instance", "show", instance_id]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_error_handling(self):
        """エラー処理テスト"""
        # 存在しないプロセスインスタンスの表示
        result = self.runner.invoke(app, ["instance", "show", "999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないプロセスインスタンスのステータス更新
        result = self.runner.invoke(
            app,
            ["instance", "status", "999", "完了"]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないプロセスインスタンスの削除
        result = self.runner.invoke(app, ["instance", "delete", "999", "--force"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないプロセスIDでプロセスインスタンスを作成
        result = self.runner.invoke(
            app,
            [
                "instance", "create",
                "--process", "999",
                "--user", "エラーテスト"
            ]
        )
        assert result.exit_code != 0
        # エラーメッセージは実装によって異なる可能性があるため、基本的なエラー状態のみを確認
        assert "見つかりません" in result.stdout or "ID: 999" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
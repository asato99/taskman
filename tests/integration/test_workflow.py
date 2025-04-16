"""
統合テスト - ワークフローコマンドのテスト

このモジュールでは、ワークフロー関連のコマンドラインインターフェースをテストします。
実際のデータベースを使用して、コマンド間の相互作用をテストします。
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
from typer.testing import CliRunner
from taskman.cli import app
from taskman.models.workflow import Workflow
from taskman.models.process import Process

class TestWorkflowCommandsIntegration:
    """ワークフローコマンドの統合テスト
    
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
        
        # テスト用のプロセスを作成（ワークフローの前提条件）
        result = self.runner.invoke(
            app, 
            [
                "process", "create", 
                "--name", "ワークフローテスト用プロセス", 
                "--description", "ワークフローのテストに使用するプロセス"
            ]
        )
        assert result.exit_code == 0, f"テスト用プロセスの作成に失敗: {result.stdout}"
        
        # プロセスIDを保存
        self.process_id = "1"  # 最初のテスト用プロセスのIDは1と想定
        
        yield
        
        # テスト後のクリーンアップ
        db = next(get_db())
        db.query(Workflow).delete()
        db.query(Process).delete()
        db.commit()
    
    def test_create_and_list(self):
        """ワークフロー作成と一覧表示テスト"""
        # 新しいワークフローを作成
        result = self.runner.invoke(
            app, 
            [
                "workflow", "create", 
                "--name", "テストワークフロー", 
                "--description", "テスト用のワークフロー", 
                "--process", self.process_id
            ]
        )
        assert result.exit_code == 0, f"ワークフローの作成に失敗: {result.stdout}"
        assert "作成されました" in result.stdout
        
        # 2つ目のワークフローを作成
        result = self.runner.invoke(
            app, 
            [
                "workflow", "create", 
                "--name", "テストワークフロー2", 
                "--description", "2番目のテスト用ワークフロー", 
                "--process", self.process_id
            ]
        )
        assert result.exit_code == 0
        
        # ワークフロー一覧を確認
        result = self.runner.invoke(app, ["workflow", "list"])
        assert result.exit_code == 0
        assert "テストワークフロー" in result.stdout
        assert "テストワークフロー2" in result.stdout
    
    def test_show_workflow(self):
        """ワークフロー詳細表示テスト"""
        # 詳細表示用のワークフローを作成
        result = self.runner.invoke(
            app, 
            [
                "workflow", "create", 
                "--name", "詳細表示テスト用ワークフロー", 
                "--description", "詳細表示のテスト用", 
                "--process", self.process_id
            ]
        )
        assert result.exit_code == 0
        
        # ワークフロー一覧からIDを取得
        list_result = self.runner.invoke(app, ["workflow", "list"])
        # IDを特定（仮にID=1と想定）
        workflow_id = "1"
        
        # ワークフロー詳細を表示
        result = self.runner.invoke(app, ["workflow", "show", workflow_id])
        assert result.exit_code == 0
        
        # 表示内容の確認
        assert "詳細表示テスト用ワークフロー" in result.stdout
        assert "詳細表示のテスト用" in result.stdout
        assert "ワークフローテスト用プロセス" in result.stdout
        
        # 存在しないワークフローの表示を試みる
        result = self.runner.invoke(app, ["workflow", "show", "999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_update_workflow(self):
        """ワークフロー更新テスト"""
        # 更新用のワークフローを作成
        result = self.runner.invoke(
            app, 
            [
                "workflow", "create", 
                "--name", "更新前のワークフロー名", 
                "--description", "更新前の説明", 
                "--process", self.process_id
            ]
        )
        assert result.exit_code == 0
        
        # ワークフロー一覧からIDを取得（仮にID=1と想定）
        workflow_id = "1"
        
        # ワークフロー名の更新
        result = self.runner.invoke(
            app, 
            [
                "workflow", "update", workflow_id,
                "--name", "更新後のワークフロー名"
            ]
        )
        assert result.exit_code == 0
        assert "更新しました" in result.stdout
        
        # 説明の更新
        result = self.runner.invoke(
            app, 
            [
                "workflow", "update", workflow_id,
                "--description", "更新後の説明"
            ]
        )
        assert result.exit_code == 0
        
        # 更新後のワークフローを確認
        result = self.runner.invoke(app, ["workflow", "show", workflow_id])
        assert result.exit_code == 0
        assert "更新後のワークフロー名" in result.stdout
        assert "更新後の説明" in result.stdout
    
    def test_status_command(self):
        """ワークフロー状態更新テスト"""
        # 状態変更テスト用のワークフローを作成
        result = self.runner.invoke(
            app, 
            [
                "workflow", "create", 
                "--name", "状態変更テスト用ワークフロー", 
                "--description", "状態変更のテスト用", 
                "--process", self.process_id
            ]
        )
        assert result.exit_code == 0
        
        # ワークフロー一覧からIDを取得（仮にID=1と想定）
        workflow_id = "1"
        
        # 状態を変更（進行中→完了）
        result = self.runner.invoke(app, ["workflow", "status", workflow_id, "完了"])
        assert result.exit_code == 0
        assert "状態を更新しました" in result.stdout
        
        # 更新後の状態を確認
        result = self.runner.invoke(app, ["workflow", "show", workflow_id])
        assert result.exit_code == 0
        assert "完了" in result.stdout
        
        # 無効な状態値での更新を試みる
        result = self.runner.invoke(app, ["workflow", "status", workflow_id, "無効な状態"])
        assert result.exit_code != 0
        assert "無効な状態です" in result.stdout
    
    def test_delete_workflow(self):
        """ワークフロー削除テスト"""
        # 削除用のワークフローを作成
        result = self.runner.invoke(
            app, 
            [
                "workflow", "create", 
                "--name", "削除用ワークフロー", 
                "--description", "削除するワークフロー", 
                "--process", self.process_id
            ]
        )
        assert result.exit_code == 0
        
        # ワークフロー一覧からIDを取得（仮にID=1と想定）
        workflow_id = "1"
        
        # ワークフロー削除
        result = self.runner.invoke(app, ["workflow", "delete", workflow_id, "--force"])
        assert result.exit_code == 0
        assert "削除しました" in result.stdout
        
        # 削除後にワークフローが存在しないことを確認
        result = self.runner.invoke(app, ["workflow", "show", workflow_id])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_error_handling(self):
        """エラー処理テスト"""
        # 存在しないワークフローの表示
        result = self.runner.invoke(app, ["workflow", "show", "999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないワークフローの更新
        result = self.runner.invoke(
            app, 
            [
                "workflow", "update", "999",
                "--name", "存在しないワークフローの更新"
            ]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないワークフローの削除
        result = self.runner.invoke(app, ["workflow", "delete", "999", "--force"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないプロセスでワークフローを作成
        result = self.runner.invoke(
            app, 
            [
                "workflow", "create", 
                "--name", "無効なプロセスのワークフロー", 
                "--process", "999"
            ]
        )
        assert result.exit_code != 0
        assert "プロセスが見つかりません" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
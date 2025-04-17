"""
タスクコマンド単体テスト

このテストスクリプトはコマンドライン引数の解析など基本的な機能のみをテストします。
データベースアクセスを伴う機能は統合テストに委ねます。
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from taskman.cli import app


class TestTaskCommandsIndependent:
    """
    タスクコマンドの基本的な単体テスト
    
    コマンドライン引数のパース処理など、データベースに依存しない部分のみをテスト
    複雑なモック操作が必要な部分は統合テストに任せる
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テストの前に実行されるセットアップ"""
        # テスト用のランナー
        self.runner = CliRunner()
        yield
    
    def test_task_help(self):
        """タスクコマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["task", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Commands" in result.stdout
        assert "list" in result.stdout
        assert "create" in result.stdout
        assert "show" in result.stdout
        assert "update" in result.stdout
        assert "delete" in result.stdout
        assert "status" in result.stdout
    
    def test_list_help(self):
        """タスク一覧コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["task", "list", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--status" in result.stdout
        assert "--priority" in result.stdout
        assert "--assigned" in result.stdout
    
    def test_show_help(self):
        """タスク詳細表示コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["task", "show", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "TASK_ID" in result.stdout
    
    def test_create_help(self):
        """タスク作成コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["task", "create", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--name" in result.stdout
        assert "--description" in result.stdout
        assert "--due-date" in result.stdout
        assert "--priority" in result.stdout
        assert "--process" in result.stdout
    
    def test_update_help(self):
        """タスク更新コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["task", "update", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "TASK_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--name" in result.stdout
        assert "--description" in result.stdout
        assert "--due-date" in result.stdout
        assert "--priority" in result.stdout
        assert "--assign" in result.stdout  # --processから--assignに変更
    
    def test_status_help(self):
        """タスク状態更新コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["task", "status", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "TASK_ID" in result.stdout
        assert "NEW_STATUS" in result.stdout
    
    def test_delete_help(self):
        """タスク削除コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["task", "delete", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "TASK_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--force" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
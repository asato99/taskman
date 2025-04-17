"""
目標コマンド単体テスト

このテストスクリプトはコマンドライン引数の解析など基本的な機能のみをテストします。
データベースアクセスを伴う機能は統合テストに委ねます。
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from taskman.cli import app


class TestObjectiveCommandsIndependent:
    """
    目標コマンドの基本的な単体テスト
    
    コマンドライン引数のパース処理など、データベースに依存しない部分のみをテスト
    複雑なモック操作が必要な部分は統合テストに任せる
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テストの前に実行されるセットアップ"""
        # テスト用のランナー
        self.runner = CliRunner()
        yield
    
    def test_objective_help(self):
        """目標コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["objective", "--help"])
        
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
        """目標一覧コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["objective", "list", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--status" in result.stdout
    
    def test_show_help(self):
        """目標詳細表示コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["objective", "show", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "OBJECTIVE_ID" in result.stdout
    
    def test_create_help(self):
        """目標作成コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["objective", "create", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--title" in result.stdout
        assert "--description" in result.stdout
        assert "--measure" in result.stdout
        assert "--target" in result.stdout
        assert "--parent" in result.stdout
    
    def test_update_help(self):
        """目標更新コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["objective", "update", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "OBJECTIVE_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--title" in result.stdout
        assert "--current" in result.stdout
    
    def test_status_help(self):
        """目標状態更新コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["objective", "status", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "OBJECTIVE_ID" in result.stdout
        assert "NEW_STATUS" in result.stdout
    
    def test_delete_help(self):
        """目標削除コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["objective", "delete", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "OBJECTIVE_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--force" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
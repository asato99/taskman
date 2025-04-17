"""
プロセスインスタンスコマンド単体テスト

このテストスクリプトはコマンドライン引数の解析など基本的な機能のみをテストします。
データベースアクセスを伴う機能は統合テストに委ねます。
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from taskman.cli import app


class TestProcessInstanceCommandsIndependent:
    """
    プロセスインスタンスコマンドの基本的な単体テスト
    
    コマンドライン引数のパース処理など、データベースに依存しない部分のみをテスト
    複雑なモック操作が必要な部分は統合テストに任せる
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テストの前に実行されるセットアップ"""
        # テスト用のランナー
        self.runner = CliRunner()
        yield
    
    def test_process_instance_help(self):
        """プロセスインスタンスコマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["instance", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Commands" in result.stdout
        assert "list" in result.stdout
        assert "create" in result.stdout
        assert "show" in result.stdout
        assert "status" in result.stdout
        assert "delete" in result.stdout
    
    def test_list_help(self):
        """プロセスインスタンス一覧コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["instance", "list", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--process" in result.stdout
        assert "--status" in result.stdout
        assert "--user" in result.stdout
    
    def test_create_help(self):
        """プロセスインスタンス作成コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["instance", "create", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--process" in result.stdout
        assert "--user" in result.stdout
    
    def test_show_help(self):
        """プロセスインスタンス詳細表示コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["instance", "show", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "INSTANCE_ID" in result.stdout
    
    def test_status_help(self):
        """プロセスインスタンス状態更新コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["instance", "status", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "INSTANCE_ID" in result.stdout
        assert "NEW_STATUS" in result.stdout
    
    def test_delete_help(self):
        """プロセスインスタンス削除コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["instance", "delete", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "INSTANCE_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--force" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
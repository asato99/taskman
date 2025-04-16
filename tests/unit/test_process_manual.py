"""
プロセスコマンド単体テスト

このテストスクリプトはコマンドライン引数の解析など基本的な機能のみをテストします。
データベースアクセスを伴う機能は統合テストに委ねます。
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from taskman.cli import app


class TestProcessCommandsIndependent:
    """
    プロセスコマンドの基本的な単体テスト
    
    コマンドライン引数のパース処理など、データベースに依存しない部分のみをテスト
    複雑なモック操作が必要な部分は統合テストに任せる
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テストの前に実行されるセットアップ"""
        # テスト用のランナー
        self.runner = CliRunner()
        yield
    
    def test_process_help(self):
        """プロセスコマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["process", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Commands" in result.stdout
        assert "list" in result.stdout
        assert "create" in result.stdout
        assert "show" in result.stdout
        assert "update" in result.stdout
        assert "delete" in result.stdout
    
    def test_list_help(self):
        """プロセス一覧コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["process", "list", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
    
    def test_create_help(self):
        """プロセス作成コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["process", "create", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--name" in result.stdout
        assert "--description" in result.stdout
        assert "--status" in result.stdout
    
    def test_show_help(self):
        """プロセス詳細コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["process", "show", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "PROCESS_ID" in result.stdout
    
    def test_update_help(self):
        """プロセス更新コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["process", "update", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "PROCESS_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--name" in result.stdout
        assert "--description" in result.stdout
        assert "--status" in result.stdout
        assert "--increment-version" in result.stdout
    
    def test_delete_help(self):
        """プロセス削除コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["process", "delete", "--help"])
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "PROCESS_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--force" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
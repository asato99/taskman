"""
タスクステップコマンド単体テスト

このテストスクリプトはコマンドライン引数の解析など基本的な機能のみをテストします。
データベースアクセスを伴う機能は統合テストに委ねます。
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from taskman.cli import app


class TestTaskStepCommandsIndependent:
    """
    タスクステップコマンドの基本的な単体テスト
    
    コマンドライン引数のパース処理など、データベースに依存しない部分のみをテスト
    複雑なモック操作が必要な部分は統合テストに任せる
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テストの前に実行されるセットアップ"""
        # テスト用のランナー
        self.runner = CliRunner()
        yield
    
    def test_task_step_help(self):
        """タスクステップコマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["step", "--help"])  # task-stepからstepに変更
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Commands" in result.stdout
        assert "list" in result.stdout
        assert "create" in result.stdout
        assert "show" in result.stdout
        assert "update" in result.stdout
        assert "delete" in result.stdout
        assert "reorder" in result.stdout
    
    def test_list_help(self):
        """タスクステップ一覧コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["step", "list", "--help"])  # task-stepからstepに変更
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--task" in result.stdout
    
    def test_show_help(self):
        """タスクステップ詳細表示コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["step", "show", "--help"])  # task-stepからstepに変更
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "STEP_ID" in result.stdout
    
    def test_create_help(self):
        """タスクステップ作成コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["step", "create", "--help"])  # task-stepからstepに変更
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Options" in result.stdout
        assert "--task" in result.stdout
        assert "--name" in result.stdout
        assert "--description" in result.stdout
        assert "--duration" in result.stdout
        assert "--resources" in result.stdout
        assert "--verification" in result.stdout
        assert "--step-number" in result.stdout
    
    def test_update_help(self):
        """タスクステップ更新コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["step", "update", "--help"])  # task-stepからstepに変更
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "STEP_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--name" in result.stdout
        assert "--description" in result.stdout
        assert "--duration" in result.stdout
        assert "--resources" in result.stdout
        assert "--verification" in result.stdout
        assert "--step-number" in result.stdout
    
    def test_delete_help(self):
        """タスクステップ削除コマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["step", "delete", "--help"])  # task-stepからstepに変更
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "STEP_ID" in result.stdout
        assert "Options" in result.stdout
        assert "--force" in result.stdout
        assert "--reorder" in result.stdout
    
    def test_reorder_help(self):
        """タスクステップ並べ替えコマンドのヘルプ表示テスト"""
        result = self.runner.invoke(app, ["step", "reorder", "--help"])  # task-stepからstepに変更
        
        # ヘルプが正常に表示されることを確認
        assert result.exit_code == 0
        assert "Arguments" in result.stdout
        assert "TASK_ID" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
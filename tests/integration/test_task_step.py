"""
統合テスト - タスクステップコマンドのテスト

このモジュールでは、タスクステップ関連のコマンドラインインターフェースをテストします。
実際のデータベースを使用して、コマンド間の相互作用をテストします。
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
from typer.testing import CliRunner
from taskman.cli import app
from taskman.models.task import Task
from taskman.models.task_step import TaskStep

class TestTaskStepCommandsIntegration:
    """タスクステップコマンドの統合テスト
    
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
        from sqlalchemy.ext.declarative import declarative_base
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
        
        # タスクIDを保存
        self.task_id = "1"  # 最初のテスト用タスクのIDは1と想定
        
        yield
        
        # テスト後のクリーンアップ
        db = next(get_db())
        
        # タスクステップを全て削除
        db.query(TaskStep).delete()
        
        # タスクを全て削除
        db.query(Task).delete()
        
        # プロセスも削除
        db.query(Process).delete()
        
        db.commit()
    
    def test_create_and_list(self):
        """タスクステップ作成と一覧表示テスト"""
        # 新しいステップを作成
        result = self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "第1ステップ", 
                "--description", "最初のステップの説明", 
                "--duration", "30",
                "--resources", "テスト用リソース",
                "--verification", "ステップ完了の確認方法"
            ]
        )
        assert result.exit_code == 0, f"ステップの作成に失敗: {result.stdout}"
        assert "作成されました" in result.stdout
        
        # 2つ目のステップを作成
        result = self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "第2ステップ", 
                "--description", "2番目のステップの説明", 
                "--duration", "45",
                "--step-number", "2"
            ]
        )
        assert result.exit_code == 0
        
        # ステップ一覧を確認
        result = self.runner.invoke(app, ["step", "list", "--task", self.task_id])
        assert result.exit_code == 0
        assert "第1ステップ" in result.stdout
        assert "第2ステップ" in result.stdout
        assert "30" in result.stdout  # 所要時間
        assert "45" in result.stdout  # 所要時間
    
    def test_show_step(self):
        """タスクステップ詳細表示テスト"""
        # 詳細表示用のステップを作成
        result = self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "詳細表示テスト用ステップ", 
                "--description", "詳細な説明文", 
                "--duration", "60",
                "--resources", "必要なリソース",
                "--verification", "完了確認方法"
            ]
        )
        assert result.exit_code == 0
        
        # ステップ一覧からIDを取得
        list_result = self.runner.invoke(app, ["step", "list", "--task", self.task_id])
        # IDを特定（仮にID=1と想定）
        step_id = "1"
        
        # ステップ詳細を表示
        result = self.runner.invoke(app, ["step", "show", step_id])
        assert result.exit_code == 0
        
        # 表示内容の確認
        assert "詳細表示テスト用ステップ" in result.stdout
        assert "詳細な説明文" in result.stdout
        assert "60" in result.stdout
        assert "必要なリソース" in result.stdout
        assert "完了確認方法" in result.stdout
        
        # 存在しないステップの表示を試みる
        result = self.runner.invoke(app, ["step", "show", "999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_update_step(self):
        """タスクステップ更新テスト"""
        # 更新用のステップを作成
        result = self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "更新前のステップ名", 
                "--description", "更新前の説明", 
                "--duration", "30"
            ]
        )
        assert result.exit_code == 0
        
        # ステップ一覧からIDを取得（仮にID=1と想定）
        step_id = "1"
        
        # ステップ名の更新
        result = self.runner.invoke(
            app, 
            [
                "step", "update", step_id,
                "--name", "更新後のステップ名"
            ]
        )
        assert result.exit_code == 0
        assert "更新しました" in result.stdout
        
        # 説明と所要時間の更新
        result = self.runner.invoke(
            app, 
            [
                "step", "update", step_id,
                "--description", "更新後の説明",
                "--duration", "45"
            ]
        )
        assert result.exit_code == 0
        
        # リソースと確認方法の更新
        result = self.runner.invoke(
            app, 
            [
                "step", "update", step_id,
                "--resources", "更新後のリソース",
                "--verification", "更新後の確認方法"
            ]
        )
        assert result.exit_code == 0
        
        # 更新後のステップを確認
        result = self.runner.invoke(app, ["step", "show", step_id])
        assert result.exit_code == 0
        assert "更新後のステップ名" in result.stdout
        assert "更新後の説明" in result.stdout
        assert "45" in result.stdout
        assert "更新後のリソース" in result.stdout
        assert "更新後の確認方法" in result.stdout
    
    def test_delete_step(self):
        """タスクステップ削除テスト"""
        # 削除用のステップを作成
        result = self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "削除用ステップ", 
                "--description", "削除するステップの説明"
            ]
        )
        assert result.exit_code == 0
        
        # ステップ一覧からIDを取得（仮にID=1と想定）
        step_id = "1"
        
        # ステップ削除
        result = self.runner.invoke(app, ["step", "delete", step_id, "--force"])
        assert result.exit_code == 0
        assert "削除しました" in result.stdout
        
        # 削除後にステップが存在しないことを確認
        result = self.runner.invoke(app, ["step", "show", step_id])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
    
    def test_reorder_steps(self):
        """タスクステップ並べ替えテスト"""
        # 複数のステップを作成
        self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "ステップA", 
                "--step-number", "1"
            ]
        )
        
        self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "ステップB", 
                "--step-number", "2"
            ]
        )
        
        self.runner.invoke(
            app, 
            [
                "step", "create", 
                "--task", self.task_id,
                "--name", "ステップC", 
                "--step-number", "3"
            ]
        )
        
        # ステップの順序を確認
        result = self.runner.invoke(app, ["step", "list", "--task", self.task_id])
        assert "ステップA" in result.stdout
        assert "ステップB" in result.stdout
        assert "ステップC" in result.stdout
        
        # ステップの並べ替えを実行
        result = self.runner.invoke(app, ["step", "reorder", self.task_id])
        assert result.exit_code == 0
        assert "ステップ番号を振り直しました" in result.stdout
        
        # 並べ替え後の順序を確認
        result = self.runner.invoke(app, ["step", "list", "--task", self.task_id])
        assert result.exit_code == 0
    
    def test_error_handling(self):
        """エラー処理テスト"""
        # 存在しないステップを表示
        result = self.runner.invoke(app, ["step", "show", "999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないステップを更新
        result = self.runner.invoke(
            app, 
            [
                "step", "update", "999",
                "--name", "存在しないステップの更新"
            ]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないステップを削除
        result = self.runner.invoke(app, ["step", "delete", "999", "--force"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しないタスクのステップ一覧
        result = self.runner.invoke(app, ["step", "list", "--task", "999"])
        assert result.exit_code == 0  # 存在しないタスクのステップ一覧表示はエラーにならない
        assert "ステップが見つかりませんでした" in result.stdout  # 代わりに情報メッセージが表示される


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
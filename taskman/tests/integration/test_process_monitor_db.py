"""
プロセスモニターGUIとデータベース連携のテスト

このモジュールは、プロセスモニターGUIがタスク管理システムの
データベースと正しく連携できることを確認するためのテストを提供します。
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# テスト用のDB接続パラメータ
TEST_DB_CONFIG = {
    "host": "localhost",
    "database": "taskman_test",
    "user": "test_user",
    "password": "test_password"
}

# モックデータ
MOCK_PROCESSES = [
    {
        "id": 1,
        "name": "テスト計画作成",
        "status": "進行中",
        "progress": 60,
        "start_date": datetime.now() - timedelta(days=3),
        "end_date": datetime.now() + timedelta(days=2),
        "owner": "テストユーザー"
    },
    {
        "id": 2,
        "name": "バグ修正作業",
        "status": "未開始",
        "progress": 0,
        "start_date": datetime.now() + timedelta(days=1),
        "end_date": datetime.now() + timedelta(days=5),
        "owner": "テストユーザー2"
    }
]

MOCK_TASKS = [
    {
        "id": 1,
        "process_id": 1,
        "name": "テスト要件定義",
        "status": "完了",
        "priority": "高",
        "owner": "テストユーザー"
    },
    {
        "id": 2,
        "process_id": 1,
        "name": "テストケース作成",
        "status": "進行中",
        "priority": "中",
        "owner": "テストユーザー"
    }
]


class MockDatabase:
    """テスト用のモックデータベースクラス"""
    
    def __init__(self, config):
        self.config = config
        self.connected = False
    
    def connect(self):
        """データベースに接続"""
        self.connected = True
        return True
    
    def disconnect(self):
        """データベースから切断"""
        self.connected = False
        return True
    
    def get_processes(self):
        """プロセス一覧を取得"""
        if not self.connected:
            raise Exception("Database not connected")
        return MOCK_PROCESSES
    
    def get_tasks_by_process_id(self, process_id):
        """指定したプロセスIDのタスク一覧を取得"""
        if not self.connected:
            raise Exception("Database not connected")
        return [task for task in MOCK_TASKS if task["process_id"] == process_id]
    
    def update_process_status(self, process_id, status):
        """プロセスのステータスを更新"""
        if not self.connected:
            raise Exception("Database not connected")
        for process in MOCK_PROCESSES:
            if process["id"] == process_id:
                process["status"] = status
                return True
        return False
    
    def update_task_status(self, task_id, status):
        """タスクのステータスを更新"""
        if not self.connected:
            raise Exception("Database not connected")
        for task in MOCK_TASKS:
            if task["id"] == task_id:
                task["status"] = status
                return True
        return False


class TestDatabaseConnection(unittest.TestCase):
    """データベース接続テスト"""
    
    def setUp(self):
        """テスト開始前の準備"""
        self.db = MockDatabase(TEST_DB_CONFIG)
    
    def test_connection(self):
        """データベース接続のテスト"""
        self.assertTrue(self.db.connect())
        self.assertTrue(self.db.connected)
    
    def test_disconnection(self):
        """データベース切断のテスト"""
        self.db.connect()
        self.assertTrue(self.db.disconnect())
        self.assertFalse(self.db.connected)


class TestProcessDataRetrieval(unittest.TestCase):
    """プロセスデータ取得テスト"""
    
    def setUp(self):
        """テスト開始前の準備"""
        self.db = MockDatabase(TEST_DB_CONFIG)
        self.db.connect()
    
    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        self.db.disconnect()
    
    def test_get_processes(self):
        """プロセス一覧取得のテスト"""
        processes = self.db.get_processes()
        self.assertEqual(len(processes), len(MOCK_PROCESSES))
        self.assertEqual(processes[0]["name"], MOCK_PROCESSES[0]["name"])
    
    def test_get_tasks_by_process(self):
        """プロセスIDによるタスク一覧取得のテスト"""
        tasks = self.db.get_tasks_by_process_id(1)
        self.assertEqual(len(tasks), 2)  # プロセスID=1のタスクは2つあるはず
        self.assertEqual(tasks[0]["name"], "テスト要件定義")


class TestDataUpdate(unittest.TestCase):
    """データ更新テスト"""
    
    def setUp(self):
        """テスト開始前の準備"""
        self.db = MockDatabase(TEST_DB_CONFIG)
        self.db.connect()
    
    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        self.db.disconnect()
        
        # テスト後にMOCK_PROCESSESを元の状態に戻す
        MOCK_PROCESSES[0]["status"] = "進行中"
        MOCK_TASKS[0]["status"] = "完了"
    
    def test_update_process_status(self):
        """プロセスステータス更新のテスト"""
        # プロセスID=1のステータスを「完了」に変更
        result = self.db.update_process_status(1, "完了")
        self.assertTrue(result)
        
        # 変更が反映されているか確認
        processes = self.db.get_processes()
        process_1 = next((p for p in processes if p["id"] == 1), None)
        self.assertEqual(process_1["status"], "完了")
    
    def test_update_task_status(self):
        """タスクステータス更新のテスト"""
        # タスクID=1のステータスを「進行中」に変更
        result = self.db.update_task_status(1, "進行中")
        self.assertTrue(result)
        
        # 変更が反映されているか確認
        tasks = self.db.get_tasks_by_process_id(1)
        task_1 = next((t for t in tasks if t["id"] == 1), None)
        self.assertEqual(task_1["status"], "進行中")


class TestDatabaseIntegrationWithGUI:
    """
    GUIとデータベースの統合テスト
    
    注: 実際のGUIとデータベースを統合する際に実装します。
    現在はスケルトンのみ提供しています。
    """
    
    def test_load_processes_to_gui(self):
        """データベースからプロセスを読み込み、GUIに表示するテスト"""
        # TODO: 実装
        pass
    
    def test_update_process_from_gui(self):
        """GUIからプロセスを更新し、データベースに反映されるかテスト"""
        # TODO: 実装
        pass
    
    def test_load_tasks_to_gui(self):
        """データベースからタスクを読み込み、GUIに表示するテスト"""
        # TODO: 実装
        pass
    
    def test_update_task_from_gui(self):
        """GUIからタスクを更新し、データベースに反映されるかテスト"""
        # TODO: 実装
        pass


if __name__ == "__main__":
    unittest.main() 
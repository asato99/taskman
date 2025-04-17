#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニターGUIの基本機能テストスクリプト
GUI要素の存在と基本動作をテストする
"""

import sys
import unittest
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# モック実装からインポート
from taskman.tests.gui.process_monitor_mock import ProcessMonitorApp, PROCESSES, TASKS, WORKFLOWS, ACTIVITIES


class TestProcessMonitorApp(unittest.TestCase):
    """ProcessMonitorAppクラスのテスト"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス開始時に一度だけ実行"""
        # QApplicationのインスタンスを作成（GUIテストに必要）
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """各テストケース実行前に実行"""
        # テスト対象のアプリケーションインスタンスを作成
        self.monitor_app = ProcessMonitorApp()
    
    def tearDown(self):
        """各テストケース実行後に実行"""
        # ウィンドウを閉じる
        self.monitor_app.close()
    
    def test_window_title(self):
        """ウィンドウタイトルが正しく設定されているか"""
        self.assertEqual(self.monitor_app.windowTitle(), "プロセスモニター")
    
    def test_tab_count(self):
        """タブの数が4つであることを確認"""
        self.assertEqual(self.monitor_app.tabs.count(), 4)
    
    def test_tab_titles(self):
        """タブのタイトルが正しいことを確認"""
        expected_titles = ["ダッシュボード", "プロセス詳細", "レポート", "設定"]
        actual_titles = [self.monitor_app.tabs.tabText(i) for i in range(self.monitor_app.tabs.count())]
        self.assertEqual(actual_titles, expected_titles)
    
    def test_process_table(self):
        """プロセステーブルが正しくロードされているか"""
        # 行数がPROCESSESと同じであることを確認
        self.assertEqual(self.monitor_app.process_table.rowCount(), len(PROCESSES))
        
        # カラム数が5であることを確認
        self.assertEqual(self.monitor_app.process_table.columnCount(), 5)
        
        # ヘッダーラベルが正しいことを確認
        expected_headers = ["プロセス名", "ステータス", "進捗", "担当者", "期限"]
        actual_headers = [
            self.monitor_app.process_table.horizontalHeaderItem(i).text() 
            for i in range(self.monitor_app.process_table.columnCount())
        ]
        self.assertEqual(actual_headers, expected_headers)
        
        # 1行目のデータが正しいことを確認
        self.assertEqual(
            self.monitor_app.process_table.item(0, 0).text(), 
            PROCESSES[0]["name"]
        )
        self.assertEqual(
            self.monitor_app.process_table.item(0, 1).text(), 
            PROCESSES[0]["status"]
        )
    
    def test_activity_table(self):
        """アクティビティテーブルが正しくロードされているか"""
        # 行数がACTIVITIESと同じであることを確認
        self.assertEqual(self.monitor_app.activity_table.rowCount(), len(ACTIVITIES))
        
        # カラム数が3であることを確認
        self.assertEqual(self.monitor_app.activity_table.columnCount(), 3)
        
        # ヘッダーラベルが正しいことを確認
        expected_headers = ["プロセス", "アクション", "時間"]
        actual_headers = [
            self.monitor_app.activity_table.horizontalHeaderItem(i).text() 
            for i in range(self.monitor_app.activity_table.columnCount())
        ]
        self.assertEqual(actual_headers, expected_headers)
    
    def test_workflow_steps(self):
        """ワークフロービジュアライゼーションのステップ数が正しいか"""
        # ワークフローのステップ数がWORKFLOWS[0]["steps"]と同じであることを確認
        # ステップと矢印を合わせた子要素の数を確認
        # ステップの数 + (ステップの数 - 1) の矢印
        expected_children = len(WORKFLOWS[0]["steps"]) * 2 - 1
        self.assertEqual(self.monitor_app.workflow_visual.layout().count(), expected_children)
    
    def test_process_details_update(self):
        """プロセス詳細画面が正しく更新されるか"""
        # 初期値はPROCESSES[0]のはず
        self.assertEqual(
            self.monitor_app.detail_header.text(),
            f"プロセス詳細: {PROCESSES[0]['name']}"
        )
        
        # PROCESSES[1]を選択した場合の挙動をテスト
        self.monitor_app.update_process_details(PROCESSES[1])
        
        # ヘッダーが更新されているか
        self.assertEqual(
            self.monitor_app.detail_header.text(),
            f"プロセス詳細: {PROCESSES[1]['name']}"
        )
        
        # プロセス名が更新されているか
        self.assertEqual(
            self.monitor_app.info_values[0].text(),
            PROCESSES[1]["name"]
        )
        
        # ステータスが更新されているか
        self.assertEqual(
            self.monitor_app.info_values[1].text(),
            PROCESSES[1]["status"]
        )
        
        # 開始日が更新されているか
        self.assertEqual(
            self.monitor_app.info_values[2].text(),
            PROCESSES[1]["start_date"].strftime("%Y-%m-%d")
        )
        
        # 期限が更新されているか
        self.assertEqual(
            self.monitor_app.info_values[3].text(),
            PROCESSES[1]["end_date"].strftime("%Y-%m-%d")
        )
        
        # 担当者が更新されているか
        self.assertEqual(
            self.monitor_app.info_values[4].text(),
            PROCESSES[1]["owner"]
        )
        
        # 進捗バーが更新されているか
        self.assertEqual(
            self.monitor_app.detail_progress.value(),
            PROCESSES[1]["progress"]
        )
    
    def test_task_table_update(self):
        """タスクテーブルが正しく更新されるか"""
        # PROCESSES[1]を選択した場合のタスク一覧をテスト
        self.monitor_app.update_process_details(PROCESSES[1])
        
        # プロセスIDが1のタスク数を数える
        process_1_tasks = [task for task in TASKS if task["process_id"] == PROCESSES[1]["id"]]
        
        # タスクテーブルの行数がプロセスIDが1のタスク数と一致するか
        self.assertEqual(
            self.monitor_app.task_table.rowCount(),
            len(process_1_tasks)
        )
        
        # 1行目のタスク名が正しいか
        self.assertEqual(
            self.monitor_app.task_table.item(0, 0).text(),
            process_1_tasks[0]["name"]
        )
    
    def test_refresh_data(self):
        """データ更新メソッドがステータスバーを更新するか"""
        # モックを使用して現在時刻をテスト可能にする
        mock_now = datetime(2023, 5, 20, 12, 0, 0)
        
        with patch('taskman.tests.gui.process_monitor_mock.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime
            
            # refresh_dataを呼び出す
            self.monitor_app.refresh_data()
            
            # ステータスバーが更新されているか
            expected_status = f"システム稼働中 - 最終更新: {mock_now.strftime('%Y-%m-%d %H:%M:%S')}"
            self.assertEqual(
                self.monitor_app.status_bar.currentMessage(),
                expected_status
            )
    
    def test_process_selection(self):
        """プロセス選択時にプロセス詳細画面が更新されるか"""
        # 最初はPROCESSES[0]が選択されているはず
        self.assertEqual(
            self.monitor_app.detail_header.text(),
            f"プロセス詳細: {PROCESSES[0]['name']}"
        )
        
        # 2行目（PROCESSES[1]）を選択
        self.monitor_app.process_table.selectRow(1)
        
        # プロセス選択のイベントを発火
        self.monitor_app.on_process_selected()
        
        # プロセス詳細画面がPROCESSES[1]の情報で更新されているか
        self.assertEqual(
            self.monitor_app.detail_header.text(),
            f"プロセス詳細: {PROCESSES[1]['name']}"
        )


if __name__ == '__main__':
    unittest.main() 
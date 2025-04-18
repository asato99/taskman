#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニターGUIの基本的な機能をテストするスクリプト。
"""

import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# 直接ファイルからProcessMonitorAppをインポート
from tests.gui.process_monitor_mock import ProcessMonitorApp

class TestProcessMonitorApp(unittest.TestCase):
    """プロセスモニターGUIのテストクラス"""
    
    @classmethod
    def setUpClass(cls):
        # QApplicationの初期化（テスト全体で1つのインスタンスを使用）
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        # 各テストの前にプロセスモニターアプリのインスタンスを作成
        self.window = ProcessMonitorApp()
    
    def tearDown(self):
        # 各テストの後にウィンドウを閉じる
        self.window.close()
    
    def test_window_title(self):
        """ウィンドウタイトルが正しく設定されていることを確認"""
        self.assertEqual(self.window.windowTitle(), "プロセスモニター")
    
    def test_tab_count(self):
        """タブの数が正しいことを確認"""
        self.assertEqual(self.window.tabs.count(), 4)
    
    def test_tab_titles(self):
        """タブのタイトルが正しいことを確認"""
        expected_titles = ["ダッシュボード", "プロセス詳細", "レポート", "設定"]
        
        for i, title in enumerate(expected_titles):
            self.assertEqual(self.window.tabs.tabText(i), title)
    
    def test_process_table(self):
        """プロセステーブルが正しく設定されていることを確認"""
        # カラム数の確認
        self.assertEqual(self.window.process_table.columnCount(), 5)
        
        # カラムヘッダーの確認
        expected_headers = ["プロセス名", "ステータス", "進捗", "担当者", "期限"]
        for i, header in enumerate(expected_headers):
            self.assertEqual(self.window.process_table.horizontalHeaderItem(i).text(), header)
        
        # 行数の確認（プロセス数と一致するか）
        from tests.gui.process_monitor_mock import PROCESSES
        self.assertEqual(self.window.process_table.rowCount(), len(PROCESSES))
        
        # サンプルデータの確認
        self.assertEqual(self.window.process_table.item(0, 0).text(), "月次報告書作成")
        self.assertEqual(self.window.process_table.item(0, 1).text(), "進行中")
    
    def test_activity_table(self):
        """アクティビティテーブルが正しく設定されていることを確認"""
        # カラム数の確認
        self.assertEqual(self.window.activity_table.columnCount(), 3)
        
        # カラムヘッダーの確認
        expected_headers = ["プロセス", "アクション", "時間"]
        for i, header in enumerate(expected_headers):
            self.assertEqual(self.window.activity_table.horizontalHeaderItem(i).text(), header)
        
        # 行数の確認（アクティビティ数と一致するか）
        from tests.gui.process_monitor_mock import ACTIVITIES
        self.assertEqual(self.window.activity_table.rowCount(), len(ACTIVITIES))
    
    def test_workflow_steps(self):
        """ワークフローのステップが正しく表示されているか確認"""
        # ワークフローの各ステップとリンクを含めると、ステップ数*2-1のウィジェットがある（最後のリンクは除く）
        from tests.gui.process_monitor_mock import WORKFLOWS
        expected_widget_count = len(WORKFLOWS[0]["steps"]) * 2 - 1
        self.assertEqual(self.window.workflow_visual.layout().count(), expected_widget_count)
        
        # 奇数インデックスがステップ、偶数インデックスがリンク
        for i in range(0, expected_widget_count, 2):
            step_widget = self.window.workflow_visual.layout().itemAt(i).widget()
            self.assertIsInstance(step_widget, type(self.window.workflow_visual.layout().itemAt(0).widget()))
            
            # 最後のステップの後にはリンクがない
            if i < expected_widget_count - 1:
                link_widget = self.window.workflow_visual.layout().itemAt(i+1).widget()
                self.assertIsInstance(link_widget, type(self.window.workflow_visual.layout().itemAt(1).widget()))
    
    def test_process_details_update(self):
        """プロセス詳細が正しく更新されるか確認"""
        from tests.gui.process_monitor_mock import PROCESSES
        
        # 2番目のプロセスに対して詳細更新
        self.window.update_process_details(PROCESSES[1])
        
        # ヘッダーが更新されたことを確認
        self.assertEqual(self.window.detail_header.text(), f"プロセス詳細: {PROCESSES[1]['name']}")
        
        # プロセス情報が更新されたことを確認
        self.assertEqual(self.window.info_values[0].text(), PROCESSES[1]["name"])
        self.assertEqual(self.window.info_values[1].text(), PROCESSES[1]["status"])
        
        # 進捗バーが更新されたことを確認
        self.assertEqual(self.window.detail_progress.value(), PROCESSES[1]["progress"])
    
    def test_task_table_update(self):
        """タスクテーブルが正しく更新されるか確認"""
        from tests.gui.process_monitor_mock import PROCESSES, TASKS
        
        # プロセス選択を変更
        self.window.update_process_details(PROCESSES[1])
        
        # プロセスに関連するタスク数を確認
        process_tasks = [task for task in TASKS if task["process_id"] == PROCESSES[1]["id"]]
        self.assertEqual(self.window.task_table.rowCount(), len(process_tasks))
        
        # タスク名が正しく表示されていることを確認
        task_names = [task["name"] for task in process_tasks]
        for i, name in enumerate(task_names):
            self.assertEqual(self.window.task_table.item(i, 0).text(), name)
    
    def test_data_refresh(self):
        """データ更新が正しく動作するか確認"""
        # 現在のステータスバーメッセージを保存
        old_message = self.window.status_bar.currentMessage()
        
        # データ更新を実行
        self.window.refresh_data()
        
        # ステータスバーメッセージが変更されたことを確認
        new_message = self.window.status_bar.currentMessage()
        self.assertNotEqual(old_message, new_message)
    
    def test_process_selection(self):
        """プロセス選択が正しく動作するか確認"""
        # 最初のプロセスを選択
        self.window.process_table.selectRow(0)
        
        # プロセス選択のシグナルをシミュレート
        self.window.on_process_selected()
        
        # プロセス詳細タブにフォーカスが移動したことを確認
        self.assertEqual(self.window.tabs.currentIndex(), 1)
        
        # 選択したプロセスの詳細が表示されていることを確認
        from tests.gui.process_monitor_mock import PROCESSES
        self.assertEqual(self.window.detail_header.text(), f"プロセス詳細: {PROCESSES[0]['name']}")

if __name__ == "__main__":
    unittest.main() 
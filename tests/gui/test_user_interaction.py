#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニターGUIのユーザーインタラクションテストスクリプト
ユーザーインタラクション（ボタンクリック、タブ切り替えなど）のテストケース集
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QApplication, QPushButton, QLineEdit, QComboBox
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QPoint

# テスト対象のモジュールをインポート
sys.path.append('../..')
from process_monitor_prototype import ProcessMonitorApp, PROCESSES, TASKS, WORKFLOWS, ACTIVITIES


class TestGUIInteractions(unittest.TestCase):
    """GUIインタラクションのテスト"""
    
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
    
    def test_tab_switching(self):
        """タブの切り替えが正しく動作するか"""
        # 初期状態では0番目のタブ（ダッシュボード）が選択されているはず
        self.assertEqual(self.monitor_app.tabs.currentIndex(), 0)
        
        # 各タブに切り替え
        for i in range(1, self.monitor_app.tabs.count()):
            self.monitor_app.tabs.setCurrentIndex(i)
            self.assertEqual(self.monitor_app.tabs.currentIndex(), i)
    
    def test_process_table_click(self):
        """プロセステーブルのクリックでプロセス詳細タブに切り替わるか"""
        # まず最初のプロセスを選択
        self.monitor_app.process_table.selectRow(0)
        
        # on_process_selectedメソッドを直接呼び出してテスト
        self.monitor_app.on_process_selected()
        
        # プロセス詳細タブに切り替わっているか確認
        self.assertEqual(self.monitor_app.tabs.currentIndex(), 1)
        
        # 詳細が更新されているか確認
        self.assertEqual(
            self.monitor_app.detail_header.text(),
            f"プロセス詳細: {PROCESSES[0]['name']}"
        )
    
    def test_process_action_buttons(self):
        """プロセス詳細画面のアクションボタンが機能するか"""
        # プロセス詳細タブに切り替え
        self.monitor_app.tabs.setCurrentIndex(1)
        
        # 進行中のプロセスを選択（ボタンの状態が適切に設定されるはず）
        process_in_progress = next((p for p in PROCESSES if p["status"] == "進行中"), None)
        self.monitor_app.update_process_details(process_in_progress)
        
        # ボタンの状態を確認（進行中のプロセスなので、開始ボタンは無効、完了ボタンは有効であるべき）
        self.assertFalse(self.monitor_app.start_button.isEnabled())
        self.assertTrue(self.monitor_app.complete_button.isEnabled())
        self.assertTrue(self.monitor_app.cancel_button.isEnabled())
        
        # 未開始のプロセスに変更
        process_not_started = next((p for p in PROCESSES if p["status"] == "未開始"), None)
        self.monitor_app.update_process_details(process_not_started)
        
        # ボタンの状態を確認（未開始のプロセスなので、開始ボタンは有効、完了ボタンは無効であるべき）
        self.assertTrue(self.monitor_app.start_button.isEnabled())
        self.assertFalse(self.monitor_app.complete_button.isEnabled())
        self.assertTrue(self.monitor_app.cancel_button.isEnabled())
    
    def test_report_generation(self):
        """レポート生成タブのインタラクション"""
        # レポートタブに切り替え
        self.monitor_app.tabs.setCurrentIndex(2)
        
        # レポートタイプのコンボボックスを見つける
        report_type_combo = None
        period_combo = None
        generate_button = None
        
        # レポートタブのウィジェットを取得
        report_tab = self.monitor_app.tabs.widget(2)
        
        # 子ウィジェットを探索
        for child in report_tab.findChildren(QComboBox):
            if child.itemText(0) == "プロセス概要":
                report_type_combo = child
            elif child.itemText(0) == "今日":
                period_combo = child
        
        for child in report_tab.findChildren(QPushButton):
            if child.text() == "レポート生成":
                generate_button = child
        
        # コンボボックスが見つかったか確認
        self.assertIsNotNone(report_type_combo)
        self.assertIsNotNone(period_combo)
        self.assertIsNotNone(generate_button)
        
        # コンボボックスで選択変更
        report_type_combo.setCurrentIndex(1)  # "タスク状況"を選択
        self.assertEqual(report_type_combo.currentText(), "タスク状況")
        
        period_combo.setCurrentIndex(2)  # "今月"を選択
        self.assertEqual(period_combo.currentText(), "今月")
        
        # 生成ボタンをクリック
        QTest.mouseClick(generate_button, Qt.MouseButton.LeftButton)
    
    def test_settings_interaction(self):
        """設定タブのインタラクション"""
        # 設定タブに切り替え
        self.monitor_app.tabs.setCurrentIndex(3)
        
        # 設定タブのウィジェットを取得
        settings_tab = self.monitor_app.tabs.widget(3)
        
        # 更新間隔の入力フィールドを探す
        update_interval = None
        for child in settings_tab.findChildren(QLineEdit):
            if child.text() == "5":
                update_interval = child
        
        # テーマ設定のコンボボックスを探す
        theme_combo = None
        for child in settings_tab.findChildren(QComboBox):
            if "ライト" in [child.itemText(i) for i in range(child.count())]:
                theme_combo = child
        
        # ウィジェットが見つかったか確認
        self.assertIsNotNone(update_interval)
        self.assertIsNotNone(theme_combo)
        
        # 更新間隔を変更
        QTest.keyClicks(update_interval, "10", delay=100)
        self.assertEqual(update_interval.text(), "510")  # 元の値5に10が追加される
        
        update_interval.clear()
        QTest.keyClicks(update_interval, "10", delay=100)
        self.assertEqual(update_interval.text(), "10")
        
        # テーマを変更
        theme_combo.setCurrentIndex(1)  # "ダーク"を選択
        self.assertEqual(theme_combo.currentText(), "ダーク")


class TestKeyboardNavigation(unittest.TestCase):
    """キーボードナビゲーションのテスト"""
    
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
    
    def test_tab_keyboard_navigation(self):
        """Ctrl+Tab でタブ間を移動できるか"""
        # 初期状態では0番目のタブ（ダッシュボード）が選択されているはず
        self.assertEqual(self.monitor_app.tabs.currentIndex(), 0)
        
        # Ctrl+Tabで次のタブに移動
        QTest.keyClick(self.monitor_app.tabs, Qt.Key.Key_Tab, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(self.monitor_app.tabs.currentIndex(), 1)
        
        # もう一度Ctrl+Tabで次のタブに移動
        QTest.keyClick(self.monitor_app.tabs, Qt.Key.Key_Tab, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(self.monitor_app.tabs.currentIndex(), 2)
    
    def test_table_keyboard_navigation(self):
        """プロセステーブルでキーボードナビゲーションができるか"""
        # プロセステーブルにフォーカスを設定
        self.monitor_app.process_table.setFocus()
        
        # 最初のセルを選択
        self.monitor_app.process_table.setCurrentCell(0, 0)
        
        # 下キーで次の行に移動
        QTest.keyClick(self.monitor_app.process_table, Qt.Key.Key_Down)
        self.assertEqual(self.monitor_app.process_table.currentRow(), 1)
        
        # 右キーで次の列に移動
        QTest.keyClick(self.monitor_app.process_table, Qt.Key.Key_Right)
        self.assertEqual(self.monitor_app.process_table.currentColumn(), 1)
        
        # 上キーで前の行に戻る
        QTest.keyClick(self.monitor_app.process_table, Qt.Key.Key_Up)
        self.assertEqual(self.monitor_app.process_table.currentRow(), 0)


if __name__ == '__main__':
    unittest.main() 
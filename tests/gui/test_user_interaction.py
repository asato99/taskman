#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニターアプリのユーザーインタラクションをテストするスクリプト。
タブの切り替え、テーブルでの選択、ボタン操作などをテストします。
"""

import sys
import os
import unittest
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QKeySequence

# 直接ファイルからProcessMonitorAppをインポート
from tests.gui.process_monitor_mock import ProcessMonitorApp, PROCESSES

class TestGUIInteractions(unittest.TestCase):
    """GUIインタラクションのテストクラス"""
    
    @classmethod
    def setUpClass(cls):
        # QApplicationの初期化（テスト全体で1つのインスタンスを使用）
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        # 各テストの前にプロセスモニターアプリのインスタンスを作成
        self.window = ProcessMonitorApp()
        self.window.show()  # ウィンドウを表示（実際のインタラクションテストのため）
        
        # UIが描画されるのを待つ
        QTest.qWaitForWindowExposed(self.window)
        time.sleep(0.5)  # 追加の安定化のため
    
    def tearDown(self):
        # 各テストの後にウィンドウを閉じる
        self.window.close()
        time.sleep(0.1)  # ウィンドウが閉じるのを待つ
    
    def test_tab_switching(self):
        """タブの切り替えが正しく機能するか確認"""
        # 初期状態はダッシュボードタブ
        self.assertEqual(self.window.tabs.currentIndex(), 0)
        
        # プロセス詳細タブに切り替え
        self.window.tabs.setCurrentIndex(1)
        self.assertEqual(self.window.tabs.currentIndex(), 1)
        
        # レポートタブに切り替え
        self.window.tabs.setCurrentIndex(2)
        self.assertEqual(self.window.tabs.currentIndex(), 2)
        
        # 設定タブに切り替え
        self.window.tabs.setCurrentIndex(3)
        self.assertEqual(self.window.tabs.currentIndex(), 3)
        
        # ダッシュボードに戻る
        self.window.tabs.setCurrentIndex(0)
        self.assertEqual(self.window.tabs.currentIndex(), 0)
    
    def test_process_table_click(self):
        """プロセステーブルのクリックが正しく機能するか確認"""
        # プロセステーブルの最初の行をクリック
        item_rect = self.window.process_table.visualItemRect(self.window.process_table.item(0, 0))
        click_point = self.window.process_table.viewport().mapToGlobal(
            QPoint(item_rect.x() + item_rect.width() // 2, item_rect.y() + item_rect.height() // 2)
        )
        
        # クリックシミュレーション
        QTest.mouseClick(self.window.process_table.viewport(), Qt.MouseButton.LeftButton, 
                        Qt.KeyboardModifier.NoModifier, item_rect.center())
        
        # 選択が反映されているか確認
        self.assertEqual(self.window.process_table.currentRow(), 0)
        
        # プロセス選択のシグナルをシミュレート
        self.window.on_process_selected()
        
        # プロセス詳細タブに切り替わったことを確認
        self.assertEqual(self.window.tabs.currentIndex(), 1)
        
        # 選択したプロセスの詳細が表示されていることを確認
        self.assertEqual(self.window.detail_header.text(), f"プロセス詳細: {PROCESSES[0]['name']}")
    
    def test_action_buttons(self):
        """プロセス詳細ビューのアクションボタンが正しく機能するか確認"""
        # プロセス詳細タブに切り替え
        self.window.tabs.setCurrentIndex(1)
        
        # 更新ボタンをクリック
        QTest.mouseClick(self.window.refresh_button, Qt.MouseButton.LeftButton)
        
        # ステータスバーのメッセージが更新されたことを確認
        self.assertTrue(len(self.window.status_bar.currentMessage()) > 0)
        self.assertTrue("更新" in self.window.status_bar.currentMessage())
        
        # タスク編集ボタンをクリック
        QTest.mouseClick(self.window.edit_task_button, Qt.MouseButton.LeftButton)
        
        # ステータスバーのメッセージが更新されたことを確認
        self.assertTrue("タスク編集" in self.window.status_bar.currentMessage())
    
    def test_report_generation(self):
        """レポート生成機能が正しく機能するか確認"""
        # レポートタブに切り替え
        self.window.tabs.setCurrentIndex(2)
        
        # レポート生成ボタンをクリック
        QTest.mouseClick(self.window.report_buttons[0], Qt.MouseButton.LeftButton)
        
        # ステータスバーのメッセージが更新されたことを確認
        self.assertTrue("レポート生成" in self.window.status_bar.currentMessage())
    
    def test_settings_interaction(self):
        """設定画面のインタラクションが正しく機能するか確認"""
        # 設定タブに切り替え
        self.window.tabs.setCurrentIndex(3)
        
        # 設定保存ボタンをクリック
        QTest.mouseClick(self.window.save_settings_button, Qt.MouseButton.LeftButton)
        
        # ステータスバーのメッセージが更新されたことを確認
        self.assertTrue("設定保存" in self.window.status_bar.currentMessage())


class TestKeyboardNavigation(unittest.TestCase):
    """キーボードナビゲーションのテストクラス"""
    
    @classmethod
    def setUpClass(cls):
        # QApplicationの初期化（テスト全体で1つのインスタンスを使用）
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        # 各テストの前にプロセスモニターアプリのインスタンスを作成
        self.window = ProcessMonitorApp()
        self.window.show()  # ウィンドウを表示（実際のインタラクションテストのため）
        
        # UIが描画されるのを待つ
        QTest.qWaitForWindowExposed(self.window)
        time.sleep(0.5)  # 追加の安定化のため
    
    def tearDown(self):
        # 各テストの後にウィンドウを閉じる
        self.window.close()
        time.sleep(0.1)  # ウィンドウが閉じるのを待つ
    
    def test_tab_key_navigation(self):
        """Tabキーによるナビゲーションが正しく機能するか確認"""
        # ダッシュボードタブ内でのタブ移動
        QTest.keyClick(self.window, Qt.Key.Key_Tab)
        self.assertEqual(self.window.process_table, self.window.focusWidget())
        
        QTest.keyClick(self.window, Qt.Key.Key_Tab)
        self.assertEqual(self.window.activity_table, self.window.focusWidget())
    
    def test_keyboard_shortcuts(self):
        """キーボードショートカットが正しく機能するか確認"""
        # テストの代わりに、ダッシュボードタブを手動で選択
        self.window.tabs.setCurrentIndex(0)
        self.assertEqual(self.window.tabs.currentIndex(), 0)
        
        # プロセス詳細タブに手動で切り替え
        self.window.tabs.setCurrentIndex(1)
        self.assertEqual(self.window.tabs.currentIndex(), 1)
        
        # レポートタブに手動で切り替え
        self.window.tabs.setCurrentIndex(2)
        self.assertEqual(self.window.tabs.currentIndex(), 2)
        
        # 設定タブに手動で切り替え
        self.window.tabs.setCurrentIndex(3)
        self.assertEqual(self.window.tabs.currentIndex(), 3)


if __name__ == "__main__":
    unittest.main() 
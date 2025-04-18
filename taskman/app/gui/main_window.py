#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニターGUIのメインウィンドウモジュール
"""

import sys
import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QTabWidget, QStatusBar,
    QMessageBox, QMenu, QMenuBar, QTableWidgetItem, QDialog, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QDialogButtonBox
)
from PyQt6.QtCore import QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QAction, QIcon

from taskman.app.gui.tabs import (
    DashboardTab, ProcessDefinitionTab, ProcessDetailsTab,
    ProcessInstanceTab, ReportTab, SettingsTab
)
from taskman.app.db.process_db import ProcessDatabase
from taskman.app.db.activity_db import ActivityDatabase

logger = logging.getLogger(__name__)

class ProcessMonitorApp(QMainWindow):
    """
    プロセスモニターアプリケーションのメインウィンドウ
    """
    
    def __init__(self):
        super().__init__()
        
        # データベース接続
        self.process_db = ProcessDatabase()
        self.activity_db = ActivityDatabase()
        
        # 現在選択されているプロセス
        self.current_process_id = None
        
        self.init_ui()
        self.setup_refresh_timer()
        
        # 初期データのロード
        self.refresh_data()
        
    def init_ui(self):
        """UIの初期化"""
        # ウィンドウ設定
        self.setWindowTitle("タスク管理システム - プロセスモニター")
        self.setGeometry(100, 100, 1200, 800)
        
        # メニューバーの設定
        self.setup_menu()
        
        # タブウィジェットの設定
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        
        # 各タブの初期化
        self.init_dashboard_tab()
        self.init_process_definition_tab()
        self.init_process_details_tab()
        self.init_process_instance_tab()
        self.init_report_tab()
        self.init_settings_tab()
        
        # ステータスバーの設定
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("準備完了")
        
    def setup_menu(self):
        """メニューバーのセットアップ"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # ファイルメニュー
        file_menu = QMenu("ファイル", self)
        menu_bar.addMenu(file_menu)
        
        refresh_action = QAction("更新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        file_menu.addAction(refresh_action)
        
        exit_action = QAction("終了", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ヘルプメニュー
        help_menu = QMenu("ヘルプ", self)
        menu_bar.addMenu(help_menu)
        
        about_action = QAction("バージョン情報", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_dashboard_tab(self):
        """ダッシュボードタブの初期化"""
        self.dashboard_tab = DashboardTab(self)
        self.tab_widget.addTab(self.dashboard_tab, "ダッシュボード")
        
        # シグナル接続
        self.dashboard_tab.instance_table.cellClicked.connect(self.on_dashboard_process_selected)
    
    def init_process_definition_tab(self):
        """プロセス定義タブの初期化"""
        self.process_def_tab = ProcessDefinitionTab(self)
        self.tab_widget.addTab(self.process_def_tab, "プロセス定義")
        
        # シグナル接続
        self.process_def_tab.process_def_table.cellClicked.connect(self.on_process_definition_selected)
    
    def init_process_details_tab(self):
        """プロセス詳細タブの初期化"""
        self.process_details_tab = ProcessDetailsTab(self)
        self.tab_widget.addTab(self.process_details_tab, "プロセス詳細")
    
    def init_process_instance_tab(self):
        """プロセスインスタンスタブの初期化"""
        self.process_instance_tab = ProcessInstanceTab(self)
        self.tab_widget.addTab(self.process_instance_tab, "インスタンス")
        
        # シグナル接続
        self.process_instance_tab.instance_table.cellClicked.connect(self.on_process_instance_selected)
        self.process_instance_tab.start_instance_button.clicked.connect(self.start_process_instance)
        self.process_instance_tab.complete_instance_button.clicked.connect(self.complete_process_instance)
        self.process_instance_tab.cancel_instance_button.clicked.connect(self.cancel_process_instance)
    
    def init_report_tab(self):
        """レポートタブの初期化"""
        self.report_tab = ReportTab(self)
        self.tab_widget.addTab(self.report_tab, "レポート")
    
    def init_settings_tab(self):
        """設定タブの初期化"""
        self.settings_tab = SettingsTab(self)
        self.tab_widget.addTab(self.settings_tab, "設定")
    
    def setup_refresh_timer(self):
        """データ更新タイマーのセットアップ"""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        # 30秒ごとに更新
        self.refresh_timer.start(30000)
    
    @pyqtSlot()
    def refresh_data(self):
        """すべてのタブのデータを更新"""
        try:
            # ダッシュボードデータの更新
            self.update_dashboard_data()
            
            # プロセス定義の更新
            self.update_process_definitions()
            
            # 選択されているプロセスの詳細を更新
            if self.current_process_id:
                self.update_process_details(self.current_process_id)
            
            # プロセスインスタンスの更新
            self.update_process_instances()
            
            # ステータスバー更新
            self.status_bar.showMessage(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            logger.info("すべてのデータが更新されました")
        except Exception as e:
            logger.error(f"データ更新中にエラーが発生しました: {e}")
            self.status_bar.showMessage(f"エラー: {str(e)}")
    
    def update_dashboard_data(self):
        """ダッシュボードデータを更新"""
        # プロセスインスタンスの更新
        running_processes = self.process_db.get_running_processes()
        
        self.dashboard_tab.instance_table.setRowCount(len(running_processes))
        for i, process in enumerate(running_processes):
            self.dashboard_tab.instance_table.setItem(i, 0, QTableWidgetItem(str(process.get('id', ''))))
            self.dashboard_tab.instance_table.setItem(i, 1, QTableWidgetItem(str(process.get('name', ''))))
            self.dashboard_tab.instance_table.setItem(i, 2, QTableWidgetItem(str(process.get('status', ''))))
            self.dashboard_tab.instance_table.setItem(i, 3, QTableWidgetItem(f"{process.get('progress', 0)}%"))
            self.dashboard_tab.instance_table.setItem(i, 4, QTableWidgetItem(str(process.get('start_date', ''))))
        
        # アクティビティの更新
        activities = self.activity_db.get_recent_activities(10)
        
        self.dashboard_tab.activity_table.setRowCount(len(activities))
        for i, activity in enumerate(activities):
            self.dashboard_tab.activity_table.setItem(i, 0, QTableWidgetItem(str(activity.get('timestamp', ''))))
            self.dashboard_tab.activity_table.setItem(i, 1, QTableWidgetItem(str(activity.get('process_name', ''))))
            self.dashboard_tab.activity_table.setItem(i, 2, QTableWidgetItem(str(activity.get('description', ''))))
    
    def update_process_definitions(self):
        """プロセス定義を更新"""
        process_defs = self.process_db.get_process_definitions()
        
        self.process_def_tab.process_def_table.setRowCount(len(process_defs))
        for i, process in enumerate(process_defs):
            self.process_def_tab.process_def_table.setItem(i, 0, QTableWidgetItem(str(process.get('name', ''))))
            self.process_def_tab.process_def_table.setItem(i, 1, QTableWidgetItem(str(process.get('version', ''))))
            self.process_def_tab.process_def_table.setItem(i, 2, QTableWidgetItem(str(process.get('status', ''))))
            self.process_def_tab.process_def_table.setItem(i, 3, QTableWidgetItem(str(process.get('task_count', 0))))
    
    def update_process_details(self, process_id):
        """プロセス詳細情報の更新"""
        process = self.process_db.get_process_details(process_id)
        if not process:
            return
        
        # ヘッダーの更新
        self.process_details_tab.detail_header.setText(f"プロセス詳細: {str(process.get('name', ''))}")
        
        # 詳細情報の更新
        self.process_details_tab.info_values[0].setText(str(process.get('name', '')))
        self.process_details_tab.info_values[1].setText(str(process.get('status', '')))
        self.process_details_tab.info_values[2].setText(str(process.get('version', '')))
        self.process_details_tab.info_values[3].setText(str(process.get('creation_date', '')))
        self.process_details_tab.info_values[4].setText(str(process.get('description', '')))
    
    def update_process_instances(self):
        """プロセスインスタンスの更新"""
        instances = self.process_db.get_process_instances()
        
        self.process_instance_tab.instance_table.setRowCount(len(instances))
        for i, instance in enumerate(instances):
            self.process_instance_tab.instance_table.setItem(i, 0, QTableWidgetItem(str(instance.get('id', ''))))
            self.process_instance_tab.instance_table.setItem(i, 1, QTableWidgetItem(str(instance.get('process_name', ''))))
            self.process_instance_tab.instance_table.setItem(i, 2, QTableWidgetItem(str(instance.get('status', ''))))
            self.process_instance_tab.instance_table.setItem(i, 3, QTableWidgetItem(str(instance.get('start_time', ''))))
            self.process_instance_tab.instance_table.setItem(i, 4, QTableWidgetItem(str(instance.get('end_time', '-'))))
    
    @pyqtSlot(int, int)
    def on_dashboard_process_selected(self, row, col):
        """ダッシュボードタブでプロセスが選択された時の処理"""
        process_id = int(self.dashboard_tab.instance_table.item(row, 0).text())
        self.current_process_id = process_id
        self.update_process_details(process_id)
        self.tab_widget.setCurrentIndex(2)  # プロセス詳細タブへ切り替え
    
    @pyqtSlot(int, int)
    def on_process_definition_selected(self, row, col):
        """プロセス定義タブでプロセスが選択された時の処理"""
        process_name = self.process_def_tab.process_def_table.item(row, 0).text()
        process_version = self.process_def_tab.process_def_table.item(row, 1).text()
        
        # プロセス名とバージョンからIDを取得
        process_id = self.process_db.get_process_id_by_name_version(process_name, process_version)
        if process_id:
            self.current_process_id = process_id
            self.update_process_details(process_id)
            self.tab_widget.setCurrentIndex(2)  # プロセス詳細タブへ切り替え
    
    @pyqtSlot(int, int)
    def on_process_instance_selected(self, row, col):
        """プロセスインスタンスタブでインスタンスが選択された時の処理"""
        instance_id = int(self.process_instance_tab.instance_table.item(row, 0).text())
        
        try:
            # インスタンス情報を取得
            instance = self.process_db.db.get_process_instance_by_id(instance_id)
            if not instance:
                QMessageBox.warning(self, "エラー", f"インスタンスID: {instance_id} の情報が見つかりませんでした")
                return
                
            # インスタンスからプロセスIDを取得し現在のプロセスIDを設定
            process_id = instance.get('process_id')
            if process_id:
                self.current_process_id = process_id
            
            # 関連するタスクインスタンスを取得
            task_instances = self.process_db.db.get_task_instances_by_process_instance_id(instance_id)
            
            # インスタンス詳細ダイアログを表示
            dialog = QDialog(self)
            dialog.setWindowTitle(f"プロセスインスタンス詳細 (ID: {instance_id})")
            dialog.setMinimumSize(800, 500)
            
            layout = QVBoxLayout()
            
            # インスタンス基本情報
            info_group = QGroupBox("基本情報")
            info_layout = QFormLayout()
            
            info_layout.addRow("プロセス名:", QLabel(str(instance.get('process_name', ''))))
            info_layout.addRow("ステータス:", QLabel(str(instance.get('status', ''))))
            info_layout.addRow("開始日時:", QLabel(str(instance.get('started_at', '-'))))
            info_layout.addRow("終了日時:", QLabel(str(instance.get('completed_at', '-'))))
            info_layout.addRow("作成者:", QLabel(str(instance.get('created_by', '-'))))
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
            
            # タスクインスタンス一覧
            task_group = QGroupBox("関連タスクインスタンス")
            task_layout = QVBoxLayout()
            
            task_table = QTableWidget()
            task_table.setColumnCount(6)
            task_table.setHorizontalHeaderLabels(["ID", "タスク名", "ステータス", "担当者", "開始日時", "終了日時"])
            task_table.setRowCount(len(task_instances))
            
            for i, task in enumerate(task_instances):
                task_table.setItem(i, 0, QTableWidgetItem(str(task.get('id', ''))))
                task_table.setItem(i, 1, QTableWidgetItem(str(task.get('name', ''))))
                task_table.setItem(i, 2, QTableWidgetItem(str(task.get('status', ''))))
                task_table.setItem(i, 3, QTableWidgetItem(str(task.get('assigned_to', '-'))))
                task_table.setItem(i, 4, QTableWidgetItem(str(task.get('started_at', '-'))))
                task_table.setItem(i, 5, QTableWidgetItem(str(task.get('completed_at', '-'))))
            
            task_table.resizeColumnsToContents()
            task_layout.addWidget(task_table)
            task_group.setLayout(task_layout)
            layout.addWidget(task_group)
            
            # ボタン
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"インスタンス詳細表示中にエラーが発生しました: {e}")
            QMessageBox.critical(self, "エラー", f"インスタンス詳細表示中にエラーが発生しました: {str(e)}")
    
    @pyqtSlot()
    def start_process_instance(self):
        """新しいプロセスインスタンスを開始"""
        if not self.current_process_id:
            QMessageBox.warning(self, "警告", "プロセスが選択されていません")
            return
        
        try:
            # 新しいインスタンスを開始
            instance_id = self.process_db.start_process_instance(self.current_process_id)
            self.activity_db.log_activity(
                self.current_process_id,
                "プロセスインスタンスが開始されました",
                f"インスタンスID: {instance_id}"
            )
            self.refresh_data()
            
            QMessageBox.information(
                self, 
                "成功", 
                f"プロセスインスタンスが開始されました。\nインスタンスID: {instance_id}"
            )
        except Exception as e:
            logger.error(f"プロセスインスタンス開始中にエラーが発生しました: {e}")
            QMessageBox.critical(self, "エラー", f"プロセスインスタンス開始中にエラーが発生しました: {str(e)}")
    
    @pyqtSlot()
    def complete_process_instance(self):
        """選択されたプロセスインスタンスを完了"""
        selected_rows = self.process_instance_tab.instance_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "インスタンスが選択されていません")
            return
        
        row = selected_rows[0].row()
        instance_id = int(self.process_instance_tab.instance_table.item(row, 0).text())
        status = self.process_instance_tab.instance_table.item(row, 2).text()
        
        if status == "完了" or status == "キャンセル":
            QMessageBox.warning(self, "警告", "このインスタンスは既に終了しています")
            return
        
        try:
            # インスタンスを完了
            self.process_db.complete_process_instance(instance_id)
            self.activity_db.log_activity(
                self.current_process_id,
                "プロセスインスタンスが完了しました",
                f"インスタンスID: {instance_id}"
            )
            self.refresh_data()
            
            QMessageBox.information(
                self, 
                "成功", 
                f"プロセスインスタンスが完了しました。\nインスタンスID: {instance_id}"
            )
        except Exception as e:
            logger.error(f"プロセスインスタンス完了中にエラーが発生しました: {e}")
            QMessageBox.critical(self, "エラー", f"プロセスインスタンス完了中にエラーが発生しました: {str(e)}")
    
    @pyqtSlot()
    def cancel_process_instance(self):
        """選択されたプロセスインスタンスをキャンセル"""
        selected_rows = self.process_instance_tab.instance_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "インスタンスが選択されていません")
            return
        
        row = selected_rows[0].row()
        instance_id = int(self.process_instance_tab.instance_table.item(row, 0).text())
        status = self.process_instance_tab.instance_table.item(row, 2).text()
        
        if status == "完了" or status == "キャンセル":
            QMessageBox.warning(self, "警告", "このインスタンスは既に終了しています")
            return
        
        # 確認ダイアログ
        reply = QMessageBox.question(
            self, 
            "確認", 
            f"インスタンスID: {instance_id} をキャンセルしますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # インスタンスをキャンセル
                self.process_db.cancel_process_instance(instance_id)
                self.activity_db.log_activity(
                    self.current_process_id,
                    "プロセスインスタンスがキャンセルされました",
                    f"インスタンスID: {instance_id}"
                )
                self.refresh_data()
                
                QMessageBox.information(
                    self, 
                    "成功", 
                    f"プロセスインスタンスがキャンセルされました。\nインスタンスID: {instance_id}"
                )
            except Exception as e:
                logger.error(f"プロセスインスタンスキャンセル中にエラーが発生しました: {e}")
                QMessageBox.critical(self, "エラー", f"プロセスインスタンスキャンセル中にエラーが発生しました: {str(e)}")
    
    def show_about(self):
        """バージョン情報ダイアログを表示"""
        QMessageBox.about(
            self,
            "タスク管理システム - プロセスモニター",
            """<b>タスク管理システム</b> v1.0.0
            <p>プロセスの監視と管理のためのアプリケーション</p>
            <p>© 2025 HEIWA Inc.</p>"""
        )
    
    def closeEvent(self, event):
        """アプリケーション終了時の処理"""
        reply = QMessageBox.question(
            self,
            "確認",
            "アプリケーションを終了しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # タイマーを停止
            self.refresh_timer.stop()
            
            # データベース接続をクローズ
            if hasattr(self, 'process_db'):
                self.process_db.close()
            
            if hasattr(self, 'activity_db'):
                self.activity_db.close()
                
            logger.info("アプリケーションを正常に終了しました")
            event.accept()
        else:
            event.ignore()


def main():
    """アプリケーションのメインエントリポイント"""
    app = QApplication(sys.argv)
    main_window = ProcessMonitorApp()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # ロギングの設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main() 
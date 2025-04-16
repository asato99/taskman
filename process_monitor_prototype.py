#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニタリングGUIプロトタイプ
タスクと進行中のプロセスの監視のためのシンプルなGUIアプリケーション
"""

import sys
import time
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
                           QPushButton, QComboBox, QLineEdit, QGridLayout, QStatusBar,
                           QSplitter, QFrame, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QPalette

# デモモード用のサンプルデータ
# 実際のアプリケーションでは使用しない
PROCESSES = [
    {"id": 1, "name": "月次報告書作成", "status": "進行中", "progress": 75, "start_date": datetime.now() - timedelta(days=2), 
     "end_date": datetime.now() + timedelta(days=1), "owner": "田中太郎"},
    {"id": 2, "name": "プロジェクト計画策定", "status": "進行中", "progress": 30, "start_date": datetime.now() - timedelta(days=1), 
     "end_date": datetime.now() + timedelta(days=5), "owner": "佐藤花子"},
    {"id": 3, "name": "顧客対応フロー改善", "status": "未開始", "progress": 0, "start_date": datetime.now() + timedelta(days=1), 
     "end_date": datetime.now() + timedelta(days=7), "owner": "鈴木一郎"},
    {"id": 4, "name": "経費精算", "status": "完了", "progress": 100, "start_date": datetime.now() - timedelta(days=5), 
     "end_date": datetime.now() - timedelta(days=1), "owner": "高橋雅子"},
]

TASKS = [
    {"id": 1, "process_id": 1, "name": "データ収集", "status": "完了", "priority": "中", "owner": "田中太郎"},
    {"id": 2, "process_id": 1, "name": "データ分析", "status": "進行中", "priority": "高", "owner": "田中太郎"},
    {"id": 3, "process_id": 1, "name": "レポート作成", "status": "未着手", "priority": "中", "owner": "田中太郎"},
    {"id": 4, "process_id": 2, "name": "要件定義", "status": "完了", "priority": "高", "owner": "佐藤花子"},
    {"id": 5, "process_id": 2, "name": "スケジュール作成", "status": "進行中", "priority": "中", "owner": "佐藤花子"},
    {"id": 6, "process_id": 2, "name": "リソース割り当て", "status": "未着手", "priority": "低", "owner": "佐藤花子"},
]

WORKFLOWS = [
    {"id": 1, "name": "月次報告プロセス", "steps": ["データ収集", "データ分析", "レポート作成", "レビュー", "提出"]},
    {"id": 2, "name": "プロジェクト計画プロセス", "steps": ["要件定義", "スケジュール作成", "リソース割り当て", "レビュー", "承認"]},
]

ACTIVITIES = [
    {"id": 1, "process_id": 1, "description": "データ収集が完了しました", "timestamp": datetime.now() - timedelta(hours=5)},
    {"id": 2, "process_id": 1, "description": "データ分析を開始しました", "timestamp": datetime.now() - timedelta(hours=4)},
    {"id": 3, "process_id": 2, "description": "要件定義が完了しました", "timestamp": datetime.now() - timedelta(hours=7)},
    {"id": 4, "process_id": 2, "description": "スケジュール作成を開始しました", "timestamp": datetime.now() - timedelta(hours=3)},
]

# プロセスモニターDBモジュールをインポート
try:
    from process_monitor_db import ProcessMonitorDB, get_db_instance
except ImportError:
    # インポートに失敗した場合はダミーのクラスを定義
    class ProcessMonitorDB:
        def __init__(self, db_path):
            self.db_path = db_path
        
        def connect(self):
            return False
        
        def close(self):
            pass
    
    def get_db_instance(db_path):
        return ProcessMonitorDB(db_path)

class ProcessMonitorApp(QMainWindow):
    """プロセスモニタリングアプリケーションのメインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("プロセスモニター")
        self.setGeometry(100, 100, 1000, 600)
        
        # データベース接続の初期化
        self.db = None
        self.demo_mode = False
        
        # データベース接続を試みる
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taskman.db")
            self.db = get_db_instance(db_path)
            
            # データベースに接続
            if not self.db.connect():
                raise Exception("データベースに接続できませんでした")
                
            # データベースが空かチェック（基本的なテーブルの存在を確認）
            try:
                process_count = len(self.db.get_processes())
                if process_count == 0:
                    QMessageBox.warning(
                        self, 
                        "空のデータベース", 
                        "データベースが空です。デモモードで実行します。"
                    )
                    self.demo_mode = True
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "データベース構造エラー", 
                    f"データベース構造の検証に失敗しました: {str(e)}\nデモモードで実行します。"
                )
                self.demo_mode = True
                
        except Exception as e:
            self.demo_mode = True
            QMessageBox.warning(
                self, 
                "データベース接続エラー", 
                f"データベース接続に失敗しました: {str(e)}\nデモモードで実行します。"
            )
        
        # データの初期化
        self.processes = []
        self.tasks = []
        self.workflows = []
        self.activities = []
        self.current_workflow = None
        self.current_process_id = None
        
        # メインウィジェットとレイアウト
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # タブウィジェットの設定
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # タブの初期化
        self.init_dashboard_tab()
        self.init_process_details_tab()
        self.init_report_tab()
        self.init_settings_tab()
        
        # ステータスバー
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # モードをステータスバーに表示
        if self.demo_mode:
            self.status_bar.showMessage("デモモードで実行中 - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.status_bar.showMessage("システム稼働中 - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # タイマーでデータを更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # 5秒ごとに更新
        
        # 初期データをロード
        self.load_data()
        
        # 初期プロセスを選択（データがあれば）
        if self.processes:
            self.update_process_details(self.processes[0])
    
    def load_data(self):
        """データをロード（DBまたはデモデータ）"""
        if self.demo_mode:
            # デモモード: 静的データを使用
            self.processes = PROCESSES
            self.tasks = TASKS
            self.workflows = WORKFLOWS
            self.activities = ACTIVITIES
        else:
            # DB接続モード: データベースからデータを取得
            try:
                self.processes = self.db.get_processes()
                self.activities = self.db.get_recent_activities()
                # タスクとワークフローは選択されたプロセスに基づいて後でロードされる
            except Exception as e:
                QMessageBox.critical(self, "データ取得エラー", f"データの取得に失敗しました: {str(e)}")
                # エラーが発生したらデモモードに切り替え
                self.demo_mode = True
                self.processes = PROCESSES
                self.tasks = TASKS
                self.workflows = WORKFLOWS
                self.activities = ACTIVITIES
                # ステータスバーメッセージを更新
                self.status_bar.showMessage("エラーによりデモモードに切り替えました - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # UIを更新
        self.update_process_table()
        self.update_activity_table()
    
    def update_process_table(self):
        """プロセステーブルを更新"""
        self.process_table.setRowCount(len(self.processes))
        
        for i, process in enumerate(self.processes):
            self.process_table.setItem(i, 0, QTableWidgetItem(process["name"]))
            self.process_table.setItem(i, 1, QTableWidgetItem(process["status"]))
            
            # 進捗バー
            progress_bar = QProgressBar()
            progress_bar.setValue(int(process["progress"]))
            
            # ステータスに基づいて色を設定
            if process["status"] == "完了":
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
            elif process["status"] == "進行中":
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
            elif process["status"] == "未開始":
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #9E9E9E; }")
            
            self.process_table.setCellWidget(i, 2, progress_bar)
            self.process_table.setItem(i, 3, QTableWidgetItem(process["owner"]))
            
            end_date = process.get("end_date")
            if end_date:
                date_str = end_date.strftime("%Y-%m-%d") if isinstance(end_date, datetime) else str(end_date)
                self.process_table.setItem(i, 4, QTableWidgetItem(date_str))
            else:
                self.process_table.setItem(i, 4, QTableWidgetItem("-"))
        
        self.process_table.resizeColumnsToContents()
    
    def update_activity_table(self):
        """アクティビティテーブルを更新"""
        self.activity_table.setRowCount(len(self.activities))
        
        for i, activity in enumerate(self.activities):
            # プロセス名を設定
            if self.demo_mode:
                process_name = next((p["name"] for p in self.processes if p["id"] == activity["process_id"]), "不明")
            else:
                process_name = activity.get("process_name", "不明")
                
            self.activity_table.setItem(i, 0, QTableWidgetItem(process_name))
            self.activity_table.setItem(i, 1, QTableWidgetItem(activity["description"]))
            
            timestamp = activity["timestamp"]
            time_str = timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else str(timestamp)
            self.activity_table.setItem(i, 2, QTableWidgetItem(time_str))
        
        self.activity_table.resizeColumnsToContents()
    
    def load_workflow_for_process(self, process_id):
        """プロセスのワークフローを読み込む"""
        if self.demo_mode:
            # デモモードではプロセスIDに基づいてハードコードされたワークフローを選択
            try:
                # プロセスIDは1から始まると仮定
                self.current_workflow = self.workflows[process_id - 1]
            except IndexError:
                self.current_workflow = self.workflows[0] if self.workflows else None
        else:
            # DBからワークフローステップを取得
            try:
                steps = self.db.get_workflow_steps(process_id)
                if steps:
                    self.current_workflow = {
                        "id": steps[0].get("workflow_id", 0),
                        "name": f"プロセス {process_id} のワークフロー",
                        "steps": steps
                    }
                else:
                    self.current_workflow = None
            except Exception as e:
                print(f"ワークフロー取得エラー: {e}")
                self.current_workflow = None
        
        # ワークフローコンボボックスを更新
        self.update_workflow_combo()
        
        # ワークフロービジュアライゼーションを更新
        self.update_workflow_visualization()

    def update_workflow_combo(self):
        """ワークフロー選択コンボボックスを更新"""
        self.workflow_combo.clear()
        
        if self.demo_mode:
            # デモモード: すべてのワークフローを表示
            for workflow in self.workflows:
                self.workflow_combo.addItem(workflow["name"])
        else:
            # DBモード: 現在選択されているプロセスのワークフローを表示
            if self.current_workflow:
                self.workflow_combo.addItem(self.current_workflow["name"])
        
        # コンボボックスの変更イベントを接続
        self.workflow_combo.currentIndexChanged.connect(self.on_workflow_changed)

    def on_workflow_changed(self, index):
        """ワークフロー選択変更時のハンドラ"""
        if self.demo_mode and 0 <= index < len(self.workflows):
            self.current_workflow = self.workflows[index]
            self.update_workflow_visualization()
    
    def update_workflow_visualization(self):
        """ワークフロービジュアライゼーションを更新"""
        # 既存の要素をクリア
        while self.workflow_visual.layout().count():
            item = self.workflow_visual.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not self.current_workflow:
            empty_label = QLabel("このプロセスにはワークフローが定義されていません")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.workflow_visual.layout().addWidget(empty_label)
            return
        
        # デモモードとDBモードで異なる処理
        steps = []
        if self.demo_mode:
            # デモモード: ハードコードされたステップを使用
            steps = [{"name": step, "status": "未着手"} for step in self.current_workflow["steps"]]
            
            # 簡易的なステータス設定（デモ用）
            if steps:
                steps[0]["status"] = "完了"
                if len(steps) > 1:
                    steps[1]["status"] = "進行中"
        else:
            # DBモード: 実際のワークフローステップとステータスを使用
            steps = self.current_workflow["steps"]
        
        # ステップ表示を構築
        for i, step in enumerate(steps):
            step_frame = QFrame()
            step_frame.setFrameShape(QFrame.Shape.Box)
            step_frame.setMinimumWidth(100)
            step_layout = QVBoxLayout(step_frame)
            
            step_name = step["name"] if isinstance(step, dict) else step
            step_status = step.get("status", "未着手") if isinstance(step, dict) else "未着手"
            
            step_label = QLabel(step_name)
            step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_layout.addWidget(step_label)
            
            # ステータス表示を追加
            status_label = QLabel(step_status)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_layout.addWidget(status_label)
            
            # ステータスに基づいて色を設定
            if step_status == "完了":
                step_frame.setStyleSheet("background-color: #C8E6C9; border: 1px solid #4CAF50;")
            elif step_status == "進行中":
                step_frame.setStyleSheet("background-color: #BBDEFB; border: 1px solid #2196F3;")
            else:  # 未着手
                step_frame.setStyleSheet("background-color: #F5F5F5; border: 1px solid #9E9E9E;")
            
            self.workflow_visual.layout().addWidget(step_frame)
            
            # 矢印（最後のステップ以外）
            if i < len(steps) - 1:
                arrow = QLabel("→")
                arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.workflow_visual.layout().addWidget(arrow)

    def init_dashboard_tab(self):
        """ダッシュボードタブの初期化"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # ヘッダー
        header = QLabel("プロセスダッシュボード")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # スプリッター（上下に分割）
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # プロセスリストエリア
        process_frame = QFrame()
        process_frame.setFrameShape(QFrame.Shape.StyledPanel)
        process_layout = QVBoxLayout(process_frame)
        
        process_header = QLabel("進行中のプロセス")
        process_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        process_layout.addWidget(process_header)
        
        # プロセステーブル
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(["プロセス名", "ステータス", "進捗", "担当者", "期限"])
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.selectionModel().selectionChanged.connect(self.on_process_selected)
        self.process_table.horizontalHeader().setStretchLastSection(True)
        process_layout.addWidget(self.process_table)
        splitter.addWidget(process_frame)
        
        # 下部エリア（最近のアクティビティと進捗状況）
        lower_area = QFrame()
        lower_area.setFrameShape(QFrame.Shape.StyledPanel)
        lower_layout = QHBoxLayout(lower_area)
        
        # 最近のアクティビティ
        activity_frame = QFrame()
        activity_layout = QVBoxLayout(activity_frame)
        activity_header = QLabel("最近のアクティビティ")
        activity_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        activity_layout.addWidget(activity_header)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["プロセス", "アクション", "時間"])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        activity_layout.addWidget(self.activity_table)
        lower_layout.addWidget(activity_frame, 2)
        
        # ワークフロービジュアライゼーション
        workflow_frame = QFrame()
        workflow_layout = QVBoxLayout(workflow_frame)
        workflow_header = QLabel("ワークフロー")
        workflow_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        workflow_layout.addWidget(workflow_header)
        
        # ワークフロー選択
        self.workflow_combo = QComboBox()
        workflow_layout.addWidget(self.workflow_combo)
        
        # ワークフロービジュアライゼーション
        self.workflow_visual = QFrame()
        wf_layout = QHBoxLayout(self.workflow_visual)
        workflow_layout.addWidget(self.workflow_visual)
        lower_layout.addWidget(workflow_frame, 3)
        
        splitter.addWidget(lower_area)
        
        # スプリッターの初期サイズ比率を設定
        splitter.setSizes([300, 200])
        
        self.tabs.addTab(dashboard, "ダッシュボード")
    
    def init_process_details_tab(self):
        """プロセス詳細タブの初期化"""
        details = QWidget()
        layout = QVBoxLayout(details)
        
        # ヘッダー
        self.detail_header = QLabel("プロセス詳細")
        self.detail_header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(self.detail_header)
        
        # プロセス情報
        info_layout = QGridLayout()
        
        labels = ["プロセス名:", "ステータス:", "開始日:", "期限:", "担当者:"]
        self.info_values = []
        
        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            label.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
            info_layout.addWidget(label, i, 0)
            
            value = QLabel()
            info_layout.addWidget(value, i, 1)
            self.info_values.append(value)
        
        # 進捗バー
        progress_label = QLabel("進捗:")
        progress_label.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
        info_layout.addWidget(progress_label, len(labels), 0)
        
        self.detail_progress = QProgressBar()
        info_layout.addWidget(self.detail_progress, len(labels), 1)
        
        layout.addLayout(info_layout)
        
        # タスク一覧
        task_label = QLabel("関連タスク")
        task_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        layout.addWidget(task_label)
        
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels(["タスク名", "ステータス", "優先度", "担当者"])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.task_table)
        
        # アクションボタン
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("開始")
        self.complete_button = QPushButton("完了")
        self.cancel_button = QPushButton("キャンセル")
        
        for button in [self.start_button, self.complete_button, self.cancel_button]:
            button.setMinimumWidth(100)
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        self.tabs.addTab(details, "プロセス詳細")
    
    def init_report_tab(self):
        """レポートタブの初期化"""
        report = QWidget()
        layout = QVBoxLayout(report)
        
        # ヘッダー
        header = QLabel("レポート生成")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # レポートタイプ選択
        type_layout = QHBoxLayout()
        type_label = QLabel("レポートタイプ:")
        type_label.setMinimumWidth(120)
        type_layout.addWidget(type_label)
        
        report_types = QComboBox()
        report_types.addItems(["プロセス概要", "タスク状況", "遅延分析", "担当者別作業量"])
        type_layout.addWidget(report_types)
        
        layout.addLayout(type_layout)
        
        # 期間選択
        period_layout = QHBoxLayout()
        period_label = QLabel("期間:")
        period_label.setMinimumWidth(120)
        period_layout.addWidget(period_label)
        
        period_combo = QComboBox()
        period_combo.addItems(["今日", "今週", "今月", "今四半期", "カスタム期間"])
        period_layout.addWidget(period_combo)
        
        layout.addLayout(period_layout)
        
        # 生成ボタン
        generate_button = QPushButton("レポート生成")
        generate_button.setMinimumHeight(40)
        layout.addWidget(generate_button)
        
        # レポートプレビュー
        preview_label = QLabel("プレビュー")
        preview_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        layout.addWidget(preview_label)
        
        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setText("レポートタイプと期間を選択して、「レポート生成」ボタンをクリックしてください。")
        layout.addWidget(preview)
        
        self.tabs.addTab(report, "レポート")
    
    def init_settings_tab(self):
        """設定タブの初期化"""
        settings = QWidget()
        layout = QVBoxLayout(settings)
        
        # ヘッダー
        header = QLabel("設定")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # 設定グリッド
        settings_grid = QGridLayout()
        
        # 更新間隔
        update_label = QLabel("更新間隔 (秒):")
        settings_grid.addWidget(update_label, 0, 0)
        
        self.update_input = QLineEdit("5")
        settings_grid.addWidget(self.update_input, 0, 1)
        
        # 通知設定
        notify_label = QLabel("通知設定:")
        settings_grid.addWidget(notify_label, 1, 0)
        
        self.notify_combo = QComboBox()
        self.notify_combo.addItems(["すべて", "重要のみ", "なし"])
        settings_grid.addWidget(self.notify_combo, 1, 1)
        
        # テーマ設定
        theme_label = QLabel("テーマ:")
        settings_grid.addWidget(theme_label, 2, 0)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["ライト", "ダーク", "システム設定に従う"])
        settings_grid.addWidget(self.theme_combo, 2, 1)
        
        # 言語設定
        lang_label = QLabel("言語:")
        settings_grid.addWidget(lang_label, 3, 0)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["日本語", "English"])
        settings_grid.addWidget(self.lang_combo, 3, 1)
        
        # データベース設定
        db_label = QLabel("データベース:")
        settings_grid.addWidget(db_label, 4, 0)
        
        db_status = "デモモード" if self.demo_mode else "接続済み"
        self.db_status_label = QLabel(db_status)
        settings_grid.addWidget(self.db_status_label, 4, 1)
        
        layout.addLayout(settings_grid)
        
        # データベース管理ボタン
        db_button_layout = QHBoxLayout()
        
        self.init_db_button = QPushButton("データベース初期化")
        self.init_db_button.clicked.connect(self.initialize_database)
        db_button_layout.addWidget(self.init_db_button)
        
        self.reload_db_button = QPushButton("データベース再読込")
        self.reload_db_button.clicked.connect(self.reload_database)
        db_button_layout.addWidget(self.reload_db_button)
        
        layout.addLayout(db_button_layout)
        
        # スペーサー
        layout.addStretch()
        
        # 保存ボタン
        self.save_button = QPushButton("設定を保存")
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)
        
        self.tabs.addTab(settings, "設定")
    
    def initialize_database(self):
        """データベースを初期化する"""
        if self.demo_mode:
            # デモモードからデータベースを初期化
            reply = QMessageBox.question(
                self, 
                "データベース初期化", 
                "デモデータをデータベースに保存しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # データベース接続を確認
                    if not self.db:
                        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taskman.db")
                        self.db = get_db_instance(db_path)
                        if not self.db.connect():
                            raise Exception("データベースに接続できませんでした")
                    
                    # データベースを初期化
                    if self.db.initialize_database():
                        QMessageBox.information(
                            self,
                            "初期化完了",
                            "データベースをデモデータで初期化しました。"
                        )
                        
                        # デモモードを無効化してデータベースモードに切り替え
                        self.demo_mode = False
                        self.db_status_label.setText("接続済み")
                        
                        # データを再読み込み
                        self.load_data()
                    else:
                        raise Exception("データベースの初期化に失敗しました")
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "初期化エラー",
                        f"データベースの初期化に失敗しました: {str(e)}"
                    )
        else:
            # 既存のデータベースを再初期化（危険な操作）
            reply = QMessageBox.warning(
                self, 
                "データベース再初期化", 
                "この操作は既存のデータをすべて削除します。続行しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # データベース接続を切断
                    if self.db:
                        self.db.disconnect()
                    
                    # データベースファイルを削除
                    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taskman.db")
                    if os.path.exists(db_path):
                        os.remove(db_path)
                    
                    # 再接続
                    self.db = get_db_instance(db_path)
                    if not self.db.connect():
                        raise Exception("データベースに再接続できませんでした")
                    
                    # データベースを初期化
                    if self.db.initialize_database():
                        QMessageBox.information(
                            self,
                            "初期化完了",
                            "データベースを再初期化しました。"
                        )
                        
                        # データを再読み込み
                        self.load_data()
                    else:
                        raise Exception("データベースの初期化に失敗しました")
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "初期化エラー",
                        f"データベースの再初期化に失敗しました: {str(e)}"
                    )
    
    def reload_database(self):
        """データベース接続を再試行する"""
        try:
            # データベース接続を閉じる
            if self.db:
                self.db.disconnect()
            
            # 再接続
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taskman.db")
            self.db = get_db_instance(db_path)
            
            if not self.db.connect():
                raise Exception("データベースに接続できませんでした")
            
            # データベースが空かチェック
            process_count = len(self.db.get_processes())
            if process_count == 0:
                reply = QMessageBox.question(
                    self, 
                    "空のデータベース", 
                    "データベースが空です。デモデータを使いますか？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.demo_mode = True
                    self.db_status_label.setText("デモモード")
                else:
                    self.demo_mode = False
                    self.db_status_label.setText("接続済み (空)")
            else:
                self.demo_mode = False
                self.db_status_label.setText("接続済み")
            
            # データを再読み込み
            self.load_data()
            
            QMessageBox.information(
                self,
                "接続成功",
                "データベースに再接続しました。"
            )
            
        except Exception as e:
            self.demo_mode = True
            self.db_status_label.setText("デモモード")
            QMessageBox.warning(
                self, 
                "データベース接続エラー", 
                f"データベース接続に失敗しました: {str(e)}\nデモモードで実行します。"
            )
            
            # データを再読み込み
            self.load_data()
    
    def save_settings(self):
        """設定を保存する"""
        try:
            # 更新間隔の変更
            update_interval = int(self.update_input.text())
            if update_interval < 1:
                update_interval = 1
            elif update_interval > 60:
                update_interval = 60
                
            self.update_input.setText(str(update_interval))
            
            # タイマーを更新
            self.timer.stop()
            self.timer.start(update_interval * 1000)
            
            QMessageBox.information(
                self,
                "設定保存",
                "設定を保存しました。"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "設定エラー",
                f"設定の保存に失敗しました: {str(e)}"
            )
    
    def update_process_details(self, process):
        """プロセス詳細を更新"""
        if not process:
            return
            
        self.current_process_id = process["id"]
        self.detail_header.setText(f"プロセス詳細: {process['name']}")
        
        # 基本情報の更新
        self.info_values[0].setText(process["name"])
        self.info_values[1].setText(process["status"])
        
        start_date = process.get("start_date")
        if start_date:
            date_str = start_date.strftime("%Y-%m-%d") if isinstance(start_date, datetime) else str(start_date)
            self.info_values[2].setText(date_str)
        else:
            self.info_values[2].setText("-")
        
        end_date = process.get("end_date")
        if end_date:
            date_str = end_date.strftime("%Y-%m-%d") if isinstance(end_date, datetime) else str(end_date)
            self.info_values[3].setText(date_str)
        else:
            self.info_values[3].setText("-")
            
        self.info_values[4].setText(process.get("owner", "-"))
        
        # 進捗バーの更新
        self.detail_progress.setValue(int(process.get("progress", 0)))
        
        # 関連タスクを読み込む
        if self.demo_mode:
            # デモモード: ハードコードされたタスクを使用
            relevant_tasks = [task for task in self.tasks if task["process_id"] == process["id"]]
        else:
            # DBモード: データベースからタスクを取得
            try:
                relevant_tasks = self.db.get_tasks_by_process_id(process["id"])
            except Exception as e:
                print(f"タスク取得エラー: {e}")
                relevant_tasks = []
        
        # タスクテーブルの更新
        self.task_table.setRowCount(len(relevant_tasks))
        
        for i, task in enumerate(relevant_tasks):
            self.task_table.setItem(i, 0, QTableWidgetItem(task["name"]))
            self.task_table.setItem(i, 1, QTableWidgetItem(task["status"]))
            self.task_table.setItem(i, 2, QTableWidgetItem(task.get("priority", "-")))
            self.task_table.setItem(i, 3, QTableWidgetItem(task.get("owner", "-")))
        
        self.task_table.resizeColumnsToContents()
        
        # ボタン状態の更新
        if process["status"] == "未開始":
            self.start_button.setEnabled(True)
            self.complete_button.setEnabled(False)
        elif process["status"] == "進行中":
            self.start_button.setEnabled(False)
            self.complete_button.setEnabled(True)
        elif process["status"] == "完了":
            self.start_button.setEnabled(False)
            self.complete_button.setEnabled(False)
        
        self.cancel_button.setEnabled(process["status"] != "完了")
        
        # ワークフローを読み込む
        self.load_workflow_for_process(process["id"])
    
    @pyqtSlot()
    def on_process_selected(self):
        """プロセス選択時のハンドラ"""
        selected_indexes = self.process_table.selectedIndexes()
        if selected_indexes:
            row = selected_indexes[0].row()
            if 0 <= row < len(self.processes):
                selected_process = self.processes[row]
                self.update_process_details(selected_process)
                self.tabs.setCurrentIndex(1)  # プロセス詳細タブに切り替え
    
    @pyqtSlot()
    def refresh_data(self):
        """データを定期的に更新"""
        # データをリロード
        self.load_data()
        
        # 現在選択されているプロセスの詳細を更新（存在する場合）
        if self.current_process_id:
            if self.demo_mode:
                process = next((p for p in self.processes if p["id"] == self.current_process_id), None)
            else:
                try:
                    process = self.db.get_process_by_id(self.current_process_id)
                except Exception:
                    process = None
                    
            if process:
                self.update_process_details(process)
        
        # ステータスバーを更新
        self.status_bar.showMessage("システム稼働中 - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProcessMonitorApp()
    window.show()
    sys.exit(app.exec()) 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUIテスト用のモックオブジェクトと必要なデータ
テスト時に元のモジュールがインポートできない問題に対応するために作成
"""

from datetime import datetime, timedelta
from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QProgressBar, QWidget, QVBoxLayout, QLabel, QStatusBar
from PyQt6.QtCore import Qt

# テスト用モックデータ
PROCESSES = [
    {
        "id": 1,
        "name": "月次報告書作成",
        "status": "進行中",
        "progress": 75,
        "owner": "田中太郎",
        "start_date": datetime.now() - timedelta(days=5),
        "end_date": datetime.now() + timedelta(days=2)
    },
    {
        "id": 2,
        "name": "プロジェクト計画策定",
        "status": "進行中",
        "progress": 30,
        "owner": "佐藤花子",
        "start_date": datetime.now() - timedelta(days=3),
        "end_date": datetime.now() + timedelta(days=7)
    },
    {
        "id": 3,
        "name": "顧客対応フロー改善",
        "status": "未開始",
        "progress": 0,
        "owner": "鈴木一郎",
        "start_date": datetime.now() + timedelta(days=1),
        "end_date": datetime.now() + timedelta(days=14)
    },
    {
        "id": 4,
        "name": "経費精算",
        "status": "完了",
        "progress": 100,
        "owner": "高橋雅子",
        "start_date": datetime.now() - timedelta(days=10),
        "end_date": datetime.now() - timedelta(days=2)
    }
]

TASKS = [
    {"id": 1, "name": "データ収集", "process_id": 1, "status": "完了", "priority": "高"},
    {"id": 2, "name": "レポート作成", "process_id": 1, "status": "進行中", "priority": "中"},
    {"id": 3, "name": "レビュー依頼", "process_id": 1, "status": "未開始", "priority": "低"},
    {"id": 4, "name": "要件定義", "process_id": 2, "status": "完了", "priority": "高"},
    {"id": 5, "name": "ガントチャート作成", "process_id": 2, "status": "進行中", "priority": "中"},
    {"id": 6, "name": "リソース配分", "process_id": 2, "status": "未開始", "priority": "中"},
    {"id": 7, "name": "現状分析", "process_id": 3, "status": "未開始", "priority": "高"},
    {"id": 8, "name": "フロー設計", "process_id": 3, "status": "未開始", "priority": "中"},
    {"id": 9, "name": "レシート整理", "process_id": 4, "status": "完了", "priority": "中"},
    {"id": 10, "name": "申請書記入", "process_id": 4, "status": "完了", "priority": "中"},
    {"id": 11, "name": "承認取得", "process_id": 4, "status": "完了", "priority": "低"}
]

WORKFLOWS = [
    {
        "id": 1,
        "name": "一般的な業務プロセス",
        "steps": ["計画", "実行", "確認", "調整", "完了"]
    }
]

ACTIVITIES = [
    {"process": "月次報告書作成", "action": "データ収集完了", "time": datetime.now() - timedelta(hours=5)},
    {"process": "プロジェクト計画策定", "action": "要件定義完了", "time": datetime.now() - timedelta(hours=12)},
    {"process": "経費精算", "action": "プロセス完了", "time": datetime.now() - timedelta(hours=28)},
    {"process": "月次報告書作成", "action": "レポート作成開始", "time": datetime.now() - timedelta(hours=3)},
    {"process": "プロジェクト計画策定", "action": "ガントチャート作成開始", "time": datetime.now() - timedelta(hours=8)}
]

# ProcessMonitorAppのモック実装
class ProcessMonitorApp(QMainWindow):
    """モックアプリケーションクラス"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("プロセスモニター")
        
        # タブウィジェットの作成
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # タブの追加
        dashboard_tab = QWidget()
        details_tab = QWidget()
        report_tab = QWidget()
        settings_tab = QWidget()
        
        self.tabs.addTab(dashboard_tab, "ダッシュボード")
        self.tabs.addTab(details_tab, "プロセス詳細")
        self.tabs.addTab(report_tab, "レポート")
        self.tabs.addTab(settings_tab, "設定")
        
        # ダッシュボードタブのレイアウト
        dashboard_layout = QVBoxLayout(dashboard_tab)
        
        # プロセステーブルの作成
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(["プロセス名", "ステータス", "進捗", "担当者", "期限"])
        self.process_table.setRowCount(len(PROCESSES))
        
        # プロセステーブルにデータを設定
        for i, process in enumerate(PROCESSES):
            self.process_table.setItem(i, 0, QTableWidgetItem(process["name"]))
            self.process_table.setItem(i, 1, QTableWidgetItem(process["status"]))
            self.process_table.setItem(i, 2, QTableWidgetItem(f"{process['progress']}%"))
            self.process_table.setItem(i, 3, QTableWidgetItem(process["owner"]))
            self.process_table.setItem(i, 4, QTableWidgetItem(process["end_date"].strftime("%Y-%m-%d")))
        
        dashboard_layout.addWidget(self.process_table)
        
        # アクティビティテーブルの作成
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["プロセス", "アクション", "時間"])
        self.activity_table.setRowCount(len(ACTIVITIES))
        
        # アクティビティテーブルにデータを設定
        for i, activity in enumerate(ACTIVITIES):
            self.activity_table.setItem(i, 0, QTableWidgetItem(activity["process"]))
            self.activity_table.setItem(i, 1, QTableWidgetItem(activity["action"]))
            self.activity_table.setItem(i, 2, QTableWidgetItem(activity["time"].strftime("%Y-%m-%d %H:%M")))
        
        dashboard_layout.addWidget(self.activity_table)
        
        # プロセス詳細タブのレイアウト
        details_layout = QVBoxLayout(details_tab)
        
        # プロセス詳細ヘッダー
        self.detail_header = QLabel(f"プロセス詳細: {PROCESSES[0]['name']}")
        details_layout.addWidget(self.detail_header)
        
        # プロセス情報
        info_labels = ["プロセス名:", "ステータス:", "開始日:", "期限:", "担当者:"]
        self.info_values = []
        
        for i, label_text in enumerate(info_labels):
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            label = QLabel(label_text)
            value = QLabel()
            info_layout.addWidget(label)
            info_layout.addWidget(value)
            details_layout.addWidget(info_widget)
            self.info_values.append(value)
        
        # 進捗バー
        self.detail_progress = QProgressBar()
        details_layout.addWidget(self.detail_progress)
        
        # タスクテーブル
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["タスク名", "ステータス", "優先度"])
        details_layout.addWidget(self.task_table)
        
        # 初期プロセスの詳細を表示
        self.update_process_details(PROCESSES[0])
        
        # ワークフロービジュアライゼーション
        self.workflow_visual = QWidget()
        self.workflow_visual.setLayout(QVBoxLayout())
        
        # ステップとリンクを追加
        for step in WORKFLOWS[0]["steps"]:
            self.workflow_visual.layout().addWidget(QLabel(step))
            if step != WORKFLOWS[0]["steps"][-1]:
                self.workflow_visual.layout().addWidget(QLabel("↓"))
        
        details_layout.addWidget(self.workflow_visual)
        
        # ステータスバー
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("システム稼働中 - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # シグナル接続
        self.process_table.itemSelectionChanged.connect(self.on_process_selected)
    
    def update_process_details(self, process):
        """プロセス詳細画面を更新"""
        self.detail_header.setText(f"プロセス詳細: {process['name']}")
        
        # プロセス情報の更新
        self.info_values[0].setText(process["name"])
        self.info_values[1].setText(process["status"])
        self.info_values[2].setText(process["start_date"].strftime("%Y-%m-%d"))
        self.info_values[3].setText(process["end_date"].strftime("%Y-%m-%d"))
        self.info_values[4].setText(process["owner"])
        
        # 進捗バーの更新
        self.detail_progress.setValue(process["progress"])
        
        # タスクテーブルの更新
        process_tasks = [task for task in TASKS if task["process_id"] == process["id"]]
        self.task_table.setRowCount(len(process_tasks))
        
        for i, task in enumerate(process_tasks):
            self.task_table.setItem(i, 0, QTableWidgetItem(task["name"]))
            self.task_table.setItem(i, 1, QTableWidgetItem(task["status"]))
            self.task_table.setItem(i, 2, QTableWidgetItem(task["priority"]))
    
    def on_process_selected(self):
        """プロセス選択時の処理"""
        selected_rows = self.process_table.selectedItems()
        if selected_rows:
            # 選択された行のインデックスを取得
            row = self.process_table.row(selected_rows[0])
            # 対応するプロセスを取得
            process = PROCESSES[row]
            # プロセス詳細タブに切り替え
            self.tabs.setCurrentIndex(1)
            # 詳細画面を更新
            self.update_process_details(process)
    
    def refresh_data(self):
        """データ更新処理"""
        # 実際のアプリケーションではここでデータベースからデータを再読み込みするが、
        # テストでは現在時刻の更新のみを行う
        self.status_bar.showMessage("システム稼働中 - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
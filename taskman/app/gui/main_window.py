#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニターGUIのメインウィンドウ実装

このモジュールは、タスク管理システムのGUIインターフェースの
メインウィンドウを実装します。
"""

import sys
import os
import json
import math
import logging
import traceback
from datetime import datetime, timedelta

# PyQt6をインポート
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QMessageBox, QLineEdit, QComboBox, QDialog, QDialogButtonBox,
    QStackedWidget, QFrame, QGridLayout, QProgressBar, QSplitter,
    QTextEdit, QSpacerItem, QSizePolicy, QSpinBox, QDateEdit,
    QFormLayout, QFileDialog, QGroupBox, QRadioButton, QCheckBox,
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsPolygonItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QThread, pyqtSignal, QSize, QDate
from PyQt6.QtGui import (
    QFont, QAction, QIcon, QPalette, QColor, QPainter, QPen, QBrush,
    QPixmap, QPolygonF, QLinearGradient, QStandardItemModel, QTextCursor,
    QImage, QTransform
)
# チャート関連のインポートは必要に応じて追加
# from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QValueAxis, QBarCategoryAxis

# データベースアクセス層をインポート
from taskman.app.db.monitor_db import ProcessMonitorDB

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# グローバル変数
_db_instance = None

# デモモード用のサンプルデータ
PROCESSES = [
    {"id": 1, "name": "月次報告書作成", "status": "進行中", "start_date": datetime.now() - timedelta(days=2), "end_date": datetime.now() + timedelta(days=1), "owner": "田中太郎", "progress": 75, "description": "毎月の業績レポートを作成するプロセス", "version": 1},
    {"id": 2, "name": "プロジェクト計画策定", "status": "進行中", "start_date": datetime.now() - timedelta(days=1), "end_date": datetime.now() + timedelta(days=5), "owner": "佐藤花子", "progress": 30, "description": "新規プロジェクトの計画を作成するプロセス", "version": 2},
    {"id": 3, "name": "顧客対応フロー改善", "status": "未開始", "start_date": datetime.now() + timedelta(days=1), "end_date": datetime.now() + timedelta(days=7), "owner": "鈴木一郎", "progress": 0, "description": "顧客対応の効率化を図るプロセス", "version": 1},
    {"id": 4, "name": "経費精算プロセス", "status": "完了", "start_date": datetime.now() - timedelta(days=5), "end_date": datetime.now() - timedelta(days=1), "owner": "高橋雅子", "progress": 100, "description": "従業員の経費精算を処理するプロセス", "version": 3},
]

TASKS = [
    {"id": 1, "process_id": 1, "name": "データ収集", "status": "完了", "priority": "中", "owner": "田中太郎", "description": "報告書用のデータを収集する"},
    {"id": 2, "process_id": 1, "name": "データ分析", "status": "進行中", "priority": "高", "owner": "田中太郎", "description": "収集したデータを分析する"},
    {"id": 3, "process_id": 1, "name": "レポート作成", "status": "未着手", "priority": "中", "owner": "田中太郎", "description": "分析結果をもとにレポートを作成する"},
    {"id": 4, "process_id": 1, "name": "レビュー", "status": "未着手", "priority": "低", "owner": "山本部長", "description": "作成したレポートをレビューする"},
    {"id": 5, "process_id": 1, "name": "提出", "status": "未着手", "priority": "中", "owner": "田中太郎", "description": "最終レポートを提出する"},
    {"id": 6, "process_id": 2, "name": "要件定義", "status": "完了", "priority": "高", "owner": "佐藤花子", "description": "プロジェクトの要件を定義する"},
    {"id": 7, "process_id": 2, "name": "スケジュール作成", "status": "進行中", "priority": "中", "owner": "佐藤花子", "description": "プロジェクトのスケジュールを立案する"},
    {"id": 8, "process_id": 2, "name": "リソース割り当て", "status": "未着手", "priority": "低", "owner": "佐藤花子", "description": "必要なリソースを割り当てる"},
    {"id": 9, "process_id": 2, "name": "レビュー", "status": "未着手", "priority": "低", "owner": "鈴木部長", "description": "計画内容をレビューする"},
    {"id": 10, "process_id": 2, "name": "承認", "status": "未着手", "priority": "高", "owner": "田中社長", "description": "最終的な計画を承認する"},
]

WORKFLOWS = [
    # 月次報告書作成プロセスのワークフロー
    {"id": 1, "process_id": 1, "from_task_id": 1, "to_task_id": 2, "condition_type": "常時", "sequence_number": 1, 
     "from_task_name": "データ収集", "to_task_name": "データ分析"},
    {"id": 2, "process_id": 1, "from_task_id": 2, "to_task_id": 3, "condition_type": "常時", "sequence_number": 2,
     "from_task_name": "データ分析", "to_task_name": "レポート作成"},
    {"id": 3, "process_id": 1, "from_task_id": 3, "to_task_id": 4, "condition_type": "常時", "sequence_number": 3,
     "from_task_name": "レポート作成", "to_task_name": "レビュー"},
    {"id": 4, "process_id": 1, "from_task_id": 4, "to_task_id": 5, "condition_type": "常時", "sequence_number": 4,
     "from_task_name": "レビュー", "to_task_name": "提出"},
    
    # プロジェクト計画策定プロセスのワークフロー
    {"id": 5, "process_id": 2, "from_task_id": 6, "to_task_id": 7, "condition_type": "常時", "sequence_number": 1,
     "from_task_name": "要件定義", "to_task_name": "スケジュール作成"},
    {"id": 6, "process_id": 2, "from_task_id": 7, "to_task_id": 8, "condition_type": "常時", "sequence_number": 2,
     "from_task_name": "スケジュール作成", "to_task_name": "リソース割り当て"},
    {"id": 7, "process_id": 2, "from_task_id": 8, "to_task_id": 9, "condition_type": "常時", "sequence_number": 3,
     "from_task_name": "リソース割り当て", "to_task_name": "レビュー"},
    {"id": 8, "process_id": 2, "from_task_id": 9, "to_task_id": 10, "condition_type": "常時", "sequence_number": 4,
     "from_task_name": "レビュー", "to_task_name": "承認"},
]

ACTIVITIES = [
    {"id": 1, "process_id": 1, "description": "データ収集が完了しました", "timestamp": datetime.now() - timedelta(hours=5), "process_name": "月次報告書作成"},
    {"id": 2, "process_id": 1, "description": "データ分析を開始しました", "timestamp": datetime.now() - timedelta(hours=4), "process_name": "月次報告書作成"},
    {"id": 3, "process_id": 2, "description": "要件定義が完了しました", "timestamp": datetime.now() - timedelta(hours=7), "process_name": "プロジェクト計画策定"},
    {"id": 4, "process_id": 2, "description": "スケジュール作成を開始しました", "timestamp": datetime.now() - timedelta(hours=3), "process_name": "プロジェクト計画策定"},
]

class ProcessMonitorApp(QMainWindow):
    """プロセスモニタリングアプリケーションのメインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("プロセスモニター")
        self.setGeometry(100, 100, 1000, 600)
        
        # ロガーの初期化
        self.logger = logging.getLogger(__name__)
        
        # データベース接続の初期化
        self.db = None
        self.demo_mode = False
        
        # データベース接続を試みる
        try:
            # データベース接続（タスク管理システムと同じデータベース）
            self.db = get_db_instance()
            
            # データベースに接続
            if not self.db.connect():
                raise Exception("データベースに接続できませんでした")
                
            # データベースが空かチェック（基本的なテーブルの存在を確認）
            try:
                process_count = len(self.db.get_processes())
                if process_count == 0:
                    QMessageBox.warning(
                        self, 
                        "データが見つかりません", 
                        "プロセスデータが見つかりません。デモモードで実行します。"
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
        self.process_instances = []
        self.tasks = []
        self.workflows = []
        self.activities = []
        self.current_workflow = None
        self.current_process_id = None
        self.current_instance_id = None
        
        # メインウィジェットとレイアウト
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # タブウィジェットの設定
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # タブの初期化
        self.init_dashboard_tab()
        self.init_process_definition_tab()
        self.init_process_details_tab()
        self.init_process_instance_tab()
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
        
        # 初期プロセスインスタンスを選択（データがあれば）
        # 自動的にダイアログを表示するのではなく、現在のインスタンスIDを設定するだけにする
        if self.process_instances:
            self.current_instance_id = self.process_instances[0]["id"]
            # ダイアログを表示する処理は削除: self.update_instance_details(self.process_instances[0])
    
    def load_data(self):
        """データをロード（DBまたはデモデータ）"""
        if self.demo_mode:
            # デモモード: 静的データを使用
            self.processes = PROCESSES
            self.tasks = TASKS
            self.workflows = WORKFLOWS
            self.activities = ACTIVITIES
            
            # デモ用のプロセスインスタンスデータ
            self.process_instances = [
                {
                    "id": 1,
                    "process_name": "月次報告書作成",
                    "process_id": 1,
                    "status": "実行中",
                    "started_at": datetime.now() - timedelta(days=2),
                    "completed_at": None,
                    "created_by": "田中太郎",
                    "progress": 75
                },
                {
                    "id": 2,
                    "process_name": "プロジェクト計画策定",
                    "process_id": 2,
                    "status": "実行中",
                    "started_at": datetime.now() - timedelta(days=1),
                    "completed_at": None,
                    "created_by": "佐藤花子",
                    "progress": 30
                }
            ]
            
            # デモ用のダッシュボードデータ
            self.dashboard_data = {
                "active_instances_count": 3,
                "completed_instances_count": 12,
                "overdue_tasks_count": 2,
                "today_tasks_count": 5,
                "active_instances": self.process_instances,
                "activities": [
                    {
                        "timestamp": datetime.now() - timedelta(hours=2),
                        "process_name": "月次報告書作成",
                        "description": "データ分析が完了しました",
                        "user": "田中太郎"
                    },
                    {
                        "timestamp": datetime.now() - timedelta(hours=4),
                        "process_name": "プロジェクト計画策定",
                        "description": "スケジュール作成が進行中になりました",
                        "user": "佐藤花子"
                    },
                    {
                        "timestamp": datetime.now() - timedelta(hours=8),
                        "process_name": "月次報告書作成",
                        "description": "データ収集が完了しました",
                        "user": "田中太郎"
                    }
                ],
                "urgent_tasks": [
                    {
                        "task_name": "レポート提出",
                        "process_name": "月次報告書作成",
                        "deadline": datetime.now().date(),
                        "priority": "高",
                        "status": "進行中"
                    },
                    {
                        "task_name": "経費精算",
                        "process_name": "経費精算プロセス",
                        "deadline": datetime.now().date() - timedelta(days=1),
                        "priority": "中",
                        "status": "未着手"
                    }
                ],
                "process_stats": [
                    {
                        "process_type": "月次報告書作成",
                        "active_count": 2,
                        "completed_count": 5
                    },
                    {
                        "process_type": "プロジェクト計画策定",
                        "active_count": 1,
                        "completed_count": 3
                    },
                    {
                        "process_type": "経費精算プロセス",
                        "active_count": 0,
                        "completed_count": 4
                    }
                ]
            }
        else:
            # DB接続モード: データベースからデータを取得
            try:
                self.processes = self.db.get_processes()
                self.activities = self.db.get_recent_activities()
                # プロセスインスタンスの取得を追加
                self.process_instances = self.db.get_process_instances()
                # ダッシュボードデータを取得
                self.dashboard_data = self.db.get_dashboard_summary()
                # タスクとワークフローは選択されたプロセスに基づいて後でロードされる
            except Exception as e:
                QMessageBox.critical(self, "データ取得エラー", f"データの取得に失敗しました: {str(e)}")
                # エラーが発生したらデモモードに切り替え
                self.demo_mode = True
                self.processes = PROCESSES
                self.tasks = TASKS
                self.workflows = WORKFLOWS
                self.activities = ACTIVITIES
                
                # デモ用のプロセスインスタンスデータ
                self.process_instances = [
                    {
                        "id": 1,
                        "process_name": "月次報告書作成",
                        "process_id": 1,
                        "status": "実行中",
                        "started_at": datetime.now() - timedelta(days=2),
                        "completed_at": None,
                        "created_by": "田中太郎",
                        "progress": 75
                    },
                    {
                        "id": 2,
                        "process_name": "プロジェクト計画策定",
                        "process_id": 2,
                        "status": "実行中",
                        "started_at": datetime.now() - timedelta(days=1),
                        "completed_at": None,
                        "created_by": "佐藤花子",
                        "progress": 30
                    }
                ]
                
                # デモ用のダッシュボードデータ
                self.dashboard_data = {
                    "active_instances_count": 3,
                    "completed_instances_count": 12,
                    "overdue_tasks_count": 2,
                    "today_tasks_count": 5,
                    "active_instances": self.process_instances,
                    "activities": [
                        {
                            "timestamp": datetime.now() - timedelta(hours=2),
                            "process_name": "月次報告書作成",
                            "description": "データ分析が完了しました",
                            "user": "田中太郎"
                        },
                        {
                            "timestamp": datetime.now() - timedelta(hours=4),
                            "process_name": "プロジェクト計画策定",
                            "description": "スケジュール作成が進行中になりました",
                            "user": "佐藤花子"
                        }
                    ],
                    "urgent_tasks": [
                        {
                            "task_name": "レポート提出",
                            "process_name": "月次報告書作成",
                            "deadline": datetime.now().date(),
                            "priority": "高",
                            "status": "進行中"
                        }
                    ],
                    "process_stats": [
                        {
                            "process_type": "月次報告書作成",
                            "active_count": 2,
                            "completed_count": 5
                        },
                        {
                            "process_type": "プロジェクト計画策定",
                            "active_count": 1,
                            "completed_count": 3
                        }
                    ]
                }
                
                # ステータスバーメッセージを更新
                self.status_bar.showMessage("エラーによりデモモードに切り替えました - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # UIを更新
        self.update_process_table()
        self.update_activity_table()
        self.update_instance_table()
        self.update_dashboard()
    
    def update_process_table(self):
        """プロセステーブルを更新（ダッシュボードの代わりにプロセス定義タブを追加）"""
        # プロセス定義タブがなければ初期化
        if not hasattr(self, 'process_def_table'):
            self.init_process_definition_tab()
            
        self.process_def_table.setRowCount(len(self.processes))
        
        for i, process in enumerate(self.processes):
            # プロセス名
            self.process_def_table.setItem(i, 0, QTableWidgetItem(process["name"]))
            
            # バージョン
            version = process.get("version", "1")
            self.process_def_table.setItem(i, 1, QTableWidgetItem(str(version)))
            
            # ステータス情報（データベースからの取得値、なければデフォルト値「ドラフト」を表示）
            status = process.get("status", "ドラフト")
            status_item = QTableWidgetItem(status)
            
            # ステータスに基づいて色を設定
            if status == "アクティブ":
                status_item.setForeground(QColor("#4CAF50"))  # 緑色
            elif status == "非アクティブ":
                status_item.setForeground(QColor("#F44336"))  # 赤色
            elif status == "ドラフト":
                status_item.setForeground(QColor("#2196F3"))  # 青色
                
            self.process_def_table.setItem(i, 2, status_item)
            
            # タスク数
            task_count = 0
            if self.demo_mode:
                # デモモードでは関連するタスクを数える
                task_count = sum(1 for task in self.tasks if task.get("process_id") == process["id"])
            else:
                # DB接続モードでは取得済みデータがない場合はDBから取得
                try:
                    if hasattr(self, 'db') and self.db:
                        tasks = self.db.get_tasks_by_process_id(process["id"])
                        task_count = len(tasks)
                except Exception as e:
                    logger.error(f"タスク数取得エラー: {e}")
                    task_count = 0
            
            self.process_def_table.setItem(i, 3, QTableWidgetItem(str(task_count)))
        
        self.process_def_table.resizeColumnsToContents()
    
    def init_process_definition_tab(self):
        """プロセス定義タブの初期化"""
        process_def = QWidget()
        layout = QVBoxLayout(process_def)
        
        # ヘッダー
        header = QLabel("プロセス定義")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # プロセス定義テーブル
        self.process_def_table = QTableWidget()
        self.process_def_table.setColumnCount(4)
        self.process_def_table.setHorizontalHeaderLabels(["プロセス名", "バージョン", "ステータス", "タスク数"])
        self.process_def_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_def_table.selectionModel().selectionChanged.connect(self.on_process_selected)
        self.process_def_table.horizontalHeader().setStretchLastSection(True)
        self.process_def_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.process_def_table)
        
        self.tabs.addTab(process_def, "プロセス定義")
    
    def update_activity_table(self):
        """アクティビティテーブルを更新"""
        # ダッシュボードタブでは dashboard_activity_table を使用
        if hasattr(self, 'dashboard_activity_table'):
            self.dashboard_activity_table.setRowCount(len(self.activities))
            
            for i, activity in enumerate(self.activities):
                # 時間
                timestamp = activity["timestamp"]
                time_str = timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else str(timestamp)
                self.dashboard_activity_table.setItem(i, 0, QTableWidgetItem(time_str))
                
                # プロセス名
                process_name = activity.get("process_name", "不明")
                self.dashboard_activity_table.setItem(i, 1, QTableWidgetItem(process_name))
                
                # アクション
                self.dashboard_activity_table.setItem(i, 2, QTableWidgetItem(activity["description"]))
            
            self.dashboard_activity_table.resizeColumnsToContents()
    
    def load_workflow_for_process(self, process_id):
        """指定したプロセスIDのワークフローをロードする"""
        try:
            # デモモードの場合
            if self.demo_mode:
                # デモデータから該当するワークフローを見つける
                self.workflow_data = []
                for wf in self.workflows:
                    if wf['process_id'] == process_id:
                        self.workflow_data.append(wf)
                
                if not self.workflow_data:
                    self.add_message_to_workflow_scene("ワークフローデータが見つかりません")
                    return
                
                self.draw_workflow({'process_id': process_id, 'transitions': self.workflow_data})
            else:
                # データベースからワークフローを取得
                workflow_data = self.db.get_workflow_for_process(process_id)
                if not workflow_data:
                    self.add_message_to_workflow_scene("ワークフローデータが見つかりません")
                    return
                
                self.workflow_data = workflow_data
                self.draw_workflow(workflow_data)
        
        except Exception as e:
            self.log_error(f"ワークフローのロードエラー: {str(e)}")
            self.add_message_to_workflow_scene(f"ワークフローの読み込みに失敗しました: {str(e)}")

    def update_workflow_combo(self):
        """ワークフローコンボボックスの更新（現在のUIには存在しないため、何もしない）"""
        # 現在のUIには workflow_combo が実装されていないため、このメソッドは何もしない
        pass

    def on_workflow_changed(self, index):
        """ワークフローが変更されたときの処理（現在のUIには存在しないため、何もしない）"""
        # 現在のUIには workflow_combo が実装されていないため、このメソッドは何もしない
        pass

    def update_workflow_visualization(self):
        """ワークフロー可視化エリアを更新"""
        try:
            if not hasattr(self, 'workflow_data') or not self.workflow_data:
                logger.debug("ワークフローデータがありません")
                return
                
            # ワークフロー可視化エリアが初期化されていない場合は初期化
            if not hasattr(self, 'workflow_scene'):
                self.workflow_scene = QGraphicsScene()
                
                if not hasattr(self, 'workflow_view'):
                    return
                    
                self.workflow_view.setScene(self.workflow_scene)
                # PyQt6ではRenderHintの指定方法が変更されているため修正
                self.workflow_view.setRenderHints(QPainter.RenderHint.Antialiasing)
            
            # シーンをクリア
            self.workflow_scene.clear()
            
            # タスク間の距離を設定
            task_width = 150
            task_height = 80
            
            # タスクをノードとして表示
            task_nodes = {}
            for task in self.workflow_data.get('tasks', []):
                task_id = task.get('id')
                task_name = task.get('name')
                pos_x = task.get('position_x', 0)
                pos_y = task.get('position_y', 0)
                
                # タスクノードを作成
                rect = QGraphicsRectItem(0, 0, task_width, task_height)
                rect.setPos(pos_x, pos_y)
                rect.setBrush(QBrush(QColor(230, 230, 250)))
                rect.setPen(QPen(Qt.GlobalColor.black, 1))
                self.workflow_scene.addItem(rect)
                
                # タスク名を表示
                text = QGraphicsTextItem(task_name)
                text.setPos(pos_x + 10, pos_y + 10)
                self.workflow_scene.addItem(text)
                
                # タスク状態を表示
                status_text = f"状態: {task.get('status', '未定義')}"
                status = QGraphicsTextItem(status_text)
                status.setPos(pos_x + 10, pos_y + 40)
                self.workflow_scene.addItem(status)
                
                task_nodes[task_id] = (rect, pos_x, pos_y)
            
            # 遷移（矢印）を表示
            for transition in self.workflow_data.get('transitions', []):
                from_id = transition.get('from_task_id')
                to_id = transition.get('to_task_id')
                
                if from_id in task_nodes and to_id in task_nodes:
                    from_node, from_x, from_y = task_nodes[from_id]
                    to_node, to_x, to_y = task_nodes[to_id]
                    
                    # 矢印の開始点と終了点を計算
                    start_x = from_x + task_width
                    start_y = from_y + task_height / 2
                    end_x = to_x
                    end_y = to_y + task_height / 2
                    
                    # 矢印を描画
                    arrow = QGraphicsLineItem(start_x, start_y, end_x, end_y)
                    arrow.setPen(QPen(Qt.GlobalColor.black, 2))
                    self.workflow_scene.addItem(arrow)
                    
                    # 矢印の終端を描画
                    arrow_size = 10
                    angle = math.atan2(end_y - start_y, end_x - start_x)
                    end_point = QPointF(end_x, end_y)
                    
                    # 矢印の先端を描画
                    arrow_p1 = QPointF(
                        end_x - arrow_size * math.cos(angle - math.pi / 6),
                        end_y - arrow_size * math.sin(angle - math.pi / 6)
                    )
                    arrow_p2 = QPointF(
                        end_x - arrow_size * math.cos(angle + math.pi / 6),
                        end_y - arrow_size * math.sin(angle + math.pi / 6)
                    )
                    
                    arrow_head = QPolygonF([end_point, arrow_p1, arrow_p2])
                    self.workflow_scene.addPolygon(arrow_head, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.black))
            
            # シーン全体を表示
            self.workflow_scene.setSceneRect(self.workflow_scene.itemsBoundingRect())
            self.workflow_view.fitInView(self.workflow_scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
            logger.debug(f"ワークフロー可視化を更新: {len(self.workflow_data.get('tasks', []))}タスク, {len(self.workflow_data.get('transitions', []))}遷移")
            
        except Exception as e:
            logger.error(f"ワークフロー可視化更新エラー: {str(e)}")
            traceback.print_exc()

    def add_message_to_workflow_scene(self, message):
        """ワークフロービューにメッセージを表示"""
        if not hasattr(self, 'workflow_scene') or self.workflow_scene is None:
            # シーンがまだ初期化されていない場合は作成
            if not hasattr(self, 'workflow_view') or self.workflow_view is None:
                return
            
            self.workflow_scene = QGraphicsScene()
            self.workflow_view.setScene(self.workflow_scene)
        
        # シーンをクリアして新しいメッセージを表示
        self.workflow_scene.clear()
        text_item = QGraphicsTextItem(message)
        text_item.setPos(10, 10)
        self.workflow_scene.addItem(text_item)

    def draw_workflow(self, workflow_data):
        """ワークフローを描画する"""
        try:
            if not hasattr(self, 'workflow_scene') or self.workflow_scene is None:
                self.workflow_scene = QGraphicsScene()
                self.workflow_view.setScene(self.workflow_scene)
            
            self.workflow_scene.clear()
            
            # ワークフロータイトルを追加
            title_text = f"ワークフロー: {workflow_data.get('process_name', '無名プロセス')}"
            title_item = QGraphicsTextItem(title_text)
            title_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            title_item.setPos(10, 10)
            self.workflow_scene.addItem(title_item)
            
            # タスクノードの生成
            task_items = {}
            for task in workflow_data.get('tasks', []):
                # タスクの位置を取得
                pos_x = task.get('position_x', 0)
                pos_y = task.get('position_y', 50) + 40  # タイトルの下にスペースを確保
                
                # タスクの表示名
                task_name = task.get('name', f"タスク {task.get('id', '')}")
                
                # タスクのステータスによって色を変更
                status = task.get('status', '未着手')
                if status == '完了':
                    color = QColor(150, 200, 150)  # 緑色
                elif status == '進行中':
                    color = QColor(200, 200, 150)  # 黄色
                else:
                    color = QColor(200, 200, 200)  # グレー
                
                # タスクの矩形を作成
                task_rect = QGraphicsRectItem(pos_x, pos_y, 150, 80)
                task_rect.setBrush(QBrush(color))
                task_rect.setPen(QPen(Qt.GlobalColor.black, 1))
                
                # タスク名のテキストアイテム
                task_text = QGraphicsTextItem(task_name)
                task_text.setPos(pos_x + 10, pos_y + 10)
                task_text.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                
                # タスクの詳細情報
                details = []
                if task.get('assignee'):
                    details.append(f"担当: {task['assignee']}")
                if task.get('priority'):
                    details.append(f"優先度: {task['priority']}")
                
                details_text = QGraphicsTextItem("\n".join(details))
                details_text.setPos(pos_x + 10, pos_y + 30)
                details_text.setFont(QFont("Arial", 8))
                
                # シーンに追加
                self.workflow_scene.addItem(task_rect)
                self.workflow_scene.addItem(task_text)
                self.workflow_scene.addItem(details_text)
                
                # 後で遷移線を引くために辞書に保存
                task_items[task['id']] = {
                    'rect': task_rect,
                    'center_x': pos_x + 75,
                    'center_y': pos_y + 40
                }
            
            # 遷移の矢印を描画
            for transition in workflow_data.get('transitions', []):
                from_id = transition.get('from_task_id')
                to_id = transition.get('to_task_id')
                
                if from_id in task_items and to_id in task_items:
                    # 始点と終点の座標
                    start_x = task_items[from_id]['center_x'] + 75  # 矩形の右端
                    start_y = task_items[from_id]['center_y']
                    end_x = task_items[to_id]['center_x'] - 75      # 矩形の左端
                    end_y = task_items[to_id]['center_y']
                    
                    # 矢印を描画
                    arrow = QGraphicsLineItem(start_x, start_y, end_x, end_y)
                    arrow.setPen(QPen(Qt.GlobalColor.black, 1.5))
                    self.workflow_scene.addItem(arrow)
                    
                    # 矢印の先端を描画
                    arrowhead_size = 10
                    angle = math.atan2(end_y - start_y, end_x - start_x)
                    arrowhead1_x = end_x - arrowhead_size * math.cos(angle - math.pi/6)
                    arrowhead1_y = end_y - arrowhead_size * math.sin(angle - math.pi/6)
                    arrowhead2_x = end_x - arrowhead_size * math.cos(angle + math.pi/6)
                    arrowhead2_y = end_y - arrowhead_size * math.sin(angle + math.pi/6)
                    
                    arrowhead1 = QGraphicsLineItem(end_x, end_y, arrowhead1_x, arrowhead1_y)
                    arrowhead2 = QGraphicsLineItem(end_x, end_y, arrowhead2_x, arrowhead2_y)
                    arrowhead1.setPen(QPen(Qt.GlobalColor.black, 1.5))
                    arrowhead2.setPen(QPen(Qt.GlobalColor.black, 1.5))
                    self.workflow_scene.addItem(arrowhead1)
                    self.workflow_scene.addItem(arrowhead2)
                    
                    # 条件テキストを表示（存在する場合）
                    condition = transition.get('condition', '')
                    if condition:
                        # 矢印の中間点に条件テキストを表示
                        mid_x = (start_x + end_x) / 2
                        mid_y = (start_y + end_y) / 2 - 10  # 少し上に表示
                        
                        condition_text = QGraphicsTextItem(condition)
                        condition_text.setFont(QFont("Arial", 8))
                        text_width = condition_text.boundingRect().width()
                        condition_text.setPos(mid_x - text_width / 2, mid_y)
                        
                        # 背景を追加して見やすくする
                        text_rect = condition_text.boundingRect()
                        bg_rect = QGraphicsRectItem(
                            mid_x - text_width / 2 - 2,
                            mid_y - 2,
                            text_rect.width() + 4,
                            text_rect.height() + 4
                        )
                        bg_rect.setBrush(QBrush(QColor(255, 255, 220)))
                        bg_rect.setPen(QPen(Qt.GlobalColor.lightGray, 0.5))
                        
                        self.workflow_scene.addItem(bg_rect)
                        self.workflow_scene.addItem(condition_text)
            
            # ビューを調整
            self.workflow_view.setRenderHints(QPainter.RenderHint.Antialiasing)
            self.workflow_view.fitInView(self.workflow_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
        except Exception as e:
            self.logger.error(f"ワークフロー描画エラー: {str(e)}")
            self.add_message_to_workflow_scene(f"ワークフローの描画中にエラーが発生しました: {str(e)}")
    
    def create_task_node(self, task_name, position):
        """ワークフロー図のタスクノードを作成"""
        rect = QGraphicsRectItem(0, 0, 150, 50)
        rect.setBrush(QBrush(QColor("#E3F2FD")))
        rect.setPen(QPen(QColor("#1976D2"), 2))
        rect.setPos(position[0], position[1])
        
        text = QGraphicsTextItem(task_name)
        text.setParentItem(rect)
        text.setPos(10, 10)
        
        return rect
    
    def draw_workflow_arrow(self, start_pos, end_pos, condition=""):
        """ワークフロー図の矢印を描画"""
        # 矢印の始点・終点を計算
        start_x = start_pos[0] + 150  # タスクの右端
        start_y = start_pos[1] + 25   # タスクの中央
        end_x = end_pos[0]            # 次のタスクの左端
        end_y = end_pos[1] + 25       # 次のタスクの中央
        
        # 矢印の線を描画
        line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
        line.setPen(QPen(QColor("#1976D2"), 2))
        self.workflow_scene.addItem(line)
        
        # 矢印の先端を描画
        arrow_size = 10
        angle = math.atan2(end_y - start_y, end_x - start_x)
        arrow_p1 = QPointF(end_x - arrow_size * math.cos(angle - math.pi/6),
                          end_y - arrow_size * math.sin(angle - math.pi/6))
        arrow_p2 = QPointF(end_x - arrow_size * math.cos(angle + math.pi/6),
                          end_y - arrow_size * math.sin(angle + math.pi/6))
        
        arrow = QGraphicsPolygonItem(QPolygonF([QPointF(end_x, end_y), arrow_p1, arrow_p2]))
        arrow.setBrush(QBrush(QColor("#1976D2")))
        arrow.setPen(QPen(QColor("#1976D2"), 2))
        self.workflow_scene.addItem(arrow)
        
        # 条件があれば表示
        if condition:
            condition_text = QGraphicsTextItem(condition)
            condition_text.setPos((start_x + end_x) / 2 - 30, (start_y + end_y) / 2 - 20)
            condition_text.setDefaultTextColor(QColor("#1976D2"))
            self.workflow_scene.addItem(condition_text)
    
    def update_process_details(self, process):
        """プロセス詳細を更新"""
        if not process:
            return
            
        self.current_process_id = process["id"]
        self.detail_header.setText(f"プロセス詳細: {process['name']}")
        
        # 基本情報の更新
        self.info_values[0].setText(process["name"])
        
        # ステータス
        status = process.get("status", "ドラフト")
        status_text = status
        self.info_values[1].setText(status_text)
        
        # バージョン
        version = process.get("version", "1")
        self.info_values[2].setText(str(version))
        
        # 作成日
        start_date = process.get("start_date")
        if start_date:
            date_str = start_date.strftime("%Y-%m-%d") if isinstance(start_date, datetime) else str(start_date)
            self.info_values[3].setText(date_str)
        else:
            self.info_values[3].setText("-")
            
        # 説明
        description = process.get("description", "-")
        self.info_values[4].setText(description)
        
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
            self.task_table.setItem(i, 1, QTableWidgetItem(task.get("description", "-")))
            self.task_table.setItem(i, 2, QTableWidgetItem(task.get("priority", "-")))
            self.task_table.setItem(i, 3, QTableWidgetItem(task.get("owner", "-")))
        
        self.task_table.resizeColumnsToContents()
        
        # ボタン状態の更新
        if process.get("status", "ドラフト") == "アクティブ":
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
        
        self.complete_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        
        # ワークフローを読み込む
        self.load_workflow_for_process(process["id"])
    
    @pyqtSlot()
    def on_process_selected(self):
        """プロセス選択時のハンドラ"""
        selected_indexes = self.process_def_table.selectedIndexes()
        if selected_indexes:
            row = selected_indexes[0].row()
            if 0 <= row < len(self.processes):
                selected_process = self.processes[row]
                self.update_process_details(selected_process)
                self.tabs.setCurrentIndex(1)  # プロセス詳細タブに切り替え
    
    def refresh_data(self):
        """データを更新（5秒ごとに呼び出される）"""
        if self.demo_mode:
            # デモモードでは何もしない（静的データのまま）
            return
            
        # データベースからデータを再取得
        try:
            # すでに選択されているプロセスとインスタンスのIDを保存
            current_process_id = self.current_process_id
            current_instance_id = self.current_instance_id
            
            self.processes = self.db.get_processes()
            self.activities = self.db.get_recent_activities()
            self.process_instances = self.db.get_process_instances()
            self.dashboard_data = self.db.get_dashboard_summary()
            
            # UIを更新
            self.update_process_table()
            self.update_activity_table()
            self.update_instance_table()
            self.update_dashboard()
            
            # 以前選択していたプロセスの詳細を更新
            if current_process_id:
                for process in self.processes:
                    if process["id"] == current_process_id:
                        self.update_process_details(process)
                        break
            
            # 以前選択していたインスタンスの詳細を更新する代わりに
            # インスタンスIDを保持するだけにする
            self.current_instance_id = current_instance_id
            
            # ステータスバーを更新
            self.status_bar.showMessage("システム稼働中 - 最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            print(f"データ更新エラー: {e}")
            # エラーが発生してもクラッシュさせない
    
    def update_dashboard(self):
        """ダッシュボードのUI要素を更新"""
        # サマリーカードの更新
        self.active_instances_card.value_label.setText(str(self.dashboard_data["active_instances_count"]))
        self.completed_instances_card.value_label.setText(str(self.dashboard_data["completed_instances_count"]))
        self.overdue_tasks_card.value_label.setText(str(self.dashboard_data["overdue_tasks_count"]))
        self.today_tasks_card.value_label.setText(str(self.dashboard_data["today_tasks_count"]))
        
        # 実行中のプロセスインスタンス
        active_instances = self.dashboard_data["active_instances"]
        self.dashboard_instance_table.setRowCount(len(active_instances))
        
        for i, instance in enumerate(active_instances):
            # インスタンスID
            self.dashboard_instance_table.setItem(i, 0, QTableWidgetItem(str(instance["id"])))
            # プロセス名
            self.dashboard_instance_table.setItem(i, 1, QTableWidgetItem(instance["process_name"]))
            # ステータス
            self.dashboard_instance_table.setItem(i, 2, QTableWidgetItem(instance["status"]))
            
            # 進捗バー
            progress_bar = QProgressBar()
            progress_bar.setValue(int(instance.get("progress", 0)))
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
            self.dashboard_instance_table.setCellWidget(i, 3, progress_bar)
            
            # 開始時間
            started_at = instance.get("started_at")
            if started_at:
                date_str = started_at.strftime("%Y-%m-%d %H:%M") if isinstance(started_at, datetime) else str(started_at)
                self.dashboard_instance_table.setItem(i, 4, QTableWidgetItem(date_str))
            else:
                self.dashboard_instance_table.setItem(i, 4, QTableWidgetItem("-"))
        
        self.dashboard_instance_table.resizeColumnsToContents()
        
        # 最近のアクティビティ
        activities = self.dashboard_data["activities"]
        self.dashboard_activity_table.setRowCount(len(activities))
        
        for i, activity in enumerate(activities):
            # 時間
            timestamp = activity.get("timestamp")
            if timestamp:
                time_str = timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else str(timestamp)
                self.dashboard_activity_table.setItem(i, 0, QTableWidgetItem(time_str))
            else:
                self.dashboard_activity_table.setItem(i, 0, QTableWidgetItem("-"))
            
            # プロセス名
            self.dashboard_activity_table.setItem(i, 1, QTableWidgetItem(activity.get("process_name", "")))
            
            # アクション
            self.dashboard_activity_table.setItem(i, 2, QTableWidgetItem(activity.get("description", "")))
        
        self.dashboard_activity_table.resizeColumnsToContents()
        
        # 注意が必要なタスク
        urgent_tasks = self.dashboard_data["urgent_tasks"]
        self.dashboard_urgent_table.setRowCount(len(urgent_tasks))
        
        for i, task in enumerate(urgent_tasks):
            # タスク名
            self.dashboard_urgent_table.setItem(i, 0, QTableWidgetItem(task.get("task_name", "")))
            
            # 関連プロセス
            self.dashboard_urgent_table.setItem(i, 1, QTableWidgetItem(task.get("process_name", "")))
            
            # 期限
            deadline = task.get("deadline")
            if deadline:
                if isinstance(deadline, datetime):
                    deadline = deadline.date()
                if isinstance(deadline, str):
                    # 文字列の場合、そのまま表示
                    date_str = deadline
                else:
                    # datetime.dateオブジェクトなどの場合
                    date_str = deadline.strftime("%Y-%m-%d")
                self.dashboard_urgent_table.setItem(i, 2, QTableWidgetItem(date_str))
            else:
                self.dashboard_urgent_table.setItem(i, 2, QTableWidgetItem("-"))
            
            # 優先度
            priority = task.get("priority", "")
            priority_item = QTableWidgetItem(priority)
            
            # 優先度に基づいて背景色を設定
            if priority == "緊急":
                priority_item.setBackground(QColor("#FFCDD2"))  # 薄い赤
            elif priority == "高":
                priority_item.setBackground(QColor("#FFECB3"))  # 薄いオレンジ
            elif priority == "中":
                priority_item.setBackground(QColor("#FFF9C4"))  # 薄い黄色
            elif priority == "低":
                priority_item.setBackground(QColor("#DCEDC8"))  # 薄い緑
                
            self.dashboard_urgent_table.setItem(i, 3, priority_item)
        
        self.dashboard_urgent_table.resizeColumnsToContents()
        
        # プロセスタイプ別統計
        process_stats = self.dashboard_data["process_stats"]
        self.process_stats_table.setRowCount(len(process_stats))
        
        for i, stat in enumerate(process_stats):
            # プロセスタイプ
            self.process_stats_table.setItem(i, 0, QTableWidgetItem(stat.get("process_type", "")))
            
            # 実行中
            self.process_stats_table.setItem(i, 1, QTableWidgetItem(str(stat.get("active_count", 0))))
            
            # 完了済
            self.process_stats_table.setItem(i, 2, QTableWidgetItem(str(stat.get("completed_count", 0))))
        
        self.process_stats_table.resizeColumnsToContents()
    
    def update_instance_table(self):
        """プロセスインスタンステーブルを更新"""
        self.instance_table.setRowCount(len(self.process_instances))
        
        for i, instance in enumerate(self.process_instances):
            # インスタンスID
            self.instance_table.setItem(i, 0, QTableWidgetItem(str(instance["id"])))
            
            # プロセス名
            self.instance_table.setItem(i, 1, QTableWidgetItem(instance["process_name"]))
            
            # ステータス
            self.instance_table.setItem(i, 2, QTableWidgetItem(instance["status"]))
            
            # 開始時間
            started_at = instance.get("started_at")
            if started_at:
                date_str = started_at.strftime("%Y-%m-%d %H:%M") if isinstance(started_at, datetime) else str(started_at)
                self.instance_table.setItem(i, 3, QTableWidgetItem(date_str))
            else:
                self.instance_table.setItem(i, 3, QTableWidgetItem("-"))
            
            # 終了時間
            completed_at = instance.get("completed_at")
            if completed_at:
                date_str = completed_at.strftime("%Y-%m-%d %H:%M") if isinstance(completed_at, datetime) else str(completed_at)
                self.instance_table.setItem(i, 4, QTableWidgetItem(date_str))
            else:
                self.instance_table.setItem(i, 4, QTableWidgetItem("-"))
        
        self.instance_table.resizeColumnsToContents()
    
    def on_instance_selected(self):
        """インスタンス選択時のハンドラ"""
        selected_indexes = self.instance_table.selectedIndexes()
        if selected_indexes:
            row = selected_indexes[0].row()
            if 0 <= row < len(self.process_instances):
                selected_instance = self.process_instances[row]
                self.update_instance_details(selected_instance)
    
    def update_instance_details(self, instance):
        """インスタンス詳細を更新"""
        if not instance:
            return
            
        self.current_instance_id = instance["id"]
        
        # インスタンス詳細ダイアログを表示
        dialog = QDialog(self)
        dialog.setWindowTitle(f"インスタンス詳細: {instance['process_name']}")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # 基本情報
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Panel)
        info_frame.setFrameShadow(QFrame.Shadow.Raised)
        info_layout = QGridLayout(info_frame)
        info_layout.setColumnStretch(0, 1)  # ラベル列を小さく
        info_layout.setColumnStretch(1, 3)  # 値列を大きく
        
        labels = [
            ("プロセス:", instance['process_name']),
            ("ステータス:", instance.get('status', '-')),
            ("開始時間:", instance.get('started_at', '-')),
            ("作成者:", instance.get('created_by', '-')),
        ]
        
        for i, (label_text, value) in enumerate(labels):
            label = QLabel(label_text)
            label.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            info_layout.addWidget(label, i, 0)
            
            value = QLabel(str(value))
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            info_layout.addWidget(value, i, 1)
        
        layout.addWidget(info_frame)
        
        # 関連タスクインスタンス
        task_label = QLabel("関連タスクインスタンス")
        task_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        layout.addWidget(task_label)
        
        task_table = QTableWidget()
        task_table.setColumnCount(4)
        task_table.setHorizontalHeaderLabels(["タスク名", "ステータス", "担当者", "完了日時"])
        task_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(task_table)
        
        # タスクインスタンスを取得
        if self.demo_mode:
            # デモモード: ダミーデータ
            task_instances = [
                {"task_name": "データ収集", "status": "完了", "assigned_to": "山田太郎", "completed_at": datetime.now() - timedelta(days=1)},
                {"task_name": "分析", "status": "進行中", "assigned_to": "鈴木一郎", "completed_at": None},
                {"task_name": "レポート作成", "status": "未着手", "assigned_to": "佐藤花子", "completed_at": None},
            ]
        else:
            # DB接続モード: データベースからタスクインスタンスを取得
            try:
                if hasattr(self, 'db') and self.db:
                    task_instances = self.db.get_task_instances_by_process_instance_id(instance["id"])
                else:
                    task_instances = []
            except Exception as e:
                print(f"タスクインスタンス取得エラー: {e}")
                task_instances = []
        
        # タスク一覧を表示
        task_table.setRowCount(len(task_instances))
        for i, task in enumerate(task_instances):
            task_table.setItem(i, 0, QTableWidgetItem(task.get("task_name", "")))
            task_table.setItem(i, 1, QTableWidgetItem(task.get("status", "")))
            task_table.setItem(i, 2, QTableWidgetItem(task.get("assigned_to", "")))
            
            completed_at = task.get("completed_at")
            if completed_at:
                date_str = completed_at.strftime("%Y-%m-%d %H:%M") if isinstance(completed_at, datetime) else str(completed_at)
                task_table.setItem(i, 3, QTableWidgetItem(date_str))
            else:
                task_table.setItem(i, 3, QTableWidgetItem("-"))
        
        task_table.resizeColumnsToContents()
        
        # 閉じるボタン
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.exec()

    def closeEvent(self, event):
        """アプリケーション終了時の処理"""
        # データベース接続を閉じる
        if hasattr(self, 'db') and self.db:
            try:
                self.db.disconnect()
                logger.info("データベース接続を閉じました")
            except Exception as e:
                logger.error(f"データベース切断エラー: {e}")
        
        # タイマーを停止
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
            logger.info("更新タイマーを停止しました")
        
        # イベントを受け入れて閉じる
        event.accept()

    def init_process_details_tab(self):
        """プロセス詳細タブの初期化"""
        details = QWidget()
        layout = QVBoxLayout(details)
        
        # ヘッダー
        self.detail_header = QLabel("プロセス詳細")
        self.detail_header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(self.detail_header)
        
        # プロセス情報
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Panel)
        info_frame.setFrameShadow(QFrame.Shadow.Raised)
        info_layout = QGridLayout(info_frame)
        
        # グリッドレイアウトの設定を調整
        info_layout.setColumnStretch(0, 0)  # ラベル列は自然な幅
        info_layout.setColumnStretch(1, 1)  # 値列は伸縮可能
        info_layout.setHorizontalSpacing(15)  # ラベルと値の間の水平方向の間隔
        info_layout.setVerticalSpacing(10)   # 行間の垂直方向の間隔
        info_layout.setContentsMargins(15, 15, 15, 15)  # 余白を設定
        
        labels = ["プロセス名:", "ステータス:", "バージョン:", "作成日:", "説明:"]
        self.info_values = []
        
        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            label.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            info_layout.addWidget(label, i, 0)
            
            value = QLabel()
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setWordWrap(True)  # 長いテキストの折り返し
            info_layout.addWidget(value, i, 1)
            self.info_values.append(value)
        
        layout.addWidget(info_frame)
        
        # タスクとワークフローのタブ
        details_tabs = QTabWidget()
        
        # タスク一覧タブ
        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)
        
        task_label = QLabel("関連タスク")
        task_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        task_layout.addWidget(task_label)
        
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels(["タスク名", "説明", "優先度", "担当者"])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        task_layout.addWidget(self.task_table)
        
        details_tabs.addTab(task_widget, "タスク一覧")
        
        # ワークフロー表示タブ
        workflow_widget = QWidget()
        workflow_layout = QVBoxLayout(workflow_widget)
        
        workflow_label = QLabel("ワークフロー")
        workflow_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        workflow_layout.addWidget(workflow_label)
        
        self.workflow_view = QGraphicsView()
        self.workflow_scene = QGraphicsScene()
        self.workflow_view.setScene(self.workflow_scene)
        # PyQt6ではRenderHintの指定方法が変更されているため修正
        self.workflow_view.setRenderHints(QPainter.RenderHint.Antialiasing)
        workflow_layout.addWidget(self.workflow_view)
        
        details_tabs.addTab(workflow_widget, "ワークフロー")
        
        layout.addWidget(details_tabs)
        
        # アクションボタン
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("インスタンス作成")
        self.complete_button = QPushButton("編集")
        self.cancel_button = QPushButton("複製")
        
        for button in [self.start_button, self.complete_button, self.cancel_button]:
            button.setMinimumWidth(100)
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        self.tabs.addTab(details, "プロセス詳細")

    def init_dashboard_tab(self):
        """ダッシュボードタブの初期化"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # 1. ヘッダー
        header = QLabel("プロセスモニターダッシュボード")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # 2. サマリーカード（横並び）
        summary_layout = QHBoxLayout()
        
        # サマリーカードを追加
        self.active_instances_card = self.create_summary_card("実行中インスタンス", 0, "#2196F3")
        self.completed_instances_card = self.create_summary_card("完了済インスタンス(30日)", 0, "#4CAF50")
        self.overdue_tasks_card = self.create_summary_card("期限切れタスク", 0, "#F44336")
        self.today_tasks_card = self.create_summary_card("今日期限のタスク", 0, "#FF9800")
        
        summary_layout.addWidget(self.active_instances_card)
        summary_layout.addWidget(self.completed_instances_card)
        summary_layout.addWidget(self.overdue_tasks_card)
        summary_layout.addWidget(self.today_tasks_card)
        
        layout.addLayout(summary_layout)
        
        # 3. メインコンテンツエリア（分割）
        main_splitter = QSplitter()
        main_splitter.setOrientation(Qt.Orientation.Horizontal)
        
        # 3.1 実行中プロセスインスタンス
        instance_frame = QFrame()
        instance_layout = QVBoxLayout(instance_frame)
        instance_header = QLabel("実行中のプロセスインスタンス")
        instance_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        instance_layout.addWidget(instance_header)
        
        self.dashboard_instance_table = QTableWidget()
        self.dashboard_instance_table.setColumnCount(5)
        self.dashboard_instance_table.setHorizontalHeaderLabels(["ID", "プロセス名", "ステータス", "進捗", "開始日時"])
        self.dashboard_instance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.dashboard_instance_table.horizontalHeader().setStretchLastSection(True)
        self.dashboard_instance_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        instance_layout.addWidget(self.dashboard_instance_table)
        
        instance_button = QPushButton("すべて表示")
        instance_button.clicked.connect(lambda: self.tabs.setCurrentIndex(3))  # インスタンスタブに移動
        instance_layout.addWidget(instance_button)
        
        main_splitter.addWidget(instance_frame)
        
        # 3.2 最近のアクティビティ
        activity_frame = QFrame()
        activity_layout = QVBoxLayout(activity_frame)
        activity_header = QLabel("最近のアクティビティ")
        activity_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        activity_layout.addWidget(activity_header)
        
        self.dashboard_activity_table = QTableWidget()
        self.dashboard_activity_table.setColumnCount(3)
        self.dashboard_activity_table.setHorizontalHeaderLabels(["時間", "プロセス", "アクション"])
        self.dashboard_activity_table.horizontalHeader().setStretchLastSection(True)
        self.dashboard_activity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        activity_layout.addWidget(self.dashboard_activity_table)
        
        main_splitter.addWidget(activity_frame)
        layout.addWidget(main_splitter)
        
        # 4. 下部エリア（分割）
        bottom_splitter = QSplitter()
        bottom_splitter.setOrientation(Qt.Orientation.Horizontal)
        
        # 4.1 プロセスタイプ別統計
        stats_frame = QFrame()
        stats_layout = QVBoxLayout(stats_frame)
        stats_header = QLabel("プロセスタイプ別統計")
        stats_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        stats_layout.addWidget(stats_header)
        
        # シンプルな統計テーブルを追加
        self.process_stats_table = QTableWidget()
        self.process_stats_table.setColumnCount(3)
        self.process_stats_table.setHorizontalHeaderLabels(["プロセスタイプ", "実行中", "完了済"])
        self.process_stats_table.horizontalHeader().setStretchLastSection(True)
        self.process_stats_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        stats_layout.addWidget(self.process_stats_table)
        
        bottom_splitter.addWidget(stats_frame)
        
        # 4.2 注意が必要なタスク
        urgent_frame = QFrame()
        urgent_layout = QVBoxLayout(urgent_frame)
        urgent_header = QLabel("注意が必要なタスク")
        urgent_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        urgent_layout.addWidget(urgent_header)
        
        self.dashboard_urgent_table = QTableWidget()
        self.dashboard_urgent_table.setColumnCount(4)
        self.dashboard_urgent_table.setHorizontalHeaderLabels(["タスク名", "関連プロセス", "期限", "優先度"])
        self.dashboard_urgent_table.horizontalHeader().setStretchLastSection(True)
        self.dashboard_urgent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        urgent_layout.addWidget(self.dashboard_urgent_table)
        
        bottom_splitter.addWidget(urgent_frame)
        layout.addWidget(bottom_splitter)
        
        # サイズ比率を設定
        main_splitter.setSizes([500, 500])
        bottom_splitter.setSizes([500, 500])
        
        self.tabs.addTab(dashboard, "ダッシュボード")
    
    def create_summary_card(self, title, value, color):
        """サマリーカードを作成"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.Box)
        card.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        card.setMinimumHeight(100)
        
        card_layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white;")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        # 値ラベルを後で更新できるようにメンバーとして保持
        card.value_label = value_label
        
        return card

    def init_process_instance_tab(self):
        """プロセスインスタンスタブの初期化"""
        instances = QWidget()
        layout = QVBoxLayout(instances)
        
        # ヘッダー
        header = QLabel("プロセスインスタンス")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # プロセスインスタンステーブル
        self.instance_table = QTableWidget()
        self.instance_table.setColumnCount(5)
        self.instance_table.setHorizontalHeaderLabels(["インスタンスID", "プロセス名", "ステータス", "開始時間", "終了時間"])
        self.instance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.instance_table.selectionModel().selectionChanged.connect(self.on_instance_selected)
        self.instance_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.instance_table)
        
        # アクションボタン
        button_layout = QHBoxLayout()
        
        self.start_instance_button = QPushButton("開始")
        self.complete_instance_button = QPushButton("完了")
        self.cancel_instance_button = QPushButton("キャンセル")
        
        for button in [self.start_instance_button, self.complete_instance_button, self.cancel_instance_button]:
            button.setMinimumWidth(100)
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        self.tabs.addTab(instances, "プロセスインスタンス")

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
                "タスク管理システムのデータベースにデモデータを追加しますか？\n(注意: これはテスト環境でのみ実行してください)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # データベース接続を確認
                    if not self.db:
                        self.db = get_db_instance()
                        if not self.db.connect():
                            raise Exception("データベースに接続できませんでした")
                    
                    # データベースを初期化
                    if hasattr(self.db, 'initialize_database') and self.db.initialize_database():
                        QMessageBox.information(
                            self,
                            "初期化完了",
                            "タスク管理システムのデータベースにデモデータを追加しました。"
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
            # 既存のデータの再読み込み
            reply = QMessageBox.question(
                self, 
                "データ再読み込み", 
                "タスク管理システムのデータベースからデータを再読み込みしますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # データベース接続を確認
                    if not self.db:
                        self.db = get_db_instance()
                        if not self.db.connect():
                            raise Exception("データベースに接続できませんでした")
                    
                    # データを再読み込み
                    self.load_data()
                    
                    QMessageBox.information(
                        self,
                        "再読み込み完了",
                        "タスク管理システムのデータベースからデータを再読み込みしました。"
                    )
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "再読み込みエラー",
                        f"データベースの再読み込みに失敗しました: {str(e)}"
                    )
    
    def reload_database(self):
        """データベース接続を再試行する"""
        try:
            # データベース接続を閉じる
            if self.db:
                self.db.disconnect()
            
            # 再接続
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taskman.db")
            self.db = get_db_instance()
            
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

    def log_error(self, message):
        """エラーメッセージをログに記録する"""
        logging.error(message)
        print(f"エラー: {message}")

def get_db_instance(db_path=None):
    """データベース接続インスタンスを取得するヘルパー"""
    from process_monitor_db import ProcessMonitorDB
    global _db_instance
    
    if _db_instance is None:
        _db_instance = ProcessMonitorDB()
    
    return _db_instance

# アプリケーション実行のエントリーポイント
if __name__ == "__main__":
    try:
        # アプリケーションの起動
        app = QApplication(sys.argv)
        window = ProcessMonitorApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"アプリケーションの起動中にエラーが発生しました: {e}")
        traceback.print_exc() 
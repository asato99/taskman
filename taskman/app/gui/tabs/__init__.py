"""
タブモジュール - プロセスモニターGUIのタブコンポーネントを提供します
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QTabWidget, QFrame, QSplitter, QPushButton, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

class DashboardTab(QWidget):
    """ダッシュボードタブ - プロセスの概要と最近のアクティビティを表示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # ヘッダー
        header = QLabel("ダッシュボード")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        self.layout.addWidget(header)
        
        # メインスプリッター（上部エリア）
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # プロセスインスタンス一覧
        instance_frame = QFrame()
        instance_layout = QVBoxLayout(instance_frame)
        instance_header = QLabel("実行中のプロセス")
        instance_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        instance_layout.addWidget(instance_header)
        
        self.instance_table = QTableWidget()
        self.instance_table.setColumnCount(5)
        self.instance_table.setHorizontalHeaderLabels(["ID", "プロセス名", "ステータス", "進捗", "開始日時"])
        self.instance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.instance_table.horizontalHeader().setStretchLastSection(True)
        self.instance_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        instance_layout.addWidget(self.instance_table)
        
        instance_button = QPushButton("すべて表示")
        instance_layout.addWidget(instance_button)
        
        main_splitter.addWidget(instance_frame)
        
        # 最近のアクティビティ
        activity_frame = QFrame()
        activity_layout = QVBoxLayout(activity_frame)
        activity_header = QLabel("最近のアクティビティ")
        activity_header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        activity_layout.addWidget(activity_header)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["時間", "プロセス", "アクション"])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        activity_layout.addWidget(self.activity_table)
        
        main_splitter.addWidget(activity_frame)
        self.layout.addWidget(main_splitter)


class ProcessDefinitionTab(QWidget):
    """プロセス定義タブ - プロセス定義の一覧を表示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # ヘッダー
        header = QLabel("プロセス定義")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # プロセス定義テーブル
        self.process_def_table = QTableWidget()
        self.process_def_table.setColumnCount(4)
        self.process_def_table.setHorizontalHeaderLabels(["プロセス名", "バージョン", "ステータス", "タスク数"])
        self.process_def_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_def_table.horizontalHeader().setStretchLastSection(True)
        self.process_def_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.process_def_table)


class ProcessDetailsTab(QWidget):
    """プロセス詳細タブ - 選択されたプロセスの詳細情報を表示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # ヘッダー
        self.detail_header = QLabel("プロセス詳細")
        self.detail_header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(self.detail_header)
        
        # プロセス情報
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Panel)
        info_frame.setFrameShadow(QFrame.Shadow.Raised)
        info_layout = QGridLayout(info_frame)
        
        # グリッドレイアウトの設定
        info_layout.setColumnStretch(0, 0)
        info_layout.setColumnStretch(1, 1)
        info_layout.setHorizontalSpacing(15)
        info_layout.setVerticalSpacing(10)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        labels = ["プロセス名:", "ステータス:", "バージョン:", "作成日:", "説明:"]
        self.info_values = []
        
        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            label.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            info_layout.addWidget(label, i, 0)
            
            value = QLabel()
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setWordWrap(True)
            info_layout.addWidget(value, i, 1)
            self.info_values.append(value)
        
        layout.addWidget(info_frame)
        
        # タスクとワークフローのタブ
        self.details_tabs = QTabWidget()
        layout.addWidget(self.details_tabs)


class ProcessInstanceTab(QWidget):
    """プロセスインスタンスタブ - プロセスインスタンスの一覧と管理"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # ヘッダー
        header = QLabel("プロセスインスタンス")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # プロセスインスタンステーブル
        self.instance_table = QTableWidget()
        self.instance_table.setColumnCount(5)
        self.instance_table.setHorizontalHeaderLabels(["インスタンスID", "プロセス名", "ステータス", "開始時間", "終了時間"])
        self.instance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
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


class ReportTab(QWidget):
    """レポートタブ - プロセスのレポート生成と表示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # ヘッダー
        header = QLabel("レポート")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)


class SettingsTab(QWidget):
    """設定タブ - アプリケーションの設定管理"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # ヘッダー
        header = QLabel("設定")
        header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(header)

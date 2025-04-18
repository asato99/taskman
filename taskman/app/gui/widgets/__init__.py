"""
ウィジェットモジュール - プロセスモニターGUIのカスタムウィジェットを提供します
"""

from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, 
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon


class StatusLabel(QLabel):
    """ステータスを色付きで表示するラベル"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.update_style(text)
    
    def setText(self, text):
        """テキストを設定し、スタイルを更新"""
        super().setText(text)
        self.update_style(text)
    
    def update_style(self, status):
        """ステータスに応じてスタイルを更新"""
        if status in ["進行中", "実行中", "アクティブ"]:
            self.setStyleSheet("background-color: #e6f7ff; color: #0066cc; padding: 3px; border-radius: 3px;")
        elif status in ["完了", "終了"]:
            self.setStyleSheet("background-color: #e6ffe6; color: #009900; padding: 3px; border-radius: 3px;")
        elif status in ["未開始", "ドラフト", "準備中"]:
            self.setStyleSheet("background-color: #f2f2f2; color: #666666; padding: 3px; border-radius: 3px;")
        elif status in ["中止", "キャンセル", "エラー"]:
            self.setStyleSheet("background-color: #ffe6e6; color: #cc0000; padding: 3px; border-radius: 3px;")
        else:
            self.setStyleSheet("background-color: #f2f2f2; color: #000000; padding: 3px; border-radius: 3px;")


class PriorityLabel(QLabel):
    """優先度を色付きで表示するラベル"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.update_style(text)
    
    def setText(self, text):
        """テキストを設定し、スタイルを更新"""
        super().setText(text)
        self.update_style(text)
    
    def update_style(self, priority):
        """優先度に応じてスタイルを更新"""
        if priority in ["高", "緊急"]:
            self.setStyleSheet("background-color: #ffe6e6; color: #cc0000; padding: 3px; border-radius: 3px;")
        elif priority in ["中"]:
            self.setStyleSheet("background-color: #fff7e6; color: #cc7a00; padding: 3px; border-radius: 3px;")
        elif priority in ["低"]:
            self.setStyleSheet("background-color: #e6ffe6; color: #009900; padding: 3px; border-radius: 3px;")
        else:
            self.setStyleSheet("background-color: #f2f2f2; color: #000000; padding: 3px; border-radius: 3px;")


class InfoCard(QFrame):
    """情報カード - タイトルと値を表示するカード"""
    
    def __init__(self, title="", value="", unit="", parent=None):
        super().__init__(parent)
        
        # スタイル設定
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            InfoCard {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        
        # レイアウト
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # タイトル
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.title_label)
        
        # 値
        value_layout = QHBoxLayout()
        value_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.value_label = QLabel(str(value))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        value_layout.addWidget(self.value_label)
        
        if unit:
            self.unit_label = QLabel(unit)
            self.unit_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.unit_label.setStyleSheet("font-size: 14px; color: #666; padding-left: 5px;")
            value_layout.addWidget(self.unit_label)
        
        layout.addLayout(value_layout)
    
    def set_value(self, value):
        """値を更新"""
        self.value_label.setText(str(value))


class ActionButton(QPushButton):
    """アクションボタン - 一貫したスタイルのボタン"""
    
    def __init__(self, text="", icon=None, parent=None):
        super().__init__(text, parent)
        
        # スタイル設定
        self.setMinimumWidth(100)
        self.setMinimumHeight(30)
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(16, 16))
        
        # デフォルトスタイル
        self.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
    
    def set_primary(self):
        """プライマリボタンスタイルを設定"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: 1px solid #0D47A1;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
    
    def set_success(self):
        """成功ボタンスタイルを設定"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #388E3C;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
    
    def set_danger(self):
        """危険ボタンスタイルを設定"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: 1px solid #D32F2F;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)

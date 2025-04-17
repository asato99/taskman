#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
タスク管理システムのメインエントリポイント
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="タスク管理システム")
    parser.add_argument('--gui', action='store_true', help='GUIモードで起動')
    parser.add_argument('command', nargs='?', help='実行するコマンド')
    args, unknown = parser.parse_known_args()
    
    if args.gui:
        try:
            from PyQt6.QtWidgets import QApplication
            from taskman.app.gui import ProcessMonitorApp
            
            app = QApplication(sys.argv[:1])  # コマンドライン引数を除去
            window = ProcessMonitorApp()
            window.show()
            sys.exit(app.exec())
        except ImportError as e:
            print(f"GUIモードのインポートに失敗しました: {e}")
            import traceback
            traceback.print_exc()
            print("\nインポートパスの確認:")
            for path in sys.path:
                print(f" - {path}")
            sys.exit(1)
    else:
        # CLIモード（既存のコード）
        from taskman.cli import app
        app()

if __name__ == "__main__":
    main() 
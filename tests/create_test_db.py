#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
テスト用SQLiteデータベースの作成スクリプト

このスクリプトは、プロセスモニターGUIのテスト用にSQLiteデータベースを作成し、
サンプルデータを挿入します。
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# テスト用データベースのパス
TEST_DB_PATH = "./test_taskman.db"

# データベーススキーマ定義
SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS processes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT '未開始',
        start_date TEXT,
        end_date TEXT,
        owner TEXT,
        workflow_id INTEGER,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT '未着手',
        priority TEXT NOT NULL DEFAULT '中',
        owner TEXT,
        due_date TEXT,
        step TEXT,
        FOREIGN KEY (process_id) REFERENCES processes(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS workflows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        steps TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (process_id) REFERENCES processes(id)
    )
    """
]

# サンプルデータ
WORKFLOWS_DATA = [
    {
        "name": "月次報告プロセス",
        "steps": json.dumps(["データ収集", "データ分析", "レポート作成", "レビュー", "提出"])
    },
    {
        "name": "プロジェクト計画プロセス",
        "steps": json.dumps(["要件定義", "スケジュール作成", "リソース割り当て", "レビュー", "承認"])
    },
    {
        "name": "顧客対応プロセス",
        "steps": json.dumps(["問題特定", "解決策検討", "顧客連絡", "解決策実施", "フォローアップ"])
    }
]

PROCESSES_DATA = [
    {
        "name": "月次報告書作成",
        "status": "進行中",
        "start_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "owner": "田中太郎",
        "workflow_id": 1
    },
    {
        "name": "プロジェクト計画策定",
        "status": "進行中",
        "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "owner": "佐藤花子",
        "workflow_id": 2
    },
    {
        "name": "顧客対応フロー改善",
        "status": "未開始",
        "start_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "owner": "鈴木一郎",
        "workflow_id": 3
    },
    {
        "name": "経費精算",
        "status": "完了",
        "start_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "owner": "高橋雅子",
        "workflow_id": None
    }
]

TASKS_DATA = [
    # 月次報告書作成のタスク
    {
        "process_id": 1,
        "name": "データ収集",
        "status": "完了",
        "priority": "中",
        "owner": "田中太郎",
        "due_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "step": "データ収集"
    },
    {
        "process_id": 1,
        "name": "データ分析",
        "status": "進行中",
        "priority": "高",
        "owner": "田中太郎",
        "due_date": (datetime.now()).strftime("%Y-%m-%d"),
        "step": "データ分析"
    },
    {
        "process_id": 1,
        "name": "レポート作成",
        "status": "未着手",
        "priority": "中",
        "owner": "田中太郎",
        "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "step": "レポート作成"
    },
    
    # プロジェクト計画策定のタスク
    {
        "process_id": 2,
        "name": "要件定義",
        "status": "完了",
        "priority": "高",
        "owner": "佐藤花子",
        "due_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "step": "要件定義"
    },
    {
        "process_id": 2,
        "name": "スケジュール作成",
        "status": "進行中",
        "priority": "中",
        "owner": "佐藤花子",
        "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "step": "スケジュール作成"
    },
    {
        "process_id": 2,
        "name": "リソース割り当て",
        "status": "未着手",
        "priority": "低",
        "owner": "佐藤花子",
        "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "step": "リソース割り当て"
    },
    
    # 顧客対応フロー改善のタスク
    {
        "process_id": 3,
        "name": "現状分析",
        "status": "未着手",
        "priority": "高",
        "owner": "鈴木一郎",
        "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "step": "問題特定"
    },
    {
        "process_id": 3,
        "name": "改善案策定",
        "status": "未着手",
        "priority": "中",
        "owner": "鈴木一郎",
        "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "step": "解決策検討"
    },
    
    # 経費精算のタスク
    {
        "process_id": 4,
        "name": "領収書確認",
        "status": "完了",
        "priority": "中",
        "owner": "高橋雅子",
        "due_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "step": None
    },
    {
        "process_id": 4,
        "name": "経費入力",
        "status": "完了",
        "priority": "高",
        "owner": "高橋雅子",
        "due_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "step": None
    }
]

ACTIVITIES_DATA = [
    {
        "process_id": 1,
        "description": "データ収集が完了しました",
        "timestamp": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "process_id": 1,
        "description": "データ分析を開始しました",
        "timestamp": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "process_id": 2,
        "description": "要件定義が完了しました",
        "timestamp": (datetime.now() - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "process_id": 2,
        "description": "スケジュール作成を開始しました",
        "timestamp": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "process_id": 4,
        "description": "経費精算プロセスが完了しました",
        "timestamp": (datetime.now() - timedelta(hours=20)).strftime("%Y-%m-%d %H:%M:%S")
    }
]


def create_test_database():
    """テスト用データベースを作成"""
    # 既存のテストDBが存在する場合は削除
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        logger.info(f"既存のテストデータベース {TEST_DB_PATH} を削除しました")
    
    # データベース接続を作成
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # スキーマを作成
        for schema in SCHEMA:
            cursor.execute(schema)
        logger.info("データベーススキーマを作成しました")
        
        # ワークフローデータを挿入
        for workflow in WORKFLOWS_DATA:
            cursor.execute(
                "INSERT INTO workflows (name, steps) VALUES (?, ?)",
                (workflow["name"], workflow["steps"])
            )
        logger.info(f"{len(WORKFLOWS_DATA)} 件のワークフローデータを挿入しました")
        
        # プロセスデータを挿入
        for process in PROCESSES_DATA:
            cursor.execute(
                """
                INSERT INTO processes (name, status, start_date, end_date, owner, workflow_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    process["name"],
                    process["status"],
                    process["start_date"],
                    process["end_date"],
                    process["owner"],
                    process["workflow_id"]
                )
            )
        logger.info(f"{len(PROCESSES_DATA)} 件のプロセスデータを挿入しました")
        
        # タスクデータを挿入
        for task in TASKS_DATA:
            cursor.execute(
                """
                INSERT INTO tasks (process_id, name, status, priority, owner, due_date, step)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task["process_id"],
                    task["name"],
                    task["status"],
                    task["priority"],
                    task["owner"],
                    task["due_date"],
                    task["step"]
                )
            )
        logger.info(f"{len(TASKS_DATA)} 件のタスクデータを挿入しました")
        
        # アクティビティデータを挿入
        for activity in ACTIVITIES_DATA:
            cursor.execute(
                """
                INSERT INTO activities (process_id, description, timestamp)
                VALUES (?, ?, ?)
                """,
                (
                    activity["process_id"],
                    activity["description"],
                    activity["timestamp"]
                )
            )
        logger.info(f"{len(ACTIVITIES_DATA)} 件のアクティビティデータを挿入しました")
        
        # 変更をコミット
        conn.commit()
        logger.info(f"テストデータベース {TEST_DB_PATH} を正常に作成しました")
        
    except sqlite3.Error as e:
        logger.error(f"データベース作成エラー: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """メイン関数"""
    create_test_database()
    
    # 作成したデータベースの内容を表示（確認用）
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # テーブル一覧を取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("==== テストデータベースの内容 ====")
        for table in tables:
            table_name = table[0]
            print(f"\n-- {table_name} テーブル --")
            
            # テーブルの内容を取得
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # カラム名を取得
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            
            # カラム名を表示
            print("| " + " | ".join(columns) + " |")
            print("|-" + "-|-".join(["-" * len(col) for col in columns]) + "-|")
            
            # 行データを表示
            for row in rows:
                print("| " + " | ".join(str(val) if val is not None else "NULL" for val in row) + " |")
    
    except sqlite3.Error as e:
        print(f"エラー: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main() 
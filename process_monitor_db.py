#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスモニターGUIのデータベースアクセス層

このモジュールは、プロセスモニターGUIとタスク管理システムの
データベースを連携するためのインターフェースを提供します。
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

# シングルトン用のインスタンス
_db_instance = None

class DatabaseConnection:
    """データベース接続を管理するクラス"""
    
    def __init__(self, db_path):
        """
        初期化
        
        Args:
            db_path: SQLiteデータベースファイルのパス
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """データベースに接続"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            # 日付型とdatetimeの変換を有効化
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.connection.cursor()
            logger.info(f"データベース {self.db_path} に接続しました")
            return True
        except sqlite3.Error as e:
            logger.error(f"データベース接続エラー: {e}")
            return False
    
    def disconnect(self):
        """データベースから切断"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            logger.info("データベースから切断しました")
            return True
        return False
    
    def execute_query(self, query, params=None):
        """
        SQLクエリを実行
        
        Args:
            query: 実行するSQLクエリ
            params: クエリパラメータ (オプション)
            
        Returns:
            クエリ結果
        """
        if not self.connection:
            raise Exception("データベースに接続されていません")
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"クエリ実行エラー: {e}")
            logger.error(f"実行クエリ: {query}")
            logger.error(f"パラメータ: {params}")
            raise
    
    def execute_insert(self, query, params=None):
        """
        INSERT文を実行
        
        Args:
            query: 実行するSQLクエリ
            params: クエリパラメータ (オプション)
            
        Returns:
            新しく挿入された行のID
        """
        if not self.connection:
            raise Exception("データベースに接続されていません")
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error(f"INSERT実行エラー: {e}")
            logger.error(f"実行クエリ: {query}")
            logger.error(f"パラメータ: {params}")
            raise
    
    def execute_update(self, query, params=None):
        """
        UPDATE文を実行
        
        Args:
            query: 実行するSQLクエリ
            params: クエリパラメータ (オプション)
            
        Returns:
            影響を受けた行数
        """
        if not self.connection:
            raise Exception("データベースに接続されていません")
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error(f"UPDATE実行エラー: {e}")
            logger.error(f"実行クエリ: {query}")
            logger.error(f"パラメータ: {params}")
            raise


class ProcessMonitorDB:
    """プロセスモニターのデータベースアクセスクラス"""
    
    def __init__(self, db_path="./taskman.db"):
        """
        初期化
        
        Args:
            db_path: SQLiteデータベースファイルのパス
        """
        self.db = DatabaseConnection(db_path)
    
    def connect(self):
        """データベースに接続"""
        return self.db.connect()
    
    def disconnect(self):
        """データベースから切断"""
        return self.db.disconnect()
    
    def initialize_database(self):
        """
        データベースを初期化し、必要なテーブルを作成します
        
        Returns:
            bool: 初期化が成功したかどうか
        """
        try:
            # プロセステーブルの作成
            self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT '未開始',
                start_date TEXT,
                end_date TEXT,
                owner TEXT,
                description TEXT
            )
            """)
            
            # タスクテーブルの作成
            self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_id INTEGER,
                name TEXT NOT NULL,
                status TEXT DEFAULT '未着手',
                priority TEXT DEFAULT '中',
                owner TEXT,
                description TEXT,
                FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
            )
            """)
            
            # アクティビティテーブルの作成
            self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_id INTEGER,
                description TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user TEXT,
                FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
            )
            """)
            
            # ワークフローテーブルの作成
            self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
            """)
            
            # ワークフローステップテーブルの作成
            self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER,
                name TEXT NOT NULL,
                sequence INTEGER,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
            )
            """)
            
            # プロセスワークフロー関連付けテーブル
            self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS process_workflows (
                process_id INTEGER,
                workflow_id INTEGER,
                PRIMARY KEY (process_id, workflow_id),
                FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
            )
            """)
            
            logger.info("データベーステーブルが作成されました")
            
            # サンプルデータの追加
            self._add_sample_data()
            
            return True
        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}")
            return False
    
    def _add_sample_data(self):
        """サンプルデータを追加"""
        # サンプルプロセスの追加
        process_ids = []
        sample_processes = [
            ("月次報告書作成", "進行中", datetime.now() - timedelta(days=2), datetime.now() + timedelta(days=1), "田中太郎"),
            ("プロジェクト計画策定", "進行中", datetime.now() - timedelta(days=1), datetime.now() + timedelta(days=5), "佐藤花子"),
            ("顧客対応フロー改善", "未開始", datetime.now() + timedelta(days=1), datetime.now() + timedelta(days=7), "鈴木一郎"),
            ("経費精算", "完了", datetime.now() - timedelta(days=5), datetime.now() - timedelta(days=1), "高橋雅子")
        ]
        
        for process in sample_processes:
            query = """
            INSERT INTO processes (name, status, start_date, end_date, owner)
            VALUES (?, ?, ?, ?, ?)
            """
            process_id = self.db.execute_insert(query, process)
            process_ids.append(process_id)
        
        # サンプルタスクの追加
        sample_tasks = [
            (process_ids[0], "データ収集", "完了", "中", "田中太郎"),
            (process_ids[0], "データ分析", "進行中", "高", "田中太郎"),
            (process_ids[0], "レポート作成", "未着手", "中", "田中太郎"),
            (process_ids[1], "要件定義", "完了", "高", "佐藤花子"),
            (process_ids[1], "スケジュール作成", "進行中", "中", "佐藤花子"),
            (process_ids[1], "リソース割り当て", "未着手", "低", "佐藤花子")
        ]
        
        for task in sample_tasks:
            query = """
            INSERT INTO tasks (process_id, name, status, priority, owner)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute_insert(query, task)
        
        # サンプルワークフローの追加
        workflow_ids = []
        sample_workflows = [
            "月次報告プロセス",
            "プロジェクト計画プロセス"
        ]
        
        for workflow in sample_workflows:
            query = """
            INSERT INTO workflows (name)
            VALUES (?)
            """
            workflow_id = self.db.execute_insert(query, (workflow,))
            workflow_ids.append(workflow_id)
        
        # サンプルワークフローステップの追加
        workflow_steps = [
            (workflow_ids[0], "データ収集", 1),
            (workflow_ids[0], "データ分析", 2),
            (workflow_ids[0], "レポート作成", 3),
            (workflow_ids[0], "レビュー", 4),
            (workflow_ids[0], "提出", 5),
            (workflow_ids[1], "要件定義", 1),
            (workflow_ids[1], "スケジュール作成", 2),
            (workflow_ids[1], "リソース割り当て", 3),
            (workflow_ids[1], "レビュー", 4),
            (workflow_ids[1], "承認", 5)
        ]
        
        for step in workflow_steps:
            query = """
            INSERT INTO workflow_steps (workflow_id, name, sequence)
            VALUES (?, ?, ?)
            """
            self.db.execute_insert(query, step)
        
        # ワークフローとプロセスの関連付け
        process_workflows = [
            (process_ids[0], workflow_ids[0]),  # 月次報告書作成 → 月次報告プロセス
            (process_ids[1], workflow_ids[1])   # プロジェクト計画策定 → プロジェクト計画プロセス
        ]
        
        for pw in process_workflows:
            query = """
            INSERT INTO process_workflows (process_id, workflow_id)
            VALUES (?, ?)
            """
            self.db.execute_insert(query, pw)
        
        # サンプルアクティビティの追加
        sample_activities = [
            (process_ids[0], "データ収集が完了しました", datetime.now() - timedelta(hours=5), "システム"),
            (process_ids[0], "データ分析を開始しました", datetime.now() - timedelta(hours=4), "田中太郎"),
            (process_ids[1], "要件定義が完了しました", datetime.now() - timedelta(hours=7), "システム"),
            (process_ids[1], "スケジュール作成を開始しました", datetime.now() - timedelta(hours=3), "佐藤花子")
        ]
        
        for activity in sample_activities:
            query = """
            INSERT INTO activities (process_id, description, timestamp, user)
            VALUES (?, ?, ?, ?)
            """
            self.db.execute_insert(query, activity)
        
        logger.info("サンプルデータが追加されました")
    
    def get_processes(self):
        """
        プロセス一覧を取得
        
        Returns:
            プロセスのリスト（辞書形式）
        """
        query = """
        SELECT 
            p.id, 
            p.name, 
            p.status, 
            IFNULL(
                (SELECT COUNT(*) FROM tasks t WHERE t.process_id = p.id AND t.status = '完了') * 100.0 / 
                NULLIF((SELECT COUNT(*) FROM tasks t WHERE t.process_id = p.id), 0),
                0
            ) as progress,
            p.start_date, 
            p.end_date, 
            p.owner
        FROM processes p
        ORDER BY p.status != '完了', p.end_date
        """
        
        rows = self.db.execute_query(query)
        processes = []
        
        for row in rows:
            process = {
                "id": row[0],
                "name": row[1],
                "status": row[2],
                "progress": round(row[3]),  # 進捗率は四捨五入して整数に
                "start_date": self._parse_date(row[4]),
                "end_date": self._parse_date(row[5]),
                "owner": row[6]
            }
            processes.append(process)
        
        return processes
    
    def get_process_by_id(self, process_id):
        """
        指定したIDのプロセスを取得
        
        Args:
            process_id: プロセスID
            
        Returns:
            プロセス情報（辞書形式）
        """
        query = """
        SELECT 
            p.id, 
            p.name, 
            p.status, 
            IFNULL(
                (SELECT COUNT(*) FROM tasks t WHERE t.process_id = p.id AND t.status = '完了') * 100.0 / 
                NULLIF((SELECT COUNT(*) FROM tasks t WHERE t.process_id = p.id), 0),
                0
            ) as progress,
            p.start_date, 
            p.end_date, 
            p.owner
        FROM processes p
        WHERE p.id = ?
        """
        
        rows = self.db.execute_query(query, (process_id,))
        
        if not rows:
            return None
        
        row = rows[0]
        process = {
            "id": row[0],
            "name": row[1],
            "status": row[2],
            "progress": round(row[3]),  # 進捗率は四捨五入して整数に
            "start_date": self._parse_date(row[4]),
            "end_date": self._parse_date(row[5]),
            "owner": row[6]
        }
        
        return process
    
    def get_tasks_by_process_id(self, process_id):
        """
        指定したプロセスIDに関連するタスクを取得
        
        Args:
            process_id: プロセスID
            
        Returns:
            タスクのリスト（辞書形式）
        """
        query = """
        SELECT 
            id, 
            process_id, 
            name, 
            status, 
            priority,
            owner,
            description
        FROM tasks
        WHERE process_id = ?
        ORDER BY id
        """
        
        rows = self.db.execute_query(query, (process_id,))
        tasks = []
        
        for row in rows:
            task = {
                "id": row[0],
                "process_id": row[1],
                "name": row[2],
                "status": row[3],
                "priority": row[4],
                "owner": row[5],
                "description": row[6]
            }
            tasks.append(task)
        
        return tasks
    
    def get_workflow_steps(self, process_id):
        """
        指定したプロセスIDに関連するワークフローステップを取得
        
        Args:
            process_id: プロセスID
            
        Returns:
            ワークフローステップのリスト（辞書形式）
        """
        query = """
        SELECT 
            ws.id,
            ws.workflow_id,
            ws.name,
            ws.sequence,
            (SELECT status FROM tasks t WHERE t.process_id = ? AND t.name = ws.name LIMIT 1) as status
        FROM workflow_steps ws
        JOIN process_workflows pw ON ws.workflow_id = pw.workflow_id
        WHERE pw.process_id = ?
        ORDER BY ws.sequence
        """
        
        rows = self.db.execute_query(query, (process_id, process_id))
        steps = []
        
        for row in rows:
            step = {
                "id": row[0],
                "workflow_id": row[1],
                "name": row[2],
                "sequence": row[3],
                "status": row[4] if row[4] else "未着手"
            }
            steps.append(step)
        
        return steps
    
    def get_recent_activities(self, limit=10):
        """
        最近のアクティビティを取得
        
        Args:
            limit: 取得する件数
            
        Returns:
            アクティビティのリスト（辞書形式）
        """
        query = """
        SELECT 
            a.id,
            a.process_id,
            p.name as process_name,
            a.description,
            a.timestamp,
            a.user
        FROM activities a
        LEFT JOIN processes p ON a.process_id = p.id
        ORDER BY a.timestamp DESC
        LIMIT ?
        """
        
        rows = self.db.execute_query(query, (limit,))
        activities = []
        
        for row in rows:
            activity = {
                "id": row[0],
                "process_id": row[1],
                "process_name": row[2],
                "description": row[3],
                "timestamp": self._parse_date(row[4]),
                "user": row[5]
            }
            activities.append(activity)
        
        return activities
    
    def _parse_date(self, date_str):
        """
        日付文字列をdatetimeオブジェクトに変換
        
        Args:
            date_str: 日付文字列
            
        Returns:
            datetimeオブジェクトまたはNone
        """
        if not date_str:
            return None
            
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return date_str  # 変換できない場合は元の文字列を返す


def get_db_instance(db_path="./taskman.db"):
    """
    データベースインスタンスを取得（シングルトンパターン）
    
    Args:
        db_path: データベースファイルのパス
        
    Returns:
        ProcessMonitorDBのインスタンス
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = ProcessMonitorDB(db_path)
    
    return _db_instance


if __name__ == "__main__":
    # モジュールのテスト用コード
    db = get_db_instance()
    
    try:
        db.connect()
        
        print("プロセス一覧:")
        processes = db.get_processes()
        for process in processes:
            print(f"  {process['id']}: {process['name']} ({process['status']}) - 進捗: {process['progress']}%")
        
        if processes:
            process_id = processes[0]["id"]
            print(f"\nプロセス {process_id} のタスク一覧:")
            tasks = db.get_tasks_by_process_id(process_id)
            for task in tasks:
                print(f"  {task['id']}: {task['name']} ({task['status']}) - 優先度: {task['priority']}")
            
            print(f"\nプロセス {process_id} のワークフローステップ:")
            steps = db.get_workflow_steps(process_id)
            for step in steps:
                print(f"  {step['order']}: {step['name']} ({step['status']})")
        
        print("\n最近のアクティビティ:")
        activities = db.get_recent_activities(5)
        for activity in activities:
            timestamp = activity["timestamp"].strftime("%Y-%m-%d %H:%M") if activity["timestamp"] else "不明"
            print(f"  {timestamp} - {activity['process_name']}: {activity['description']}")
    
    finally:
        db.disconnect() 
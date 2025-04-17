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
import logging
from datetime import datetime, timedelta

# SQLAlchemyをインポート
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# タスク管理システムの設定をインポート
try:
    # タスク管理システムのパスを追加
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from taskman.config.database import db_settings
    from taskman.database.connection import engine, SessionLocal
    logger.info("タスク管理システムの設定とデータベース接続をインポートしました")
    # タスク管理システムの既存のエンジンとセッションを使用
    use_existing_connection = True
except ImportError as e:
    logger.warning(f"タスク管理システムの設定をインポートできませんでした: {e}")
    # デフォルトの設定
    from collections import namedtuple
    DatabaseSettings = namedtuple('DatabaseSettings', ['host', 'port', 'user', 'password', 'database'])
    db_settings = DatabaseSettings(
        host="localhost",
        port=3306,
        user="kazuasato",
        password="password",
        database="taskman_db"
    )
    # 独自のエンジンとセッションを作成
    DATABASE_URL = f"mysql+pymysql://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.database}"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    use_existing_connection = False

# シングルトン用のインスタンス
_db_instance = None

class ProcessMonitorDB:
    """プロセスモニターのデータベースアクセスクラス"""
    
    def __init__(self, db_config=None):
        """
        初期化
        
        Args:
            db_config: データベース設定（host, port, user, password, database）
        """
        self.db_config = db_config
        self.session = None
        self.connected = False
    
    def connect(self):
        """データベースに接続"""
        try:
            self.session = SessionLocal()
            self.connected = True
            logger.info(f"データベース {db_settings.database} に接続しました (ホスト: {db_settings.host})")
            return True
        except Exception as e:
            logger.error(f"データベース接続エラー: {e}")
            return False
    
    def disconnect(self):
        """データベースから切断"""
        if self.session:
            self.session.close()
            self.session = None
            self.connected = False
            logger.info("データベースから切断しました")
            return True
        return False
    
    def get_processes(self):
        """
        プロセス一覧を取得
        
        Returns:
            プロセスのリスト（辞書形式）
        """
        if not self.connected:
            raise Exception("データベースに接続されていません")
            
        query = text("""
        SELECT 
            p.id as id, 
            p.name as name, 
            p.status, 
            IFNULL(
                (SELECT COUNT(*) FROM task t WHERE t.process_id = p.id AND t.status = '完了') * 100.0 / 
                NULLIF((SELECT COUNT(*) FROM task t WHERE t.process_id = p.id), 0),
                0
            ) as progress,
            p.created_at as start_date, 
            p.updated_at as end_date, 
            NULL as owner
        FROM process p
        ORDER BY p.status != 'アクティブ', p.created_at DESC
        """)
        
        result = self.session.execute(query)
        processes = []
        
        for row in result:
            # SQLAlchemyの行をディクショナリに変換
            process = dict(row._mapping)
            # 進捗率を整数に
            if 'progress' in process:
                process['progress'] = round(float(process['progress']))
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
        if not self.connected:
            raise Exception("データベースに接続されていません")
            
        query = text("""
        SELECT 
            p.id as id, 
            p.name as name, 
            p.status, 
            IFNULL(
                (SELECT COUNT(*) FROM task t WHERE t.process_id = p.id AND t.status = '完了') * 100.0 / 
                NULLIF((SELECT COUNT(*) FROM task t WHERE t.process_id = p.id), 0),
                0
            ) as progress,
            p.created_at as start_date, 
            p.updated_at as end_date, 
            NULL as owner
        FROM process p
        WHERE p.id = :process_id
        """)
        
        result = self.session.execute(query, {"process_id": process_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        # SQLAlchemyの行をディクショナリに変換
        process = dict(row._mapping)
        # 進捗率を整数に
        if 'progress' in process:
            process['progress'] = round(float(process['progress']))
        
        return process
    
    def get_tasks_by_process_id(self, process_id):
        """
        指定したプロセスIDに関連するタスクを取得
        
        Args:
            process_id: プロセスID
            
        Returns:
            タスクのリスト（辞書形式）
        """
        if not self.connected:
            raise Exception("データベースに接続されていません")
            
        query = text("""
        SELECT 
            t.id as id, 
            t.process_id, 
            t.name as name, 
            t.status, 
            t.priority,
            t.assigned_to as owner,
            t.description
        FROM task t
        WHERE t.process_id = :process_id
        ORDER BY t.id
        """)
        
        result = self.session.execute(query, {"process_id": process_id})
        tasks = []
        
        for row in result:
            task = dict(row._mapping)
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
        if not self.connected:
            raise Exception("データベースに接続されていません")
            
        # ワークフロー情報の取得
        query = text("""
        SELECT 
            w.id,
            w.from_task_id,
            w.to_task_id,
            w.condition_type,
            w.sequence_number
        FROM workflow w
        WHERE w.process_id = :process_id
        ORDER BY w.sequence_number
        """)
        
        result = self.session.execute(query, {"process_id": process_id})
        workflows = []
        
        for row in result:
            workflow = dict(row._mapping)
            # タスク情報の取得
            start_task_query = text("""
            SELECT name FROM task WHERE id = :task_id
            """)
            start_task_result = self.session.execute(start_task_query, {"task_id": workflow['from_task_id']})
            start_task_row = start_task_result.fetchone()
            
            end_task_query = text("""
            SELECT name FROM task WHERE id = :task_id
            """)
            end_task_result = self.session.execute(end_task_query, {"task_id": workflow['to_task_id']})
            end_task_row = end_task_result.fetchone()
            
            # ワークフロー情報の構築
            step = {
                "id": workflow['id'],
                "workflow_id": workflow['id'],
                "name": f"{start_task_row[0] if start_task_row else 'スタート'} → {end_task_row[0] if end_task_row else 'エンド'}",
                "sequence": workflow['sequence_number'],
                "status": "未着手"  # ステータスはタスクの状態から計算する必要がある
            }
            workflows.append(step)
        
        return workflows
    
    def get_recent_activities(self, limit=10):
        """
        最近のアクティビティを取得
        
        Args:
            limit: 取得する件数
            
        Returns:
            アクティビティのリスト（辞書形式）
        """
        if not self.connected:
            raise Exception("データベースに接続されていません")
        
        # アクティビティテーブルがない場合は、タスクの更新履歴などから構築
        query = text("""
        SELECT 
            t.id as id,
            t.process_id,
            p.name as process_name,
            CONCAT(t.name, 'が', t.status, 'になりました') as description,
            t.updated_at as timestamp,
            t.assigned_to as user
        FROM task t
        JOIN process p ON t.process_id = p.id
        ORDER BY t.updated_at DESC
        LIMIT :limit
        """)
        
        result = self.session.execute(query, {"limit": limit})
        activities = []
        
        for row in result:
            activity = dict(row._mapping)
            activities.append(activity)
        
        return activities
    
    def get_process_instances(self, filters=None):
        """
        プロセスインスタンス一覧を取得
        
        Args:
            filters: フィルタリング条件（process_id, status, created_by）
            
        Returns:
            プロセスインスタンスのリスト（辞書形式）
        """
        if not self.connected:
            raise Exception("データベースに接続されていません")
            
        query = text("""
        SELECT 
            pi.id, 
            p.name as process_name,
            p.id as process_id,
            pi.status,
            pi.started_at,
            pi.completed_at,
            pi.created_by,
            (SELECT COUNT(*) FROM task_instance ti WHERE ti.process_instance_id = pi.id AND ti.status = '完了') * 100.0 / 
            NULLIF((SELECT COUNT(*) FROM task_instance ti WHERE ti.process_instance_id = pi.id), 0) as progress
        FROM process_instance pi
        JOIN process p ON pi.process_id = p.id
        WHERE 1=1
        """)
        
        # フィルター条件の追加
        params = {}
        if filters:
            if 'process_id' in filters and filters['process_id']:
                query = text(str(query) + " AND pi.process_id = :process_id")
                params['process_id'] = filters['process_id']
            if 'status' in filters and filters['status']:
                query = text(str(query) + " AND pi.status = :status")
                params['status'] = filters['status']
            if 'created_by' in filters and filters['created_by']:
                query = text(str(query) + " AND pi.created_by = :created_by")
                params['created_by'] = filters['created_by']
        
        query = text(str(query) + " ORDER BY pi.started_at DESC")
        
        result = self.session.execute(query, params)
        instances = []
        
        for row in result:
            instance = dict(row._mapping)
            if 'progress' in instance and instance['progress'] is not None:
                instance['progress'] = round(float(instance['progress']))
            else:
                instance['progress'] = 0
            instances.append(instance)
        
        return instances
    
    def get_process_instance_by_id(self, instance_id):
        """
        指定したIDのプロセスインスタンスを取得
        
        Args:
            instance_id: プロセスインスタンスID
            
        Returns:
            プロセスインスタンス情報（辞書形式）
        """
        if not self.connected:
            raise Exception("データベースに接続されていません")
            
        query = text("""
        SELECT 
            pi.id, 
            p.name as process_name,
            p.id as process_id,
            pi.status,
            pi.started_at,
            pi.completed_at,
            pi.created_by,
            (SELECT COUNT(*) FROM task_instance ti WHERE ti.process_instance_id = pi.id AND ti.status = '完了') * 100.0 / 
            NULLIF((SELECT COUNT(*) FROM task_instance ti WHERE ti.process_instance_id = pi.id), 0) as progress
        FROM process_instance pi
        JOIN process p ON pi.process_id = p.id
        WHERE pi.id = :instance_id
        """)
        
        result = self.session.execute(query, {"instance_id": instance_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        instance = dict(row._mapping)
        if 'progress' in instance and instance['progress'] is not None:
            instance['progress'] = round(float(instance['progress']))
        else:
            instance['progress'] = 0
        
        return instance
    
    def get_task_instances_by_process_instance_id(self, instance_id):
        """
        指定したプロセスインスタンスIDに関連するタスクインスタンスを取得
        
        Args:
            instance_id: プロセスインスタンスID
            
        Returns:
            タスクインスタンスのリスト（辞書形式）
        """
        if not self.connected:
            raise Exception("データベースに接続されていません")
            
        query = text("""
        SELECT 
            ti.id, 
            ti.process_instance_id,
            t.name,
            ti.status,
            ti.assigned_to,
            ti.started_at,
            ti.completed_at,
            t.priority
        FROM task_instance ti
        JOIN task t ON ti.task_id = t.id
        WHERE ti.process_instance_id = :instance_id
        ORDER BY ti.id
        """)
        
        result = self.session.execute(query, {"instance_id": instance_id})
        task_instances = []
        
        for row in result:
            task_instance = dict(row._mapping)
            task_instances.append(task_instance)
        
        return task_instances
        
    def get_dashboard_summary(self):
        """ダッシュボード用の概要データを取得"""
        try:
            summary = {}
            
            # SQLAlchemyのSessionを使って結果を取得する
            # アクティブなプロセスインスタンス数
            query = text("""
                SELECT COUNT(*) as active_count
                FROM process_instance
                WHERE status != '完了'
            """)
            result = self.session.execute(query).fetchone()
            summary['active_instances_count'] = result[0] if result else 0
            
            # 完了したプロセスインスタンス数
            query = text("""
                SELECT COUNT(*) as completed_count
                FROM process_instance
                WHERE status = '完了'
            """)
            result = self.session.execute(query).fetchone()
            summary['completed_instances_count'] = result[0] if result else 0
            
            # 期限切れタスク数
            query = text("""
                SELECT COUNT(*) as overdue_count
                FROM task_instance ti
                WHERE ti.status != '完了' AND ti.created_at < CURRENT_DATE()
            """)
            result = self.session.execute(query).fetchone()
            summary['overdue_tasks_count'] = result[0] if result else 0
            
            # 今日が期限のタスク数
            query = text("""
                SELECT COUNT(*) as today_count
                FROM task_instance ti
                WHERE ti.status != '完了' AND DATE(ti.created_at) = CURRENT_DATE()
            """)
            result = self.session.execute(query).fetchone()
            summary['today_tasks_count'] = result[0] if result else 0
            
            # アクティブなプロセスインスタンス一覧
            query = text("""
                SELECT 
                    pi.id, 
                    p.name as process_name,
                    pi.status,
                    pi.started_at as start_time, 
                    (SELECT COUNT(*) FROM task_instance ti WHERE ti.process_instance_id = pi.id) as total_tasks,
                    (SELECT COUNT(*) FROM task_instance ti WHERE ti.process_instance_id = pi.id AND ti.status = '完了') as completed_tasks
                FROM process_instance pi
                JOIN process p ON pi.process_id = p.id
                WHERE pi.status != '完了'
                ORDER BY pi.started_at DESC
                LIMIT 10
            """)
            
            result = self.session.execute(query)
            active_instances = []
            for row in result:
                row_dict = dict(row._mapping)
                total_tasks = row_dict.get('total_tasks') or 1  # 0除算を防ぐ
                completed_tasks = row_dict.get('completed_tasks') or 0
                progress = int((completed_tasks / total_tasks) * 100)
                
                active_instances.append({
                    'id': row_dict.get('id'),
                    'process_name': row_dict.get('process_name'),
                    'status': row_dict.get('status'),
                    'started_at': row_dict.get('start_time'),
                    'progress': progress
                })
            summary['active_instances'] = active_instances
            
            # 最近のアクティビティ
            query = text("""
                SELECT 
                    ti.updated_at as last_updated, 
                    p.name as process_name, 
                    t.name as task_name, 
                    ti.status
                FROM task_instance ti
                JOIN process_instance pi ON ti.process_instance_id = pi.id
                JOIN process p ON pi.process_id = p.id
                JOIN task t ON ti.task_id = t.id
                ORDER BY ti.updated_at DESC
                LIMIT 15
            """)
            result = self.session.execute(query)
            activities = []
            for row in result:
                row_dict = dict(row._mapping)
                activities.append({
                    'timestamp': row_dict.get('last_updated'),
                    'process_name': row_dict.get('process_name'),
                    'task_name': row_dict.get('task_name'),
                    'description': f"タスク「{row_dict.get('task_name')}」のステータスが「{row_dict.get('status')}」に変更されました"
                })
            summary['activities'] = activities
            
            # 緊急タスク一覧
            query = text("""
                SELECT 
                    t.name as task_name, 
                    p.name as process_name, 
                    ti.created_at as deadline, 
                    t.priority
                FROM task_instance ti
                JOIN task t ON ti.task_id = t.id
                JOIN process_instance pi ON ti.process_instance_id = pi.id
                JOIN process p ON pi.process_id = p.id
                WHERE ti.status != '完了'
                ORDER BY 
                    CASE 
                        WHEN t.priority = '緊急' THEN 1
                        WHEN t.priority = '高' THEN 2
                        WHEN t.priority = '中' THEN 3
                        WHEN t.priority = '低' THEN 4
                        ELSE 5
                    END,
                    ti.created_at ASC
                LIMIT 10
            """)
            result = self.session.execute(query)
            urgent_tasks = []
            for row in result:
                row_dict = dict(row._mapping)
                urgent_tasks.append({
                    'task_name': row_dict.get('task_name'),
                    'process_name': row_dict.get('process_name'),
                    'deadline': row_dict.get('deadline'),
                    'priority': row_dict.get('priority')
                })
            summary['urgent_tasks'] = urgent_tasks
            
            # プロセスタイプ統計
            query = text("""
                SELECT 
                    p.name as process_type,
                    COUNT(CASE WHEN pi.status != '完了' THEN 1 ELSE NULL END) as active_count,
                    COUNT(CASE WHEN pi.status = '完了' THEN 1 ELSE NULL END) as completed_count
                FROM process_instance pi
                JOIN process p ON pi.process_id = p.id
                GROUP BY p.name
                ORDER BY active_count DESC
            """)
            result = self.session.execute(query)
            process_stats = []
            for row in result:
                row_dict = dict(row._mapping)
                process_stats.append({
                    'process_type': row_dict.get('process_type', '未分類'),
                    'active_count': row_dict.get('active_count', 0),
                    'completed_count': row_dict.get('completed_count', 0)
                })
            summary['process_stats'] = process_stats
            
            return summary
            
        except Exception as e:
            logger.error(f"ダッシュボードデータ取得エラー: {str(e)}")
            return None

    def get_workflow_for_process(self, process_id):
        """
        プロセスIDに基づくワークフローデータを取得する
        
        Args:
            process_id: プロセスID
            
        Returns:
            ワークフローデータを含む辞書
        """
        try:
            # プロセスの基本情報を取得
            query = text("""
                SELECT id, name, description, version, status
                FROM process
                WHERE id = :process_id
            """)
            result = self.session.execute(query, {"process_id": process_id}).fetchone()
            
            if not result:
                return None
            
            process_row = dict(result._mapping)
            
            # プロセスに関連するタスクを取得
            query = text("""
                SELECT id, name, description, status, assigned_to as assignee, priority
                FROM task
                WHERE process_id = :process_id
                ORDER BY id
            """)
            
            result = self.session.execute(query, {"process_id": process_id})
            
            tasks = []
            task_ids = []
            
            for i, row in enumerate(result):
                row_dict = dict(row._mapping)
                # タスクの位置情報を自動生成
                pos_x = i * 200
                pos_y = 0
                
                tasks.append({
                    'id': row_dict.get('id'),
                    'name': row_dict.get('name'),
                    'description': row_dict.get('description'),
                    'status': row_dict.get('status'),
                    'assignee': row_dict.get('assignee'),
                    'priority': row_dict.get('priority'),
                    'position_x': pos_x,
                    'position_y': pos_y
                })
                task_ids.append(row_dict.get('id'))
            
            # タスク間の遷移を取得（今はダミーデータ）
            transitions = []
            
            # タスクが複数ある場合、単純な順序で遷移を作成
            for i in range(len(task_ids) - 1):
                transitions.append({
                    'from_task_id': task_ids[i],
                    'to_task_id': task_ids[i + 1],
                    'condition': ''
                })
            
            workflow_data = {
                'process_id': process_row.get('id'),
                'process_name': process_row.get('name'),
                'tasks': tasks,
                'transitions': transitions
            }
            
            return workflow_data
            
        except Exception as e:
            logger.error(f"ワークフローデータ取得エラー (プロセスID: {process_id}): {str(e)}")
            return None

def get_db_instance(db_config=None):
    """
    データベースインスタンスを取得（シングルトンパターン）
    
    Args:
        db_config: データベース設定（host, port, user, password, database）
        
    Returns:
        ProcessMonitorDBのインスタンス
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = ProcessMonitorDB(db_config)
    
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
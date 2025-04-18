#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロセスデータベースのダミー実装
実際の機能はmonitor_dbに依存します
"""

import logging
from taskman.app.db.monitor_db import ProcessMonitorDB, get_db_instance

logger = logging.getLogger(__name__)

class ProcessDatabase:
    """
    ProcessDatabaseクラス - ProcessMonitorDBとの互換性を提供
    """
    
    def __init__(self):
        """
        初期化: 実際の処理はProcessMonitorDBに委譲
        """
        self.db = get_db_instance()
        self.db.connect()
        logger.info("ProcessDatabaseを初期化しました")
    
    def get_running_processes(self):
        """実行中のプロセスを取得"""
        return self.db.get_processes()
    
    def get_process_definitions(self):
        """プロセス定義を取得"""
        return self.db.get_processes()
    
    # 他の必要なメソッドも同様に実装
    def __getattr__(self, name):
        """未実装メソッドはProcessMonitorDBに転送"""
        return getattr(self.db, name)
    
    def close(self):
        """データベース接続を閉じる"""
        if hasattr(self, 'db') and self.db:
            self.db.disconnect()
    
    def get_process_id_by_instance(self, instance_id):
        """
        インスタンスIDからプロセスIDを取得
        
        Args:
            instance_id: インスタンスID
            
        Returns:
            プロセスID
        """
        try:
            # インスタンスの情報を取得
            instance = self.db.get_process_instance_by_id(instance_id)
            if instance and 'process_id' in instance:
                return instance['process_id']
            return None
        except Exception as e:
            logging.getLogger(__name__).error(f"インスタンスからプロセスIDを取得中にエラー: {e}")
            return None
    
    def get_process_details(self, process_id):
        """
        プロセスの詳細情報を取得
        
        Args:
            process_id: プロセスID
            
        Returns:
            プロセスの詳細情報
        """
        process = self.db.get_process_by_id(process_id)
        # 必要に応じて追加情報を設定
        if process:
            process['creation_date'] = process.get('start_date', '')
            process['version'] = process.get('version', '1.0')
            process['description'] = process.get('description', 'プロセスの詳細情報')
        return process
    
    def get_process_id_by_name_version(self, name, version):
        """
        プロセス名とバージョンからIDを取得
        
        Args:
            name: プロセス名
            version: バージョン
            
        Returns:
            プロセスID
        """
        # プロセス定義を取得して名前とバージョンで検索
        processes = self.db.get_processes()
        for process in processes:
            if (process.get('name', '') == name and 
                process.get('version', '') == version):
                return process.get('id')
        return None
        
    def __del__(self):
        """デストラクタ: データベース接続を閉じる"""
        if hasattr(self, 'db') and self.db:
            self.db.disconnect() 
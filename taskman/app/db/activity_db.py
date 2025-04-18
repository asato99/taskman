#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
アクティビティデータベースのダミー実装
実際の機能はmonitor_dbに依存します
"""

import logging
from datetime import datetime, timedelta
from taskman.app.db.monitor_db import ProcessMonitorDB, get_db_instance

logger = logging.getLogger(__name__)

class ActivityDatabase:
    """
    ActivityDatabaseクラス - ProcessMonitorDBとの互換性を提供
    """
    
    def __init__(self):
        """
        初期化: 実際の処理はProcessMonitorDBに委譲
        """
        self.db = get_db_instance()
        self.db.connect()
        logger.info("ActivityDatabaseを初期化しました")
    
    def get_recent_activities(self, limit=10):
        """最近のアクティビティを取得"""
        return self.db.get_recent_activities(limit)
    
    # 他の必要なメソッドも同様に実装
    def __getattr__(self, name):
        """未実装メソッドはProcessMonitorDBに転送"""
        return getattr(self.db, name)
    
    def close(self):
        """データベース接続を閉じる"""
        if hasattr(self, 'db') and self.db:
            self.db.disconnect()
        
    def __del__(self):
        """デストラクタ: データベース接続を閉じる"""
        if hasattr(self, 'db') and self.db:
            self.db.disconnect() 
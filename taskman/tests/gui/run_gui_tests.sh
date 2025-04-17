#!/bin/bash

# GUIテスト実行スクリプト

# 環境変数の設定
export PYTHONPATH=$(pwd)
export TASKMAN_TEST_MODE=1
export QT_QPA_PLATFORM=offscreen  # ヘッドレス環境でのテスト用

# テストの実行
echo "GUIテストを実行します..."
cd taskman
python -m unittest discover -s tests/gui -p "test_*.py" -v

# 終了ステータスの確認
if [ $? -eq 0 ]; then
    echo "GUIテスト成功！"
    exit 0
else
    echo "GUIテスト失敗。"
    exit 1
fi 
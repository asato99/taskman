#!/bin/bash

# GUIテスト実行用のスクリプト
BASE_DIR=$(pwd)
TEST_DIR="${BASE_DIR}/tests/gui"

# ヘッドレステスト用の環境変数設定
export QT_QPA_PLATFORM=offscreen

# ヘルプメッセージ
show_help() {
    echo "使用方法: bash run_gui_tests.sh [オプション]"
    echo ""
    echo "オプション:"
    echo "  all                すべてのGUIテストを実行"
    echo "  process-monitor    プロセスモニターGUIテストを実行"
    echo "  user-interaction   ユーザー操作GUIテストを実行"
    echo "  command-execution  コマンド実行GUIテストを実行"
    echo "  --help, -h         このヘルプメッセージを表示"
    echo ""
}

# ヘルプオプションの処理
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# 引数がない場合はすべてのテストを実行
if [ -z "$1" ] || [ "$1" = "all" ]; then
    echo "すべてのGUIテストを実行中..."
    python -m unittest discover -s "${TEST_DIR}" -p "test_*.py" -v
    exit $?
fi

# プロセスモニターGUIテストの実行
if [ "$1" = "process-monitor" ]; then
    echo "プロセスモニターGUIテストを実行中..."
    python -m unittest discover -s "${TEST_DIR}" -p "test_process_monitor.py" -v
    exit $?
fi

# ユーザー操作GUIテストの実行
if [ "$1" = "user-interaction" ]; then
    echo "ユーザー操作GUIテストを実行中..."
    python -m unittest discover -s "${TEST_DIR}" -p "test_user_interaction.py" -v
    exit $?
fi

# コマンド実行GUIテストの実行
if [ "$1" = "command-execution" ]; then
    echo "コマンド実行GUIテストを実行中..."
    python -m unittest discover -s "${TEST_DIR}" -p "test_command_execution.py" -v
    exit $?
fi

# 指定されたテストが見つからない場合
echo "エラー: 指定されたテスト '$1' は見つかりませんでした。"
echo "使用可能なオプションは 'all', 'process-monitor', 'user-interaction', 'command-execution' です。"
echo "詳細については '--help' を使用してください。"
exit 1 
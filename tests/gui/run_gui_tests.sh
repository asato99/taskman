#!/bin/bash

# GUIテスト実行スクリプト

# 基本ディレクトリを設定
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GUI_TEST_DIR="${BASE_DIR}/tests/gui"

# Pythonパスを設定
export PYTHONPATH="${BASE_DIR}:${PYTHONPATH}"

# ヘルプメッセージ
function show_help {
    echo "使用方法: $0 [オプション]"
    echo "オプション:"
    echo "  all                  - すべてのGUIテストを実行"
    echo "  process-monitor      - プロセスモニターGUIテストを実行"
    echo "  user-interaction     - ユーザー操作テストを実行"
    echo "  <file_path>          - 指定したテストファイルを実行"
    echo "  --help, -h           - このヘルプメッセージを表示"
    exit 0
}

# ヘルプが要求された場合
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
fi

echo "GUIテストを実行します..."

# 引数がない場合、全てのテストを実行
if [ $# -eq 0 ]; then
    echo "すべてのGUIテストを実行します..."
    python -m unittest discover -s "${GUI_TEST_DIR}" -p "test_*.py"
    exit 0
fi

# 特定のテストを実行
case "$1" in
    "all")
        echo "すべてのGUIテストを実行します..."
        python -m unittest discover -s "${GUI_TEST_DIR}" -p "test_*.py"
        ;;
    "process-monitor")
        echo "プロセスモニターGUIテストを実行します..."
        python -m unittest "${GUI_TEST_DIR}/test_process_monitor.py"
        ;;
    "user-interaction")
        echo "ユーザー操作テストを実行します..."
        python -m unittest "${GUI_TEST_DIR}/test_user_interaction.py"
        ;;
    *)
        # 特定のファイルを探す
        if [ -f "$1" ]; then
            echo "$1 を実行します..."
            python -m unittest "$1"
        elif [ -f "${GUI_TEST_DIR}/$1" ]; then
            echo "${GUI_TEST_DIR}/$1 を実行します..."
            python -m unittest "${GUI_TEST_DIR}/$1"
        else
            echo "エラー: $1 が見つかりません"
            exit 1
        fi
        ;;
esac

echo "GUIテスト完了" 
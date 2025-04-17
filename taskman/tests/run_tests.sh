#!/bin/bash

# カレントディレクトリを設定
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_DIR="${BASE_DIR}/tests"

# 環境変数設定
export PYTHONPATH="${BASE_DIR}:${PYTHONPATH}"

# ヘルプ表示
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "タスク管理システムのテスト実行スクリプト (新構造対応版)"
    echo ""
    echo "使用方法:"
    echo "  ./taskman/tests/run_tests.sh [option]"
    echo ""
    echo "オプション:"
    echo "  all                  すべてのテストを実行"
    echo "  unit                 単体テストのみ実行"
    echo "  integration          結合テストのみ実行"
    echo "  gui                  GUIテストのみ実行"
    echo "  task                 タスク機能に関するテストのみ実行"
    echo "  task-instance        タスクインスタンス機能に関するテストのみ実行"
    echo "  process              プロセス機能に関するテストのみ実行"
    echo "  process-instance     プロセスインスタンス機能に関するテストのみ実行"
    echo "  process-monitor      プロセスモニター機能に関するテストのみ実行"
    echo "  <file_path>          指定したテストファイルを実行"
    echo "  --help, -h           このヘルプメッセージを表示"
    echo ""
    echo "オプションなしで実行すると、すべての単体テストと結合テストを実行します。"
    exit 0
fi

# テスト実行
echo "すべてのテストを実行中..."

echo "単体テストを実行中..."
python -m pytest -xvs ${TEST_DIR}/unit/

echo ""
echo "結合テストを実行中..."
python -m pytest -xvs ${TEST_DIR}/integration/

echo ""
echo "GUIテストを実行中..."
cd ${BASE_DIR} && QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests/gui -p "test_*.py" -v

echo ""
echo "全テスト完了！"

# すべてのテストを実行
if [ "$1" = "all" ]; then
    echo "すべてのテストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/unit ${TEST_DIR}/integration
    exit $?
fi

# 単体テストのみ実行
if [ "$1" = "unit" ]; then
    echo "単体テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/unit
    exit $?
fi

# 結合テストのみ実行
if [ "$1" = "integration" ]; then
    echo "結合テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/integration
    exit $?
fi

# GUIテストのみ実行
if [ "$1" = "gui" ]; then
    echo "GUIテストを実行中..."
    if [ -d "${TEST_DIR}/gui" ]; then
        python -m pytest -xvs ${TEST_DIR}/gui
    else
        echo "GUIテストディレクトリが見つかりません"
    fi
    exit $?
fi

# タスク機能に関するテストのみ実行
if [ "$1" = "task" ]; then
    echo "タスク機能のテストを実行中..."
    echo "タスク機能の単体テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/unit/test_task_manual.py
    echo ""
    echo "タスク機能の結合テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/integration/test_task.py
    exit $?
fi

# タスクインスタンス機能に関するテストのみ実行
if [ "$1" = "task-instance" ]; then
    echo "タスクインスタンス機能のテストを実行中..."
    echo "タスクインスタンス機能の単体テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/unit/test_task_instance_manual.py
    echo ""
    echo "タスクインスタンス機能の結合テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/integration/test_task_instance.py
    exit $?
fi

# プロセス機能に関するテストのみ実行
if [ "$1" = "process" ]; then
    echo "プロセス機能のテストを実行中..."
    echo "プロセス機能の単体テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/unit/test_process_manual.py
    echo ""
    echo "プロセス機能の結合テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/integration/test_process.py
    exit $?
fi

# プロセスインスタンス機能に関するテストのみ実行
if [ "$1" = "process-instance" ]; then
    echo "プロセスインスタンス機能のテストを実行中..."
    echo "プロセスインスタンス機能の単体テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/unit/test_process_instance_manual.py
    echo ""
    echo "プロセスインスタンス機能の結合テストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/integration/test_process_instance.py
    exit $?
fi

# プロセスモニター機能に関するテストのみ実行
if [ "$1" = "process-monitor" ]; then
    echo "プロセスモニター機能のテストを実行中..."
    python -m pytest -xvs ${TEST_DIR}/integration/test_process_monitor_db.py
    exit $?
fi

# 特定のテストファイルを実行
if [ -n "$1" ]; then
    # 入力されたファイルパスが存在する場合はそのまま実行
    if [ -f "$1" ]; then
        python -m pytest -xvs "$1"
    # テストディレクトリ内のファイルを検索
    elif [ -f "${TEST_DIR}/$1" ]; then
        python -m pytest -xvs "${TEST_DIR}/$1"
    else
        echo "指定されたテストファイルが見つかりません: $1"
        exit 1
    fi
    exit $?
fi

# デフォルトではすべての単体テストと結合テストを実行
echo "すべてのテストを実行中..."
echo "単体テストを実行中..."
python -m pytest -xvs ${TEST_DIR}/unit
echo ""
echo "結合テストを実行中..."
python -m pytest -xvs ${TEST_DIR}/integration

echo ""
echo "GUIテストを実行中..."
PYTHONPATH=$PYTHONPATH:$(pwd) QT_QPA_PLATFORM=offscreen python -m unittest discover -s taskman/tests/gui -p "test_*.py" -v

echo ""
echo "全テスト完了！" 
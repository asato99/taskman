#!/bin/bash

# PYTHONPATHを設定して現在のディレクトリをインポートパスに追加
export PYTHONPATH=$PYTHONPATH:$(pwd)

# ヘルプ表示
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "タスク管理システムのテスト実行スクリプト"
    echo ""
    echo "使用方法:"
    echo "  ./run_tests.sh [option]"
    echo ""
    echo "オプション:"
    echo "  all                  すべてのテストを実行"
    echo "  unit                 単体テストのみ実行"
    echo "  integration          結合テストのみ実行"
    echo "  objective            目標機能に関するテストのみ実行"
    echo "  task                 タスク機能に関するテストのみ実行"
    echo "  step                 タスクステップ機能に関するテストのみ実行"
    echo "  task-instance        タスクインスタンス機能に関するテストのみ実行"
    echo "  process              プロセス機能に関するテストのみ実行"
    echo "  process-instance     プロセスインスタンス機能に関するテストのみ実行"
    echo "  workflow             ワークフロー機能に関するテストのみ実行"
    echo "  <file_path>          指定したテストファイルを実行"
    echo "  --help, -h           このヘルプメッセージを表示"
    echo ""
    echo "オプションなしで実行すると、すべての単体テストと結合テストを実行します。"
    exit 0
fi

# すべてのテストを実行
if [ "$1" = "all" ]; then
    python -m pytest -xvs tests/unit tests/integration
    exit $?
fi

# 単体テストのみ実行
if [ "$1" = "unit" ]; then
    python -m pytest -xvs tests/unit
    exit $?
fi

# 結合テストのみ実行
if [ "$1" = "integration" ]; then
    python -m pytest -xvs tests/integration
    exit $?
fi

# 目標機能に関するテストのみ実行
if [ "$1" = "objective" ]; then
    echo "目標機能の単体テストを実行中..."
    python -m pytest -xvs tests/unit/test_objective_manual.py
    echo ""
    echo "目標機能の結合テストを実行中..."
    python -m pytest -xvs tests/integration/test_objective.py
    exit $?
fi

# タスク機能に関するテストのみ実行
if [ "$1" = "task" ]; then
    echo "タスク機能の単体テストを実行中..."
    python -m pytest -xvs tests/unit/test_task_manual.py
    echo ""
    echo "タスク機能の結合テストを実行中..."
    python -m pytest -xvs tests/integration/test_task.py
    exit $?
fi

# タスクステップ機能に関するテストのみ実行
if [ "$1" = "step" ]; then
    echo "タスクステップ機能の単体テストを実行中..."
    python -m pytest -xvs tests/unit/test_task_step_manual.py
    echo ""
    echo "タスクステップ機能の結合テストを実行中..."
    python -m pytest -xvs tests/integration/test_task_step.py
    exit $?
fi

# タスクインスタンス機能に関するテストのみ実行
if [ "$1" = "task-instance" ]; then
    echo "タスクインスタンス機能の単体テストを実行中..."
    python -m pytest -xvs tests/unit/test_task_instance_manual.py
    echo ""
    echo "タスクインスタンス機能の結合テストを実行中..."
    python -m pytest -xvs tests/integration/test_task_instance.py
    exit $?
fi

# プロセス機能に関するテストのみ実行
if [ "$1" = "process" ]; then
    echo "プロセス機能の単体テストを実行中..."
    python -m pytest -xvs tests/unit/test_process_manual.py
    echo ""
    echo "プロセス機能の結合テストを実行中..."
    python -m pytest -xvs tests/integration/test_process.py
    exit $?
fi

# プロセスインスタンス機能に関するテストのみ実行
if [ "$1" = "process-instance" ]; then
    echo "プロセスインスタンス機能の単体テストを実行中..."
    python -m pytest -xvs tests/unit/test_process_instance_manual.py
    echo ""
    echo "プロセスインスタンス機能の結合テストを実行中..."
    python -m pytest -xvs tests/integration/test_process_instance.py
    exit $?
fi

# ワークフロー機能に関するテストのみ実行
if [ "$1" = "workflow" ]; then
    echo "ワークフロー機能の単体テストを実行中..."
    python -m pytest -xvs tests/unit/test_workflow_manual.py
    echo ""
    echo "ワークフロー機能の結合テストを実行中..."
    python -m pytest -xvs tests/integration/test_workflow.py
    exit $?
fi

# 特定のテストファイルを実行
if [ -n "$1" ]; then
    python -m pytest -xvs "$1"
    exit $?
fi

# デフォルトではすべての単体テストと結合テストを実行
echo "単体テストを実行中..."
python -m pytest -xvs tests/unit
echo ""
echo "結合テストを実行中..."
python -m pytest -xvs tests/integration 
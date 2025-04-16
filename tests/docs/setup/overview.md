# テスト環境セットアップガイド

## 前提条件

- Python 3.9以上
- pipまたはpip3がインストール済み

## テスト環境のセットアップ

### 1. 仮想環境の作成と有効化

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. 依存パッケージのインストール

```bash
# requirements.txtからインストール
pip install -r requirements.txt

# テスト実行に必要な追加パッケージ
pip install pytest pytest-cov
```

## テスト実行

### テスト実行スクリプト

プロジェクトには `run_tests.sh`（macOS/Linux用）と `run_tests.bat`（Windows用）が用意されています。これらのスクリプトを使用して、異なるタイプのテストを実行できます。

```bash
# すべてのテストを実行
./run_tests.sh

# 単体テストのみ実行
./run_tests.sh unit

# 統合テストのみ実行
./run_tests.sh integration

# 特定のテストファイルを実行
./run_tests.sh tests/unit/test_objective_manual.py
```

### 手動でのテスト実行

スクリプトを使わずに直接pytestコマンドを実行することもできます：

```bash
# すべてのテストを実行
python -m pytest -xvs tests/

# 単体テストのみ実行
python -m pytest -xvs tests/unit/

# 統合テストのみ実行
python -m pytest -xvs tests/integration/

# テストカバレッジレポートの生成
python -m pytest --cov=taskman tests/
```

## テスト環境のカスタマイズ

### 環境変数

テスト実行時に環境変数を設定することで、テストの挙動をカスタマイズできます。

| 環境変数 | 説明 | デフォルト値 |
|---------|------|------------|
| `TEST_DB_URL` | テスト用データベースのURL | `sqlite:///:memory:` |
| `LOG_LEVEL` | ロギングレベル | `WARNING` |

例：

```bash
# 特定のデータベースURLを使用してテスト実行
TEST_DB_URL="sqlite:///test.db" ./run_tests.sh

# 詳細なログ出力でテスト実行
LOG_LEVEL=DEBUG ./run_tests.sh
```

### conftest.pyの利用

テスト設定や共通フィクスチャは以下のファイルで管理されています：

- `tests/conftest.py`: すべてのテストで共有される設定とフィクスチャ
- `tests/unit/conftest.py`: 単体テスト特有の設定とフィクスチャ
- `tests/integration/conftest.py`: 統合テスト特有の設定とフィクスチャ

これらのファイルをカスタマイズすることで、テスト環境を拡張できます。

## CIパイプラインの設定

### GitHub Actions

`.github/workflows/test.yml`にGitHub Actionsの設定が含まれています（まだ実装されていない場合は、以下を参考に設定できます）：

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        python -m pytest --cov=taskman tests/
```

## トラブルシューティング

### よくある問題と解決方法

1. **テストデータベースへの接続エラー**
   - 解決方法: 一時ファイルの書き込み権限を確認、またはインメモリデータベースを使用

2. **特定のテストだけが失敗する**
   - 解決方法: `-v`オプションで詳細な出力を確認し、特定のテストを個別に実行

3. **モジュールのインポートエラー**
   - 解決方法: `PYTHONPATH`環境変数が正しく設定されているか確認

4. **テスト間の干渉**
   - 解決方法: 各テストが適切にクリーンアップしているか確認 
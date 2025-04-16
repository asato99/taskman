# 統合テスト仕様書

## 概要

統合テストでは、実際のデータベースを使用してコマンドの一連の動作をテストします。特に単体テストでモックするのが複雑なデータベース操作や親子関係の処理などを重点的にテストします。

## テスト対象

- データベースを含む機能の完全な実行フロー
- 親子関係のある目標の作成と管理
- 削除など副作用のある操作の検証
- 目標の状態変更とフィルタリング機能
- エラー処理と例外ケースの確認

## テストファイル構成

- `tests/integration/test_objective.py`: 目標コマンドの統合テスト

## テストケース詳細

### 1. 目標コマンド統合テスト (`TestObjectiveCommandsIntegration`)

#### 1.1 目標の基本操作テスト

| テストケース | 説明 | 期待結果 |
|------------|------|---------|
| `test_create_and_list` | 目標を作成し、一覧に表示されることを確認 | 目標が正常に作成され、一覧に表示される |
| `test_simple_delete` | 単独の目標を作成して削除 | 目標が正常に削除され、削除後は見つからない |
| `test_update_objective` | 目標の各フィールドを更新 | タイトル、説明、指標、目標値、現在値、期限が正しく更新される |

#### 1.2 親子関係のテスト

| テストケース | 説明 | 期待結果 |
|------------|------|---------|
| `test_create_subobjective` | 親目標を作成し、その下にサブ目標を作成 | サブ目標が正常に作成され、親目標の詳細表示でサブ目標が表示される |
| `test_delete_with_force` | サブ目標がある親目標を削除 | forceオプション無しでは削除できず、forceオプション有りで削除できる |

#### 1.3 状態管理テスト

| テストケース | 説明 | 期待結果 |
|------------|------|---------|
| `test_status_command` | 目標の状態を「進行中」→「達成」→「未達成」→「中止」と変更 | 各状態変更が正常に実行され、変更後の状態が正しく表示される |
| `test_list_filter_by_status` | 異なる状態の目標を作成し、状態でフィルタリング | 各状態のフィルタで該当する目標のみが表示される |

#### 1.4 エラー処理テスト

| テストケース | 説明 | 期待結果 |
|------------|------|---------|
| `test_error_handling` | 不正なパラメータや存在しない目標へのアクセスを試行 | 適切なエラーメッセージが表示され、コマンドが失敗する |

## テスト実行環境

### データベース設定

統合テストでは、テスト専用の一時的なSQLiteデータベースを使用します：

```python
@pytest.fixture(scope="function")
def test_db(monkeypatch):
    """統合テスト用の一時データベースを設定する"""
    # 一時データベースファイルを作成
    fd, path = tempfile.mkstemp(suffix='.db')
    db_url = f"sqlite:///{path}"
    
    # 環境変数をパッチして一時DBを使用
    monkeypatch.setenv("DATABASE_URL", db_url)
    
    # ... テスト実行 ...
    
    yield
    
    # テスト後にファイルを削除
    os.unlink(path)
```

## テスト実装パターン

### セットアップとクリーンアップ

```python
@pytest.fixture(autouse=True)
def setup(self, test_db):
    """各テストの前に実行されるセットアップ"""
    # テスト用のランナー初期化
    self.runner = CliRunner()
    
    # テスト用データの作成
    # ...省略...
    
    yield
    
    # テスト後のクリーンアップ
    # ...省略...
```

### 統合テスト実装例

```python
def test_example(self):
    # 1. 初期状態の確認
    result = self.runner.invoke(app, ["command", "list"])
    assert result.exit_code == 0
    
    # 2. 操作の実行
    result = self.runner.invoke(app, ["command", "create", "--option", "value"])
    assert result.exit_code == 0
    assert "Success message" in result.stdout
    
    # 3. 結果の検証
    result = self.runner.invoke(app, ["command", "show", "1"])
    assert result.exit_code == 0
    assert "Expected data" in result.stdout
```

## 今後の拡張予定

### 追加テストケース
- 複雑な親子関係（多階層）のテスト
- コマンド間の依存関係が複雑なシナリオのテスト

### 性能テスト
- 大量のデータがある場合の挙動テスト
- 長時間実行時の安定性テスト

## 注意事項

1. 各テストは独立して実行可能で、テスト間の順序依存がないように設計されています
2. テスト用データベースは各テスト実行時に新しく作成され、テスト終了後に削除されます
3. テスト中に作成したデータは明示的にクリーンアップします
4. 実際のデータベースには影響を与えません 
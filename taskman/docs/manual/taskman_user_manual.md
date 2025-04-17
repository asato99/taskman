# タスク管理システム利用者マニュアル

## はじめに

タスク管理システム（taskman）は、目標管理、タスク管理、プロセス管理を一元化したコマンドラインツールです。このシステムを使用することで、プロジェクトの目標設定から具体的なタスク管理、さらにはプロセスの定義と実行までを効率的に行うことができます。

## インストールと初期設定

### 前提条件
- Python 3.9以上
- pip（Pythonパッケージマネージャー）

### インストール手順

1. システムをインストールします：
   ```
   pip install taskman
   ```

2. データベースを初期化します：
   ```
   python -m taskman db init
   ```

3. （オプション）サンプルデータを作成します：
   ```
   python -m taskman db seed
   ```

## 基本的な使い方

タスク管理システムは次のようなコマンド体系になっています：

```
python -m taskman [コマンド] [サブコマンド] [オプション]
```

ヘルプを表示するには：
```
python -m taskman --help
```

特定のコマンドのヘルプを表示するには：
```
python -m taskman [コマンド] --help
```

## 主要機能の使い方

### 1. 目標管理（objective）

目標は、達成したい成果を表します。目標は階層構造を持ち、親目標と子目標（サブ目標）の関係を定義できます。

#### 目標の作成
```
python -m taskman objective create --title "2023年第4四半期の売上目標" --metric "売上高" --target 10000000 --current 0
```

#### 目標の一覧表示
```
python -m taskman objective list
```

#### 目標の詳細表示
```
python -m taskman objective show 1
```

#### 目標の更新
```
python -m taskman objective update 1 --current 5000000
```

#### 目標のステータス変更
```
python -m taskman objective status 1 進行中
```

#### 目標の削除
```
python -m taskman objective delete 1
```

### 2. タスク管理（task）

タスクは、目標を達成するための具体的な作業を表します。

#### タスクの作成
```
python -m taskman task create --name "タスク名" --description "タスクの説明" --priority 中 --status 未着手 --deadline 2023-12-31
```

#### タスクの一覧表示
```
python -m taskman task list
```

#### タスクの詳細表示
```
python -m taskman task show 1
```

#### タスクの更新
```
python -m taskman task update 1 --name "更新後のタスク名"
```

#### タスクのステータス変更
```
python -m taskman task status 1 進行中
```

#### タスクの削除
```
python -m taskman task delete 1
```

### 3. タスクステップ管理（step）

タスクステップは、タスクを細分化した具体的な作業手順を表します。

#### ステップの作成
```
python -m taskman step create --task 1 --description "最初のステップ" --sequence 1
```

#### ステップの一覧表示
```
python -m taskman step list --task 1
```

#### ステップの詳細表示
```
python -m taskman step show 1
```

#### ステップの更新
```
python -m taskman step update 1 --description "更新後のステップ"
```

#### ステップの並べ替え
```
python -m taskman step reorder --task 1
```

#### ステップの削除
```
python -m taskman step delete 1
```

### 4. プロセス管理（process）

プロセスは、特定の目的を達成するための一連の手順を定義します。

#### プロセスの作成
```
python -m taskman process create --name "顧客対応プロセス" --description "新規顧客への対応手順"
```

#### プロセスの一覧表示
```
python -m taskman process list
```

#### プロセスの詳細表示
```
python -m taskman process show 1
```

#### プロセスの更新
```
python -m taskman process update 1 --name "更新後のプロセス名"
```

#### プロセスのステータス変更
```
python -m taskman process status 1 有効
```

#### プロセスの削除
```
python -m taskman process delete 1
```

### 5. ワークフロー管理（workflow）

ワークフローは、プロセス間の関係とフローを定義します。

#### ワークフローの作成
```
python -m taskman workflow create --process 1 --from 2 --to 3 --condition-type 常時
```

#### ワークフローの一覧表示
```
python -m taskman workflow list
```

#### ワークフローの詳細表示
```
python -m taskman workflow show 1
```

#### ワークフローの更新
```
python -m taskman workflow update 1 --condition-type 条件付き --condition "task.status == '完了'"
```

#### ワークフローの削除
```
python -m taskman workflow delete 1
```

### 6. プロセスインスタンス管理（instance）

プロセスインスタンスは、定義されたプロセスの実行インスタンスを表します。

#### プロセスインスタンスの作成
```
python -m taskman instance create --process 1 --name "顧客A対応"
```

#### プロセスインスタンスの一覧表示
```
python -m taskman instance list
```

#### プロセスインスタンスの詳細表示
```
python -m taskman instance show 1
```

#### プロセスインスタンスのステータス変更
```
python -m taskman instance status 1 進行中
```

#### プロセスインスタンスの削除
```
python -m taskman instance delete 1
```

### 7. タスクインスタンス管理（task-instance）

タスクインスタンスは、プロセスインスタンスに関連付けられた具体的なタスクの実行を表します。

#### タスクインスタンスの作成
```
python -m taskman task-instance create --task 1 --instance 1
```

#### タスクインスタンスの一覧表示
```
python -m taskman task-instance list
```

#### タスクインスタンスの詳細表示
```
python -m taskman task-instance show 1
```

#### タスクインスタンスの更新
```
python -m taskman task-instance update 1 --notes "進捗メモ"
```

#### タスクインスタンスのステータス変更
```
python -m taskman task-instance status 1 進行中
```

#### タスクインスタンスの削除
```
python -m taskman task-instance delete 1
```

## データベース管理

### データベースの初期化
```
python -m taskman db init
```

### データベースのリセット
```
python -m taskman db reset
```

### サンプルデータの作成
```
python -m taskman db seed
```

## 使用例

### 例1: 目標とタスクの設定

1. 目標を作成する：
   ```
   python -m taskman objective create --title "第4四半期の売上目標" --metric "売上高" --target 10000000 --current 0
   ```

2. 目標に関連するタスクを作成する：
   ```
   python -m taskman task create --name "新規顧客開拓" --description "10社の新規顧客獲得" --priority 高 --objective 1
   ```

3. タスクにステップを追加する：
   ```
   python -m taskman step create --task 1 --description "見込み客リストの作成" --sequence 1
   python -m taskman step create --task 1 --description "初回コンタクト" --sequence 2
   python -m taskman step create --task 1 --description "提案資料作成" --sequence 3
   ```

### 例2: プロセスとワークフローの定義

1. 複数のプロセスを作成する：
   ```
   python -m taskman process create --name "顧客調査" --description "顧客ニーズの調査"
   python -m taskman process create --name "提案作成" --description "顧客向け提案書の作成"
   python -m taskman process create --name "提案プレゼン" --description "顧客への提案プレゼンテーション"
   ```

2. プロセス間のワークフローを定義する：
   ```
   python -m taskman workflow create --process 1 --from 1 --to 2 --condition-type 常時
   python -m taskman workflow create --process 1 --from 2 --to 3 --condition-type 条件付き --condition "提案書.status == '承認済み'"
   ```

### 例3: プロセスの実行

1. プロセスインスタンスを作成する：
   ```
   python -m taskman instance create --process 1 --name "顧客A向けプロジェクト"
   ```

2. タスクインスタンスを作成する：
   ```
   python -m taskman task-instance create --task 1 --instance 1
   ```

3. タスクインスタンスのステータスを更新する：
   ```
   python -m taskman task-instance status 1 進行中
   ```

4. プロセスインスタンスのステータスを更新する：
   ```
   python -m taskman instance status 1 進行中
   ```

## ヒントとコツ

1. **目標の階層構造を活用する**：大きな目標を設定し、それを小さなサブ目標に分割することで、達成可能な単位に分解できます。

2. **タスクにステップを詳細に定義する**：タスクをステップに分解することで、進捗管理や作業委任が容易になります。

3. **プロセスを再利用する**：繰り返し行う作業はプロセスとして定義しておくことで、効率的に作業を進められます。

4. **定期的にステータスを更新する**：目標、タスク、プロセスのステータスを定期的に更新することで、現在の進捗状況を正確に把握できます。

5. **ワークフローの条件を活用する**：条件付きワークフローを使用することで、特定の条件が満たされた場合にのみ次のプロセスに進むようなフローを設計できます。

## トラブルシューティング

### データベースエラーが発生する場合
```
python -m taskman db reset
```
を実行して、データベースをリセットしてください。

### コマンドが見つからない場合
Pythonのパスが正しく設定されているか確認してください。また、モジュールが正しくインストールされているか確認してください。

### IDが見つからないエラー
操作しようとしているオブジェクト（目標、タスクなど）が存在するか確認してください。
```
python -m taskman [オブジェクト] list
```
で一覧を表示できます。

## システム情報

バージョン情報を表示するには：
```
python -m taskman version
```

## まとめ

タスク管理システムは、目標設定からタスク管理、プロセス実行までを一元管理するための強力なツールです。コマンドラインインターフェースを通じて、様々な操作を効率的に行うことができます。

このマニュアルでは基本的な使い方を説明しましたが、各コマンドの詳細なオプションについては、ヘルプコマンド（`--help`）を使用して確認してください。 
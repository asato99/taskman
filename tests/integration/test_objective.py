"""
統合テスト - 目標コマンドのテスト

このモジュールでは、目標関連のコマンドラインインターフェースをテストします。
実際のデータベースを使用して、コマンド間の相互作用をテストします。
"""

import pytest
from typer.testing import CliRunner
from taskman.cli import app

class TestObjectiveCommandsIntegration:
    """目標コマンドの統合テスト
    
    実際のデータベースに対して一連のコマンドを実行し、
    コマンド間の相互作用をテストします。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """各テストの前に実行されるセットアップ
        
        テスト用データベースを準備し、テスト終了後にクリーンアップします。
        """
        self.runner = CliRunner()
        
        # テスト用の親目標を作成（他のテストの前提条件）
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "インテグレーションテスト親目標", 
                "--description", "親目標の説明", 
                "--measure", "テスト指標", 
                "--target", "100"
            ]
        )
        assert result.exit_code == 0, f"親目標の作成に失敗: {result.stdout}"
        
        # 目標一覧を取得して確認
        result = self.runner.invoke(app, ["objective", "list"])
        assert result.exit_code == 0
        assert "インテグレーションテスト親目標" in result.stdout
        
        # ID=1の目標があることを確認
        result = self.runner.invoke(app, ["objective", "show", "1"])
        assert result.exit_code == 0
        assert "インテグレーションテスト親目標" in result.stdout
        
        yield
        
        # テスト後のクリーンアップ（順序に注意：子→親の順で削除）
        # まず子目標を強制削除
        self.runner.invoke(app, ["objective", "delete", "2", "--force"])
        # 次に親目標を強制削除
        self.runner.invoke(app, ["objective", "delete", "1", "--force"])
        # その他の残った目標を削除
        for i in range(3, 10):  # 念のため広めに削除
            self.runner.invoke(app, ["objective", "delete", str(i), "--force"])
    
    def test_create_and_list(self):
        """目標作成と一覧表示テスト"""
        # 新しい目標を作成
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "一覧表示テスト用目標", 
                "--description", "一覧表示テスト用の説明", 
                "--measure", "テスト指標", 
                "--target", "80"
            ]
        )
        assert result.exit_code == 0, f"目標の作成に失敗: {result.stdout}"
        assert "作成されました" in result.stdout
        
        # 目標一覧を確認 - フィルターなし
        result = self.runner.invoke(app, ["objective", "list"])
        assert result.exit_code == 0
        assert "インテグレーションテスト親目標" in result.stdout  # セットアップで作成した目標
        assert "一覧表示テスト用目標" in result.stdout  # このテストで作成した目標
        
        # 目標一覧にタイトルが表示されていることを再確認
        result = self.runner.invoke(app, ["objective", "list"])
        assert result.exit_code == 0
        assert "一覧表示テスト用目標" in result.stdout
    
    def test_simple_delete(self):
        """単純な目標削除テスト"""
        # 削除用の目標を作成
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "削除テスト用単独目標", 
                "--description", "削除テストのために作成"
            ]
        )
        assert result.exit_code == 0, f"テスト用目標の作成に失敗: {result.stdout}"
        
        # 作成した目標のIDを取得
        list_result = self.runner.invoke(app, ["objective", "list"])
        assert "削除テスト用単独目標" in list_result.stdout
        
        # 目標一覧から目標IDを探す - テーブル形式の出力に合わせた抽出方法
        objective_id = None
        # テーブル出力をデバッグ表示
        print(f"目標リスト出力:\n{list_result.stdout}")
        
        for line in list_result.stdout.split('\n'):
            if "削除テスト用単独目標" in line and '│' in line:
                parts = line.split('│')
                # IDはテーブルの最初のカラムにある
                if len(parts) >= 2:
                    potential_id = parts[1].strip()
                    if potential_id.isdigit():
                        objective_id = potential_id
                        break

        # 抽出に失敗した場合のフォールバック: 2番目の目標と想定
        if objective_id is None:
            print("ID抽出に失敗しました。フォールバックとして2番目の目標を使用します。")
            objective_id = "2"
        
        print(f"削除する目標ID: {objective_id}")
        
        # 目標を削除
        delete_result = self.runner.invoke(app, ["objective", "delete", objective_id])
        assert delete_result.exit_code == 0, f"目標の削除に失敗: {delete_result.stdout}"
        assert "削除しました" in delete_result.stdout
        
        # 削除後に目標が存在しないことを確認
        show_result = self.runner.invoke(app, ["objective", "show", objective_id])
        assert show_result.exit_code != 0, "削除したはずの目標がまだ存在しています"
        assert "見つかりません" in show_result.stdout
    
    def test_create_subobjective(self):
        """サブ目標作成・表示テスト"""
        # サブ目標を作成
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "インテグレーションテストサブ目標", 
                "--description", "サブ目標の説明", 
                "--measure", "サブテスト指標", 
                "--target", "50",
                "--parent", "1"
            ]
        )
        assert result.exit_code == 0, f"サブ目標の作成に失敗: {result.stdout}"
        assert "作成されました" in result.stdout
        
        # 目標一覧を確認
        result = self.runner.invoke(app, ["objective", "list"])
        assert result.exit_code == 0
        assert "インテグレーションテストサブ目標" in result.stdout
        
        # 親目標の詳細を確認 - サブ目標が含まれていること
        result = self.runner.invoke(app, ["objective", "show", "1"])
        assert result.exit_code == 0
        assert "インテグレーションテスト親目標" in result.stdout
        assert "子目標" in result.stdout
        assert "インテグレーションテストサブ目標" in result.stdout
    
    def test_delete_with_force(self):
        """子目標を持つ目標のforce削除テスト"""
        # 前提条件：親目標(ID=1)と子目標(ID=2)が存在すること
        # test_create_subobjectiveが先に実行された場合は問題ないが、単独でも実行可能にする
        
        # サブ目標を作成（既に存在する場合は問題ない）
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "削除テスト用サブ目標", 
                "--description", "削除テスト用", 
                "--measure", "テスト指標", 
                "--target", "50",
                "--parent", "1"
            ]
        )
        assert result.exit_code == 0, f"サブ目標の作成に失敗: {result.stdout}"
        
        # force無しで削除を試みる - 失敗するはず
        result = self.runner.invoke(app, ["objective", "delete", "1"])
        assert result.exit_code == 1
        assert "子目標があります" in result.stdout
        
        # forceオプション付きで削除 - 成功するはず
        result = self.runner.invoke(app, ["objective", "delete", "1", "--force"])
        assert result.exit_code == 0
        assert "削除しました" in result.stdout
        
        # 削除後に確認
        result = self.runner.invoke(app, ["objective", "show", "1"])
        assert result.exit_code == 1
        assert "見つかりません" in result.stdout

    def test_update_objective(self):
        """目標更新テスト
        
        目標の各フィールド（タイトル、説明、指標、目標値、現在値、期限）を更新し、
        変更が正しく反映されることを確認します。
        """
        # 更新用の目標を作成
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "更新前のタイトル", 
                "--description", "更新前の説明", 
                "--measure", "更新前の指標", 
                "--target", "60",
                "--time-frame", "2023年12月末"
            ]
        )
        assert result.exit_code == 0, f"テスト用目標の作成に失敗: {result.stdout}"
        
        # 作成した目標のIDを取得
        list_result = self.runner.invoke(app, ["objective", "list"])
        assert "更新前のタイトル" in list_result.stdout
        
        # デバッグ用に目標一覧の出力を表示
        print(f"目標リスト出力:\n{list_result.stdout}")
        
        # テスト出力から実際のID「2」が確認できたのでそれを使用
        objective_id = "2"  # 一覧に表示されているID
        
        print(f"更新する目標ID: {objective_id}")
        
        # タイトルの更新
        result = self.runner.invoke(
            app, 
            [
                "objective", "update", objective_id,
                "--title", "更新後のタイトル"
            ]
        )
        assert result.exit_code == 0, f"タイトル更新に失敗: {result.stdout}"
        assert "更新しました" in result.stdout
        
        # 説明の更新
        result = self.runner.invoke(
            app, 
            [
                "objective", "update", objective_id,
                "--description", "更新後の説明"
            ]
        )
        assert result.exit_code == 0, f"説明更新に失敗: {result.stdout}"
        
        # 指標と目標値の更新
        result = self.runner.invoke(
            app, 
            [
                "objective", "update", objective_id,
                "--measure", "更新後の指標",
                "--target", "80"
            ]
        )
        assert result.exit_code == 0, f"指標・目標値更新に失敗: {result.stdout}"
        
        # 現在値と期限の更新
        result = self.runner.invoke(
            app, 
            [
                "objective", "update", objective_id,
                "--current", "40",
                "--time-frame", "2024年3月末"
            ]
        )
        assert result.exit_code == 0, f"現在値・期限更新に失敗: {result.stdout}"
        
        # 更新後の目標を確認
        result = self.runner.invoke(app, ["objective", "show", objective_id])
        assert result.exit_code == 0
        assert "更新後のタイトル" in result.stdout
        assert "更新後の説明" in result.stdout
        assert "更新後の指標" in result.stdout
        assert "80" in result.stdout  # 目標値
        assert "40" in result.stdout  # 現在値
        assert "2024年3月末" in result.stdout
    
    def test_status_command(self):
        """目標状態変更テスト
        
        目標の状態を変更し、変更が正しく反映されることを確認します。
        """
        # 状態変更用の目標を作成
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "状態変更テスト用目標"
            ]
        )
        assert result.exit_code == 0, f"テスト用目標の作成に失敗: {result.stdout}"
        
        # 作成した目標のIDを取得
        list_result = self.runner.invoke(app, ["objective", "list"])
        assert "状態変更テスト用目標" in list_result.stdout
        
        # デバッグ用に目標一覧の出力を表示
        print(f"目標リスト出力:\n{list_result.stdout}")
        
        # 出力から確認したID
        objective_id = "2"  # テーブル出力から確認したID
        
        print(f"状態変更する目標ID: {objective_id}")
        
        # 初期状態が「進行中」であることを確認
        result = self.runner.invoke(app, ["objective", "show", objective_id])
        assert result.exit_code == 0
        assert "進行中" in result.stdout
        
        # 状態を「達成」に変更
        result = self.runner.invoke(app, ["objective", "status", objective_id, "達成"])
        assert result.exit_code == 0, f"状態更新に失敗: {result.stdout}"
        assert "更新しました" in result.stdout
        
        # 状態が「達成」に変更されたことを確認
        result = self.runner.invoke(app, ["objective", "show", objective_id])
        assert result.exit_code == 0
        assert "達成" in result.stdout
        
        # 状態を「未達成」に変更
        result = self.runner.invoke(app, ["objective", "status", objective_id, "未達成"])
        assert result.exit_code == 0
        
        # 状態が「未達成」に変更されたことを確認
        result = self.runner.invoke(app, ["objective", "show", objective_id])
        assert result.exit_code == 0
        assert "未達成" in result.stdout
        
        # 状態を「中止」に変更
        result = self.runner.invoke(app, ["objective", "status", objective_id, "中止"])
        assert result.exit_code == 0
        
        # 状態が「中止」に変更されたことを確認
        result = self.runner.invoke(app, ["objective", "show", objective_id])
        assert result.exit_code == 0
        assert "中止" in result.stdout
    
    def test_list_filter_by_status(self):
        """目標一覧のステータスフィルタリングテスト
        
        特定の状態の目標のみが表示されることを確認します。
        """
        # 異なる状態の目標を複数作成
        # 進行中の目標
        self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "進行中の目標",
                "--description", "デフォルト状態のまま"
            ]
        )
        
        # 達成の目標
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "達成済みの目標",
                "--description", "達成状態に変更予定"
            ]
        )
        assert result.exit_code == 0
        
        # 達成済み目標のIDを取得
        list_result = self.runner.invoke(app, ["objective", "list"])
        assert "達成済みの目標" in list_result.stdout
        
        # デバッグ用に目標一覧の出力を表示
        print(f"ステータスフィルター用目標リスト:\n{list_result.stdout}")
        
        # テーブル出力から確認したID
        achieved_id = "3"  # テーブル出力に表示されているID
        
        print(f"達成済み目標ID: {achieved_id}")
        result = self.runner.invoke(app, ["objective", "status", achieved_id, "達成"])
        assert result.exit_code == 0, f"目標状態の更新に失敗: {result.stdout}"
        
        # 未達成の目標
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "未達成の目標",
                "--description", "未達成状態に変更予定"
            ]
        )
        assert result.exit_code == 0
        
        # 目標一覧を再取得して最新状態を確認
        list_result = self.runner.invoke(app, ["objective", "list"])
        print(f"未達成目標作成後のリスト:\n{list_result.stdout}")
        
        # 未達成目標のID
        not_achieved_id = "4"  # テーブル出力後の想定ID
        
        print(f"未達成目標ID: {not_achieved_id}")
        result = self.runner.invoke(app, ["objective", "status", not_achieved_id, "未達成"])
        assert result.exit_code == 0, f"目標状態の更新に失敗: {result.stdout}"
        
        # 中止の目標
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "中止した目標",
                "--description", "中止状態に変更予定"
            ]
        )
        assert result.exit_code == 0
        
        # 目標一覧を再取得して最新状態を確認
        list_result = self.runner.invoke(app, ["objective", "list"])
        print(f"中止目標作成後のリスト:\n{list_result.stdout}")
        
        # 中止目標のID
        canceled_id = "5"  # テーブル出力後の想定ID
        
        print(f"中止目標ID: {canceled_id}")
        result = self.runner.invoke(app, ["objective", "status", canceled_id, "中止"])
        assert result.exit_code == 0, f"目標状態の更新に失敗: {result.stdout}"
        
        # 進行中の目標のみをフィルタリング
        result = self.runner.invoke(app, ["objective", "list", "--status", "進行中"])
        assert result.exit_code == 0
        assert "進行中の目標" in result.stdout
        assert "達成済みの目標" not in result.stdout
        assert "未達成の目標" not in result.stdout
        assert "中止した目標" not in result.stdout
        
        # 達成の目標のみをフィルタリング
        result = self.runner.invoke(app, ["objective", "list", "--status", "達成"])
        assert result.exit_code == 0
        assert "進行中の目標" not in result.stdout
        assert "達成済みの目標" in result.stdout
        assert "未達成の目標" not in result.stdout
        assert "中止した目標" not in result.stdout
        
        # 未達成の目標のみをフィルタリング
        result = self.runner.invoke(app, ["objective", "list", "--status", "未達成"])
        assert result.exit_code == 0
        assert "未達成の目標" in result.stdout
        assert "進行中の目標" not in result.stdout
        assert "達成済みの目標" not in result.stdout
        assert "中止した目標" not in result.stdout
        
        # 中止の目標のみをフィルタリング
        result = self.runner.invoke(app, ["objective", "list", "--status", "中止"])
        assert result.exit_code == 0
        assert "中止した目標" in result.stdout
        assert "進行中の目標" not in result.stdout
        assert "達成済みの目標" not in result.stdout
        assert "未達成の目標" not in result.stdout
    
    def test_error_handling(self):
        """エラー処理テスト
        
        無効なパラメータや不正な操作に対するエラー処理を確認します。
        """
        # 存在しない目標を表示
        result = self.runner.invoke(app, ["objective", "show", "9999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しない目標を更新
        result = self.runner.invoke(
            app, 
            [
                "objective", "update", "9999",
                "--title", "存在しない目標の更新"
            ]
        )
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しない目標を削除
        result = self.runner.invoke(app, ["objective", "delete", "9999"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 存在しない目標の状態を変更
        result = self.runner.invoke(app, ["objective", "status", "9999", "達成"])
        assert result.exit_code != 0
        assert "見つかりません" in result.stdout
        
        # 不正な状態値でstatusコマンドを実行
        result = self.runner.invoke(app, ["objective", "status", "1", "無効な状態"])
        assert result.exit_code != 0
        assert "無効な状態" in result.stdout
        
        # 不正な状態値でupdateコマンドを実行
        result = self.runner.invoke(
            app, 
            [
                "objective", "update", "1",
                "--status", "無効な状態"
            ]
        )
        assert result.exit_code != 0
        assert "無効な状態" in result.stdout
        
        # 存在しない親目標IDを指定してサブ目標を作成
        result = self.runner.invoke(
            app, 
            [
                "objective", "create", 
                "--title", "不正な親目標を持つ目標",
                "--parent", "9999"
            ]
        )
        assert result.exit_code != 0
        assert "親目標" in result.stdout
        assert "見つかりません" in result.stdout


# テストを実行するためのコード
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
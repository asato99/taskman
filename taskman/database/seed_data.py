"""
Script for seeding sample data into the database
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from taskman.database.connection import SessionLocal
from taskman.models import Objective, Process, Task, Workflow

def create_sample_data():
    """
    Create sample data for testing
    """
    db = SessionLocal()
    try:
        # Create sample objective
        objective = Objective(
            title="顧客対応時間の短縮",
            description="問い合わせから解決までの平均時間を短縮",
            measure="平均対応時間（時間）",
            target_value=4.0,
            current_value=0.0,
            time_frame="2024Q2",
            status="進行中"
        )
        db.add(objective)
        db.commit()

        # Create sample process
        process = Process(
            name="顧客問い合わせ対応プロセス",
            description="顧客からの問い合わせ受付から解決までのプロセス",
            status="アクティブ"
        )
        db.add(process)
        db.commit()

        # Create sample tasks
        tasks = [
            Task(
                process_id=process.id,
                name="問い合わせ受付",
                description="顧客からの問い合わせを受け付け、内容を記録する",
                estimated_duration=15,
                priority="高",
                status="未着手"
            ),
            Task(
                process_id=process.id,
                name="担当者割り当て",
                description="問い合わせ内容に基づいて適切な担当者を割り当てる",
                estimated_duration=10,
                priority="高",
                status="未着手"
            ),
            Task(
                process_id=process.id,
                name="問題調査",
                description="問題の詳細を調査し、解決策を検討する",
                estimated_duration=60,
                priority="中",
                status="未着手"
            ),
            Task(
                process_id=process.id,
                name="解決策提示",
                description="顧客に解決策を提示し、実行する",
                estimated_duration=30,
                priority="中",
                status="未着手"
            ),
            Task(
                process_id=process.id,
                name="フォローアップ",
                description="解決後の顧客満足度確認と記録",
                estimated_duration=15,
                priority="低",
                status="未着手"
            )
        ]
        db.add_all(tasks)
        db.commit()

        # Create workflow between tasks
        workflow = [
            Workflow(
                process_id=process.id,
                from_task_id=tasks[0].id,
                to_task_id=tasks[1].id,
                condition_type="常時",
                sequence_number=1
            ),
            Workflow(
                process_id=process.id,
                from_task_id=tasks[1].id,
                to_task_id=tasks[2].id,
                condition_type="常時",
                sequence_number=2
            ),
            Workflow(
                process_id=process.id,
                from_task_id=tasks[2].id,
                to_task_id=tasks[3].id,
                condition_type="常時",
                sequence_number=3
            ),
            Workflow(
                process_id=process.id,
                from_task_id=tasks[3].id,
                to_task_id=tasks[4].id,
                condition_type="常時",
                sequence_number=4
            )
        ]
        db.add_all(workflow)
        db.commit()

        print("Sample data created successfully!")
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data() 
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess, datetime

def run_pipeline():
    print(f"\n🔄 Pipeline started at {datetime.datetime.now()}")
    subprocess.run(["python", "01_collect_data.py"])
    subprocess.run(["python", "02_clean_data.py"])
    subprocess.run(["python", "03_store_postgres.py"])
    print("✅ Pipeline complete.")

scheduler = BlockingScheduler()
scheduler.add_job(run_pipeline, "interval", hours=24)
print("⏰ Scheduler started — pipeline runs every 24 hours.")
run_pipeline()  # run once immediately
scheduler.start()
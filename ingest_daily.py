import pandas as pd
import os
import shutil
from datetime import datetime

MASTER_FILE = "data.csv"
INCOMING_DIR = "incoming"
PROCESSED_DIR = "processed"


def run():
    os.makedirs(INCOMING_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    new_files = [f for f in os.listdir(INCOMING_DIR) if f.endswith('.csv')]

    if not new_files:
        print("No new files in incoming/ - nothing to ingest today.")
        return False

    print(f"Found {len(new_files)} new file(s): {new_files}")

    master_exists = os.path.exists(MASTER_FILE)
    total_new_rows = 0

    for filename in sorted(new_files):
        path = os.path.join(INCOMING_DIR, filename)
        new_data = pd.read_csv(path, encoding='latin1', dtype={'InvoiceNo': str, 'StockCode': str})
        total_new_rows += len(new_data)

        new_data.to_csv(MASTER_FILE, mode='a', header=not master_exists, index=False)
        master_exists = True

        archived_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        shutil.move(path, os.path.join(PROCESSED_DIR, archived_name))
        print(f"  Ingested {len(new_data)} rows from {filename} -> archived as {archived_name}")

    print(f"Total new rows added to {MASTER_FILE}: {total_new_rows}")
    return True


if __name__ == "__main__":
    run()

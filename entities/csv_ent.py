import csv
import os

class CsvManager:
    def __init__(self, header):
        self.header = header

    def batch_csv_path(self, paginated_dir, batch_start, batch_end):
        return os.path.join(paginated_dir, f"beers_{batch_start}_{batch_end}.csv")

    def is_complete(self, batch_csv):
        if not os.path.exists(batch_csv):
            return False
        with open(batch_csv, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            return len(rows) > 1

    def write_batch(self, batch_csv, batch_rows):
        with open(batch_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.header)
            writer.writerows(batch_rows)

    def append_master(self, master_csv, batch_rows):
        file_exists = os.path.exists(master_csv)
        with open(master_csv, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(self.header)
            writer.writerows(batch_rows)

    def init_master_csv(self, master_csv):
        if not os.path.exists(master_csv):
            with open(master_csv, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.header)
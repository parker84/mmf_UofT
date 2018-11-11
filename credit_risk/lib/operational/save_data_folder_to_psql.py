import os
from lib.operational.read_write_helpers import ReadWriteData
import pandas as pd

class SaveToPsql(object):

    def __init__(self):
        self.conn = ReadWriteData()

    def save_csv_to_psql(self, filepath, table):
        df = pd.read_csv(filepath, engine="python")
        self.conn.pd_to_psql(df, table=table)

    def save_excel_to_psql(self, filepath, table):
        df = pd.read_excel(filepath)
        self.conn.pd_to_psql(df, table=table)

    def save_data_dir_to_psql(self, data_dir_path):
        files = os.listdir(data_dir_path)
        for file in files:
            print(file)
            file_split = file.split(".")
            file_type = file_split[-1]
            file_name = file_split[0]
            file_path = data_dir_path + "/" + file
            if file_type == "csv":
                self.save_csv_to_psql(file_path, file_name)
            elif file_type == 'xlsx':
                self.save_excel_to_psql(file_path, file_name)



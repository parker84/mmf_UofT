from lib.operational.save_data_folder_to_psql import SaveToPsql


if __name__ == "__main__":
    saveToPsql = SaveToPsql()
    saveToPsql.save_data_dir_to_psql("../data/original_data")

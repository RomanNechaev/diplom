import zipfile
import os
import subprocess
import logging.config
from settings import LOGGING_CONFIG
import numpy as np
logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger("my_logger")


class Utils:

    @staticmethod
    def create_zip_archive(input_file, output_archive):
        with zipfile.ZipFile(output_archive, "w") as zipf:
            zipf.write(input_file)

    @staticmethod
    def count_files(directory):
        if not os.path.exists(directory):
            raise ValueError(f"Directory '{directory}' does not exist")

        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return len(files)

    @staticmethod
    def extract_archive(input_file, directory):
        zip_f = zipfile.ZipFile(input_file)
        model_file = input_file.split("/")[-1].split(".")[0]
        zip_f.extract(f"{model_file}.txt", directory)
        zip_f.close()

    @staticmethod
    def calculate_removed_rows_percentage(input_file, output_file):
        line_count_1 = int(subprocess.check_output(['wc', '-l', input_file]).split()[0])
        line_count_2 = int(subprocess.check_output(['wc', '-l', output_file]).split()[0])
        log.info(f"Кол-во строк в файле {input_file}: {line_count_1}")
        log.info(f"Кол-во строк в файле {output_file}: {line_count_2}")
        return 100 - (line_count_2 / line_count_1) * 100

    @staticmethod
    def map_to_tuple(param):
        splitted = param.split(",")
        splitted[1].replace(" ",'')
        return int(splitted[0]), int(splitted[1])

    @staticmethod
    def get_median_metric(metrics):
        return np.median(np.array(metrics))
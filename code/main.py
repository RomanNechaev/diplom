import argparse
import subprocess
from utils import Utils
import os
import logging.config
from settings import LOGGING_CONFIG
import random
from collections import defaultdict
import yaml
from constants import COUNT_OF_PROCESSED_IMAGES
from metrics import Metrics

#prepare data:

#configure logger:
logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger("my_logger")


def prepare_data():
    try:
        # download git repo
        log.info("Подготовка данных")
        log.info("клонирование репозитория RomanNechaev/rpg_e2vid.git ")
        if not os.path.exists('/rpg_e2vid'):
            subprocess.run("git clone https://github.com/RomanNechaev/rpg_e2vid.git", capture_output=True, check=True)
        else:
            log.warning("репозиторий уже загружен")

        # download model
        if not os.path.exists('/rpg_e2vid/pretrained/E2VID_lightweight.pth.tar'):
            log.info("Загрузка модели E2VID_lightweight.pth.tar")
            subprocess.run(
                "wget http://rpg.ifi.uzh.ch/data/E2VID/models/E2VID_lightweight.pth.tar -o rpg_e2vid/pretrained/E2VID_lightweight.pth.tar",
                capture_output=True,
                check=True)
        else:
            log.warning("Модель уже E2VID_lightweight.pth.tar уже загружена")

        # download dataset
        if not os.path.exists('/rpg_e2vid/data/dynamic_6dof.zip'):
            log.info("Загрузка ")
            subprocess.run(
                "wget http://rpg.ifi.uzh.ch/data/E2VID/datasets/ECD_IJRR17/dynamic_6dof.zip -o rpg_e2vid/data/dynamic_6dof.zip",
                capture_output=True,
                check=True)
        else:
            log.warning("Датасет с событиями dynamic_6dof.zip уже загружен")

        if not os.path.exists('/rpg_e2vid/data/events_txt'):
            log.info("создание папки events_txt")
            subprocess.run("mkdir rpg_e2vid/data/events_txt", capture_output=True, check=True)

        if not os.path.exists('/rpg_e2vid/zip/'):
            log.info("создание папки zip")
            subprocess.run("mkdir rpg_e2vid/zip", capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        log.error(e)

    #run model with default parametrs
    try:
        log.info("Запуск E2VID")
        subprocess.run("python rpg_e2vid/run_reconstruction.py \
          -c rpg_e2vid/pretrained/E2VID_lightweight.pth.tar \
          -i rpg_e2vid/data/dynamic_6dof.zip \
          --auto_hdr \
          --output_folder rpg_e2vid/out/input \
          --fixed_duration")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

        #extract zip_file with events
        if not os.path.exists('/rpg_e2vid/data/events_txt/dynamic_6dof.txt'):
            log.info("Распаковка исходного датасета dynamic_6dof.zip")
            Utils.extract_archive("rpg_e2vid/data/dynamic_6dof.zip", "rpg_e2vid/data/events_txt/dynamic_6dof.txt")


#utils for test protocols

def delete_fixed_block(input_file, output_file, block_size, block_step):
    end = False
    first_line = True
    with open(input_file, 'r') as read_file:
        with open(output_file, 'w') as write_file:
            while True:
                if end:
                    break
                for i in range(block_size):
                    line = read_file.readline()
                    if i == 0 and first_line:
                        write_file.write(line)
                        first_line = False
                    if not line:
                        end = True
                        break
                for j in range(block_step):
                    line = read_file.readline()
                    write_file.write(line)
                    if not line:
                        end = True
                        break


def delete_random_string(input_file, output_file, probability):
    end = False
    with open(input_file, 'r') as read_file:
        with open(output_file, 'w') as write_file:
            while True:
                line = read_file.readline()
                if random.random() > probability:
                    write_file.write(line)
                if not line:
                    break


#EXPERIMETNS


input_data_file = "rpg_e2vid/data/events_txt/dynamic_6dof.txt"


def first_exp(in_params, output_directory):
    result = defaultdict(list)
    log.info("Запуск тестового протокола №1")
    for ind, param in enumerate(in_params):
        S = param[0]
        T = param[1]
        log.info(f"Тестовый протокол 1. Эксперимент № {ind} S={S}, T={T}")
        log.info(f"Создание тестового файла с параметрами S={S}, T={T}")
        out = f"{output_directory}_out_first_test_S_{S}_T_{T}.txt"
        delete_fixed_block(
            input_file=input_data_file,
            output_file=out,
            block_size=param[0],
            block_step=param[1])

        result["count_deleted_rows"].append(
            (ind, Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)))

    return result


def second_exp(in_params, output_directory):
    result = defaultdict(list)
    log.info("Запуск тестового протокола №2")
    for ind, param in enumerate(in_params):
        log.info(f"Тестовый протокол 2. Эксперимент № {ind} T={param}")
        log.info(f"Создание тестового файла с параметром T={param}")
        out = f"{output_directory}_T_{param}.txt"
        delete_fixed_block(
            input_file=input_data_file,
            output_file=out,
            block_size=1,
            block_step=param)

        result["count_deleted_rows"].append(
            (ind, Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)))
    return result


def third_exp(in_params, output_directory):
    result = defaultdict(list)
    log.info("Запуск тестового протокола №3")
    for ind, param in enumerate(in_params):
        log.info(f"Тестовый протокол 3. Эксперимент № {ind} T={param}")
        log.info(f"Создание тестового файла с параметром prob = {param}")
        out = f"{output_directory}_prob_{param}.txt"
        delete_random_string(
            input_file=input_data_file,
            output_file=out,
            probability=param
        )

        result["count_deleted_rows"].append(
            (ind, Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)))
    return result


def read_params_from_yaml(yaml_file):
    with open(yaml_file, 'r') as read_file:
        input_params = yaml.safe_load(read_file)
        return input_params


def add_out_file(directory):
    container = list()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            container.append(file_path)


def calculate_metrics(output_ideal_dataset_path, output_after_test_dataset_path):
    log.info(f"Вычисление метрик для тестового файла{output_after_test_dataset_path}:")

    rec_ideal_files = sorted(add_out_file(output_ideal_dataset_path))[:COUNT_OF_PROCESSED_IMAGES]
    rec_test_files = sorted(add_out_file(output_after_test_dataset_path))[:COUNT_OF_PROCESSED_IMAGES]

    metrics_res = defaultdict(list)

    for i in range(COUNT_OF_PROCESSED_IMAGES):
        mse_metric = Metrics.mse(rec_ideal_files[i], rec_test_files[i])
        metrics_res["mse"].append(mse_metric)

        ssim_metric = Metrics.ssim(rec_ideal_files[i], rec_test_files[i])
        metrics_res["ssim"].append(ssim_metric)

        lpips_metric = Metrics.lpips(rec_ideal_files[i], rec_test_files[i])
        metrics_res["lpips"].append(lpips_metric)

    return (Utils.get_median_metric(metrics_res["mse"]),
            Utils.get_median_metric(metrics_res["ssim"]),
            Utils.get_median_metric(metrics_res["lpips"]))


def create_zip_for_testing_events_files(intput, output_directory):
    for data_file in os.listdir(intput):
        file_name = data_file.split(".")[0]
        Utils.create_zip_archive(data_file, f"{output_directory}/{file_name}.zip")


def execute_models(events_directory, exp_number):
    for data_file in os.listdir(events_directory):
        try:
            log.info(f"Запуск модели на файле с событиями: {data_file} ")
            test_i = events_directory.split("/")[-1]
            subprocess.run(f"python rpg_e2vid/run_reconstruction.py \
                  -c rpg_e2vid/pretrained/E2VID_lightweight.pth.tar \
                  -i rpg_e2vid/zip/{events_directory}{data_file} \
                  --auto_hdr \
                  --output_folder rpg_e2vid/out/res/{exp_number}/{test_i} \
                  --fixed_duration")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Experiments",
        description="Script for do experiments",
    )
    parser.add_argument('input_file_parametrs')
    parser.add_argument('-f', '--first', action='store_true')
    parser.add_argument('-s', '--second', action='store_true')
    parser.add_argument('-t', '--third', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')

    args = parser.parse_args()

    params_file = args.input_file_parametrs

    ex = params_file.split('.')[-1]

    #TODO compose in def valid_param_file ?

    if ex is not 'yaml':
        log.error(f"Файл с параметрами должен быть с раширением yaml, but was: {ex}")
        exit(1)

    if not os.path.exists(params_file):
        log.error("Указанного файла не существует")
        exit(1)

    params = read_params_from_yaml(params_file)

    #TODO valid input params
    first_exp_params = list(map(Utils.map_to_tuple, params['test_1']))
    second_exp_params = list(map(Utils.map_to_tuple, params['test_2']))
    third_exp_params = list(map(Utils.map_to_tuple, params['test_3']))

    prepare_data()

    #execute experiments

    if args.all:
        log.info("Запуск трех тестовых протоколов...")
        res_1 = first_exp(first_exp_params, output_directory=params["/rpg_e2vid/data/events_txt/first/"])
        res_2 = second_exp(second_exp_params, output_directory=params["/rpg_e2vid/data/events_txt/second/"])
        res_3 = third_exp(third_exp_params, output_directory=params["/rpg_e2vid/data/events_txt/third"])

        log.info("Формирование zip файлов с измененными событиями")
        create_zip_for_testing_events_files("/rpg_e2vid/data/events_txt/first/", "/rpg_e2vid/zip/first/")
        create_zip_for_testing_events_files("/rpg_e2vid/data/events_txt/second/", "/rpg_e2vid/zip/second/")
        create_zip_for_testing_events_files("/rpg_e2vid/data/events_txt/third/", "/rpg_e2vid/zip/third/")

        for i, file in enumerate(os.listdir(params["/rpg_e2vid/zip/"])):
            execute_models(file, i)

    if args.first:
        log.info("Запуск первого тестового протокола")
        res_1 = first_exp(first_exp_params, output_directory=params["/rpg_e2vid/data/events_txt/first/"])
        create_zip_for_testing_events_files("/rpg_e2vid/data/events_txt/first/", "/rpg_e2vid/zip/first/")
        execute_models("/rpg_e2vid/zip/first/", 1)

    if args.second:
        log.info("Запуск второго тестового протокола")
        res_2 = second_exp(second_exp_params, output_directory=params["/rpg_e2vid/data/events_txt/second/"])
        create_zip_for_testing_events_files("/rpg_e2vid/data/events_txt/second/", "/rpg_e2vid/zip/second/")
        execute_models("/rpg_e2vid/zip/second/", 2)

    if args.third:
        log.info("Запуск третьего тестового протокола")
        res_3 = third_exp(third_exp_params, output_directory=params["/rpg_e2vid/data/events_txt/third"])
        create_zip_for_testing_events_files("/rpg_e2vid/data/events_txt/third/", "/rpg_e2vid/zip/third/")
        execute_models("/rpg_e2vid/zip/third/", 3)

        #exp result

    for test_number in os.listdir(params["/rpg_e2vid/out/res"]):
        mse = list()
        ssim = list()
        lpips = list()
        for res_file in os.listdir(params[f"/rpg_e2vid/out/res/{test_number}"]):
            res = calculate_metrics(output_ideal_dataset_path="/rpg_e2vid/out/input/reconstruction",
                                    output_after_test_dataset_path=f"/rpg_e2vid/out/res/{test_number}/{res_file}")

            mse.append(res[0])
            ssim.append(res[1])
            lpips.append(res[2])

            yaml_res = {
                'mse': mse,
                'ssim': ssim,
                'lpips': lpips,
            }

            with open(f'test_{test_number}_result', 'w') as f:
                yaml.dump(yaml_res, f)

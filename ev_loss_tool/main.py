import argparse
import subprocess
from utils import Utils
import os
import logging.config
from settings import LOGGING_CONFIG
import random

import yaml

# configure logger:
logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger("my_logger")
input_data_file = "events_txt/dynamic_6dof.txt"


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
    is_first_line = True
    with open(input_file, 'r') as read_file:
        with open(output_file, 'w') as write_file:
            while True:
                line = read_file.readline()
                if random.random() > probability or is_first_line:
                    write_file.write(line)
                if is_first_line:
                    is_first_line = False
                if not line:
                    break


def first_exp(in_params, output_directory):
    result = list()
    log.info("Запуск тестового протокола №1")
    for ind, param in enumerate(in_params):
        S = param[0]
        T = param[1]
        log.info(f"Тестовый протокол 1. Эксперимент № {ind} S={S}, T={T}")
        log.info(f"Создание тестового файла с параметрами S={S}, T={T}")
        out = f"{output_directory}out_first_test_S_{S}_T_{T}.txt"
        delete_fixed_block(
            input_file=input_data_file,
            output_file=out,
            block_size=param[0],
            block_step=param[1])

        proc = Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)
        log.info(proc)


def second_exp(in_params, output_directory):
    result = list()
    log.info("Запуск тестового протокола №2")
    for ind, param in enumerate(in_params):
        log.info(f"Тестовый протокол 2. Эксперимент № {ind} T={param}")
        log.info(f"Создание тестового файла с параметром T={param}")
        out = f"{output_directory}T_{param}.txt"
        delete_fixed_block(
            input_file=input_data_file,
            output_file=out,
            block_size=1,
            block_step=param)

        proc = Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)
        log.info(proc)

    return result


def third_exp(in_params, output_directory):
    result = list()
    log.info("Запуск тестового протокола №3")
    for ind, param in enumerate(in_params):
        log.info(f"Тестовый протокол 3. Эксперимент № {ind} T={param}")
        log.info(f"Создание тестового файла с параметром prob = {param}")
        out = f"{output_directory}prob_{str(param).replace('.', '_')}.txt"
        delete_random_string(
            input_file=input_data_file,
            output_file=out,
            probability=param
        )

        proc = Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)
        log.info(proc)

    return result


def prepare_data():
    if not os.path.exists('dynamic_6dof.zip'):
        log.info("Загрузка ")
        subprocess.run(
            "wget http://rpg.ifi.uzh.ch/data/E2VID/datasets/ECD_IJRR17/dynamic_6dof.zip".split(' '),
            capture_output=True,
            check=True)
        # subprocess.run('mv dynamic_6dof.zip rpg_e2vid/data/'.split(' '))
    else:
        log.warning("Датасет с событиями dynamic_6dof.zip уже загружен")

    if not os.path.exists('events_txt'):
        log.info("создание папки events_txt")
        subprocess.run("mkdir events_txt".split(' '), capture_output=True, check=True)

    if not os.path.exists('rpg_e2vid/data/events_txt/dynamic_6dof.txt'):
        log.info("Распаковка исходного датасета dynamic_6dof.zip")
        Utils.extract_archive("dynamic_6dof.zip", "events_txt/")


def read_params_from_yaml(yaml_file):
    with open(yaml_file, 'r') as read_file:
        input_params = yaml.safe_load(read_file)
        return input_params


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="EV_LOSS_TOOL",
        description="Prepare data for experiments",
    )

    parser.add_argument('input_file_parametrs')
    parser.add_argument('-f', '--first', action='store_true')
    parser.add_argument('-s', '--second', action='store_true')
    parser.add_argument('-t', '--third', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')

    args = parser.parse_args()

    params_file = args.input_file_parametrs

    ex = params_file.split('.')[-1]

    # TODO compose in def valid_param_file ?

    if ex != 'yaml':
        log.error(f"Файл с параметрами должен быть с раширением yaml, but was: {ex}")
        exit(1)

    if not os.path.exists(params_file):
        log.error("Указанного файла не существует")
        exit(1)

    params = read_params_from_yaml(params_file)

    # TODO valid input params
    first_exp_params = list(map(Utils.map_to_tuple, params['test_1']))
    second_exp_params = params['test_2']
    third_exp_params = params['test_3']

    prepare_data()

    if args.first:
        log.info("Подгтовка данных для первого тестового протокола")
        first_exp(first_exp_params, output_directory="events_txt/first/")

    if args.all:
        log.info("Запуск генерации файлов для всех экспериментов...")
        first_exp(first_exp_params, output_directory="rpg_e2vid/data/events_txt/first/")
        second_exp(second_exp_params, output_directory="rpg_e2vid/data/events_txt/second/")
        third_exp(third_exp_params, output_directory="rpg_e2vid/data/events_txt/third")

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
import re
from ExperimentResult import ExperimentResult
#prepare data:

#configure logger:
logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger("my_logger")
global res_1
global res_2
global res_3

def prepare_data():
    try:
        # download git repo
        log.info("Подготовка данных")
        if not os.path.exists('rpg_e2vid/'):
            log.info("клонирование репозитория RomanNechaev/rpg_e2vid.git ")
            subprocess.run("git clone https://github.com/RomanNechaev/rpg_e2vid.git".split(' '), capture_output=True, check=True)
        else:
            log.warning("репозиторий уже загружен")

        # download model
        if not os.path.exists('rpg_e2vid/pretrained/E2VID_lightweight.pth.tar'):
            log.info("Загрузка модели E2VID_lightweight.pth.tar")
            subprocess.run(
                "wget http://rpg.ifi.uzh.ch/data/E2VID/models/E2VID_lightweight.pth.tar".split(' '),
                capture_output=True,
                check=True)
            subprocess.run('mv E2VID_lightweight.pth.tar rpg_e2vid/pretrained/'.split(' '))
        else:
            log.warning("Модель уже E2VID_lightweight.pth.tar уже загружена")

        # download dataset
        if not os.path.exists('rpg_e2vid/data/dynamic_6dof.zip'):
            log.info("Загрузка ")
            subprocess.run(
                "wget http://rpg.ifi.uzh.ch/data/E2VID/datasets/ECD_IJRR17/dynamic_6dof.zip".split(' '),
                capture_output=True,
                check=True)
            subprocess.run('mv dynamic_6dof.zip rpg_e2vid/data/'.split(' '))
        else:
            log.warning("Датасет с событиями dynamic_6dof.zip уже загружен")

        if not os.path.exists('rpg_e2vid/data/events_txt'):
            log.info("создание папки events_txt")
            subprocess.run("mkdir rpg_e2vid/data/events_txt".split(' '), capture_output=True, check=True)

        if not os.path.exists('rpg_e2vid/data/events_txt/dynamic_6dof.txt'):
            log.info("Распаковка исходного датасета dynamic_6dof.zip")
            Utils.extract_archive("rpg_e2vid/data/dynamic_6dof.zip", "rpg_e2vid/data/events_txt/")

        if not os.path.exists('rpg_e2vid/zip/'):
            log.info('create zip folder')
            subprocess.run('mkdir rpg_e2vid/zip'.split(' '), capture_output=True, check= True)

        if not os.path.exists('rpg_e2vid/zip/first'):
            log.info('create zip/first folder')
            subprocess.run('mkdir rpg_e2vid/zip/first'.split(' '), capture_output=True, check= True)

        if not os.path.exists('rpg_e2vid/zip/second'):
            log.info('create zip/second folder')
            subprocess.run('mkdir rpg_e2vid/zip/second'.split(' '), capture_output=True, check= True)

        if not os.path.exists('rpg_e2vid/zip/third'):
            log.info('create zip/third folder')
            subprocess.run('mkdir rpg_e2vid/zip/third'.split(' '), capture_output=True, check= True)

        if not os.path.exists('rpg_e2vid/data/events_txt/first/'):
            subprocess.run('mkdir rpg_e2vid/data/events_txt/first/'.split(' '))

        if not os.path.exists('rpg_e2vid/data/events_txt/second/'):
            subprocess.run('mkdir rpg_e2vid/data/events_txt/second/'.split(' '))

        if not os.path.exists('rpg_e2vid/data/events_txt/third/'):
            subprocess.run('mkdir rpg_e2vid/data/events_txt/third/'.split(' '))
    except subprocess.CalledProcessError as e:
        log.error(e)

    #run model with default parametrs
    if not os.path.exists('rpg_e2vid/out/input/'):
        try:
            log.info("Запуск E2VID")
            t = list(filter(lambda x: x!='\n' and x!='',
              """python rpg_e2vid/run_reconstruction.py -c rpg_e2vid/pretrained/E2VID_lightweight.pth.tar -i rpg_e2vid/data/dynamic_6dof.zip --auto_hdr --output_folder rpg_e2vid/out/input --fixed_duration"""
            .split(' ')))
            print(t)
            subprocess.run(t)
        except subprocess.CalledProcessError as e:
            log.error(e)
        #extract zip_file with events


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


#EXPERIMETNS


input_data_file = "rpg_e2vid/data/events_txt/dynamic_6dof.txt"


def create_zip_for_testing_events_files(input_f, output_directory):
    for data_file in os.listdir(input_f):
        file_name = data_file.split(".")[0]
        print(f"{input_f}{data_file}")
        Utils.create_zip_archive(f"{input_f}{data_file}", f"{output_directory}{file_name}.zip")
        return f"{output_directory}{file_name}.zip"


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
                    
        out_path = create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/first/", "rpg_e2vid/zip/first/")
        
        proc = Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)

        execute_models("rpg_e2vid/zip/first/", 1)

        for res_file in os.listdir(f"rpg_e2vid/out/res/1/"):
            res = calculate_metrics(output_ideal_dataset_path="rpg_e2vid/out/input/reconstruction/",
                                    output_after_test_dataset_path=f"rpg_e2vid/out/res/1/{res_file}/reconstruction/") 
                                    
            result.append(ExperimentResult(
                name=res_file,
                proc=proc,
                mse=res[0],
                ssim=res[1],
                lpips=res[2]
            ))

        try:
            os.remove(out_path)
            # subprocess.run(f"rm -rf {out_path}", capture_output=True, check=True)
           # subprocess.run(f"rm -rf {re}", capture_output=True, check=True)
            subprocess.run(f'rm -rf rpg_e2vid/out/res/1/{res_file}'.split(' '))
            #os.remove(f'rpg_e2vid/out/res/1/{res_file}')
            # subprocess.run(f"rm -rf rpg_e2vid/out/res/1/{res_file}")
            subprocess.run(f"rm -rf {out}".split(' '))
        except subprocess.CalledProcessError as e:
            log.error(e)

    return result



# def first_exp(in_params, output_directory):
    # result = defaultdict(list)
    # log.info("Запуск тестового протокола №1")
    # for ind, param in enumerate(in_params):
        # S = param[0]
        # T = param[1]
        # log.info(f"Тестовый протокол 1. Эксперимент № {ind} S={S}, T={T}")
        # log.info(f"Создание тестового файла с параметрами S={S}, T={T}")
        # out = f"{output_directory}out_first_test_S_{S}_T_{T}.txt"
        # delete_fixed_block(
            # input_file=input_data_file,
            # output_file=out,
            # block_size=param[0],
            # block_step=param[1])

        # result["count_deleted_rows"].append(
            # (ind, Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)))

    # return result


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
                    
        out_path = create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/second/", "rpg_e2vid/zip/second/")
        
        proc = Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)

        execute_models("rpg_e2vid/zip/second/", 2)

        for res_file in os.listdir(f"rpg_e2vid/out/res/2/"):
            res = calculate_metrics(output_ideal_dataset_path="rpg_e2vid/out/input/reconstruction/",
                                    output_after_test_dataset_path=f"rpg_e2vid/out/res/2/{res_file}/reconstruction/") 
                                    
            result.append(ExperimentResult(
                name=res_file,
                proc=proc,
                mse=res[0],
                ssim=res[1],
                lpips=res[2]
            ))

        try:
            os.remove(out_path)
            # subprocess.run(f"rm -rf {out_path}", capture_output=True, check=True)
           # subprocess.run(f"rm -rf {re}", capture_output=True, check=True)
            subprocess.run(f'rm -rf rpg_e2vid/out/res/2/{res_file}'.split(' '))
            #os.remove(f'rpg_e2vid/out/res/1/{res_file}')
            # subprocess.run(f"rm -rf rpg_e2vid/out/res/1/{res_file}")
            subprocess.run(f"rm -rf {out}".split(' '))
        except subprocess.CalledProcessError as e:
            log.error(e)

    return result


def third_exp(in_params, output_directory):
    result = list()
    log.info("Запуск тестового протокола №3")
    for ind, param in enumerate(in_params):
        log.info(f"Тестовый протокол 3. Эксперимент № {ind} T={param}")
        log.info(f"Создание тестового файла с параметром prob = {param}")
        out = f"{output_directory}prob_{str(param).replace('.','_')}.txt"
        delete_random_string(
            input_file=input_data_file,
            output_file=out,
            probability=param
        )
                    
        out_path = create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/third/", "rpg_e2vid/zip/third/")
        
        proc = Utils.calculate_removed_rows_percentage(input_file=input_data_file, output_file=out)

        execute_models("rpg_e2vid/zip/third/", 3)

        for res_file in os.listdir(f"rpg_e2vid/out/res/3/"):
            res = calculate_metrics(output_ideal_dataset_path="rpg_e2vid/out/input/reconstruction/",
                                    output_after_test_dataset_path=f"rpg_e2vid/out/res/3/{res_file}/reconstruction/") 
                                    
            result.append(ExperimentResult(
                name=res_file,
                proc=proc,
                mse=res[0],
                ssim=res[1],
                lpips=res[2]
            ))

        try:
            os.remove(out_path)
            # subprocess.run(f"rm -rf {out_path}", capture_output=True, check=True)
           # subprocess.run(f"rm -rf {re}", capture_output=True, check=True)
            subprocess.run(f'rm -rf rpg_e2vid/out/res/3/{res_file}'.split(' '))
            #os.remove(f'rpg_e2vid/out/res/1/{res_file}')
            # subprocess.run(f"rm -rf rpg_e2vid/out/res/1/{res_file}")
            subprocess.run(f"rm -rf {out}".split(' '))
        except subprocess.CalledProcessError as e:
            log.error(e)

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
    return container


def calculate_metrics(output_ideal_dataset_path, output_after_test_dataset_path):
    log.info(f"Вычисление метрик для тестового файла{output_after_test_dataset_path}:")
    if(len(os.listdir(output_after_test_dataset_path))<10):
        log.info('len < 10')
        return
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




def extract_num(s):
    return [int(num) for num in re.findall(r'\d+', s)]


def execute_models(events_directory, exp_number):
    for data_file in os.listdir(events_directory):
        try:
            log.info(f"Запуск модели на файле с событиями: {data_file} ")
            subprocess.run(list(filter(lambda x: x!= '\n' and x!='',
                  f"""python rpg_e2vid/run_reconstruction.py -c rpg_e2vid/pretrained/E2VID_lightweight.pth.tar -i {events_directory}{data_file} --auto_hdr --output_folder rpg_e2vid/out/res/{exp_number}/{data_file.split('.')[0]} --fixed_duration"""
                  .split(' '))))
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

    if ex != 'yaml':
        log.error(f"Файл с параметрами должен быть с раширением yaml, but was: {ex}")
        exit(1)

    if not os.path.exists(params_file):
        log.error("Указанного файла не существует")
        exit(1)

    params = read_params_from_yaml(params_file)

    #TODO valid input params
    first_exp_params = list(map(Utils.map_to_tuple, params['test_1']))
    second_exp_params = params['test_2']
    third_exp_params =  params['test_3']

    prepare_data()

    #execute experiments

    if args.all:
        log.info("Запуск трех тестовых протоколов...")
        res_1 = first_exp(first_exp_params, output_directory="rpg_e2vid/data/events_txt/first/")
        res_2 = second_exp(second_exp_params, output_directory="rpg_e2vid/data/events_txt/second/")
        res_3 = third_exp(third_exp_params, output_directory="rpg_e2vid/data/events_txt/third")
        
        
        with open('test_1_result.yaml', 'w') as f:
            values = [{'file_name': result.name, 'frac': result.proc, 'mse':result.mse, 'ssim': result.ssim, 'lpips':result.lpips } for result in res_1]
            yaml.dump(values, f)
        
        with open('test_2_result.yaml', 'w') as f:
            values = [{'file_name': result.name, 'frac': result.proc, 'mse':result.mse, 'ssim': result.ssim, 'lpips':result.lpips } for result in res_2]
            yaml.dump(values, f)
        
        with open('test_3_result.yaml', 'w') as f:
            values = [{'file_name': result.name, 'frac': result.proc, 'mse':result.mse, 'ssim': result.ssim, 'lpips':result.lpips } for result in res_3]
            yaml.dump(values, f)
        

        # log.info("Формирование zip файлов с измененными событиями")
        # create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/first/", "rpg_e2vid/zip/first/")
        # create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/second/", "rpg_e2vid/zip/second/")
        # create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/third/", "rpg_e2vid/zip/third/")

        # for i, file in enumerate(os.listdir(params["rpg_e2vid/zip/"])):
            # execute_models(file, i)

    if args.first:
        log.info("Запуск первого тестового протокола")
        res_1 = first_exp(first_exp_params, output_directory="rpg_e2vid/data/events_txt/first/")
        
        with open('test_1_result.yaml', 'w') as f:
            values = [{'file_name': result.name, 'frac': result.proc, 'mse':result.mse, 'ssim': result.ssim, 'lpips':result.lpips } for result in res_1]
            yaml.dump(values, f)
        #res_1 = first_exp(first_exp_params, output_directory="rpg_e2vid/data/events_txt/first/")
        #log.info(f"res_1 is {res_1}")
        #log.info("create zip")
        #create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/first/", "rpg_e2vid/zip/first/")
        #execute_models("rpg_e2vid/zip/first/", 1)

    if args.second:
        log.info("Запуск второго тестового протокола")
        res_2 = second_exp(second_exp_params, output_directory="rpg_e2vid/data/events_txt/second/")
        
        with open('test_2_result.yaml', 'w') as f:
            values = [{'file_name': result.name, 'frac': result.proc, 'mse':result.mse, 'ssim': result.ssim, 'lpips':result.lpips } for result in res_2]
            yaml.dump(values, f)
        # log.info("create zip")
        # create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/second/", "rpg_e2vid/zip/second/")
        # execute_models("rpg_e2vid/zip/second/", 2)

    if args.third:
        log.info("Запуск третьего тестового протокола")
        res_3 = third_exp(third_exp_params, output_directory="rpg_e2vid/data/events_txt/third/")
        
        with open('test_3_result.yaml', 'w') as f:
            values = [{'file_name': result.name, 'frac': result.proc, 'mse':result.mse, 'ssim': result.ssim, 'lpips':result.lpips } for result in res_3]
            yaml.dump(values, f)
        # log.info("create zip")
        # create_zip_for_testing_events_files("rpg_e2vid/data/events_txt/third/", "rpg_e2vid/zip/third/")
        # execute_models("rpg_e2vid/zip/third/", 3)

        #exp result
    # log.info('result calc')
    # for test_number in os.listdir("rpg_e2vid/out/res"):
       # mse = list()
       # ssim = list()
       # lpips = list()
       # sorted_l = sorted(os.listdir(f"rpg_e2vid/out/res/{test_number}/"),key=lambda x: extract_num(x))
       # for res_file in sorted_l:
           # if res_file == 'prob_0_65':
               # break
           # res = calculate_metrics(output_ideal_dataset_path="rpg_e2vid/out/input/reconstruction/",
                                   # output_after_test_dataset_path=f"rpg_e2vid/out/res/{test_number}/{res_file}/reconstruction/")
           # print(res)
            # print(type(res[0]))
            # mse.append(res[0])
            # ssim.append(res[1])
            # lpips.append(res[2])
            # out = []

            # print(f'test number {test_number}')

            # if(test_number=='1'):
               # out = list(res_1['count_deleted_rows'])
            # if(test_number=='2'):
               # out = list(res_2['count_deleted_rows'])
         # #   if(test_number=='3'):
          # #     out = list(res_3['count_deleted_rows'])
            # log.info(f'out {out}')
            # log.info(mse)
            # print(type(mse))
            # mse_1 = [val for val in mse]
            # log.info(ssim)
            # log.info(lpips)
            # yaml_res = {
                # 'res_file': res_file,
                # 'mse': mse_1,
                # 'ssim': ssim,
                # 'lpips': lpips,
            # }

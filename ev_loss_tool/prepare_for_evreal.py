import os
import shutil
import subprocess
def prepare_for_evreal(source_dir, target_dir):
    if not os.path.exists(source_dir):
        print(f"Ошибка: Папка-источник '{source_dir}' не существует.")
        return

    os.makedirs(target_dir, exist_ok=True)

    for item_name in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item_name)
        target_path = os.path.join(target_dir, item_name)

        if os.path.isdir(source_path):  # Если это папка, перемещаем всю директорию
            shutil.move(source_path, target_path)
            print(f"Папка {item_name} перемещена в {target_dir}")
        elif os.path.isfile(source_path):  # Если это файл, перемещаем файл
            shutil.move(source_path, target_path)
            print(f"Файл {item_name} перемещен в {target_dir}")



if __name__ == "__main__":
    prepare_for_evreal("events_txt/first/", "../code/evreal_test/")

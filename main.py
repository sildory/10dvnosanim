"""Главный скрипт запуска и диспетчеризации проектов рендера."""

import sys
import os
import argparse
import importlib

# Добавляем текущую директорию в путь импорта
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import bpy
from engine.render import clear_scene, execute_render


def parse_arguments():
    """Корректно извлекает аргументы как при прямом запуске, так и через blender -b -P."""
    raw_args = sys.argv
    if "--" in raw_args:
        cli_args = raw_args[raw_args.index("--") + 1:]
    else:
        cli_args = raw_args[1:]

    parser = argparse.ArgumentParser(description="3DVNOSANIM // Кинематографический рендер-движок")
    parser.add_argument("--project", type=str, default="test_studio", help="Имя проекта из папки projects")
    parser.add_argument("--start", type=int, default=1, help="Начальный кадр")
    parser.add_argument("--end", type=int, default=60, help="Конечный кадр")
    parser.add_argument("--step", type=int, default=1, help="Шаг кадров")
    parser.add_argument("--profile", type=str, default="4k", choices=["preview", "fullhd", "4k"], help="Профиль рендера")
    parser.add_argument("--samples", type=int, default=None, help="Переопределение числа сэмплов")
    parser.add_argument("--output", type=str, default="output/frames", help="Папка вывода PNG-кадров")

    return parser.parse_args(cli_args)


def main():
    args = parse_arguments()

    print("\n" + "=" * 65)
    print(f"      3DVNOSANIM // ЗАПУСК ПРОЕКТА: {args.project.upper()}")
    print("=" * 65)

    # 1. Очистка старой дефолтной геометрии Blender
    clear_scene()

    # 2. Динамическая загрузка сцены из projects/<project_name>/scene.py
    module_path = f"projects.{args.project}.scene"
    try:
        scene_module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        print(f"[FATAL] Не удалось загрузить модуль сцены '{module_path}': {e}")
        sys.exit(1)

    if not hasattr(scene_module, "build_scene"):
        print(f"[FATAL] В модуле '{module_path}' отсутствует функция build_scene()!")
        sys.exit(1)

    # 3. Построение 3D сцены
    print(f"[+] Сборка 3D-сцены: {args.project}...")
    scene_module.build_scene()

    # 4. Рендер указанного диапазона кадров
    current_scene = bpy.context.scene
    execute_render(
        scene=current_scene,
        output_dir=args.output,
        start_frame=args.start,
        end_frame=args.end,
        profile_name=args.profile,
        samples_override=args.samples,
        step=args.step
    )


if __name__ == "__main__":
    main()

"""
Главный исполнительный скрипт 3DVNOSANIM.
Поддерживает запуск:
  1) Напрямую через Python:  python main.py --project test_studio [args]
  2) Через бинарник Blender: blender -b -P main.py -- --project test_studio [args]
"""

import sys
import os
import argparse
import importlib
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    import bpy
except ModuleNotFoundError:
    print("\n[FATAL] Модуль 'bpy' не найден.")
    print("Установите bpy через pip ('pip install bpy==4.2.0')")
    print("или запустите скрипт через Blender: 'blender -b -P main.py -- [args]'\n")
    sys.exit(1)

from engine.assets import get_asset_manager
from engine.render import clear_scene, execute_render


def parse_arguments():
    raw_args = sys.argv
    if "--" in raw_args:
        cli_args = raw_args[raw_args.index("--") + 1:]
    else:
        cli_args = raw_args[1:]

    parser = argparse.ArgumentParser(description="3DVNOSANIM Cinematic Engine")
    parser.add_argument(
        "--project",
        type=str,
        default="test_studio",
        help="Имя проекта из каталога projects (например: test_studio)"
    )
    parser.add_argument(
        "--episode",
        type=str,
        default=None,
        help="Обратная совместимость: имя эпизода из каталога episodes"
    )
    parser.add_argument("--start", type=int, default=1, help="Начальный кадр диапазона")
    parser.add_argument("--end", type=int, default=60, help="Конечный кадр диапазона")
    parser.add_argument("--step", type=int, default=1, help="Шаг рендера кадров")
    parser.add_argument(
        "--profile",
        type=str,
        default="preview",
        choices=["preview", "fullhd", "4k"],
        help="Профиль рендера (preview, fullhd, 4k)"
    )
    parser.add_argument("--samples", type=int, default=None, help="Переопределение числа сэмплов Cycles")
    parser.add_argument("--output", type=str, default="output/frames", help="Каталог сохранения кадров")

    return parser.parse_args(cli_args)


def load_project_module(project_name: str, episode_name: str = None):
    candidates = []
    if project_name:
        candidates.append(f"projects.{project_name}.scene")
        candidates.append(f"projects.{project_name}")
    if episode_name:
        candidates.append(f"episodes.{episode_name}")

    for target in candidates:
        try:
            mod = importlib.import_module(target)
            return mod, target
        except ModuleNotFoundError:
            continue

    print(f"\n[FATAL] Не удалось загрузить проект '{project_name}'. Перебраны пути: {candidates}")
    sys.exit(1)


def check_and_fetch_manifest(project_name: str):
    """Автоматически находит и загружает manifest.json проекта перед построением сцены."""
    manifest_path = os.path.join(CURRENT_DIR, "projects", project_name, "manifest.json")
    if os.path.isfile(manifest_path):
        print(f"[ENGINE] Обнаружен манифест ассетов: {manifest_path}")
        asset_mgr = get_asset_manager()
        asset_mgr.fetch_from_manifest(manifest_path)


def main():
    args = parse_arguments()
    active_target = args.project if args.project else args.episode

    print("\n" + "=" * 70)
    print(f"      3DVNOSANIM // ПОСТАНОВКА ПРОЕКТА: {str(active_target).upper()}")
    print("=" * 70)

    # 1. Фиксация детерминизма
    random.seed(42)

    # 2. Очистка сцены
    clear_scene()

    # 3. Автоматическая синхронизация ассетов по manifest.json (если есть)
    if args.project:
        check_and_fetch_manifest(args.project)

    # 4. Динамическая загрузка сценария
    module, loaded_path = load_project_module(args.project, args.episode)
    print(f"[ENGINE] Успешно подключен модуль: {loaded_path}")

    # 5. Сборка сцены
    if hasattr(module, "build_scene"):
        module.build_scene()
    elif hasattr(module, "build"):
        module.build()
    else:
        print(f"[FATAL] В модуле '{loaded_path}' не найдена функция build_scene() или build().")
        sys.exit(1)

    # 6. Запуск рендера
    execute_render(
        scene=bpy.context.scene,
        output_dir=args.output,
        start_frame=args.start,
        end_frame=args.end,
        profile_name=args.profile,
        samples_override=args.samples,
        step=args.step
    )


if __name__ == "__main__":
    main() 

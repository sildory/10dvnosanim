"""
Главный исполнительный скрипт 3DVNOSANIM.
Поддерживает запуск:
  1) Напрямую через Python:  python main.py --episode ep01_bay [args]
  2) Через бинарник Blender: blender -b -P main.py -- --episode ep01_bay [args]
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
        "--episode",
        type=str,
        default="ep01_bay",
        help="Имя эпизода из каталога episodes/ (например: ep01_bay)"
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Альтернативный путь/проект (например: test_studio или my_scene)"
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
    parser.add_argument("--samples", type=int, default=None, help="Переопределение сэмплов Cycles")
    parser.add_argument("--output", type=str, default="output/frames", help="Каталог сохранения кадров")

    return parser.parse_args(cli_args)


def load_target_module(target_name: str):
    """Ищет модуль в папках episodes и projects."""
    candidates = [
        f"episodes.{target_name}",
        f"projects.{target_name}.scene",
        f"projects.{target_name}",
        target_name
    ]

    for candidate in candidates:
        try:
            mod = importlib.import_module(candidate)
            return mod, candidate
        except ModuleNotFoundError:
            continue

    print(f"\n[FATAL] Не удалось загрузить сценарий '{target_name}'. Перебраны пути: {candidates}")
    sys.exit(1)


def sync_manifest_if_exists(target_name: str):
    """Проверяет наличие manifest.json в projects/<target> или episodes/."""
    candidates = [
        os.path.join(CURRENT_DIR, "projects", target_name, "manifest.json"),
        os.path.join(CURRENT_DIR, "episodes", f"{target_name}.manifest.json"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            print(f"[ENGINE] Обнаружен манифест ассетов: {path}")
            get_asset_manager().fetch_from_manifest(path)
            return


def main():
    args = parse_arguments()
    target_name = args.project if args.project else args.episode

    print("\n" + "=" * 70)
    print(f"      3DVNOSANIM // ПОСТАНОВКА СЦЕНЫ: {str(target_name).upper()}")
    print("=" * 70)

    random.seed(42)

    # 1. Безопасная очистка сцены
    clear_scene()

    # 2. Гарантируем наличие рабочей коллекции
    if bpy.context.scene.collection not in bpy.context.view_layer.layer_collection.collection.children.values():
        if len(bpy.data.collections) == 0:
            main_col = bpy.data.collections.new("Scene_Collection")
            bpy.context.scene.collection.children.link(main_col)

    # 3. Синхронизация манифеста (если существует)
    sync_manifest_if_exists(target_name)

    # 4. Загрузка сценария
    module, loaded_path = load_target_module(target_name)
    print(f"[ENGINE] Подключен модуль сценария: {loaded_path}")

    # 5. Построение сцены
    if hasattr(module, "build"):
        module.build()
    elif hasattr(module, "build_scene"):
        module.build_scene()
    else:
        print(f"[FATAL] В модуле '{loaded_path}' отсутствует функция build() или build_scene().")
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

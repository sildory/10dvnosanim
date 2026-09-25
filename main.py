"""
Главный исполнительный скрипт 3DVNOSANIM.
Поддерживает запуск:
  1) Напрямую через Python:  python main.py --episode ep01_anticipation [args]
  2) Через бинарник Blender: blender -b -P main.py -- --episode ep01_anticipation [args]
"""

import sys
import os
import argparse
import importlib
import traceback
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
        default="ep01_anticipation",
        help="Имя эпизода из каталога episodes/ (например: ep01_anticipation)"
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Альтернативный путь/проект"
    )
    parser.add_argument("--start", type=int, default=1, help="Начальный кадр диапазона")
    parser.add_argument("--end", type=int, default=180, help="Конечный кадр диапазона")
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
    """Ищет модуль в папке episodes/ с понятным выводом доступных вариантов."""
    if target_name.endswith(".py"):
        target_name = target_name[:-3]

    episodes_dir = os.path.join(CURRENT_DIR, "episodes")
    available_episodes = []
    if os.path.isdir(episodes_dir):
        available_episodes = [
            f[:-3] for f in os.listdir(episodes_dir)
            if f.endswith(".py") and not f.startswith("__")
        ]

    episode_path = os.path.join(episodes_dir, f"{target_name}.py")
    if os.path.isfile(episode_path):
        module_name = f"episodes.{target_name}"
        try:
            mod = importlib.import_module(module_name)
            return mod, module_name
        except Exception:
            print(f"\n[FATAL] Ошибка синтаксиса или логики внутри '{episode_path}':")
            traceback.print_exc()
            sys.exit(1)

    try:
        mod = importlib.import_module(target_name)
        return mod, target_name
    except Exception:
        pass

    print("\n" + "!" * 72)
    print(f" [ОШИБКА] Эпизод с именем '{target_name}' НЕ НАЙДЕН!")
    print("!" * 72)
    print(" Доступные готовые эпизоды в папке episodes/:")
    for ep in sorted(available_episodes):
        print(f"   -> {ep}")
    print("\n Пожалуйста, укажите одно из доступных имен.")
    print("!" * 72 + "\n")
    sys.exit(1)


def sync_manifest_if_exists(target_name: str):
    """Проверяет наличие manifest.json в папке episodes/."""
    candidates = [
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

    clear_scene()

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection

    sync_manifest_if_exists(target_name)

    module, loaded_path = load_target_module(target_name)
    print(f"[ENGINE] Подключен модуль сценария: {loaded_path}")

    if hasattr(module, "build"):
        module.build()
    elif hasattr(module, "build_scene"):
        module.build_scene()
    else:
        print(f"[FATAL] В модуле '{loaded_path}' отсутствует функция build() или build_scene().")
        sys.exit(1)

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

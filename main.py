"""Главный исполнительный скрипт запуска эпизодов 3DVNOSANIM."""

import sys
import os
import argparse
import importlib

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import bpy
from engine.render import clear_scene, execute_render


def parse_arguments():
    raw_args = sys.argv
    cli_args = raw_args[raw_args.index("--") + 1:] if "--" in raw_args else raw_args[1:]

    parser = argparse.ArgumentParser(description="3DVNOSANIM Cinematic Engine")
    parser.add_argument("--episode", type=str, default="ep01_bay", help="Имя эпизода из папки episodes (например: ep01_bay)")
    parser.add_argument("--start", type=int, default=1, help="Начальный кадр")
    parser.add_argument("--end", type=int, default=360, help="Конечный кадр")
    parser.add_argument("--step", type=int, default=1, help="Шаг кадров")
    parser.add_argument("--profile", type=str, default="preview", choices=["preview", "fullhd", "4k"], help="Профиль рендера")
    parser.add_argument("--samples", type=int, default=None, help="Переопределение сэмплов")
    parser.add_argument("--output", type=str, default="output/frames", help="Папка вывода")

    return parser.parse_args(cli_args)


def main():
    args = parse_arguments()

    print("\n" + "=" * 65)
    print(f"      3DVNOSANIM // ПОСТАНОВКА ЭПИЗОДА: {args.episode.upper()}")
    print("=" * 65)

    clear_scene()

    # Загрузка сценария эпизода из episodes/<name>.py
    module_path = f"episodes.{args.episode}"
    try:
        episode_module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        print(f"[FATAL] Эпизод '{module_path}' не найден: {e}")
        sys.exit(1)

    print(f"[+] Инициализация режиссерского сценария: {args.episode}...")
    episode_module.build()

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

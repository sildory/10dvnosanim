"""Модуль исполнения рендера и управления диапазонами кадров."""

import os
import time
import bpy
from engine.settings import apply_cycles_settings


def clear_scene():
    """Полностью очищает сцену от дефолтных кубов, ламп и камер."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def execute_render(
    scene: bpy.types.Scene,
    output_dir: str,
    start_frame: int,
    end_frame: int,
    profile_name: str = "4k",
    samples_override: int = None,
    step: int = 1
):
    """Конфигурирует сцену и рендерит указанный диапазон кадров."""
    os.makedirs(output_dir, exist_ok=True)

    apply_cycles_settings(scene, profile_name=profile_name, samples_override=samples_override)

    scene.frame_start = start_frame
    scene.frame_end = end_frame
    scene.frame_step = step

    total_frames = (end_frame - start_frame) // step + 1
    print(f"\n[ENGINE] Старт рендера: кадры [{start_frame}..{end_frame}] (шаг: {step}, всего: {total_frames})")
    print(f"[ENGINE] Профиль: {profile_name} | Сэмплы: {scene.cycles.samples} | Разрешение: {scene.render.resolution_x}x{scene.render.resolution_y}")

    t_start = time.time()

    for current_frame in range(start_frame, end_frame + 1, step):
        frame_t0 = time.time()
        scene.frame_set(current_frame)

        target_path = os.path.join(output_dir, f"frame_{current_frame:04d}.png")
        scene.render.filepath = target_path

        bpy.ops.render.render(write_still=True)
        frame_time = time.time() - frame_t0
        print(f"[CYCLES] Кадр {current_frame:04d}/{end_frame:04d} отрендерен за {frame_time:.2f} сек. -> {os.path.basename(target_path)}")

    total_time = time.time() - t_start
    print(f"[ENGINE] Успешно! Диапазон отрендерен за {total_time: .1f} сек.\n")

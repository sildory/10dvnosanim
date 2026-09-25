"""Модуль исполнения рендера и управления диапазонами кадров."""

import os
import time
import bpy
from engine.settings import apply_cycles_settings


def clear_scene():
    """Безопасно и полностью очищает сцену, текстуры и действия Blender."""
    if bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # Удаление всех объектов
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # Очистка всех блоков данных для предотвращения утечек памяти
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam, do_unlink=True)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve, do_unlink=True)
    for img in list(bpy.data.images):
        bpy.data.images.remove(img, do_unlink=True)
    for act in list(bpy.data.actions):
        bpy.data.actions.remove(act, do_unlink=True)

    # Очистка маркеров таймлайна
    if bpy.context.scene:
        bpy.context.scene.timeline_markers.clear()


def update_camera_for_frame(scene: bpy.types.Scene, frame: int):
    """
    Гарантирует переключение активной камеры в headless-режиме (без GUI)
    на основе маркеров шотов таймлайна.
    """
    valid_markers = [
        m for m in scene.timeline_markers
        if m.camera is not None and m.frame <= frame
    ]
    if valid_markers:
        active_marker = max(valid_markers, key=lambda m: m.frame)
        if scene.camera != active_marker.camera:
            scene.camera = active_marker.camera
    elif scene.camera is None:
        for obj in scene.objects:
            if obj.type == "CAMERA":
                scene.camera = obj
                break


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
        target_path = os.path.join(output_dir, f"frame_{current_frame:04d}.png")
        if os.path.isfile(target_path) and os.path.getsize(target_path) > 1024:
            print(f"[CYCLES] Кадр {current_frame:04d} уже есть на диске, пропуск.")
            continue

        frame_t0 = time.time()
        scene.frame_set(current_frame)

        # Гарантированное переключение камеры для текущего кадра
        update_camera_for_frame(scene, current_frame)

        if scene.camera is None:
            raise RuntimeError(f"[FATAL] В сцене отсутствует активная камера на кадре {current_frame}!")

        scene.render.filepath = target_path

        bpy.ops.render.render(write_still=True)
        frame_time = time.time() - frame_t0
        cam_name = scene.camera.name if scene.camera else "Unknown"
        print(f"[CYCLES] Кадр {current_frame:04d}/{end_frame:04d} [{cam_name}] отрендерен за {frame_time:.2f} сек. -> {os.path.basename(target_path)}")

    total_time = time.time() - t_start
    print(f"[ENGINE] Успешно! Диапазон отрендерен за {total_time:.1f} сек.\n")

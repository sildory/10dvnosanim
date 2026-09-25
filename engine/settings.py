"""Модуль глобальных настроек рендера и конфигурации движка Cycles (High-Performance CPU)."""

import bpy

PROFILES = {
    # Сверхбыстрый профиль для валидации (кадр за 2-4 секунды)
    "preview": {
        "resolution_x": 960,
        "resolution_y": 540,
        "samples": 16,
        "adaptive_threshold": 0.08,
        "use_denoising": True,
        "motion_blur": False,
        "fps": 30,
    },
    # Высокое качество для Full HD
    "fullhd": {
        "resolution_x": 1920,
        "resolution_y": 1080,
        "samples": 32,
        "adaptive_threshold": 0.03,
        "use_denoising": True,
        "motion_blur": True,
        "fps": 60,
    },
    # Оптимизированный кинематографичный мастер-профиль 4K для CPU раннеров
    "4k": {
        "resolution_x": 3840,
        "resolution_y": 2160,
        "samples": 40,
        "adaptive_threshold": 0.025,
        "use_denoising": True,
        "motion_blur": True,
        "fps": 60,
    },
}


def apply_cycles_settings(scene: bpy.types.Scene, profile_name: str = "4k", samples_override: int = None):
    """Применяет высокопроизводительные настройки Cycles для CPU-раннеров."""
    profile = PROFILES.get(profile_name, PROFILES["4k"])
    samples = samples_override if samples_override is not None else profile["samples"]

    # 1. Переключение на Cycles CPU
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.render.threads_mode = "AUTO"

    # 2. Разрешение и кадровая частота
    scene.render.resolution_x = profile["resolution_x"]
    scene.render.resolution_y = profile["resolution_y"]
    scene.render.resolution_percentage = 100
    scene.render.fps = profile["fps"]

    # 3. Адаптивный сэмплинг
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = profile["adaptive_threshold"]
    scene.cycles.adaptive_min_samples = 8
    scene.cycles.samples = samples

    # 4. Высокоскоростной денойзер OpenImageDenoise
    if profile["use_denoising"]:
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
        scene.cycles.denoising_prefilter = "FAST"
        scene.cycles.denoising_quality = "BALANCED"

    # 5. Оптимизация световых путей (Главный прирост скорости CPU)
    scene.cycles.use_light_tree = True
    scene.cycles.seed = 42
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 3
    scene.cycles.volume_bounces = 0  # Исключает многократное рассеяние, сохраняя четкие God-Rays
    scene.cycles.transparent_max_bounces = 4

    # Шаг трассировки тумана (баланс скорости и детализации лучей)
    scene.cycles.volume_step_rate = 2.5
    scene.cycles.volume_preview_step_rate = 4.0
    scene.cycles.volume_max_steps = 128

    scene.cycles.sample_clamp_direct = 0.0
    scene.cycles.sample_clamp_indirect = 8.0

    # 6. Физический Motion Blur
    scene.render.use_motion_blur = profile["motion_blur"]
    if profile["motion_blur"]:
        scene.render.motion_blur_shutter = 0.5
        scene.render.motion_blur_position = "CENTER"

    # 7. Цветопередача AgX / Filmic
    scene.display_settings.display_device = "sRGB"
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "None"
    except (TypeError, ValueError):
        scene.view_settings.view_transform = "Filmic"

    # 8. Формат вывода (строго без дублирования расширения файла)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    scene.render.use_file_extension = False

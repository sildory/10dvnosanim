"""Модуль глобальных настроек рендера и конфигурации движка Cycles."""

import os
import bpy

PROFILES = {
    # Профиль для сверхбыстрой проверки композиции и анимации
    "preview": {
        "resolution_x": 960,
        "resolution_y": 540,
        "samples": 16,
        "adaptive_threshold": 0.05,
        "use_denoising": True,
        "motion_blur": False,
        "fps": 30,
    },
    # Высокое качество для тестов
    "fullhd": {
        "resolution_x": 1920,
        "resolution_y": 1080,
        "samples": 128,
        "adaptive_threshold": 0.01,
        "use_denoising": True,
        "motion_blur": True,
        "fps": 60,
    },
    # Кинематографический мастер-профиль 4K
    "4k": {
        "resolution_x": 3840,
        "resolution_y": 2160,
        "samples": 256,
        "adaptive_threshold": 0.01,
        "use_denoising": True,
        "motion_blur": True,
        "fps": 60,
    },
}


def apply_cycles_settings(scene: bpy.types.Scene, profile_name: str = "4k", samples_override: int = None):
    """Применяет физически корректные настройки Cycles и управление цветом."""
    profile = PROFILES.get(profile_name, PROFILES["4k"])
    samples = samples_override if samples_override is not None else profile["samples"]

    # 1. Переключение на Cycles CPU
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"

    # Количество потоков CPU (на раннерах Actions используется максимум)
    scene.render.threads_mode = "AUTO"

    # 2. Разрешение кадра
    scene.render.resolution_x = profile["resolution_x"]
    scene.render.resolution_y = profile["resolution_y"]
    scene.render.resolution_percentage = 100
    scene.render.fps = profile["fps"]

    # 3. Адаптивный сэмплинг (не тратит время на простые плоские участки)
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = profile["adaptive_threshold"]
    scene.cycles.adaptive_min_samples = 16
    scene.cycles.samples = samples

    # 4. Профессиональный денойзер OpenImageDenoise (Accurate)
    if profile["use_denoising"]:
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
        scene.cycles.denoising_prefilter = "ACCURATE"
        scene.cycles.denoising_quality = "HIGH"

    # 5. Оптимизация световых путей (Light Tree убирает шум от множества источников)
    scene.cycles.use_light_tree = True
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 6
    scene.cycles.volume_bounces = 2
    scene.cycles.transparent_max_bounces = 8

    # Принудительное гашение «светлячков» от сверхъярких неонов и отражений
    scene.cycles.sample_clamp_direct = 0.0
    scene.cycles.sample_clamp_indirect = 10.0

    # 6. Нативный физический Motion Blur (смаз в движении со шторкой 0.5)
    scene.render.use_motion_blur = profile["motion_blur"]
    if profile["motion_blur"]:
        scene.render.motion_blur_shutter = 0.5
        scene.render.motion_blur_position = "CENTER"

    # 7. Кинематографический тонокорректор AgX
    # AgX предотвращает выжигание ярких неонов в белизну, сохраняя оттенок
    scene.display_settings.display_device = "sRGB"
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "None"
    except TypeError:
        # Фолбэк на Filmic, если используется более старый релиз
        scene.view_settings.view_transform = "Filmic"

    # 8. Настройки формата вывода
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15

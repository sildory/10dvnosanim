"""
=============================================================================
ЭПИЗОД 2: «ВОПИЮЩАЯ НЕСПРАВЕДЛИВОСТЬ» (КАДРЫ 1 - 180 / 0:06 - 0:12)
Оператор щедро насыпает Кеше гигантскую гору корма. Кеша с упоением начинает есть.
Затем совок перемещается к Жоре и роняет лишь пару жалких семечек.
Жора замирает в немом шоке, его хохолок медленно вздымается от ярости.
=============================================================================
"""

import math
import bpy
from engine.director import Director
from kit.prefabs import (
    make_marble_island,
    make_food_bowl,
    make_seed_mound,
    make_falling_grains,
    make_grain_scoop,
    make_stylized_parrot,
)


def build():
    # Инициализация режиссера: 180 кадров (6 секунд @ 30 FPS)
    director = Director(name="Ep02_Unequal_Distribution", total_frames=180)

    # 1. Студийный утренний свет интерьера кухни
    director.set_hdri("studio_small_08", strength=1.15, rotation=0.6)

    # 2. Мягкий рассеянный солнечный свет из окна (Key Light)
    bpy.ops.object.light_add(type="AREA", location=(2.2, -1.8, 3.2))
    key_light = bpy.context.active_object
    key_light.name = "Morning_Window_Sun"
    key_light.data.energy = 900.0
    key_light.data.size = 2.4
    key_light.data.color = (1.0, 0.96, 0.90)
    key_light.rotation_euler = (math.radians(35), math.radians(18), math.radians(25))

    # 3. Контурный холодный контровой свет (Rim Light) для блеска перьев и мрамора
    bpy.ops.object.light_add(type="AREA", location=(0.0, 2.5, 2.8))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Backlight"
    rim_light.data.energy = 650.0
    rim_light.data.size = 3.0
    rim_light.data.color = (0.75, 0.88, 1.0)
    rim_light.rotation_euler = (math.radians(-40), 0, 0)

    # 4. Мраморный остров
    make_marble_island(location=(0.0, 0.0, -0.05), size=(3.2, 1.8, 0.1))

    # 5. Керамические миски
    bowl_kesha = make_food_bowl(name="Kesha_Bowl", location=(-0.45, 0.32, 0.0), color=(0.12, 0.58, 0.72, 1.0))
    bowl_zhora = make_food_bowl(name="Zhora_Bowl", location=(0.45, 0.32, 0.0), color=(0.95, 0.40, 0.32, 1.0))

    # 6. Горки корма внутри мисок
    # Гора Кеши (вырастает в огромную вершину с верхом)
    mound_kesha = make_seed_mound(name="Kesha_Seeds", location=(-0.45, 0.32, 0.0), mound_type="mountain")
    # Крохи Жоры (сиротливые зерна на самом дне)
    mound_zhora = make_seed_mound(name="Zhora_Scraps", location=(0.45, 0.32, 0.0), radius=0.10, mound_type="scraps")

    # 7. Персонажи
    kesha = make_stylized_parrot(name="Kesha", palette="green", location=(-0.45, -0.22, 0.0), rotation=(0.0, 0.0, math.radians(12)))
    zhora = make_stylized_parrot(name="Zhora", palette="red", location=(0.45, -0.22, 0.0), rotation=(0.0, 0.0, math.radians(-15)))

    # 8. Мерный совок оператора
    scoop = make_grain_scoop(name="Chef_Scoop", location=(-0.45, 0.36, 0.45))

    # 9. Падающие зерна
    grains_kesha = make_falling_grains("Grains_Kesha", grain_count=16)
    grains_zhora = make_falling_grains("Grains_Zhora", grain_count=5)

    # =========================================================================
    # АНИМАЦИЯ: ЩЕДРАЯ РАЗДАЧА КЕШЕ -> ПОДАЧКА ЖОРЕ -> ОНЕМЕНИЕ И ЯРОСТЬ
    # =========================================================================

    # 1. Анимация совка оператора
    # Фаза 1 (Кадры 1 - 60): Зависание над миской Кеши и щедрое насыпание с наклоном 68 градусов
    scoop.location = (-0.45, 0.38, 0.42)
    scoop.rotation_euler = (math.radians(15), 0, math.radians(-5))
    scoop.keyframe_insert(data_path="location", frame=1)
    scoop.keyframe_insert(data_path="rotation_euler", frame=1)

    scoop.location = (-0.45, 0.36, 0.34)
    scoop.rotation_euler = (math.radians(68), math.radians(5), math.radians(-12))
    scoop.keyframe_insert(data_path="location", frame=28)
    scoop.keyframe_insert(data_path="rotation_euler", frame=28)

    scoop.location = (-0.45, 0.36, 0.34)
    scoop.rotation_euler = (math.radians(72), math.radians(5), math.radians(-12))
    scoop.keyframe_insert(data_path="rotation_euler", frame=50)

    # Фаза 2 (Кадры 51 - 85): Выравнивание и подъем совка
    scoop.location = (-0.45, 0.38, 0.48)
    scoop.rotation_euler = (math.radians(10), 0, 0)
    scoop.keyframe_insert(data_path="location", frame=70)
    scoop.keyframe_insert(data_path="rotation_euler", frame=70)

    # Фаза 3 (Кадры 86 - 110): Перемещение к миске Жоры
    scoop.location = (0.45, 0.38, 0.46)
    scoop.rotation_euler = (math.radians(10), 0, math.radians(15))
    scoop.keyframe_insert(data_path="location", frame=95)
    scoop.keyframe_insert(data_path="rotation_euler", frame=95)

    # Фаза 4 (Кадры 111 - 135): Неохотный легкий наклон совка (всего 25 градусов) и потряхивание
    scoop.location = (0.45, 0.37, 0.38)
    scoop.rotation_euler = (math.radians(28), 0, math.radians(10))
    scoop.keyframe_insert(data_path="location", frame=110)
    scoop.keyframe_insert(data_path="rotation_euler", frame=110)

    scoop.rotation_euler = (math.radians(34), 0, math.radians(10))
    scoop.keyframe_insert(data_path="rotation_euler", frame=118)

    # Фаза 5 (Кадры 136 - 180): Быстрый уход совка вверх из кадра
    scoop.location = (0.45, 0.38, 0.46)
    scoop.rotation_euler = (math.radians(5), 0, 0)
    scoop.keyframe_insert(data_path="location", frame=135)
    scoop.keyframe_insert(data_path="rotation_euler", frame=135)

    scoop.location = (0.75, 0.50, 1.80)
    scoop.keyframe_insert(data_path="location", frame=175)

    # 2. Рост горы семян Кеши (от нуля до царской вершины)
    mound_kesha.scale = (0.01, 0.01, 0.01)
    mound_kesha.keyframe_insert(data_path="scale", frame=1)
    mound_kesha.keyframe_insert(data_path="scale", frame=18)
    mound_kesha.scale = (1.0, 1.0, 1.35)
    mound_kesha.keyframe_insert(data_path="scale", frame=52)

    # 3. Появление жалких крох Жоры
    mound_zhora.scale = (0.01, 0.01, 0.01)
    mound_zhora.keyframe_insert(data_path="scale", frame=1)
    mound_zhora.keyframe_insert(data_path="scale", frame=110)
    mound_zhora.scale = (0.55, 0.55, 0.15)
    mound_zhora.keyframe_insert(data_path="scale", frame=122)

    # 4. Анимация Кеши: радостное клевание и чавканье
    kh = kesha["head_pivot"]
    kt = kesha["tail"]
    # Кеша ждет насыпания
    kh.rotation_euler = (math.radians(-10), 0, math.radians(5))
    kh.keyframe_insert(data_path="rotation_euler", frame=1)
    kh.keyframe_insert(data_path="rotation_euler", frame=45)

    # Кеша опускает клюв в миску и энергично клюет (кадры 55 - 180)
    peck_frames = [
        (55, -35), (65, -8), (75, -42), (85, -12), (95, -40),
        (105, -10), (115, -42), (125, -12), (135, -38), (145, -14),
        (155, -42), (165, -10), (175, -40), (180, -15)
    ]
    for f, rx_deg in peck_frames:
        kh.rotation_euler = (math.radians(rx_deg), 0, math.radians(8))
        kh.keyframe_insert(data_path="rotation_euler", frame=f)

    # Радостное виляние хвостом Кеши во время еды
    for f, rot_z in [(55, 0.0), (75, 0.15), (95, -0.15), (115, 0.18), (135, -0.16), (155, 0.15), (175, 0.0)]:
        kt.rotation_euler = (math.radians(-42), 0, rot_z)
        kt.keyframe_insert(data_path="rotation_euler", frame=f)

    # 5. Анимация Жоры: предвкушение -> остолбенение -> встающий хохолок -> взгляд на Кешу
    zh = zhora["head_pivot"]
    zc = zhora["crest_pivot"]

    # Жора следит за совком и тянет шею (кадры 1 - 105)
    zh.rotation_euler = (math.radians(12), 0, math.radians(-18))
    zh.keyframe_insert(data_path="rotation_euler", frame=1)
    zh.rotation_euler = (math.radians(28), 0, math.radians(-8))
    zh.keyframe_insert(data_path="rotation_euler", frame=95)

    # Жора опускает взгляд на дно своей пустой миски (кадры 115 - 140)
    zh.rotation_euler = (math.radians(-32), 0, math.radians(-5))
    zh.keyframe_insert(data_path="rotation_euler", frame=125)
    zh.keyframe_insert(data_path="rotation_euler", frame=145)

    # Хохолок Жоры взлетает вверх от шока (кадры 130 - 165)
    zc.rotation_euler = (0, 0, 0)
    zc.keyframe_insert(data_path="rotation_euler", frame=1)
    zc.rotation_euler = (math.radians(15), 0, 0)
    zc.keyframe_insert(data_path="rotation_euler", frame=110)
    zc.rotation_euler = (math.radians(78), 0, 0)  # Стойка дыбом от возмущения!
    zc.keyframe_insert(data_path="rotation_euler", frame=160)

    # Резкий поворот головы Жоры налево на Кешу (кадр 155 - 180)
    zh.rotation_euler = (math.radians(-8), 0, math.radians(48))  # Глядит в упор на Кешу
    zh.keyframe_insert(data_path="rotation_euler", frame=165)
    zh.keyframe_insert(data_path="rotation_euler", frame=180)

    # Сглаживание ключей
    for obj in [scoop, mound_kesha, mound_zhora, kh, kt, zh, zc]:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "BEZIER"
                    kf.easing = "EASE_IN_OUT"

    # =========================================================================
    # РЕЖИССЁРСКИЙ ТАЙМЛАЙН ШОТОВ (ТРИ ДРАМАТИЧЕСКИХ РАКУРСА)
    # =========================================================================

    # Шот 1 (Кадры 1 - 75): Крупный кинематографичный план на Кешу.
    # Лавина золотых семян наполняет миску, Кеша жадно набрасывается на пищу.
    director.add_shot(
        name="Kesha_Feast_Pour",
        start_frame=1,
        end_frame=75,
        cam_start=(-0.72, -0.68, 0.44),
        cam_end=(-0.58, -0.52, 0.38),
        look_at=(-0.45, 0.22, 0.22),
        focal_length=50.0,
        fstop=2.0
    )

    # Шот 2 (Кадры 76 - 135): Средний план на Жору.
    # Совок перемещается к нему, дрожит и скупо роняет крохи на дно.
    director.add_shot(
        name="Zhora_Sad_Trickle",
        start_frame=76,
        end_frame=135,
        cam_start=(0.68, -0.65, 0.42),
        cam_end=(0.52, -0.50, 0.36),
        look_at=(0.45, 0.20, 0.20),
        focal_length=52.0,
        fstop=2.0
    )

    # Шот 3 (Кадры 136 - 180): Драматичный общий ракурс с акцентом на взгляд Жоры.
    # Жора заглядывает в свою пустую миску, его хохолок встает дыбом,
    # и он в яростном оцепенении поворачивается к чавкающему Кеше.
    director.add_shot(
        name="The_Stare_Of_Injustice",
        start_frame=136,
        end_frame=180,
        cam_start=(0.28, -0.85, 0.48),
        cam_end=(0.18, -0.72, 0.42),
        look_at=(0.0, 0.15, 0.26),
        focal_length=42.0,
        fstop=2.2
    )

    director.finalize()

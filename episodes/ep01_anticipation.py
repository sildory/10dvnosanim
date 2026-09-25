"""
=============================================================================
ЭПИЗОД 1: «ВЕЛИКОЕ ПРЕДВКУШЕНИЕ» (КАДРЫ 1 - 180 / 0:00 - 0:06)
Два попугая ждут завтрак на мраморном острове. В кадр спускается совок с зерном.
Ритмичный птичий танец ожидания, покачивание хохолков, первый контакт с камерой.
=============================================================================
"""

import math
import bpy
from engine.director import Director
from kit.prefabs import (
    make_marble_island,
    make_food_bowl,
    make_grain_scoop,
    make_stylized_parrot,
)


def build():
    # Инициализация режиссера на 180 кадров (6 секунд при 30 кадрах/сек)
    director = Director(name="Ep01_The_Great_Anticipation", total_frames=180)

    # 1. Кинематографическое мягкое студийное освещение интерьера кухни (Poly Haven Studio HDRI)
    director.set_hdri("studio_small_08", strength=1.1, rotation=0.6)

    # 2. Теплый ключевой свет (Key Light) сверху справа — утреннее солнце из кухонного окна
    bpy.ops.object.light_add(type="AREA", location=(2.2, -1.8, 3.2))
    key_light = bpy.context.active_object
    key_light.name = "Morning_Window_Sun"
    key_light.data.energy = 850.0
    key_light.data.size = 2.4
    key_light.data.color = (1.0, 0.95, 0.88)
    key_light.rotation_euler = (math.radians(35), math.radians(18), math.radians(25))

    # 3. Холодный контрастный контровой свет (Rim Light) для сияния оперения и фасок мрамора
    bpy.ops.object.light_add(type="AREA", location=(0.0, 2.5, 2.8))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Backlight"
    rim_light.data.energy = 600.0
    rim_light.data.size = 3.0
    rim_light.data.color = (0.78, 0.90, 1.0)
    rim_light.rotation_euler = (math.radians(-40), 0, 0)

    # 4. Роскошный кухонный остров из белого полированного каррарского мрамора
    make_marble_island(location=(0.0, 0.0, -0.05), size=(3.2, 1.8, 0.1))

    # 5. Две тяжелые керамические миски перед будущими местами птиц
    # Миска Кеши (слева, цвет морской волны)
    bowl_kesha = make_food_bowl(
        name="Kesha_Bowl",
        location=(-0.45, 0.32, 0.0),
        color=(0.12, 0.58, 0.72, 1.0)
    )
    # Миска Жоры (справа, кораллово-пастельная)
    bowl_zhora = make_food_bowl(
        name="Zhora_Bowl",
        location=(0.45, 0.32, 0.0),
        color=(0.95, 0.40, 0.32, 1.0)
    )

    # 6. Персонажи:
    # Кеша — вальяжный изумрудный попугай (слева)
    kesha = make_stylized_parrot(
        name="Kesha",
        palette="green",
        location=(-0.45, -0.22, 0.0),
        rotation=(0.0, 0.0, math.radians(15))
    )

    # Жора — темпераментный алый попугай с выразительным хохолком (справа)
    zhora = make_stylized_parrot(
        name="Zhora",
        palette="red",
        location=(0.45, -0.22, 0.0),
        rotation=(0.0, 0.0, math.radians(-15))
    )

    # 7. Металлический совок для зерна, управляемый оператором
    scoop = make_grain_scoop(name="Chef_Scoop", location=(0.65, 0.40, 1.45))

    # =========================================================================
    # АНИМАЦИЯ: ТАНЕЦ ПРЕДВКУШЕНИЯ, КИВАНИЕ ГОЛОВОЙ И СПУСК СОВКА
    # =========================================================================

    # Анимация спуска совка с кормом сверху в зону видимости птиц (кадры 40 - 150)
    scoop.location = (0.75, 0.55, 1.65)
    scoop.rotation_euler = (math.radians(35), 0, math.radians(-25))
    scoop.keyframe_insert(data_path="location", frame=1)
    scoop.keyframe_insert(data_path="rotation_euler", frame=1)

    scoop.location = (0.05, 0.45, 0.48)
    scoop.rotation_euler = (math.radians(18), math.radians(-5), math.radians(-10))
    scoop.keyframe_insert(data_path="location", frame=120)
    scoop.keyframe_insert(data_path="rotation_euler", frame=120)

    scoop.location = (0.0, 0.42, 0.44)
    scoop.keyframe_insert(data_path="location", frame=180)

    # Анимация Кеши: ритмичное веселое покачивание головой и наклоны
    kh = kesha["head_pivot"]
    for f, pz, rx in [
        (1, 0.0, 0.0), (30, 0.05, -0.15), (60, -0.02, 0.12),
        (90, 0.06, -0.20), (120, -0.01, 0.10), (150, 0.07, -0.18), (180, 0.04, -0.05)
    ]:
        kh.rotation_euler = (rx, 0.0, pz)
        kh.keyframe_insert(data_path="rotation_euler", frame=f)

    # Анимация Жоры: нетерпеливые резкие птичьи движения, вздергивание хохолка
    zh = zhora["head_pivot"]
    zc = zhora["crest_pivot"]

    for f, pz, rx in [
        (1, 0.0, 0.0), (25, -0.12, 0.18), (55, 0.22, -0.25),
        (85, -0.15, 0.22), (115, 0.30, -0.32), (145, -0.05, 0.15), (180, 0.12, -0.28)
    ]:
        zh.rotation_euler = (rx, 0.0, pz)
        zh.keyframe_insert(data_path="rotation_euler", frame=f)

    # Хохолок Жоры поднимается выше по мере приближения еды (кадры 60 - 180)
    zc.rotation_euler = (0.0, 0.0, 0.0)
    zc.keyframe_insert(data_path="rotation_euler", frame=1)
    zc.rotation_euler = (math.radians(-12), 0.0, 0.0)
    zc.keyframe_insert(data_path="rotation_euler", frame=60)
    zc.rotation_euler = (math.radians(35), 0.0, 0.0)  # Вздыбленный от радости хохолок!
    zc.keyframe_insert(data_path="rotation_euler", frame=140)
    zc.rotation_euler = (math.radians(45), 0.0, 0.0)
    zc.keyframe_insert(data_path="rotation_euler", frame=180)

    # Жора нетерпеливо притоптывает левой лапкой по мрамору (кадры 70 - 120)
    z_foot = zhora["feet"]["L"]
    for f, z_offset in [(70, 0.0), (76, 0.035), (82, 0.0), (88, 0.04), (94, 0.0)]:
        z_foot.location = (-0.08, 0.02, z_offset)
        z_foot.keyframe_insert(data_path="location", frame=f)

    # Легкое трепетание крыльев Жоры от восторга
    zw = zhora["wings"]["R"]
    zw.rotation_euler = (0, 0, 0)
    zw.keyframe_insert(data_path="rotation_euler", frame=80)
    zw.rotation_euler = (math.radians(15), math.radians(20), math.radians(-15))
    zw.keyframe_insert(data_path="rotation_euler", frame=95)
    zw.rotation_euler = (0, 0, 0)
    zw.keyframe_insert(data_path="rotation_euler", frame=110)

    # Сглаживание интерполяции всех кривых анимации
    for obj in [scoop, kh, zh, zc, z_foot, zw]:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "BEZIER"
                    kf.easing = "EASE_IN_OUT"

    # =========================================================================
    # РЕЖИССЁРСКИЙ ТАЙМЛАЙН ШОТОВ (ДВЕ КИНОКАМЕРЫ)
    # =========================================================================

    # Шот 1 (Кадры 1 - 90): Скользящий нижний ракурс вдоль полированного мрамора.
    # Камера скользит мимо блестящих мисок, открывая лица нетерпеливых птиц.
    director.add_shot(
        name="Marble_Low_Glider",
        start_frame=1,
        end_frame=90,
        cam_start=(-0.95, -1.20, 0.28),
        cam_end=(-0.25, -0.92, 0.38),
        look_at=(0.0, 0.0, 0.42),
        focal_length=42.0,
        fstop=2.4
    )

    # Шот 2 (Кадры 91 - 180): Фронтальный средний кинематографичный план (Two-Shot).
    # Камера следит за спуском полного совка точно между двух птиц.
    director.add_shot(
        name="Two_Parrots_Anticipation",
        start_frame=91,
        end_frame=180,
        cam_start=(0.0, -1.15, 0.58),
        cam_end=(0.0, -0.98, 0.52),
        look_at=(0.0, 0.25, 0.40),
        focal_length=55.0,
        fstop=2.0
    )

    director.finalize()

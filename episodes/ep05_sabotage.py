"""
=============================================================================
ЭПИЗОД 5: «САБОТАЖ И ХАОС» (КАДРЫ 1 - 180 / 0:24 - 0:30)
ФИНАЛ: Жора мчится в лобовую атаку, сбивает миску Кеши в эпичном слоу-мо,
семена разлетаются салютом, Кеша плюхается на хвост, а Жора взлетает
на перевернутую миску в победной позе орла прямо перед камерой!
=============================================================================
"""

import math
import bpy
from engine.director import Director
from kit.prefabs import (
    make_marble_island,
    make_food_bowl,
    make_seed_mound,
    make_scattered_seeds,
    make_seed_burst,
    make_stylized_parrot,
)


def build():
    director = Director(name="Ep05_The_Sabotage", total_frames=180)

    # 1. Интерьерный свет студии
    director.set_hdri("studio_small_08", strength=1.15, rotation=0.6)

    bpy.ops.object.light_add(type="AREA", location=(2.2, -1.8, 3.2))
    key_light = bpy.context.active_object
    key_light.name = "Morning_Window_Sun"
    key_light.data.energy = 950.0
    key_light.data.size = 2.4
    key_light.data.color = (1.0, 0.96, 0.90)
    key_light.rotation_euler = (math.radians(35), math.radians(18), math.radians(25))

    bpy.ops.object.light_add(type="AREA", location=(0.0, 2.5, 2.8))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Backlight"
    rim_light.data.energy = 750.0
    rim_light.data.size = 3.0
    rim_light.data.color = (0.75, 0.88, 1.0)
    rim_light.rotation_euler = (math.radians(-40), 0, 0)

    # 2. Мраморный остров
    make_marble_island(location=(0.0, 0.0, -0.05), size=(3.2, 1.8, 0.1))

    # 3. Уже перевернутая в Эпизоде 4 миска Жоры на дальнем конце стола
    bowl_zhora_old = make_food_bowl(name="Zhora_Old_Bowl", location=(0.98, 0.66, 0.038), color=(0.95, 0.40, 0.32, 1.0))
    bowl_zhora_old.rotation_euler = (math.radians(180), 0.0, math.radians(118))
    make_scattered_seeds("Zhora_Old_Seeds", center=(0.95, 0.62, 0.01), count=16, radius=0.35)

    # 4. Бирюзовая миска Кеши с горой корма (цель тарана)
    bowl_kesha = make_food_bowl(name="Kesha_Bowl", location=(-0.45, 0.32, 0.0), color=(0.12, 0.58, 0.72, 1.0))
    mound_kesha = make_seed_mound(name="Kesha_Feast", location=(-0.45, 0.32, 0.0), mound_type="mountain")

    # 5. Грандиозный взрыв семян в воздухе при ударе
    seed_burst = make_seed_burst(
        name="Kesha_Seed_Explosion",
        origin=(-0.45, 0.32, 0.10),
        seed_count=32,
        spread_radius=0.75,
        burst_height=0.48
    )

    # 6. Персонажи
    kesha = make_stylized_parrot(name="Kesha", palette="green", location=(-0.45, -0.15, 0.0), rotation=(0.0, 0.0, math.radians(12)))
    zhora = make_stylized_parrot(name="Zhora", palette="red", location=(0.45, -0.06, 0.0), rotation=(0.0, 0.0, math.radians(-15)))

    # =========================================================================
    # АНИМАЦИЯ: ТАРАННЫЙ СПРИНТ, СТОЛКНОВЕНИЕ И ПОБЕДНАЯ ПОЗА
    # =========================================================================

    zr = zhora["root"]
    zh = zhora["head_pivot"]
    zc = zhora["crest_pivot"]
    zw_l = zhora["wings"]["L"]
    zw_r = zhora["wings"]["R"]
    z_foot_l = zhora["feet"]["L"]
    z_foot_r = zhora["feet"]["R"]

    kr = kesha["root"]
    kh = kesha["head_pivot"]
    kt = kesha["tail"]
    kw_l = kesha["wings"]["L"]
    kw_r = kesha["wings"]["R"]

    # Хохолок Жоры воинственно распушен
    zc.rotation_euler = (math.radians(88), 0.0, 0.0)
    zc.keyframe_insert(data_path="rotation_euler", frame=1)

    # Фаза 1 (Кадры 1 - 45): Спринт Жоры через стол наперерез Кеше
    zr.location = (0.45, -0.06, 0.0)
    zr.keyframe_insert(data_path="location", frame=1)
    zr.keyframe_insert(data_path="location", frame=12)

    # Наклон вперед как у атакующего быка
    zh.rotation_euler = (math.radians(-25), 0.0, math.radians(45))
    zh.keyframe_insert(data_path="rotation_euler", frame=12)

    # Быстрый бег лапками по мрамору (Кадры 12 - 45)
    for idx, f in enumerate(range(12, 45, 4)):
        fl_z = 0.04 if idx % 2 == 0 else 0.0
        fr_z = 0.0 if idx % 2 == 0 else 0.04
        z_foot_l.location = (-0.08, 0.02, fl_z)
        z_foot_r.location = (0.08, 0.02, fr_z)
        z_foot_l.keyframe_insert(data_path="location", frame=f)
        z_foot_r.keyframe_insert(data_path="location", frame=f)

    # Жора врезается в миску Кеши на кадре 48
    zr.location = (-0.22, 0.22, 0.0)
    zr.keyframe_insert(data_path="location", frame=46)

    # Фаза 2 (Кадры 46 - 90): УДАР И ПОЛЕТ МИСКИ КЕШИ!
    bowl_kesha.location = (-0.45, 0.32, 0.0)
    bowl_kesha.rotation_euler = (0.0, 0.0, 0.0)
    bowl_kesha.keyframe_insert(data_path="location", frame=1)
    bowl_kesha.keyframe_insert(data_path="rotation_euler", frame=1)
    bowl_kesha.keyframe_insert(data_path="location", frame=46)
    bowl_kesha.keyframe_insert(data_path="rotation_euler", frame=46)

    # Взлет миски и переворот в воздухе
    bowl_kesha.location = (-0.58, 0.44, 0.28)
    bowl_kesha.rotation_euler = (math.radians(95), math.radians(-35), math.radians(50))
    bowl_kesha.keyframe_insert(data_path="location", frame=68)
    bowl_kesha.keyframe_insert(data_path="rotation_euler", frame=68)

    # Падение вверх дном
    bowl_kesha.location = (-0.68, 0.52, 0.04)
    bowl_kesha.rotation_euler = (math.radians(180), math.radians(-8), math.radians(45))
    bowl_kesha.keyframe_insert(data_path="location", frame=90)
    bowl_kesha.keyframe_insert(data_path="rotation_euler", frame=90)

    # Гора корма взрывается при ударе
    mound_kesha.scale = (1.0, 1.0, 1.35)
    mound_kesha.keyframe_insert(data_path="scale", frame=46)
    mound_kesha.scale = (0.001, 0.001, 0.001)
    mound_kesha.keyframe_insert(data_path="scale", frame=50)

    # Разлет 32 семян во все стороны
    for s in seed_burst["seeds"]:
        obj = s["object"]
        obj.location = (0.0, 0.0, 0.0)
        obj.scale = (0.001, 0.001, 0.001)
        obj.keyframe_insert(data_path="location", frame=1)
        obj.keyframe_insert(data_path="scale", frame=1)

        obj.scale = (1.0, 1.0, 1.0)
        obj.keyframe_insert(data_path="scale", frame=48)

        obj.location = s["peak"]
        obj.rotation_euler = s["rot"]
        obj.keyframe_insert(data_path="location", frame=70)
        obj.keyframe_insert(data_path="rotation_euler", frame=70)

        obj.location = s["target"]
        obj.keyframe_insert(data_path="location", frame=98)

    # Кеша отшатывается и шлепается на хвост от взрыва (Кадры 46 - 95)
    kr.location = (-0.45, -0.15, 0.0)
    kr.rotation_euler = (0.0, 0.0, math.radians(12))
    kr.keyframe_insert(data_path="location", frame=46)
    kr.keyframe_insert(data_path="rotation_euler", frame=46)

    # Шлепок назад на хвост
    kr.location = (-0.62, -0.32, 0.0)
    kr.rotation_euler = (math.radians(-38), 0.0, math.radians(25))
    kr.keyframe_insert(data_path="location", frame=72)
    kr.keyframe_insert(data_path="rotation_euler", frame=72)

    # Ошалевший взгляд Кеши с раскрытым клювом
    kh.rotation_euler = (math.radians(35), math.radians(-15), math.radians(15))
    kh.keyframe_insert(data_path="rotation_euler", frame=72)
    kesha["beak_lower"].rotation_euler = (math.radians(38), 0.0, 0.0)
    kesha["beak_lower"].keyframe_insert(data_path="rotation_euler", frame=72)

    # Фаза 3 (Кадры 105 - 180): ЖОРА ЗАПРЫГИВАЕТ НА ПЕРЕВЕРНУТУЮ МИСКУ И РАСПРАВЛЯЕТ КРЫЛЬЯ!
    zr.location = (-0.22, 0.22, 0.0)
    zr.keyframe_insert(data_path="location", frame=95)

    # Запрыгивание на дно миски
    zr.location = (-0.68, 0.50, 0.08)  # Стоит точно на перевернутой миске
    zr.rotation_euler = (0.0, 0.0, math.radians(-25))
    zr.keyframe_insert(data_path="location", frame=125)
    zr.keyframe_insert(data_path="rotation_euler", frame=125)

    # Поворот головы Жоры прямо в камеру
    zh.rotation_euler = (math.radians(8), 0.0, math.radians(-10))
    zh.keyframe_insert(data_path="rotation_euler", frame=135)

    # ВЕЛИЧЕСТВЕННЫЙ РАЗМАХ КРЫЛЬЕВ ОРЛА-ПОБЕДИТЕЛЯ (Кадры 125 - 180)
    zw_l.rotation_euler = (0.0, 0.0, 0.0)
    zw_r.rotation_euler = (0.0, 0.0, 0.0)
    zw_l.keyframe_insert(data_path="rotation_euler", frame=115)
    zw_r.keyframe_insert(data_path="rotation_euler", frame=115)

    zw_l.rotation_euler = (math.radians(15), math.radians(-65), math.radians(25))
    zw_r.rotation_euler = (math.radians(15), math.radians(65), math.radians(-25))
    zw_l.keyframe_insert(data_path="rotation_euler", frame=155)
    zw_r.keyframe_insert(data_path="rotation_euler", frame=155)

    # Сглаживание траекторий
    for obj in [zr, zh, zw_l, zw_r, kr, kh, bowl_kesha]:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "BEZIER"
                    kf.easing = "EASE_IN_OUT"

    # =========================================================================
    # РЕЖИССЁРСКИЙ ТАЙМЛАЙН ШОТОВ (ТРИ КИНЕМАТОГРАФИЧЕСКИХ ПЛАНА)
    # =========================================================================

    # Шот 1 (Кадры 1 - 45): Динамичный трекинг спринта Жоры
    director.add_shot(
        name="The_Battle_Charge",
        start_frame=1,
        end_frame=45,
        cam_start=(0.15, -0.85, 0.38),
        cam_end=(-0.10, -0.68, 0.32),
        look_at=(-0.15, 0.15, 0.25),
        focal_length=42.0,
        fstop=2.2
    )

    # Шот 2 (Кадры 46 - 105): Нижний ракурс взрыва семян в слоу-мо
    director.add_shot(
        name="Slowmo_Impact_Explosion",
        start_frame=46,
        end_frame=105,
        cam_start=(-0.45, -0.45, 0.20),
        cam_end=(-0.52, -0.38, 0.22),
        look_at=(-0.50, 0.35, 0.22),
        focal_length=45.0,
        fstop=1.8
    )

    # Шот 3 (Кадры 106 - 180): Героический наезд снизу на Жору на поверженной миске
    director.add_shot(
        name="The_Conqueror_Pose",
        start_frame=106,
        end_frame=180,
        cam_start=(-0.65, -0.42, 0.22),
        cam_end=(-0.68, -0.28, 0.20),
        look_at=(-0.68, 0.45, 0.35),
        focal_length=32.0,
        fstop=2.4
    )

    director.finalize()

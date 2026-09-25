"""
=============================================================================
ЭПИЗОД 4: «БУНТ И ШВЫРЯНИЕ МИСКИ» (КАДРЫ 1 - 180 / 0:18 - 0:24)
Жора в ярости кричит, хлопает крыльями, топает лапами, хватает клювом
свою пустую миску и с грохотом швыряет её через весь мраморный стол!
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
    animate_beak_squawk,
    animate_wing_tantrum,
)


def build():
    director = Director(name="Ep04_The_Tantrum", total_frames=180)

    # 1. Освещение студии и утреннего окна
    director.set_hdri("studio_small_08", strength=1.15, rotation=0.6)

    bpy.ops.object.light_add(type="AREA", location=(2.2, -1.8, 3.2))
    key_light = bpy.context.active_object
    key_light.name = "Morning_Window_Sun"
    key_light.data.energy = 920.0
    key_light.data.size = 2.4
    key_light.data.color = (1.0, 0.96, 0.90)
    key_light.rotation_euler = (math.radians(35), math.radians(18), math.radians(25))

    bpy.ops.object.light_add(type="AREA", location=(0.0, 2.5, 2.8))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Backlight"
    rim_light.data.energy = 720.0
    rim_light.data.size = 3.0
    rim_light.data.color = (0.75, 0.88, 1.0)
    rim_light.rotation_euler = (math.radians(-40), 0, 0)

    # 2. Мраморный остров
    make_marble_island(location=(0.0, 0.0, -0.05), size=(3.2, 1.8, 0.1))

    # 3. Миска и гора семян Кеши
    bowl_kesha = make_food_bowl(name="Kesha_Bowl", location=(-0.45, 0.32, 0.0), color=(0.12, 0.58, 0.72, 1.0))
    mound_kesha = make_seed_mound(name="Kesha_Feast", location=(-0.45, 0.32, 0.0), mound_type="mountain")
    make_scattered_seeds("Kesha_Stray_Seeds", center=(-0.45, 0.16, 0.01), count=12, radius=0.18)

    # 4. Коралловая миска Жоры (будет анимироваться в броске)
    bowl_zhora = make_food_bowl(name="Zhora_Bowl", location=(0.45, 0.32, 0.0), color=(0.95, 0.40, 0.32, 1.0))
    mound_zhora = make_seed_mound(name="Zhora_Scraps", location=(0.45, 0.32, 0.0), radius=0.10, mound_type="scraps")

    # 5. Разлетающиеся семена при броске миски
    seed_burst = make_seed_burst(
        name="Zhora_Tossed_Seeds",
        origin=(0.45, 0.32, 0.06),
        seed_count=18,
        spread_radius=0.55,
        burst_height=0.35
    )

    # 6. Персонажи
    kesha = make_stylized_parrot(name="Kesha", palette="green", location=(-0.45, -0.22, 0.0), rotation=(0.0, 0.0, math.radians(12)))
    zhora = make_stylized_parrot(name="Zhora", palette="red", location=(0.45, -0.22, 0.0), rotation=(0.0, 0.0, math.radians(-15)))

    # =========================================================================
    # АНИМАЦИЯ: ИСТЕРИКА ЖОРЫ, БРОСОК МИСКИ И ИСПУГ КЕШИ
    # =========================================================================

    # 1. Реакция Кеши: ест -> пугается вопля -> замирает в шоке
    kh = kesha["head_pivot"]
    kt = kesha["tail"]

    # Кадры 1-35: дожевывает последние зерна
    for i, rx in enumerate([-35, -12, -40, -15]):
        f = 1 + i * 8
        kh.rotation_euler = (math.radians(rx), 0.0, math.radians(8))
        kh.keyframe_insert(data_path="rotation_euler", frame=f)

    # Кадр 35-55: резко вскидывает голову и таращится на беснующегося соседа
    kh.rotation_euler = (math.radians(18), math.radians(-8), math.radians(-25))
    kh.keyframe_insert(data_path="rotation_euler", frame=45)
    kh.keyframe_insert(data_path="rotation_euler", frame=180)

    kt.rotation_euler = (math.radians(-42), 0.0, math.radians(-12))
    kt.keyframe_insert(data_path="rotation_euler", frame=45)
    kt.keyframe_insert(data_path="rotation_euler", frame=180)

    # 2. Жора: Вопль -> Топот -> Хватка клювом -> Бросок миски
    zr = zhora["root"]
    zh = zhora["head_pivot"]
    zc = zhora["crest_pivot"]
    foot_l = zhora["feet"]["L"]
    foot_r = zhora["feet"]["R"]

    # Хохолок Жоры на максимуме ярости (88 градусов)
    zc.rotation_euler = (math.radians(88), 0.0, 0.0)
    zc.keyframe_insert(data_path="rotation_euler", frame=1)

    # Вопль и хлопанье крыльями (Кадры 1 - 50)
    animate_beak_squawk(zhora, start_frame=1, end_frame=50, repeats=4)
    animate_wing_tantrum(zhora, start_frame=1, end_frame=50)

    # Движения головы во время крика
    zh.rotation_euler = (math.radians(24), 0.0, math.radians(-5))
    zh.keyframe_insert(data_path="rotation_euler", frame=1)
    zh.rotation_euler = (math.radians(35), 0.0, math.radians(-12))
    zh.keyframe_insert(data_path="rotation_euler", frame=25)
    zh.rotation_euler = (math.radians(15), 0.0, math.radians(0))
    zh.keyframe_insert(data_path="rotation_euler", frame=50)

    # Злой топот лапами по мрамору (Кадры 5 - 45)
    for idx, f in enumerate(range(5, 45, 8)):
        fl_z = 0.035 if idx % 2 == 0 else 0.0
        fr_z = 0.0 if idx % 2 == 0 else 0.035
        foot_l.location = (-0.08, 0.02, fl_z)
        foot_r.location = (0.08, 0.02, fr_z)
        foot_l.keyframe_insert(data_path="location", frame=f)
        foot_r.keyframe_insert(data_path="location", frame=f)

    foot_l.location = (-0.08, 0.02, 0.0)
    foot_r.location = (0.08, 0.02, 0.0)
    foot_l.keyframe_insert(data_path="location", frame=50)
    foot_r.keyframe_insert(data_path="location", frame=50)

    # Кадры 55 - 95: Выпад вперед и хватка миски клювом
    zr.location = (0.45, -0.22, 0.0)
    zr.keyframe_insert(data_path="location", frame=1)
    zr.keyframe_insert(data_path="location", frame=55)

    zr.location = (0.45, -0.06, 0.0)  # Подходит вплотную к миске
    zr.keyframe_insert(data_path="location", frame=80)

    # Голова наклоняется и смыкает челюсти на ободке
    zh.rotation_euler = (math.radians(-42), 0.0, 0.0)
    zh.keyframe_insert(data_path="rotation_euler", frame=80)
    zhora["beak_lower"].rotation_euler = (math.radians(45), 0.0, 0.0)
    zhora["beak_lower"].keyframe_insert(data_path="rotation_euler", frame=70)
    zhora["beak_lower"].rotation_euler = (math.radians(72), 0.0, 0.0)  # Захлопнул клюв на миске
    zhora["beak_lower"].keyframe_insert(data_path="rotation_euler", frame=82)

    # Кадры 96 - 135: РЫВОК ГОЛОВОЙ ВВЕРХ И БРОСОК!
    zh.rotation_euler = (math.radians(-42), 0.0, 0.0)
    zh.keyframe_insert(data_path="rotation_euler", frame=95)

    zh.rotation_euler = (math.radians(45), math.radians(12), math.radians(-35))  # Резкий бросок назад
    zh.keyframe_insert(data_path="rotation_euler", frame=114)

    zh.rotation_euler = (math.radians(5), 0.0, math.radians(35))  # Победный взгляд на разбитую миску
    zh.keyframe_insert(data_path="rotation_euler", frame=145)

    # 3. Физика полета коралловой миски
    bowl_zhora.location = (0.45, 0.32, 0.0)
    bowl_zhora.rotation_euler = (0.0, 0.0, 0.0)
    bowl_zhora.keyframe_insert(data_path="location", frame=1)
    bowl_zhora.keyframe_insert(data_path="rotation_euler", frame=1)
    bowl_zhora.keyframe_insert(data_path="location", frame=95)
    bowl_zhora.keyframe_insert(data_path="rotation_euler", frame=95)

    # Верхняя точка полета и кувырок (Кадр 118)
    bowl_zhora.location = (0.72, 0.48, 0.32)
    bowl_zhora.rotation_euler = (math.radians(110), math.radians(35), math.radians(65))
    bowl_zhora.keyframe_insert(data_path="location", frame=118)
    bowl_zhora.keyframe_insert(data_path="rotation_euler", frame=118)

    # Удар об стол вверх дном (Кадр 138)
    bowl_zhora.location = (0.92, 0.62, 0.04)
    bowl_zhora.rotation_euler = (math.radians(180), math.radians(12), math.radians(110))
    bowl_zhora.keyframe_insert(data_path="location", frame=138)
    bowl_zhora.keyframe_insert(data_path="rotation_euler", frame=138)

    # Затухающий отскок и скольжение (Кадр 158)
    bowl_zhora.location = (0.98, 0.66, 0.038)
    bowl_zhora.rotation_euler = (math.radians(180), 0.0, math.radians(118))
    bowl_zhora.keyframe_insert(data_path="location", frame=158)
    bowl_zhora.keyframe_insert(data_path="rotation_euler", frame=158)

    # Исчезновение прикрепленного остатка семян при отрыве миски
    mound_zhora.scale = (0.55, 0.55, 0.15)
    mound_zhora.keyframe_insert(data_path="scale", frame=95)
    mound_zhora.scale = (0.001, 0.001, 0.001)
    mound_zhora.keyframe_insert(data_path="scale", frame=100)

    # Анимация брызг разлетающихся семян из перевернутой миски
    for s in seed_burst["seeds"]:
        obj = s["object"]
        obj.location = (0.0, 0.0, 0.0)
        obj.scale = (0.001, 0.001, 0.001)
        obj.keyframe_insert(data_path="location", frame=1)
        obj.keyframe_insert(data_path="scale", frame=1)

        # Вылет при кувырке
        obj.scale = (1.0, 1.0, 1.0)
        obj.keyframe_insert(data_path="scale", frame=102)

        obj.location = s["peak"]
        obj.rotation_euler = s["rot"]
        obj.keyframe_insert(data_path="location", frame=118)
        obj.keyframe_insert(data_path="rotation_euler", frame=118)

        # Падение на мрамор
        obj.location = s["target"]
        obj.keyframe_insert(data_path="location", frame=142)

    # Сглаживание ключей
    for obj in [kh, kt, zr, zh, zc, bowl_zhora]:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "BEZIER"
                    kf.easing = "EASE_IN_OUT"

    # =========================================================================
    # РЕЖИССЁРСКИЙ ТАЙМЛАЙН ШОТОВ (ТРИ ЭКШЕН-РАКУРСА)
    # =========================================================================

    # Шот 1 (Кадры 1 - 55): Динамичный средний план на вопящего Жору
    director.add_shot(
        name="The_Volcanic_Scream",
        start_frame=1,
        end_frame=55,
        cam_start=(0.42, -0.78, 0.38),
        cam_end=(0.40, -0.62, 0.35),
        look_at=(0.45, -0.10, 0.42),
        focal_length=48.0,
        fstop=2.0
    )

    # Шот 2 (Кадры 56 - 115): Низкий кинематографичный ракурс захвата и броска
    director.add_shot(
        name="The_Disdainful_Flip",
        start_frame=56,
        end_frame=115,
        cam_start=(0.15, -0.55, 0.25),
        cam_end=(0.20, -0.42, 0.30),
        look_at=(0.55, 0.25, 0.18),
        focal_length=35.0,
        fstop=2.2
    )

    # Шот 3 (Кадры 116 - 180): Широкий план удара миски об мрамор и угрозы Кеше
    director.add_shot(
        name="Crash_And_Challenge",
        start_frame=116,
        end_frame=180,
        cam_start=(0.0, -1.05, 0.45),
        cam_end=(0.0, -0.92, 0.40),
        look_at=(0.20, 0.25, 0.20),
        focal_length=42.0,
        fstop=2.4
    )

    director.finalize()

"""
=============================================================================
ЭПИЗОД 3: «НЕМАЯ СЦЕНА И ОСОЗНАНИЕ» (КАДРЫ 1 - 180 / 0:12 - 0:18)
Жора смотрит в свою почти пустую миску. Комическое сужение зрачков в точку от шока.
Огненный хохолок встает дыбом. Медленный зловещий поворот головы на чавкающего Кешу.
Грудь Жоры раздувается от ярости — пружина конфликта сжата до предела!
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
    make_stylized_parrot,
    animate_pupil_shock,
)


def build():
    # Режиссерская хронология: 180 кадров (6 секунд @ 30 FPS)
    director = Director(name="Ep03_The_Disbelief", total_frames=180)

    # 1. Интерьерное кухонное освещение (Poly Haven Studio HDRI)
    director.set_hdri("studio_small_08", strength=1.10, rotation=0.6)

    # 2. Ключевой мягкий утренний свет из окна
    bpy.ops.object.light_add(type="AREA", location=(2.2, -1.8, 3.2))
    key_light = bpy.context.active_object
    key_light.name = "Morning_Window_Sun"
    key_light.data.energy = 880.0
    key_light.data.size = 2.4
    key_light.data.color = (1.0, 0.96, 0.90)
    key_light.rotation_euler = (math.radians(35), math.radians(18), math.radians(25))

    # 3. Драматический контровой свет (Rim Light) для подчеркивания силуэта и перьев
    bpy.ops.object.light_add(type="AREA", location=(0.0, 2.5, 2.8))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Backlight"
    rim_light.data.energy = 700.0
    rim_light.data.size = 3.0
    rim_light.data.color = (0.75, 0.88, 1.0)
    rim_light.rotation_euler = (math.radians(-40), 0, 0)

    # 4. Локальный акцентный свет на лицо Жоры для кинематографического саспенса
    bpy.ops.object.light_add(type="SPOT", location=(0.85, -0.65, 0.75))
    accent_spot = bpy.context.active_object
    accent_spot.name = "Zhora_Drama_Spot"
    accent_spot.data.energy = 160.0
    accent_spot.data.spot_size = math.radians(38)
    accent_spot.data.spot_blend = 0.5
    accent_spot.data.color = (1.0, 0.92, 0.82)

    # 5. Мраморная столешница острова
    make_marble_island(location=(0.0, 0.0, -0.05), size=(3.2, 1.8, 0.1))

    # 6. Миски с едой:
    # Кеша — бирюзовая миска с гигантской горой отборного зерна
    bowl_kesha = make_food_bowl(name="Kesha_Bowl", location=(-0.45, 0.32, 0.0), color=(0.12, 0.58, 0.72, 1.0))
    mound_kesha = make_seed_mound(name="Kesha_Feast", location=(-0.45, 0.32, 0.0), mound_type="mountain")
    # Случайно упавшие зерна возле пирующего Кеши
    make_scattered_seeds("Kesha_Stray_Seeds", center=(-0.45, 0.16, 0.01), count=12, radius=0.18)

    # Жора — коралловая миска с жалким дном (меньше четверти миски)
    bowl_zhora = make_food_bowl(name="Zhora_Bowl", location=(0.45, 0.32, 0.0), color=(0.95, 0.40, 0.32, 1.0))
    mound_zhora = make_seed_mound(name="Zhora_Scraps", location=(0.45, 0.32, 0.0), radius=0.10, mound_type="scraps")

    # 7. Персонажи:
    kesha = make_stylized_parrot(name="Kesha", palette="green", location=(-0.45, -0.22, 0.0), rotation=(0.0, 0.0, math.radians(12)))
    zhora = make_stylized_parrot(name="Zhora", palette="red", location=(0.45, -0.22, 0.0), rotation=(0.0, 0.0, math.radians(-15)))

    # Привязка спот-света драмы точно к голове Жоры
    track = accent_spot.constraints.new("TRACK_TO")
    track.target = zhora["head_pivot"]
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # =========================================================================
    # АНИМАЦИЯ: ЭКСТАЗ КЕШИ VS НЕМЕЮЩИЙ ОТ ШОКА ЖОРА
    # =========================================================================

    # 1. Кеша: непрерывный пир, покачивание головы и виляние хвостом на все 180 кадров
    kh = kesha["head_pivot"]
    kt = kesha["tail"]
    peck_cycle = [-38, -10, -44, -14, -40, -12]
    for i, rx in enumerate(peck_cycle * 5):
        frame_idx = 1 + i * 6
        if frame_idx > 180:
            break
        kh.rotation_euler = (math.radians(rx), 0.0, math.radians(8 + (i % 2) * 4))
        kh.keyframe_insert(data_path="rotation_euler", frame=frame_idx)

    for i in range(1, 181, 15):
        tail_wobble = 0.18 if (i // 15) % 2 == 0 else -0.18
        kt.rotation_euler = (math.radians(-42), 0.0, tail_wobble)
        kt.keyframe_insert(data_path="rotation_euler", frame=i)

    # 2. Жора: Оцепенение -> Сужение зрачков -> Подъем хохолка -> Поворот головы -> Закипание
    zh = zhora["head_pivot"]
    zc = zhora["crest_pivot"]
    zb_low = zhora["beak_lower"]
    zw_l = zhora["wings"]["L"]
    zw_r = zhora["wings"]["R"]

    # Фаза 1 (Кадры 1 - 40): Жора гипнотизирует взглядом пустую миску
    zh.rotation_euler = (math.radians(-32), 0.0, math.radians(-5))
    zh.keyframe_insert(data_path="rotation_euler", frame=1)
    zh.keyframe_insert(data_path="rotation_euler", frame=40)

    # Комическое сужение зрачков Жоры в точку от шока (Кадры 28 - 48)
    animate_pupil_shock(zhora, frame_start=28, frame_end=46)

    # Фаза 2 (Кадры 45 - 85): Хохолок медленно и угрожающе встает на 85 градусов, вибрируя от гнева
    zc.rotation_euler = (math.radians(15), 0.0, 0.0)
    zc.keyframe_insert(data_path="rotation_euler", frame=1)
    zc.keyframe_insert(data_path="rotation_euler", frame=45)

    for f_c in range(50, 85, 5):
        jitter = 0.04 if (f_c // 5) % 2 == 0 else -0.04
        zc.rotation_euler = (math.radians(82) + jitter, 0.0, jitter)
        zc.keyframe_insert(data_path="rotation_euler", frame=f_c)

    zc.rotation_euler = (math.radians(85), 0.0, 0.0)
    zc.keyframe_insert(data_path="rotation_euler", frame=90)

    # Фаза 3 (Кадры 75 - 115): Медленный, пугающе роботизированный поворот головы на жующего Кешу
    zh.rotation_euler = (math.radians(-32), 0.0, math.radians(-5))
    zh.keyframe_insert(data_path="rotation_euler", frame=75)
    # Поворот налево в профиль точно на Кешу
    zh.rotation_euler = (math.radians(-4), 0.0, math.radians(58))
    zh.keyframe_insert(data_path="rotation_euler", frame=110)
    zh.keyframe_insert(data_path="rotation_euler", frame=140)

    # Фаза 4 (Кадры 125 - 180): Точка кипения!
    # Грудь Жоры раздувается, крылья напряженно приподнимаются
    z_chest = bpy.data.objects.get("Zhora_Chest")
    if z_chest:
        z_chest.scale = (0.85, 0.95, 1.25)
        z_chest.keyframe_insert(data_path="scale", frame=1)
        z_chest.keyframe_insert(data_path="scale", frame=120)
        z_chest.scale = (0.98, 1.15, 1.38)  # Надутая от злости грудь!
        z_chest.keyframe_insert(data_path="scale", frame=160)

    # Крылья готовятся к удару
    zw_l.rotation_euler = (0.0, 0.0, 0.0)
    zw_r.rotation_euler = (0.0, 0.0, 0.0)
    zw_l.keyframe_insert(data_path="rotation_euler", frame=120)
    zw_r.keyframe_insert(data_path="rotation_euler", frame=120)

    zw_l.rotation_euler = (math.radians(15), math.radians(18), math.radians(-12))
    zw_r.rotation_euler = (math.radians(15), math.radians(-18), math.radians(12))
    zw_l.keyframe_insert(data_path="rotation_euler", frame=165)
    zw_r.keyframe_insert(data_path="rotation_euler", frame=165)

    # Мелкое дрожание нижней челюсти от сдерживаемого крика (Кадры 145 - 180)
    for f_jaw in range(145, 180, 4):
        angle = 68 if (f_jaw // 4) % 2 == 0 else 60
        zb_low.rotation_euler = (math.radians(angle), 0.0, 0.0)
        zb_low.keyframe_insert(data_path="rotation_euler", frame=f_jaw)

    # Сглаживание траекторий анимации
    for obj in [kh, kt, zh, zc, zb_low, zw_l, zw_r]:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "BEZIER"
                    kf.easing = "EASE_IN_OUT"

    # =========================================================================
    # РЕЖИССЁРСКИЙ ТАЙМЛАЙН ШОТОВ (ТРИ КИНЕМАТОГРАФИЧЕСКИХ ПЛАНА)
    # =========================================================================

    # Шот 1 (Кадры 1 - 65): Макро-план на глаза Жоры (Macro Eye Shock).
    # Камера в упор фиксирует сужение зрачков от шока при виде пустого дна.
    director.add_shot(
        name="Shock_Pupil_Macro",
        start_frame=1,
        end_frame=65,
        cam_start=(0.48, -0.05, 0.54),
        cam_end=(0.44, -0.01, 0.53),
        look_at=(0.45, 0.04, 0.52),
        focal_length=75.0,
        fstop=1.8
    )

    # Шот 2 (Кадры 66 - 125): Восьмерка через плечо Жоры на чавкающего Кешу.
    # Жора медленно поворачивает голову, а в глубине кадра сияет пирующий Кеша.
    director.add_shot(
        name="The_Galling_Contrast",
        start_frame=66,
        end_frame=125,
        cam_start=(0.62, -0.42, 0.48),
        cam_end=(0.55, -0.36, 0.46),
        look_at=(-0.10, 0.15, 0.35),
        focal_length=50.0,
        fstop=2.0
    )

    # Шот 3 (Кадры 126 - 180): Низкий драматический голландский угол (Dutch Tilt).
    # Камера снизу смотрит на надутую грудь Жоры, его стоящий дыбом хохолок
    # и вибрирующий клюв — последние секунды перед взрывом ярости!
    director.add_shot(
        name="Boiling_Point_Low_Dutch",
        start_frame=126,
        end_frame=180,
        cam_start=(0.32, -0.58, 0.22),
        cam_end=(0.30, -0.48, 0.24),
        look_at=(0.45, -0.05, 0.48),
        focal_length=38.0,
        fstop=2.2
    )

    director.finalize()

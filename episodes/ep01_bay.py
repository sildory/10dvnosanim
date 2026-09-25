"""
=============================================================================
ЭПИЗОД 1: АКВАТОРИЯ ТОКИЙСКОГО ЗАЛИВА // ШТОРМОВОЙ НУАР (КАДРЫ 1 - 360)
Ночная операция береговой охраны префектуры Канагава в районе Дайкоку.
=============================================================================
"""

from engine.director import Director


def build():
    director = Director(name="Ep01_Tokyo_Bay", total_frames=360)

    # 1. Ночное небо и штормовой спектральный океан
    director.set_hdri("dikhololo_night", strength=0.75, rotation=1.8)
    director.set_ocean(location=(0, 0, -0.5), repeat=(4, 4), choppiness=2.1, depth=30.0)

    # 2. Объемная атмосфера шторма и секущий косой дождь
    director.set_fog(density=0.014, anisotropy=0.65)
    director.set_rain(drops_count=450, fall_speed=26.0)

    # 3. Причальная зона пирса Хонмоку
    director.spawn_ground(
        size=(35.0, 16.0, 1.2),
        location=(0, -14.0, 0.6),
        ambientcg_id="Asphalt012",
        wetness=1.0
    )

    # 4. Неоновые сигнальные огни криминалистических гидроакустических буев
    director.spawn_neon("Buoy_Light_01", location=(-4.0, 6.0, 0.4), color=(0.1, 0.85, 1.0), strength=45.0, size=(0.25, 0.25, 0.8))
    director.spawn_neon("Buoy_Light_02", location=(6.0, 12.0, 0.5), color=(1.0, 0.75, 0.1), strength=40.0, size=(0.25, 0.25, 0.8))
    director.spawn_neon("Sunken_Car_Glow", location=(1.0, 4.0, -1.5), color=(0.95, 0.05, 0.05), strength=65.0, size=(1.8, 3.8, 0.4))

    # 5. Мощный волюметрический прожектор береговой охраны, сканирующий воду
    director.add_searchlight(
        location=(14.0, -12.0, 9.0),
        target=(0.0, 5.0, 0.0),
        energy=9500.0,
        color=(0.85, 0.95, 1.0)
    )

    # =========================================================================
    # РЕЖИССЁРСКИЙ ТАЙМЛАЙН ШОТОВ (ДВЕ КАМЕРЫ НА МАРКЕРАХ)
    # =========================================================================

    # Шот 1 (Кадры 1 - 180): Низкий стедикам-пролет над штормовой водой к светящимся буям
    director.add_shot(
        name="Bay_Establishing_Glide",
        start_frame=1,
        end_frame=180,
        cam_start=(-8.5, -18.0, 1.8),
        cam_end=(-2.0, -4.0, 2.5),
        look_at=(0.0, 6.0, 0.2),
        focal_length=35.0,
        fstop=2.0
    )

    # Шот 2 (Кадры 181 - 360): Крупный портретный ракурс на алое подводное свечение затопленного авто
    director.add_shot(
        name="Sunken_Vehicle_Inspection",
        start_frame=181,
        end_frame=360,
        cam_start=(4.5, -1.0, 2.2),
        cam_end=(1.2, 0.5, 1.4),
        look_at=(1.0, 4.0, -0.8),
        focal_length=65.0,
        fstop=1.4
    )

    director.finalize()

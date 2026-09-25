"""Высокоуровневый кинематографический движок-режиссер (Director API)."""

import math
import random
import bpy
from engine.assets import get_asset_manager
from engine.materials import make_pbr, make_neon, make_water
from engine.atmosphere import setup_volume_fog
from engine.compositor import setup_cinematic_compositor


class Director:
    def __init__(self, name: str, total_frames: int = 360):
        self.name = name
        self.total_frames = total_frames
        self.scene = bpy.context.scene
        self.scene.frame_start = 1
        self.scene.frame_end = total_frames
        self.assets = get_asset_manager()

    def set_hdri(self, asset_id: str = "dikhololo_night", strength: float = 0.8, rotation: float = 0.0):
        """Подключает ночное небо из Poly Haven через API."""
        path = self.assets.polyhaven(asset_id, asset_type="hdris", resolution="2k")
        self.assets.apply_hdri_to_world(path, strength=strength, rotation_z=rotation)

    def set_ocean(self, location=(0, 0, 0), repeat=(4, 4), choppiness: float = 1.8, depth: float = 20.0):
        """Генерирует спектральный океан через модификатор Ocean."""
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=location)
        ocean = bpy.context.active_object
        ocean.name = "Ocean_Water"

        mod = ocean.modifiers.new(name="Ocean", type="OCEAN")
        mod.geometry_mode = "GENERATE"
        mod.repeat_x = repeat[0]
        mod.repeat_y = repeat[1]
        mod.spatial_size = 40.0
        mod.resolution = 14
        mod.render_resolution = 14
        mod.choppiness = choppiness
        mod.depth = depth

        mod.time = 1.0
        mod.keyframe_insert(data_path="time", frame=1)
        mod.time = 1.0 + self.total_frames * 0.04
        mod.keyframe_insert(data_path="time", frame=self.total_frames)

        mat = make_water("PBR_Ocean_Water", color=(0.015, 0.025, 0.04, 1.0), roughness=0.04)
        ocean.data.materials.append(mat)
        return ocean

    def set_fog(self, density: float = 0.012, anisotropy: float = 0.6):
        """Включает физический объемный туман для кинематографических лучей."""
        return setup_volume_fog(density=density, anisotropy=anisotropy)

    def set_rain(self, drops_count: int = 400, fall_speed: float = 26.0):
        """
        Создает высокоскоростной зацикленный штормовой дождь.
        Капли не исчезают, а непрерывно повторяют цикл падения с физическим Motion Blur.
        """
        random.seed(42)
        rain_mat = make_water("Rain_Drop_Mat", color=(0.9, 0.95, 1.0, 1.0), roughness=0.01)

        parent = bpy.data.objects.new("Rain_System", None)
        bpy.context.collection.objects.link(parent)

        # Создаем базовый меш капли один раз
        bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.4, location=(0, 0, -100))
        base_drop = bpy.context.active_object
        base_mesh = base_drop.data
        base_mesh.materials.append(rain_mat)
        bpy.context.collection.objects.unlink(base_drop)

        # Инстанцируем капли без вызова тяжелых UI-операторов
        for i in range(drops_count):
            rx = random.uniform(-16, 16)
            ry = random.uniform(-16, 16)
            rz_top = random.uniform(8, 16)
            rz_bottom = rz_top - fall_speed

            drop = bpy.data.objects.new(f"Rain_Drop_{i:04d}", base_mesh)
            bpy.context.collection.objects.link(drop)
            drop.parent = parent

            cycle_length = random.randint(15, 25)
            start_frame = 1 - random.randint(0, cycle_length)
            end_frame = start_frame + cycle_length

            drop.location = (rx, ry, rz_top)
            drop.keyframe_insert(data_path="location", frame=start_frame)

            drop.location = (rx + 2.0, ry - 0.5, rz_bottom)
            drop.keyframe_insert(data_path="location", frame=end_frame)

            if drop.animation_data and drop.animation_data.action:
                for fcurve in drop.animation_data.action.fcurves:
                    c_mod = fcurve.modifiers.new(type="CYCLES")
                    c_mod.mode_before = "REPEAT"
                    c_mod.mode_after = "REPEAT"

        return parent

    def import_polyhaven_model(self, asset_id: str, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        """Скачивает и импортирует составную GLTF-модель Poly Haven, объединяя её в Root Empty."""
        path = self.assets.polyhaven(asset_id, asset_type="models", resolution="1k")
        existing_objs = set(bpy.data.objects)

        bpy.ops.import_scene.gltf(filepath=path)
        new_objs = [obj for obj in bpy.data.objects if obj not in existing_objs]

        if not new_objs:
            raise RuntimeError(f"[DIRECTOR] Не удалось импортировать модель Poly Haven '{asset_id}'")

        root = bpy.data.objects.new(f"PH_{asset_id}_Root", None)
        bpy.context.collection.objects.link(root)

        for obj in new_objs:
            if obj.parent is None:
                obj.parent = root

        root.location = location
        root.rotation_euler = rotation
        root.scale = scale
        return root

    def spawn_ground(self, size=(40, 40, 1), location=(0, 0, 0), ambientcg_id="Asphalt012", wetness=1.0):
        """Создает мощеный причал/улицу с PBR-картами ambientCG."""
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        slab = bpy.context.active_object
        slab.scale = size
        mat = make_pbr(f"PBR_{ambientcg_id}", ambientcg_id=ambientcg_id, scale=6.0, wetness=wetness)
        slab.data.materials.append(mat)
        return slab

    def spawn_neon(self, name: str, location=(0, 0, 2), color=(0.1, 0.8, 1.0), strength=40.0, size=(0.2, 1.5, 0.3)):
        """Создает излучающую неоновую вывеску/сигнальный огонь."""
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        neon = bpy.context.active_object
        neon.name = name
        neon.scale = size
        mat = make_neon(f"{name}_Mat", color=color, strength=strength)
        neon.data.materials.append(mat)
        return neon

    def add_searchlight(self, location=(10, -10, 8), target=(0, 0, 0), energy=8000.0, color=(0.8, 0.95, 1.0)):
        """Создает мощный прожектор с трекингом точки наведения."""
        bpy.ops.object.light_add(type="SPOT", location=location)
        spot = bpy.context.active_object
        spot.data.energy = energy
        spot.data.spot_size = math.radians(30)
        spot.data.spot_blend = 0.25
        spot.data.color = color

        target_obj = bpy.data.objects.new("Light_Target", None)
        target_obj.location = target
        bpy.context.collection.objects.link(target_obj)

        track = spot.constraints.new("TRACK_TO")
        track.target = target_obj
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"
        return spot

    def add_shot(
        self,
        name: str,
        start_frame: int,
        end_frame: int,
        cam_start: tuple,
        cam_end: tuple,
        look_at: tuple,
        focal_length: float = 50.0,
        fstop: float = 2.0
    ):
        """Создает кинокамеру, анимирует пролет и привязывает её к таймлайну."""
        bpy.ops.object.camera_add(location=cam_start)
        cam_obj = bpy.context.active_object
        cam_obj.name = f"Camera_{name}"

        cam = cam_obj.data
        cam.lens = focal_length
        cam.sensor_width = 36.0

        target_empty = bpy.data.objects.new(f"Target_{name}", None)
        target_empty.location = look_at
        bpy.context.collection.objects.link(target_empty)

        cam.dof.use_dof = True
        cam.dof.focus_object = target_empty
        cam.dof.aperture_fstop = fstop

        constraint = cam_obj.constraints.new("TRACK_TO")
        constraint.target = target_empty
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

        cam_obj.location = cam_start
        cam_obj.keyframe_insert(data_path="location", frame=start_frame)
        cam_obj.location = cam_end
        cam_obj.keyframe_insert(data_path="location", frame=end_frame)

        if cam_obj.animation_data and cam_obj.animation_data.action:
            for fcurve in cam_obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "BEZIER"
                    kf.easing = "EASE_IN_OUT"

        # Регистрируем маркер
        marker = self.scene.timeline_markers.new(name=f"Marker_{name}", frame=start_frame)
        marker.camera = cam_obj

        # Если в сцене еще нет активной камеры, выставляем текущую
        if self.scene.camera is None or start_frame == 1:
            self.scene.camera = cam_obj

    def finalize(self):
        """Завершает постановку и конфигурирует композер."""
        setup_cinematic_compositor(self.scene)
        print(f"[DIRECTOR] Эпизод '{self.name}' успешно собран ({self.total_frames} кадров).") 

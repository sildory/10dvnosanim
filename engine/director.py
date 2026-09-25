"""Высокоуровневый кинематографический движок-режиссер (Director API)."""

import math
import bpy
from engine.assets import get_asset_manager
from engine.materials import make_pbr, make_neon
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
        mod.choppiness = choppiness
        mod.depth = depth

        mod.time = 1.0
        mod.keyframe_insert(data_path="time", frame=1)
        mod.time = 1.0 + self.total_frames * 0.04
        mod.keyframe_insert(data_path="time", frame=self.total_frames)

        # Материал глубокой ночной воды
        mat = bpy.data.materials.new(name="PBR_Ocean_Water")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.015, 0.025, 0.04, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.04
        bsdf.inputs["IOR"].default_value = 1.333
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = 0.95
        ocean.data.materials.append(mat)
        return ocean

    def set_fog(self, density: float = 0.012, anisotropy: float = 0.6):
        """Включает физический объемный туман для лучей света."""
        setup_volume_fog(density=density, anisotropy=anisotropy)

    def set_rain(self, drops_count: int = 400, fall_speed: float = 24.0):
        """Создает штормовой дождь со смазом (Motion Blur)."""
        import random
        random.seed(42)

        mat = bpy.data.materials.new(name="Rain_Drop_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Roughness"].default_value = 0.02
        bsdf.inputs["IOR"].default_value = 1.333
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = 0.95

        parent = bpy.data.objects.new("Rain_System", None)
        bpy.context.collection.objects.link(parent)

        for i in range(drops_count):
            rx = random.uniform(-15, 15)
            ry = random.uniform(-15, 15)
            rz = random.uniform(2, 14)

            bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.35, location=(rx, ry, rz))
            drop = bpy.context.active_object
            drop.data.materials.append(mat)
            drop.parent = parent

            drop.location = (rx, ry, rz)
            drop.keyframe_insert(data_path="location", frame=1)
            drop.location = (rx + 2.0, ry, rz - fall_speed)
            drop.keyframe_insert(data_path="location", frame=self.total_frames)

    def import_polyhaven_model(self, asset_id: str, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        """Скачивает через API и импортирует реальную 3D-модель (GLTF/GLB) из Poly Haven."""
        path = self.assets.polyhaven(asset_id, asset_type="models", resolution="1k")
        bpy.ops.import_scene.gltf(filepath=path)
        imported = bpy.context.selected_objects[0]
        imported.location = location
        imported.rotation_euler = rotation
        imported.scale = scale
        return imported

    def spawn_ground(self, size=(40, 40, 1), location=(0, 0, 0), ambientcg_id="Asphalt012", wetness=1.0):
        """Создает мощеный причал/улицу с PBR-картами ambientCG."""
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        slab = bpy.context.active_object
        slab.scale = size
        mat = make_pbr(f"PBR_{ambientcg_id}", ambientcg_id=ambientcg_id, scale=6.0, wetness=wetness)
        slab.data.materials.append(mat)
        return slab

    def spawn_neon(self, name: str, location=(0, 0, 2), color=(0.1, 0.8, 1.0), strength=40.0, size=(0.2, 1.5, 0.3)):
        """Создает излучающую неоновую вывеску."""
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        neon = bpy.context.active_object
        neon.name = name
        neon.scale = size
        mat = make_neon(f"{name}_Mat", color=color, strength=strength)
        neon.data.materials.append(mat)
        return neon

    def add_searchlight(self, location=(10, -10, 8), target=(0, 0, 0), energy=8000.0, color=(0.8, 0.95, 1.0)):
        """Создает прожектор, пробивающий объемный туман лучом."""
        bpy.ops.object.light_add(type="SPOT", location=location)
        spot = bpy.context.active_object
        spot.data.energy = energy
        spot.data.spot_size = math.radians(30)
        spot.data.spot_blend = 0.25
        spot.data.color = color

        # Наведение на цель
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
        """Создает кинокамеру, анимирует пролет кривой Безье и ПРИВЯЗЫВАЕТ К ТАЙМЛАЙНУ."""
        bpy.ops.object.camera_add(location=cam_start)
        cam_obj = bpy.context.active_object
        cam_obj.name = f"Camera_{name}"

        cam = cam_obj.data
        cam.lens = focal_length
        cam.sensor_width = 36.0

        # Точка прицеливания (DoF Focus)
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

        # Плавная интерполяция движения камеры (Bezier In/Out)
        cam_obj.location = cam_start
        cam_obj.keyframe_insert(data_path="location", frame=start_frame)
        cam_obj.location = cam_end
        cam_obj.keyframe_insert(data_path="location", frame=end_frame)

        if cam_obj.animation_data and cam_obj.animation_data.action:
            for fcurve in cam_obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "BEZIER"
                    kf.easing = "EASE_IN_OUT"

        # Нативная привязка камеры к маркеру таймлайна Blender!
        marker = self.scene.timeline_markers.new(name=f"Marker_{name}", frame=start_frame)
        marker.camera = cam_obj

    def finalize(self):
        """Включает нативный кинематографический композер."""
        setup_cinematic_compositor(self.scene)
        print(f"[DIRECTOR] Эпизод '{self.name}' полностью собран и готов к рендеру ({self.total_frames} кадров).")

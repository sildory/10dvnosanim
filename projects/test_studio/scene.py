"""Тестовая сцена: PBR-асфальт, неоновые трубы, объемный туман, motion blur и нативный композитор."""

import math
import bpy
from engine.assets import get_asset_manager
from engine.materials import make_pbr, make_neon
from engine.atmosphere import setup_volume_fog
from engine.compositor import setup_cinematic_compositor


def create_ground():
    """Создает мокрый асфальтовый пол с вытянутыми отражениями."""
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Wet_PBR_Street"

    mat = make_pbr(
        material_name="Asphalt_Wet_PBR",
        ambientcg_id="Asphalt012",
        scale=6.0,
        wetness=1.0,
        is_metallic=False
    )
    floor.data.materials.append(mat)
    return floor


def create_neon_structures():
    """Создает две яркие неоновые конструкции (Cyan и Hot Pink) для проверки отражений."""
    # 1. Вертикальная циановая неоновая трубка
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=4.5, location=(-3.0, 2.0, 2.5))
    neon_cyan = bpy.context.active_object
    neon_cyan.name = "Neon_Tube_Cyan"
    mat_cyan = make_neon("Neon_Cyan_Shader", color=(0.05, 0.85, 1.0), strength=40.0)
    neon_cyan.data.materials.append(mat_cyan)

    # 2. Горизонтальная пурпурная неоновая вывеска
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.5, 3.5, 2.8))
    neon_pink = bpy.context.active_object
    neon_pink.name = "Neon_Bar_Magenta"
    neon_pink.scale = (3.5, 0.08, 0.35)
    mat_pink = make_neon("Neon_Magenta_Shader", color=(1.0, 0.1, 0.6), strength=45.0)
    neon_pink.data.materials.append(mat_pink)


def create_hero_monolith():
    """Центральный полированный монолит с анимацией вращения (проверка Motion Blur)."""
    bpy.ops.mesh.primitive_cube_add(size=1.6, location=(0, 0, 1.0))
    cube = bpy.context.active_object
    cube.name = "Hero_Monolith"

    bevel = cube.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.08
    bevel.segments = 4
    bpy.ops.object.shade_smooth()

    # Анимация быстрого вращения для проверки честного смаза Cycles
    cube.rotation_euler = (0, 0, 0)
    cube.keyframe_insert(data_path="rotation_euler", frame=1)
    cube.rotation_euler = (0, 0, math.radians(160))
    cube.keyframe_insert(data_path="rotation_euler", frame=60)

    mat = bpy.data.materials.new(name="Chrome_Monolith")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.9, 0.95, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.95
    bsdf.inputs["Roughness"].default_value = 0.1
    cube.data.materials.append(mat)
    return cube


def setup_volumetric_spotlight():
    """Направленный прожектор, прорезающий объемный туман видимым световым лучом (God-Ray)."""
    bpy.ops.object.light_add(type="SPOT", location=(-5.0, -4.0, 5.5))
    spot = bpy.context.active_object
    spot.name = "Volumetric_Headlight"
    spot.data.energy = 4500.0
    spot.data.spot_size = math.radians(35)
    spot.data.spot_blend = 0.25
    spot.data.color = (1.0, 0.92, 0.8)
    spot.rotation_euler = (math.radians(52), math.radians(-15), math.radians(-38))


def setup_camera(focus_target):
    """Кинокамера с оптическим DoF f/2.0."""
    bpy.ops.object.camera_add(location=(-3.6, -4.5, 1.8))
    cam_obj = bpy.context.active_object
    cam_obj.name = "Cinema_Camera"
    bpy.context.scene.camera = cam_obj

    cam = cam_obj.data
    cam.lens = 50.0
    cam.sensor_width = 36.0

    cam.dof.use_dof = True
    cam.dof.focus_object = focus_target
    cam.dof.aperture_fstop = 2.0

    constraint = cam_obj.constraints.new(type="TRACK_TO")
    constraint.target = focus_target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    cam_obj.location = (-3.8, -4.6, 1.9)
    cam_obj.keyframe_insert(data_path="location", frame=1)

    cam_obj.location = (2.6, -4.2, 2.2)
    cam_obj.keyframe_insert(data_path="location", frame=60)


def build_scene():
    """Сборка тестовой сцены Этапа 3."""
    scene = bpy.context.scene
    assets = get_asset_manager()

    # 1. Звездное ночное небо Poly Haven для отражений
    hdri_path = assets.polyhaven("dikhololo_night", asset_type="hdris", resolution="2k")
    assets.apply_hdri_to_world(hdri_path, strength=0.8, rotation_z=1.2)

    # 2. Мокрый PBR-асфальт и яркие неоны
    create_ground()
    create_neon_structures()
    monolith = create_hero_monolith()

    # 3. Объемный прожектор и атмосфера
    setup_volumetric_spotlight()
    setup_volume_fog(density=0.015, anisotropy=0.65)

    # 4. Камера
    setup_camera(monolith)

    # 5. Настройка нативного Compositor (Fog Glow, Streaks, Lens Dispersion, Color Balance)
    setup_cinematic_compositor(scene) 

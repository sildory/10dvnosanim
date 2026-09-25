"""Тестовая сцена-студия: проверка честного PBR, Cycles DoF, Motion Blur и AgX."""

import math
import bpy


def create_dielectric_floor():
    """Создает отражающий мокрый асфальтовый пол (строго диэлектрик!)."""
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Wet_PBR_Floor"

    mat = bpy.data.materials.new(name="PBR_Wet_Asphalt")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    # Жесткое физическое правило: асфальт НЕ металл!
    bsdf.inputs["Base Color"].default_value = (0.02, 0.03, 0.05, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.18
    # В Blender 4.2 лаковый слой воды задается через Coat
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.85
        bsdf.inputs["Coat Roughness"].default_value = 0.05

    floor.data.materials.append(mat)
    return floor


def create_hero_monolith():
    """Создает центральный геометрический объект со скругленными гранями."""
    bpy.ops.mesh.primitive_cube_add(size=1.6, location=(0, 0, 1.0))
    cube = bpy.context.active_object
    cube.name = "Hero_Monolith"

    # Скос граней для ловли красивых бликов
    bevel = cube.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.06
    bevel.segments = 4
    bpy.ops.object.shade_smooth()

    # Анимация вращения монолита (для проверки честного смаза Motion Blur)
    cube.rotation_euler = (0, 0, 0)
    cube.keyframe_insert(data_path="rotation_euler", frame=1)
    cube.rotation_euler = (0, 0, math.radians(120))
    cube.keyframe_insert(data_path="rotation_euler", frame=60)

    # Материал полированного темного хрома
    mat = bpy.data.materials.new(name="Monolith_Chrome")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.88, 0.92, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.95
    bsdf.inputs["Roughness"].default_value = 0.12

    cube.data.materials.append(mat)
    return cube


def setup_cinematic_lighting():
    """Кинематографический трехточечный свет."""
    # 1. Теплый ключевой свет (Key Softbox)
    bpy.ops.object.light_add(type="AREA", location=(4.0, -3.5, 4.0))
    key_light = bpy.context.active_object
    key_light.data.energy = 450.0
    key_light.data.size = 2.5
    key_light.data.color = (1.0, 0.78, 0.55)
    key_light.rotation_euler = (math.radians(45), math.radians(15), math.radians(40))

    # 2. Холодный контрастный контровой свет (Rim Light) для контура
    bpy.ops.object.light_add(type="AREA", location=(-3.5, 4.0, 3.2))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 750.0
    rim_light.data.size = 2.0
    rim_light.data.color = (0.15, 0.75, 1.0)
    rim_light.rotation_euler = (math.radians(-45), 0, math.radians(-140))

    # 3. Мягкий рассеянный неон снизу (Fill Underglow)
    bpy.ops.object.light_add(type="POINT", location=(0, 0, 0.15))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 80.0
    fill_light.data.color = (0.95, 0.15, 0.35)


def setup_world_environment():
    """Настройка глубокого ночного купола окружения."""
    world = bpy.context.scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.005, 0.008, 0.015, 1.0)
        bg_node.inputs["Strength"].default_value = 0.5


def setup_camera(focus_target):
    """Кинокамера с физическим DoF (f/1.8) и пролетом по дуге."""
    bpy.ops.object.camera_add(location=(-3.2, -4.5, 2.2))
    cam_obj = bpy.context.active_object
    cam_obj.name = "Cinema_Camera"
    bpy.context.scene.camera = cam_obj

    cam = cam_obj.data
    cam.lens = 50.0
    cam.sensor_width = 36.0  # Full-Frame 35mm

    # Честный оптический Depth of Field (DoF)
    cam.dof.use_dof = True
    cam.dof.focus_object = focus_target
    cam.dof.aperture_fstop = 1.8

    # Наведение камеры строго на объект
    constraint = cam_obj.constraints.new(type="TRACK_TO")
    constraint.target = focus_target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    # Анимация пролета камеры со сглаживанием
    cam_obj.location = (-3.8, -4.2, 2.0)
    cam_obj.keyframe_insert(data_path="location", frame=1)

    cam_obj.location = (2.8, -4.6, 2.5)
    cam_obj.keyframe_insert(data_path="location", frame=60)


def build_scene():
    """Точка сборки тестовой сцены."""
    setup_world_environment()
    create_dielectric_floor()
    monolith = create_hero_monolith()
    setup_cinematic_lighting()
    setup_camera(monolith)

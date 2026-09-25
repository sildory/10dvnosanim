"""Сцена test_studio с подключением внешних HDRI и PBR-текстур через assets.py."""

import math
import bpy
from engine.assets import get_asset_manager


def create_pbr_asphalt_floor(pbr_maps: dict):
    """Создает мокрый асфальтовый пол с настоящими PBR-картами (строго диэлектрик!)."""
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "PBR_Asphalt_Floor"

    mat = bpy.data.materials.new(name="PBR_Asphalt_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Базовые шейдерные ноды
    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")

    # Координаты текстур и масштабирование тайлинга
    node_coord = nodes.new(type="ShaderNodeTexCoord")
    node_mapping = nodes.new(type="ShaderNodeMapping")
    # Масштабируем тайлинг текстуры асфальта
    node_mapping.inputs["Scale"].default_value = (5.0, 5.0, 5.0)
    links.new(node_coord.outputs["UV"], node_mapping.inputs["Vector"])

    # 1. Base Color карта
    if "color" in pbr_maps:
        tex_col = nodes.new(type="ShaderNodeTexImage")
        tex_col.image = bpy.data.images.load(pbr_maps["color"], check_existing=True)
        tex_col.image.colorspace_settings.name = "sRGB"
        links.new(node_mapping.outputs["Vector"], tex_col.inputs["Vector"])
        links.new(tex_col.outputs["Color"], bsdf.inputs["Base Color"])

    # 2. Roughness карта
    if "roughness" in pbr_maps:
        tex_rough = nodes.new(type="ShaderNodeTexImage")
        tex_rough.image = bpy.data.images.load(pbr_maps["roughness"], check_existing=True)
        tex_rough.image.colorspace_settings.name = "Non-Color"
        links.new(node_mapping.outputs["Vector"], tex_rough.inputs["Vector"])
        links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])

    # 3. Normal карта
    if "normal" in pbr_maps:
        tex_norm = nodes.new(type="ShaderNodeTexImage")
        tex_norm.image = bpy.data.images.load(pbr_maps["normal"], check_existing=True)
        tex_norm.image.colorspace_settings.name = "Non-Color"

        node_norm_map = nodes.new(type="ShaderNodeNormalMap")
        node_norm_map.inputs["Strength"].default_value = 1.0

        links.new(node_mapping.outputs["Vector"], tex_norm.inputs["Vector"])
        links.new(tex_norm.outputs["Color"], node_norm_map.inputs["Color"])
        links.new(node_norm_map.outputs["Normal"], bsdf.inputs["Normal"])

    # Правило физики: асфальт — диэлектрик (metallic = 0)
    bsdf.inputs["Metallic"].default_value = 0.0

    # Эффект мокрой пленки воды (Coat)
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.95
        bsdf.inputs["Coat Roughness"].default_value = 0.04

    links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    floor.data.materials.append(mat)
    return floor


def create_hero_monolith():
    """Создает центральный полированный монолит со скошенными гранями."""
    bpy.ops.mesh.primitive_cube_add(size=1.6, location=(0, 0, 1.0))
    cube = bpy.context.active_object
    cube.name = "Hero_Monolith"

    bevel = cube.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.06
    bevel.segments = 4
    bpy.ops.object.shade_smooth()

    # Анимация вращения (для теста Motion Blur)
    cube.rotation_euler = (0, 0, 0)
    cube.keyframe_insert(data_path="rotation_euler", frame=1)
    cube.rotation_euler = (0, 0, math.radians(120))
    cube.keyframe_insert(data_path="rotation_euler", frame=60)

    # Материал полированного темного хрома
    mat = bpy.data.materials.new(name="Monolith_Chrome")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.9, 0.92, 0.95, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.98
    bsdf.inputs["Roughness"].default_value = 0.12

    cube.data.materials.append(mat)
    return cube


def setup_cinematic_lighting():
    """Студийная кинематографическая подсветка."""
    # Теплый Key Softbox
    bpy.ops.object.light_add(type="AREA", location=(4.0, -3.5, 4.0))
    key_light = bpy.context.active_object
    key_light.data.energy = 500.0
    key_light.data.size = 2.5
    key_light.data.color = (1.0, 0.78, 0.55)
    key_light.rotation_euler = (math.radians(45), math.radians(15), math.radians(40))

    # Контровой неоновый Rim Light
    bpy.ops.object.light_add(type="AREA", location=(-3.5, 4.0, 3.2))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 850.0
    rim_light.data.size = 2.0
    rim_light.data.color = (0.1, 0.8, 1.0)
    rim_light.rotation_euler = (math.radians(-45), 0, math.radians(-140))


def setup_camera(focus_target):
    """Кинокамера с фокусным расстоянием 50 мм и физическим размытием диафрагмы."""
    bpy.ops.object.camera_add(location=(-3.8, -4.2, 2.0))
    cam_obj = bpy.context.active_object
    cam_obj.name = "Cinema_Camera"
    bpy.context.scene.camera = cam_obj

    cam = cam_obj.data
    cam.lens = 50.0
    cam.sensor_width = 36.0

    # Честный оптический DoF f/1.8
    cam.dof.use_dof = True
    cam.dof.focus_object = focus_target
    cam.dof.aperture_fstop = 1.8

    constraint = cam_obj.constraints.new(type="TRACK_TO")
    constraint.target = focus_target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    cam_obj.location = (-3.8, -4.2, 2.0)
    cam_obj.keyframe_insert(data_path="location", frame=1)

    cam_obj.location = (2.8, -4.6, 2.5)
    cam_obj.keyframe_insert(data_path="location", frame=60)


def build_scene():
    """Точка входа сцены: скачивает ассеты по API и собирает мир."""
    assets = get_asset_manager()

    # 1. Загрузка HDRI звездного неба Poly Haven
    hdri_path = assets.polyhaven("dikhololo_night", asset_type="hdris", resolution="2k")
    assets.apply_hdri_to_world(hdri_path, strength=1.2, rotation_z=1.2)

    # 2. Загрузка PBR-текстур асфальта ambientCG
    asphalt_maps = assets.ambientcg("Asphalt012", resolution="2K", filetype="JPG")
    create_pbr_asphalt_floor(asphalt_maps)

    # 3. Монолит, свет и камера
    monolith = create_hero_monolith()
    setup_cinematic_lighting()
    setup_camera(monolith) 

"""
Библиотека высокоуровневых компонентов (кит-префабов):
ванты, кабели, океан, дождь, неон, свет, процедурные здания и импорт моделей.
"""

import math
import random
import bpy
from engine.assets import get_asset_manager
from engine.materials import make_neon, make_water, make_pbr


def make_cables(
    name: str = "Cables_Rig",
    points_pairs: list = None,
    bevel_depth: float = 0.025,
    resolution: int = 4,
    material: bpy.types.Material = None
) -> bpy.types.Object:
    """
    Создает настоящие трехмерные провода / ванты моста через кривые с Bevel.
    Устраняет мерцание субпиксельных линий на рендере.
    points_pairs: список пар точек [((x1,y1,z1), (x2,y2,z2)), ...]
    """
    if points_pairs is None:
        points_pairs = [
            ((-10.0, 5.0, 12.0), (0.0, 0.0, 3.0)),
            ((10.0, 5.0, 12.0), (0.0, 0.0, 3.0)),
        ]

    curve_data = bpy.data.curves.new(name=f"{name}_Data", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = resolution
    curve_data.use_fill_caps = True

    for p_start, p_end in points_pairs:
        spline = curve_data.splines.new(type="POLY")
        spline.points.add(1)
        spline.points[0].co = (p_start[0], p_start[1], p_start[2], 1.0)
        spline.points[1].co = (p_end[0], p_end[1], p_end[2], 1.0)

    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # Материал кабеля (темная прорезиненная сталь, диэлектрическая оболочка)
    if material is None:
        mat = bpy.data.materials.new(name=f"{name}_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.3
        bsdf.inputs["Metallic"].default_value = 0.2
        material = mat

    curve_obj.data.materials.append(material)
    return curve_obj


def make_ocean(
    name: str = "Ocean_Water",
    location=(0, 0, 0),
    repeat=(4, 4),
    spatial_size: float = 40.0,
    resolution: int = 14,
    choppiness: float = 1.8,
    depth: float = 25.0,
    total_frames: int = 60,
    wave_speed: float = 0.04
) -> bpy.types.Object:
    """Генерирует спектральный океан с волнами через нативный модификатор Ocean."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=location)
    ocean = bpy.context.active_object
    ocean.name = name

    mod = ocean.modifiers.new(name="OceanModifier", type="OCEAN")
    mod.geometry_mode = "GENERATE"
    mod.repeat_x = repeat[0]
    mod.repeat_y = repeat[1]
    mod.spatial_size = spatial_size
    mod.resolution = resolution
    mod.choppiness = choppiness
    mod.depth = depth

    # Анимация движения спектральных волн
    mod.time = 1.0
    mod.keyframe_insert(data_path="time", frame=1)
    mod.time = 1.0 + total_frames * wave_speed
    mod.keyframe_insert(data_path="time", frame=total_frames)

    # Физически корректный глубокий шейдер воды
    water_mat = make_water(f"{name}_Shader")
    ocean.data.materials.append(water_mat)
    return ocean


def make_rain(
    name: str = "Rain_System",
    drops_count: int = 500,
    bounds=(25.0, 25.0, 14.0),
    center=(0.0, 0.0, 8.0),
    fall_speed: float = 24.0,
    slant=(1.5, -0.5),
    total_frames: int = 60
) -> bpy.types.Object:
    """
    Генерирует штормовой дождь. На скорости Cycles размывает
    капли в фотореалистичные косые дождевые струи через нативный Motion Blur.
    """
    random.seed(42)
    parent = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(parent)

    rain_mat = make_water("Rain_Drop_Glass", roughness=0.01)

    half_x = bounds[0] / 2.0
    half_y = bounds[1] / 2.0
    half_z = bounds[2] / 2.0

    for i in range(drops_count):
        rx = center[0] + random.uniform(-half_x, half_x)
        ry = center[1] + random.uniform(-half_y, half_y)
        rz = center[2] + random.uniform(-half_z, half_z)

        # Капля вытянута по Z в цилиндр
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.005,
            depth=0.35,
            location=(rx, ry, rz)
        )
        drop = bpy.context.active_object
        drop.name = f"Drop_{i:04d}"
        drop.data.materials.append(rain_mat)
        drop.parent = parent

        # Анимация падения с ветровым скосом
        drop.location = (rx, ry, rz)
        drop.keyframe_insert(data_path="location", frame=1)

        drop.location = (rx + slant[0], ry + slant[1], rz - fall_speed)
        drop.keyframe_insert(data_path="location", frame=total_frames)

    return parent


def make_neon_sign(
    name: str,
    location=(0, 0, 2),
    rotation=(0, 0, 0),
    size=(2.0, 0.1, 0.4),
    color=(0.1, 0.85, 1.0),
    strength: float = 40.0
) -> bpy.types.Object:
    """Создает геометрическую световую панель газоразрядного неона."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    neon = bpy.context.active_object
    neon.name = name
    neon.scale = size
    neon.rotation_euler = rotation

    mat = make_neon(f"{name}_Mat", color=color, strength=strength)
    neon.data.materials.append(mat)
    return neon


def make_searchlight(
    name: str = "Searchlight",
    location=(10, -10, 8),
    target=(0, 0, 0),
    energy: float = 7500.0,
    color=(0.85, 0.95, 1.0),
    spot_size_deg: float = 32.0,
    spot_blend: float = 0.25
) -> tuple:
    """Создает узконаправленный прожектор с автонаведением на целевую точку."""
    bpy.ops.object.light_add(type="SPOT", location=location)
    spot = bpy.context.active_object
    spot.name = name
    spot.data.energy = energy
    spot.data.spot_size = math.radians(spot_size_deg)
    spot.data.spot_blend = spot_blend
    spot.data.color = color

    target_obj = bpy.data.objects.new(f"{name}_Target", None)
    target_obj.location = target
    bpy.context.collection.objects.link(target_obj)

    track = spot.constraints.new("TRACK_TO")
    track.target = target_obj
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    return spot, target_obj


def make_softbox(
    name: str = "Softbox_Area",
    location=(0, 0, 6),
    rotation=(math.radians(45), 0, 0),
    size=(4.0, 4.0),
    energy: float = 1200.0,
    color=(0.95, 0.98, 1.0)
) -> bpy.types.Object:
    """Создает рассеянный прямоугольный софтбокс (Area Light) для нуарного света."""
    bpy.ops.object.light_add(type="AREA", location=location)
    area = bpy.context.active_object
    area.name = name
    area.rotation_euler = rotation
    area.data.shape = "RECTANGLE"
    area.data.size = size[0]
    area.data.size_y = size[1]
    area.data.energy = energy
    area.data.color = color
    return area


def make_city_block(
    name: str = "City_Backdrop",
    location=(0, 25.0, 0),
    buildings_count: int = 6,
    spacing: float = 8.0,
    seed: int = 42
) -> bpy.types.Object:
    """Генерирует процедурный массив зданий для городского фона."""
    random.seed(seed)
    root = bpy.data.objects.new(name, None)
    root.location = location
    bpy.context.collection.objects.link(root)

    concrete_mat = bpy.data.materials.new(name="City_Concrete")
    concrete_mat.use_nodes = True
    c_bsdf = concrete_mat.node_tree.nodes.get("Principled BSDF")
    c_bsdf.inputs["Base Color"].default_value = (0.04, 0.04, 0.05, 1.0)
    c_bsdf.inputs["Roughness"].default_value = 0.8
    c_bsdf.inputs["Metallic"].default_value = 0.0

    start_x = -((buildings_count - 1) * spacing) / 2.0

    for i in range(buildings_count):
        w = random.uniform(5.0, 7.5)
        d = random.uniform(6.0, 9.0)
        h = random.uniform(18.0, 36.0)
        bx = start_x + (i * spacing) + random.uniform(-1.0, 1.0)
        by = random.uniform(-2.0, 2.0)
        bz = h / 2.0

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bz))
        b_obj = bpy.context.active_object
        b_obj.name = f"Building_{i:02d}"
        b_obj.scale = (w, d, h)
        b_obj.parent = root

        bevel = b_obj.modifiers.new("Bevel", "BEVEL")
        bevel.width = 0.2
        bevel.segments = 2

        b_obj.data.materials.append(concrete_mat)

    return root


def import_model(
    asset_id: str,
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
    name: str = None
) -> bpy.types.Object:
    """Скачивает по API и импортирует GLTF/GLB модель из Poly Haven."""
    assets = get_asset_manager()
    path = assets.polyhaven(asset_id, asset_type="models", resolution="1k")
    bpy.ops.import_scene.gltf(filepath=path)
    imported = bpy.context.selected_objects[0]

    if name:
        imported.name = name
    imported.location = location
    imported.rotation_euler = rotation
    imported.scale = scale
    return imported

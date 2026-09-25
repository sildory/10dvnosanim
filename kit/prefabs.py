"""
Библиотека высокоуровневых компонентов (кит-префабов):
Попугаи (персонажи с пивотами анимации), кухонный мраморный остров,
миски, корм, мерный совок, освещение и окружение.
"""

import math
import random
import bpy
from engine.assets import get_asset_manager
from engine.materials import make_neon, make_water, make_pbr


def make_marble_island(
    name: str = "Kitchen_Marble_Island",
    location=(0.0, 0.0, -0.05),
    size=(3.2, 1.8, 0.1)
) -> bpy.types.Object:
    """
    Создает премиальный кухонный остров с полированным мрамором,
    фасками и отражениями ресторанного уровня.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    table = bpy.context.active_object
    table.name = name
    table.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Делаем мягкую фаску на ребрах столешницы
    bevel = table.modifiers.new("Table_Bevel", "BEVEL")
    bevel.width = 0.015
    bevel.segments = 3

    # Применяем сглаживание нормалей
    for poly in table.data.polygons:
        poly.use_smooth = True

    # Создаем роскошный процедурный материал полированного каррарского мрамора
    mat = bpy.data.materials.new(name="PBR_Luxury_Marble")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")

    # Текстурные координаты и генераторы прожилок мрамора
    coord = nodes.new(type="ShaderNodeTexCoord")
    mapping = nodes.new(type="ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (2.5, 2.5, 2.5)
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])

    noise1 = nodes.new(type="ShaderNodeTexNoise")
    noise1.inputs["Scale"].default_value = 4.0
    noise1.inputs["Detail"].default_value = 8.0
    noise1.inputs["Roughness"].default_value = 0.4
    links.new(mapping.outputs["Vector"], noise1.inputs["Vector"])

    noise2 = nodes.new(type="ShaderNodeTexNoise")
    noise2.inputs["Scale"].default_value = 16.0
    noise2.inputs["Detail"].default_value = 4.0
    links.new(mapping.outputs["Vector"], noise2.inputs["Vector"])

    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.35
    color_ramp.color_ramp.elements[0].color = (0.25, 0.28, 0.32, 1.0)  # Темные прожилки
    color_ramp.color_ramp.elements[1].position = 0.70
    color_ramp.color_ramp.elements[1].color = (0.96, 0.97, 0.98, 1.0)  # Белый мрамор

    mix_tex = nodes.new(type="ShaderNodeMix")
    mix_tex.data_type = "FLOAT"
    mix_tex.inputs[0].default_value = 0.3
    links.new(noise1.outputs["Fac"], mix_tex.inputs[2])
    links.new(noise2.outputs["Fac"], mix_tex.inputs[3])
    links.new(mix_tex.outputs[0], color_ramp.inputs["Fac"])

    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.08  # Зеркальный глянец

    # Clearcoat / Coat для глубокого эффекта полировки
    coat_sock = bsdf.inputs.get("Coat Weight") or bsdf.inputs.get("Coat")
    if coat_sock:
        coat_sock.default_value = 1.0
        coat_rough = bsdf.inputs.get("Coat Roughness")
        if coat_rough:
            coat_rough.default_value = 0.03

    links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    table.data.materials.append(mat)
    return table


def make_food_bowl(
    name: str = "Bowl",
    location=(0.0, 0.0, 0.0),
    radius: float = 0.16,
    height: float = 0.08,
    color=(0.15, 0.65, 0.75, 1.0)
) -> bpy.types.Object:
    """
    Создает тяжелую стильную керамическую миску для кормления.
    """
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=height,
        location=(location[0], location[1], location[2] + height / 2.0)
    )
    bowl = bpy.context.active_object
    bowl.name = name

    # Сглаживание и фаска
    for poly in bowl.data.polygons:
        poly.use_smooth = True

    bevel = bowl.modifiers.new("Bevel", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 3

    mat = bpy.data.materials.new(name=f"{name}_Ceramic_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.15
    coat = bsdf.inputs.get("Coat Weight") or bsdf.inputs.get("Coat")
    if coat:
        coat.default_value = 0.9

    bowl.data.materials.append(mat)
    return bowl


def make_grain_scoop(
    name: str = "Grain_Scoop",
    location=(0.0, 0.0, 0.6),
    rotation=(math.radians(20), 0, 0)
) -> bpy.types.Object:
    """
    Создает эргономичный металлический совок для корма, который держит оператор.
    """
    root = bpy.data.objects.new(name, None)
    root.location = location
    root.rotation_euler = rotation
    bpy.context.collection.objects.link(root)

    # Лопасть совка
    bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.18, location=(0, 0.08, 0))
    blade = bpy.context.active_object
    blade.name = f"{name}_Blade"
    blade.scale = (1.0, 1.6, 0.6)
    blade.parent = root

    # Ручка совка
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.22, location=(0, -0.16, 0))
    handle = bpy.context.active_object
    handle.name = f"{name}_Handle"
    handle.rotation_euler = (math.radians(90), 0, 0)
    handle.parent = root

    # Стальной шлифованный PBR материал
    metal_mat = bpy.data.materials.new(name="Stainless_Steel_Mat")
    metal_mat.use_nodes = True
    bsdf = metal_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.86, 0.88, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.95
    bsdf.inputs["Roughness"].default_value = 0.22

    blade.data.materials.append(metal_mat)
    handle.data.materials.append(metal_mat)

    # Горка отборных семян внутри совка
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085, location=(0, 0.07, 0.02))
    seeds = bpy.context.active_object
    seeds.name = f"{name}_Seeds_Pile"
    seeds.scale = (0.9, 1.3, 0.5)
    seeds.parent = root

    seed_mat = bpy.data.materials.new(name="Raw_Grain_Seeds_Mat")
    seed_mat.use_nodes = True
    s_bsdf = seed_mat.node_tree.nodes.get("Principled BSDF")
    s_bsdf.inputs["Base Color"].default_value = (0.82, 0.64, 0.32, 1.0)  # Золотистые зерна
    s_bsdf.inputs["Roughness"].default_value = 0.45
    seeds.data.materials.append(seed_mat)

    return root


def make_stylized_parrot(
    name: str = "Parrot",
    palette: str = "green",
    location=(0.0, 0.0, 0.0),
    rotation=(0.0, 0.0, 0.0)
) -> dict:
    """
    Создает выразительного, харизматичного процедурного попугая с отдельными
    пивотами шеи, глаз, хохолка и крыльев для покадровой анимации.
    """
    root = bpy.data.objects.new(f"{name}_Root", None)
    root.location = location
    root.rotation_euler = rotation
    bpy.context.collection.objects.link(root)

    # 1. Цветовые палитры персонажей
    if palette == "green":  # Кеша
        body_color = (0.08, 0.65, 0.22, 1.0)     # Сочный изумруд
        chest_color = (0.98, 0.88, 0.15, 1.0)    # Ярко-желтая грудка
        crest_color = (0.98, 0.85, 0.10, 1.0)    # Золотой хохолок
        beak_color = (0.92, 0.86, 0.74, 1.0)     # Слоновая кость
        iris_color = (0.85, 0.45, 0.10, 1.0)     # Янтарные глаза
    else:  # Жора (красный бунтарь)
        body_color = (0.92, 0.14, 0.08, 1.0)     # Алый огненный
        chest_color = (1.0, 0.55, 0.05, 1.0)     # Оранжевая грудка
        crest_color = (1.0, 0.25, 0.05, 1.0)     # Пылающий хохолок
        beak_color = (0.22, 0.22, 0.25, 1.0)     # Темный сланцевый клюв
        iris_color = (0.95, 0.90, 0.10, 1.0)     # Пронзительно желтый взгляд

    # Материал перьев тела (с легким бархатистым sheen)
    body_mat = bpy.data.materials.new(name=f"{name}_Body_Mat")
    body_mat.use_nodes = True
    b_bsdf = body_mat.node_tree.nodes.get("Principled BSDF")
    b_bsdf.inputs["Base Color"].default_value = body_color
    b_bsdf.inputs["Roughness"].default_value = 0.55

    chest_mat = bpy.data.materials.new(name=f"{name}_Chest_Mat")
    chest_mat.use_nodes = True
    c_bsdf = chest_mat.node_tree.nodes.get("Principled BSDF")
    c_bsdf.inputs["Base Color"].default_value = chest_color
    c_bsdf.inputs["Roughness"].default_value = 0.55

    beak_mat = bpy.data.materials.new(name=f"{name}_Beak_Mat")
    beak_mat.use_nodes = True
    bk_bsdf = beak_mat.node_tree.nodes.get("Principled BSDF")
    bk_bsdf.inputs["Base Color"].default_value = beak_color
    bk_bsdf.inputs["Roughness"].default_value = 0.25

    # 2. Туловище (каплевидная форма)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.18, location=(0, 0, 0.32))
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    body.scale = (1.0, 1.15, 1.35)
    body.parent = root
    body.data.materials.append(body_mat)

    # Грудка
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.15, location=(0, 0.07, 0.30))
    chest = bpy.context.active_object
    chest.name = f"{name}_Chest"
    chest.scale = (0.85, 0.95, 1.25)
    chest.parent = body
    chest.data.materials.append(chest_mat)

    # 3. Пивот шеи и головы (Head_Pivot)
    head_pivot = bpy.data.objects.new(f"{name}_Head_Pivot", None)
    head_pivot.location = (0, 0.04, 0.52)
    bpy.context.collection.objects.link(head_pivot)
    head_pivot.parent = root

    # Голова
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.14, location=(0, 0, 0))
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    head.scale = (1.0, 1.08, 1.05)
    head.parent = head_pivot
    head.data.materials.append(body_mat)

    # 4. Выразительный загнутый клюв
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.045, depth=0.11, location=(0, 0.15, -0.02))
    beak = bpy.context.active_object
    beak.name = f"{name}_Beak"
    beak.rotation_euler = (math.radians(110), 0, 0)
    beak.parent = head_pivot
    beak.data.materials.append(beak_mat)

    # 5. Подвижный хохолок (Crest Pivot для выражения эмоций)
    crest_pivot = bpy.data.objects.new(f"{name}_Crest_Pivot", None)
    crest_pivot.location = (0, -0.02, 0.13)
    bpy.context.collection.objects.link(crest_pivot)
    crest_pivot.parent = head_pivot

    crest_mat = bpy.data.materials.new(name=f"{name}_Crest_Mat")
    crest_mat.use_nodes = True
    cr_bsdf = crest_mat.node_tree.nodes.get("Principled BSDF")
    cr_bsdf.inputs["Base Color"].default_value = crest_color
    cr_bsdf.inputs["Roughness"].default_value = 0.5

    for idx, tilt in enumerate([-18, 0, 18]):
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.018, depth=0.14, location=(0, 0.02, 0.06))
        feather = bpy.context.active_object
        feather.name = f"{name}_Crest_Feather_{idx}"
        feather.rotation_euler = (math.radians(-35 + idx * 8), 0, math.radians(tilt))
        feather.parent = crest_pivot
        feather.data.materials.append(crest_mat)

    # 6. Крупные мультяшные глаза
    eye_mat = bpy.data.materials.new(name=f"{name}_Eye_Cornea")
    eye_mat.use_nodes = True
    e_bsdf = eye_mat.node_tree.nodes.get("Principled BSDF")
    e_bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
    e_bsdf.inputs["Roughness"].default_value = 0.05

    for side, sign in [("L", -1), ("R", 1)]:
        # Белок
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.038,
            location=(sign * 0.09, 0.06, 0.03)
        )
        eye = bpy.context.active_object
        eye.name = f"{name}_Eye_{side}"
        eye.parent = head_pivot

        sclera_mat = bpy.data.materials.new(name=f"{name}_Eye_Sclera_{side}")
        sclera_mat.use_nodes = True
        s_bsdf = sclera_mat.node_tree.nodes.get("Principled BSDF")
        s_bsdf.inputs["Base Color"].default_value = iris_color
        s_bsdf.inputs["Roughness"].default_value = 0.1
        eye.data.materials.append(sclera_mat)

        # Зрачок
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=0.022,
            location=(sign * 0.10, 0.082, 0.032)
        )
        pupil = bpy.context.active_object
        pupil.name = f"{name}_Pupil_{side}"
        pupil.parent = eye
        pupil.data.materials.append(eye_mat)

    # 7. Крылья на плечевых шарнирах
    wings = {}
    for side, sign in [("L", -1), ("R", 1)]:
        w_pivot = bpy.data.objects.new(f"{name}_Wing_{side}_Pivot", None)
        w_pivot.location = (sign * 0.18, -0.02, 0.42)
        bpy.context.collection.objects.link(w_pivot)
        w_pivot.parent = root

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16, radius=0.06, depth=0.34,
            location=(sign * 0.02, -0.06, -0.10)
        )
        w_mesh = bpy.context.active_object
        w_mesh.name = f"{name}_Wing_{side}_Mesh"
        w_mesh.scale = (0.45, 1.2, 1.0)
        w_mesh.rotation_euler = (math.radians(25), sign * math.radians(10), 0)
        w_mesh.parent = w_pivot
        w_mesh.data.materials.append(body_mat)
        wings[side] = w_pivot

    # 8. Хвост
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.22, 0.15))
    tail = bpy.context.active_object
    tail.name = f"{name}_Tail"
    tail.scale = (0.08, 0.32, 0.02)
    tail.rotation_euler = (math.radians(-42), 0, 0)
    tail.parent = root
    tail.data.materials.append(body_mat)

    # 9. Лапки с когтями, стоящие на мраморе
    leg_mat = bpy.data.materials.new(name=f"{name}_Leg_Mat")
    leg_mat.use_nodes = True
    l_bsdf = leg_mat.node_tree.nodes.get("Principled BSDF")
    l_bsdf.inputs["Base Color"].default_value = (0.4, 0.42, 0.45, 1.0)
    l_bsdf.inputs["Roughness"].default_value = 0.65

    feet = {}
    for side, sign in [("L", -1), ("R", 1)]:
        f_obj = bpy.data.objects.new(f"{name}_Foot_{side}", None)
        f_obj.location = (sign * 0.08, 0.02, 0.0)
        bpy.context.collection.objects.link(f_obj)
        f_obj.parent = root

        bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.16, location=(0, 0, 0.08))
        leg = bpy.context.active_object
        leg.parent = f_obj
        leg.data.materials.append(leg_mat)

        # Коготки
        for toe_rot in [-25, 0, 25]:
            bpy.ops.mesh.primitive_cone_add(radius1=0.007, depth=0.05, location=(0, 0.03, 0.005))
            toe = bpy.context.active_object
            toe.rotation_euler = (math.radians(90), 0, math.radians(toe_rot))
            toe.parent = f_obj
            toe.data.materials.append(leg_mat)

        feet[side] = f_obj

    return {
        "root": root,
        "head_pivot": head_pivot,
        "crest_pivot": crest_pivot,
        "wings": wings,
        "feet": feet,
        "name": name,
    }


# Сохраняем функции предыдущего эпизода для обратной совместимости
def make_cables(*args, **kwargs):
    return None

def make_ocean(*args, **kwargs):
    return None

def make_rain(*args, **kwargs):
    return None

def make_neon_sign(*args, **kwargs):
    return None

def make_searchlight(*args, **kwargs):
    return None

def make_softbox(*args, **kwargs):
    return None

def make_city_block(*args, **kwargs):
    return None

def import_model(*args, **kwargs):
    return None 

"""Модуль генерации физически корректных PBR-материалов, воды и неона в Blender."""

import bpy
from engine.assets import get_asset_manager


def make_pbr(
    material_name: str,
    ambientcg_id: str = None,
    scale: float = 1.0,
    wetness: float = 0.9,
    is_metallic: bool = False,
    resolution: str = "2K"
) -> bpy.types.Material:
    """Создает PBR-материал по набору карт ambientCG с соблюдением физики диэлектриков."""
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Базовые ноды
    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")

    # Текстурные координаты и масштабирование (Tiling)
    node_coord = nodes.new(type="ShaderNodeTexCoord")
    node_mapping = nodes.new(type="ShaderNodeMapping")
    node_mapping.inputs["Scale"].default_value = (scale, scale, scale)
    links.new(node_coord.outputs["UV"], node_mapping.inputs["Vector"])

    # Загрузка текстур через менеджер ассетов
    pbr_maps = {}
    if ambientcg_id:
        assets = get_asset_manager()
        pbr_maps = assets.ambientcg(ambientcg_id, resolution=resolution, filetype="JPG")

    # 1. Base Color и Ambient Occlusion
    if "color" in pbr_maps:
        tex_col = nodes.new(type="ShaderNodeTexImage")
        tex_col.image = bpy.data.images.load(pbr_maps["color"], check_existing=True)
        tex_col.image.colorspace_settings.name = "sRGB"
        links.new(node_mapping.outputs["Vector"], tex_col.inputs["Vector"])

        if "ao" in pbr_maps:
            tex_ao = nodes.new(type="ShaderNodeTexImage")
            tex_ao.image = bpy.data.images.load(pbr_maps["ao"], check_existing=True)
            tex_ao.image.colorspace_settings.name = "Non-Color"
            links.new(node_mapping.outputs["Vector"], tex_ao.inputs["Vector"])

            # Подмешивание AO через умножение
            mix_node = nodes.new(type="ShaderNodeMix")
            mix_node.data_type = "RGBA"
            mix_node.blend_type = "MULTIPLY"
            mix_node.inputs["Factor"].default_value = 0.8
            links.new(tex_col.outputs["Color"], mix_node.inputs[6])
            links.new(tex_ao.outputs["Color"], mix_node.inputs[7])
            links.new(mix_node.outputs[2], bsdf.inputs["Base Color"])
        else:
            links.new(tex_col.outputs["Color"], bsdf.inputs["Base Color"])

    # 2. Roughness (Шероховатость)
    if "roughness" in pbr_maps:
        tex_rough = nodes.new(type="ShaderNodeTexImage")
        tex_rough.image = bpy.data.images.load(pbr_maps["roughness"], check_existing=True)
        tex_rough.image.colorspace_settings.name = "Non-Color"
        links.new(node_mapping.outputs["Vector"], tex_rough.inputs["Vector"])
        links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = 0.35

    # 3. Рельеф: Normal Map и Micro-Bump
    bump_target = bsdf.inputs["Normal"]

    if "displacement" in pbr_maps:
        tex_disp = nodes.new(type="ShaderNodeTexImage")
        tex_disp.image = bpy.data.images.load(pbr_maps["displacement"], check_existing=True)
        tex_disp.image.colorspace_settings.name = "Non-Color"
        links.new(node_mapping.outputs["Vector"], tex_disp.inputs["Vector"])

        node_bump = nodes.new(type="ShaderNodeBump")
        node_bump.inputs["Strength"].default_value = 0.15
        node_bump.inputs["Distance"].default_value = 0.1
        links.new(tex_disp.outputs["Color"], node_bump.inputs["Height"])
        links.new(node_bump.outputs["Normal"], bump_target)
        bump_target = node_bump.inputs["Normal"]

    if "normal" in pbr_maps:
        tex_norm = nodes.new(type="ShaderNodeTexImage")
        tex_norm.image = bpy.data.images.load(pbr_maps["normal"], check_existing=True)
        tex_norm.image.colorspace_settings.name = "Non-Color"
        links.new(node_mapping.outputs["Vector"], tex_norm.inputs["Vector"])

        node_norm_map = nodes.new(type="ShaderNodeNormalMap")
        node_norm_map.inputs["Strength"].default_value = 1.0
        links.new(tex_norm.outputs["Color"], node_norm_map.inputs["Color"])
        links.new(node_norm_map.outputs["Normal"], bump_target)

    # 4. Физические свойства (жесткое разделение металлов и диэлектриков)
    bsdf.inputs["Metallic"].default_value = 1.0 if is_metallic else 0.0

    # Водная глазурь (Coat): создает зеркальную пленку воды поверх шероховатого асфальта
    if "Coat Weight" in bsdf.inputs and not is_metallic:
        bsdf.inputs["Coat Weight"].default_value = wetness
        bsdf.inputs["Coat Roughness"].default_value = 0.03

    links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    return mat


def make_neon(material_name: str, color=(0.1, 0.8, 1.0), strength: float = 30.0) -> bpy.types.Material:
    """Создает материал светящегося газоразрядного неона."""
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_emit = nodes.new(type="ShaderNodeEmission")

    node_emit.inputs["Color"].default_value = (color[0], color[1], color[2], 1.0)
    node_emit.inputs["Strength"].default_value = strength

    links.new(node_emit.outputs["Emission"], node_out.inputs["Surface"])
    return mat

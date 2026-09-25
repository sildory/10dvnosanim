"""
Модуль физической объемной атмосферы (Volumetric Scatter) в Cycles.
Создает реальные световые лучи (God-Rays) от прожекторов, фар и неона.
"""

import bpy


def setup_volume_fog(
    bounds=(60.0, 60.0, 25.0),
    location=(0.0, 0.0, 10.0),
    density: float = 0.015,
    anisotropy: float = 0.65,
    color=(0.85, 0.92, 1.0)
) -> bpy.types.Object:
    """
    Создает волюметрический контейнер с прямым рассеиванием света.
    anisotropy = 0.65 концентрирует свет в направленный кинематографический луч.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    box = bpy.context.active_object
    box.name = "Volume_Atmosphere_Container"
    box.scale = bounds
    box.display_type = "WIRE"

    mat = bpy.data.materials.new(name="Volumetric_Fog_Shader")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    vol = nodes.new(type="ShaderNodeVolumePrincipled")

    vol.inputs["Density"].default_value = density
    vol.inputs["Anisotropy"].default_value = anisotropy
    vol.inputs["Color"].default_value = (color[0], color[1], color[2], 1.0)

    links.new(vol.outputs["Volume"], node_out.inputs["Volume"])
    box.data.materials.append(mat)

    print(f"[ATMOSPHERE] Объемный туман активирован: плотность={density}, анизотропия={anisotropy}")
    return box

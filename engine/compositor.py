"""Модуль кинематографического композера: Glare (Fog Glow + Streaks), Chromatic Aberration, Color Grading."""

import bpy


def setup_cinematic_compositor(scene: bpy.types.Scene):
    """Строит кинематографическое дерево нод композитора Blender."""
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    # 1. Входной проход рендера
    node_render = nodes.new(type="CompositorNodeRLayers")
    node_render.location = (-600, 200)

    # 2. Мягкое неоновое свечение (Fog Glow)
    glare_fog = nodes.new(type="CompositorNodeGlare")
    glare_fog.glare_type = "FOG_GLOW"
    glare_fog.quality = "HIGH"
    glare_fog.threshold = 1.2
    glare_fog.size = 8
    glare_fog.location = (-300, 200)
    links.new(node_render.outputs["Image"], glare_fog.inputs["Image"])

    # 3. Анаморфные горизонтальные полосы от фар/неона (Streaks)
    glare_streaks = nodes.new(type="CompositorNodeGlare")
    glare_streaks.glare_type = "STREAKS"
    glare_streaks.streaks = 2
    glare_streaks.angle_offset = 0.0  # Строго горизонтальные лучи
    glare_streaks.threshold = 2.5
    glare_streaks.fade = 0.95
    glare_streaks.location = (0, 200)
    links.new(glare_fog.outputs["Image"], glare_streaks.inputs["Image"])

    # 4. Оптическая дисперсия (Хроматическая аберрация по краям линзы)
    lens_dist = nodes.new(type="CompositorNodeLensdist")
    lens_dist.use_projector = False
    lens_dist.inputs["Distort"].default_value = -0.008  # Легкая бочкообразность линзы 35mm
    lens_dist.inputs["Dispersion"].default_value = 0.012  # Физическое расхождение спектра
    lens_dist.location = (300, 200)
    links.new(glare_streaks.outputs["Image"], lens_dist.inputs["Image"])

    # 5. Нуарный цветовой грейдинг (Color Balance: Lift / Gamma / Gain)
    color_balance = nodes.new(type="CompositorNodeColorBalance")
    color_balance.correction_method = "LIFT_GAMMA_GAIN"
    # Тени (Lift): холодная синева нуара
    color_balance.lift = (0.92, 0.96, 1.04)
    # Полутона (Gamma): чистый контраст
    color_balance.gamma = (0.98, 1.0, 1.02)
    # Блики (Gain): теплый отблеск
    color_balance.gain = (1.04, 1.01, 0.97)
    color_balance.location = (600, 200)
    links.new(lens_dist.outputs["Image"], color_balance.inputs["Image"])

    # 6. Финальный выходной композит
    node_composite = nodes.new(type="CompositorNodeComposite")
    node_composite.location = (900, 200)
    links.new(color_balance.outputs["Image"], node_composite.inputs["Image"])

    print("[COMPOSITOR] Кинематографический тракт постобработки успешно собран.")

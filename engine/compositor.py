"""
Модуль кинематографического композера: 
Glare (Fog Glow + Streaks), Chromatic Aberration, Color Grading.
Полная совместимость с версиями Blender 4.x+.
"""

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

    # 2. Мягкое неоновое свечение (Fog Glow) - MEDIUM работает в 5 раз быстрее HIGH на CPU без потери мягкости
    glare_fog = nodes.new(type="CompositorNodeGlare")
    glare_fog.glare_type = "FOG_GLOW"
    glare_fog.quality = "MEDIUM"
    glare_fog.threshold = 1.2
    glare_fog.size = 8
    glare_fog.location = (-300, 200)
    links.new(node_render.outputs["Image"], glare_fog.inputs["Image"])

    # 3. Анаморфные горизонтальные полосы от бликов (Streaks)
    glare_streaks = nodes.new(type="CompositorNodeGlare")
    glare_streaks.glare_type = "STREAKS"
    glare_streaks.quality = "MEDIUM"
    glare_streaks.streaks = 2
    glare_streaks.angle_offset = 0.0  # Строго горизонтальные лучи
    glare_streaks.threshold = 2.5
    glare_streaks.fade = 0.95
    glare_streaks.location = (0, 200)
    links.new(glare_fog.outputs["Image"], glare_streaks.inputs["Image"])

    # 4. Оптическая дисперсия и хроматическая аберрация (Lens Distortion)
    lens_dist = nodes.new(type="CompositorNodeLensdist")
    if hasattr(lens_dist, "use_projector"):
        lens_dist.use_projector = False

    dist_sock = lens_dist.inputs.get("Distortion") or lens_dist.inputs.get("Distort")
    if dist_sock:
        dist_sock.default_value = -0.008  # Легкая бочкообразность линзы 35mm

    disp_sock = lens_dist.inputs.get("Dispersion")
    if disp_sock:
        disp_sock.default_value = 0.012  # Физическое расхождение спектра по краям

    lens_dist.location = (300, 200)
    links.new(glare_streaks.outputs["Image"], lens_dist.inputs["Image"])

    # 5. Кинематографический цветовой грейдинг (Color Balance: Lift / Gamma / Gain)
    color_balance = nodes.new(type="CompositorNodeColorBalance")
    if hasattr(color_balance, "correction_method"):
        color_balance.correction_method = "LIFT_GAMMA_GAIN"
    if hasattr(color_balance, "lift"):
        color_balance.lift = (0.92, 0.96, 1.04)  # Тени: холодная синева
    if hasattr(color_balance, "gamma"):
        color_balance.gamma = (0.98, 1.0, 1.02)  # Полутона: контраст
    if hasattr(color_balance, "gain"):
        color_balance.gain = (1.04, 1.01, 0.97)  # Блики: теплый свет

    color_balance.location = (600, 200)
    links.new(lens_dist.outputs["Image"], color_balance.inputs["Image"])

    # 6. Финальный выходной композит
    node_composite = nodes.new(type="CompositorNodeComposite")
    node_composite.location = (900, 200)
    links.new(color_balance.outputs["Image"], node_composite.inputs["Image"])

    print("[COMPOSITOR] Кинематографический тракт постобработки успешно собран.")

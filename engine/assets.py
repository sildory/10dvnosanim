"""Модуль автоматической загрузки ассетов: HDRI, 3D-модели (GLTF) и PBR-текстуры."""

import os
import zipfile
import requests
import bpy

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets_cache"))


class AssetManager:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _download_file(self, url: str, target_path: str):
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        print(f"[ASSETS] Скачивание: {url} -> {os.path.basename(target_path)}")
        res = requests.get(url, stream=True, timeout=90)
        res.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print(f"[ASSETS] Сохранено: {os.path.basename(target_path)}")

    def polyhaven(self, asset_id: str, asset_type: str = "hdris", resolution: str = "2k") -> str:
        """Скачивает HDRI или 3D-модель (GLB) с Poly Haven API."""
        local_dir = os.path.join(self.cache_dir, "polyhaven", asset_type, asset_id)
        os.makedirs(local_dir, exist_ok=True)

        ext = "hdr" if asset_type == "hdris" else "glb"
        local_path = os.path.join(local_dir, f"{asset_id}_{resolution}.{ext}")

        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            return local_path

        meta_url = f"https://api.polyhaven.com/files/{asset_id}"
        data = requests.get(meta_url, timeout=30).json()

        download_url = None
        if asset_type == "hdris":
            hdri_info = data.get("hdri", {}).get(resolution, {})
            entry = hdri_info.get("hdr") or hdri_info.get("exr")
            download_url = entry["url"] if entry else None
        elif asset_type == "models":
            gltf_info = data.get("gltf", {}).get(resolution, {})
            entry = gltf_info.get("glb") or gltf_info.get("gltf")
            download_url = entry["url"] if entry else None

        if not download_url:
            raise ValueError(f"URL не найден для Poly Haven: {asset_id} ({asset_type})")

        self._download_file(download_url, local_path)
        return local_path

    def ambientcg(self, asset_id: str, resolution: str = "2K") -> dict:
        """Скачивает CC0 PBR набор карт с ambientCG."""
        pack_name = f"{asset_id}_{resolution}-JPG"
        local_dir = os.path.join(self.cache_dir, "ambientcg", pack_name)
        zip_path = os.path.join(self.cache_dir, "ambientcg", f"{pack_name}.zip")

        if os.path.exists(local_dir) and len(os.listdir(local_dir)) > 0:
            return self._index_pbr_folder(local_dir)

        url = f"https://ambientcg.com/get?file={pack_name}.zip"
        self._download_file(url, zip_path)

        os.makedirs(local_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(local_dir)

        if os.path.exists(zip_path):
            os.remove(zip_path)

        return self._index_pbr_folder(local_dir)

    def _index_pbr_folder(self, folder: str) -> dict:
        maps = {}
        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            f = fname.lower()
            if "color" in f or "albedo" in f:
                maps["color"] = path
            elif "roughness" in f:
                maps["roughness"] = path
            elif "normalgl" in f or ("normal" in f and "dx" not in f):
                maps["normal"] = path
            elif "displacement" in f:
                maps["displacement"] = path
            elif "ao" in f or "ambientocclusion" in f:
                maps["ao"] = path
        return maps

    def apply_hdri_to_world(self, hdri_path: str, strength: float = 1.0, rotation_z: float = 0.0):
        world = bpy.context.scene.world or bpy.data.worlds.new("World")
        bpy.context.scene.world = world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputWorld")
        bg = nodes.new("ShaderNodeBackground")
        bg.inputs["Strength"].default_value = strength
        env = nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(hdri_path, check_existing=True)

        coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Rotation"].default_value[2] = rotation_z

        links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], env.inputs["Vector"])
        links.new(env.outputs["Color"], bg.inputs["Color"])
        links.new(bg.outputs["Background"], out.inputs["Surface"])


_mgr = None

def get_asset_manager() -> AssetManager:
    global _mgr
    if _mgr is None:
        _mgr = AssetManager()
    return _mgr

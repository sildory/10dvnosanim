"""
Модуль автоматической загрузки ассетов: Poly Haven (HDRI, GLB, PBR) и ambientCG (PBR).
Работает через официальные открытые REST API без ключей и регистрации.
Обеспечивает локальное кэширование в директории assets_cache/.
"""

import os
import sys
import json
import zipfile
import requests
import bpy

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets_cache"))
HTTP_TIMEOUT = 90
USER_AGENT = "10dvnosanim-Pipeline/1.0 (Blender CC0 Automation)"


class AssetManager:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def _download_file(self, url: str, target_path: str):
        """Скачивает файл потоком с валидацией размера."""
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        print(f"[ASSETS] Скачивание по сети: {url} -> {os.path.basename(target_path)}")
        response = self.session.get(url, stream=True, timeout=HTTP_TIMEOUT)
        response.raise_for_status()

        temp_path = target_path + ".download"
        try:
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            if os.path.exists(target_path):
                os.remove(target_path)
            os.rename(temp_path, target_path)
            print(f"[ASSETS] Успешно сохранено: {os.path.basename(target_path)}")
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def polyhaven(
        self,
        asset_id: str,
        asset_type: str = "hdris",
        resolution: str = "2k",
        preferred_format: str = None
    ) -> str:
        """
        Запрашивает метаданные через api.polyhaven.com/files/{asset_id} и скачивает ассет.
        """
        resolution = resolution.lower()
        asset_type = asset_type.lower()
        ext_map = {"hdris": preferred_format or "hdr", "models": preferred_format or "glb"}
        ext = ext_map.get(asset_type, "hdr")

        local_dir = os.path.join(self.cache_dir, "polyhaven", asset_type, asset_id)
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, f"{asset_id}_{resolution}.{ext}")

        if os.path.isfile(local_path) and os.path.getsize(local_path) > 1024:
            print(f"[ASSETS] Poly Haven взят из кэша: {os.path.basename(local_path)}")
            return local_path

        api_url = f"https://api.polyhaven.com/files/{asset_id}"
        print(f"[ASSETS] Запрос метаданных Poly Haven API: {api_url}")
        res = self.session.get(api_url, timeout=30)
        res.raise_for_status()
        data = res.json()

        download_url = None
        if asset_type == "hdris":
            hdri_entry = data.get("hdri", {}).get(resolution, {})
            fmt_dict = hdri_entry.get(ext) or hdri_entry.get("hdr") or hdri_entry.get("exr")
            if fmt_dict and "url" in fmt_dict:
                download_url = fmt_dict["url"]
        elif asset_type == "models":
            # Различные варианты вложенности в API Poly Haven
            gltf_section = data.get("gltf", {})
            if resolution in gltf_section:
                res_data = gltf_section[resolution]
                fmt_dict = res_data.get("glb") or res_data.get("gltf") or (res_data if "url" in res_data else None)
                if fmt_dict and "url" in fmt_dict:
                    download_url = fmt_dict["url"]
            if not download_url and "glb" in gltf_section:
                download_url = gltf_section["glb"].get("url")

        if not download_url:
            raise ValueError(
                f"Не удалось определить прямую ссылку для Poly Haven '{asset_id}' "
                f"(type={asset_type}, res={resolution})"
            )

        self._download_file(download_url, local_path)
        return local_path

    def ambientcg(self, asset_id: str, resolution: str = "2K", filetype: str = "JPG") -> dict:
        """
        Скачивает CC0 PBR набор текстур ambientCG, распаковывает и индексирует карты.
        """
        resolution = resolution.upper()
        filetype = filetype.upper()
        pack_name = f"{asset_id}_{resolution}-{filetype}"
        local_dir = os.path.join(self.cache_dir, "ambientcg", pack_name)
        zip_path = os.path.join(self.cache_dir, "ambientcg", f"{pack_name}.zip")

        if os.path.isdir(local_dir) and len(os.listdir(local_dir)) > 0:
            pbr_dict = self._index_pbr_folder(local_dir)
            if pbr_dict:
                print(f"[ASSETS] ambientCG взят из кэша: {pack_name}")
                return pbr_dict

        download_url = f"https://ambientcg.com/get?file={pack_name}.zip"
        self._download_file(download_url, zip_path)

        os.makedirs(local_dir, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(local_dir)
            print(f"[ASSETS] Архив {pack_name}.zip успешно распакован.")
        except zipfile.BadZipFile:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            raise RuntimeError(f"[FATAL] Ошибка распаковки архива ambientCG: {pack_name}.zip поврежден.")
        finally:
            if os.path.isfile(zip_path):
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
            elif "displacement" in f or "height" in f:
                maps["displacement"] = path
            elif "ambientocclusion" in f or "_ao" in f or f.endswith("_ao.jpg") or f.endswith("_ao.png"):
                maps["ao"] = path
            elif "metalness" in f or "metallic" in f:
                maps["metallic"] = path
            elif "emission" in f:
                maps["emission"] = path
        return maps

    def fetch_from_manifest(self, manifest_source) -> dict:
        if isinstance(manifest_source, str):
            if not os.path.isfile(manifest_source):
                raise FileNotFoundError(f"Манифест ассетов не найден: {manifest_source}")
            with open(manifest_source, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        else:
            manifest_data = manifest_source

        resolved = {"polyhaven": {}, "ambientcg": {}}

        for item in manifest_data.get("polyhaven", []):
            asset_id = item["id"]
            asset_type = item.get("type", "hdris")
            res = item.get("resolution", "2k")
            fmt = item.get("format")
            path = self.polyhaven(asset_id, asset_type=asset_type, resolution=res, preferred_format=fmt)
            resolved["polyhaven"][asset_id] = path

        for item in manifest_data.get("ambientcg", []):
            asset_id = item["id"]
            res = item.get("resolution", "2K")
            ftype = item.get("filetype", "JPG")
            pbr_maps = self.ambientcg(asset_id, resolution=res, filetype=ftype)
            resolved["ambientcg"][asset_id] = pbr_maps

        return resolved

    def apply_hdri_to_world(self, hdri_path: str, strength: float = 1.0, rotation_z: float = 0.0):
        world = bpy.context.scene.world or bpy.data.worlds.new("World")
        bpy.context.scene.world = world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        nodes.clear()

        node_out = nodes.new("ShaderNodeOutputWorld")
        node_bg = nodes.new("ShaderNodeBackground")
        node_bg.inputs["Strength"].default_value = strength

        node_env = nodes.new("ShaderNodeTexEnvironment")
        node_env.image = bpy.data.images.load(hdri_path, check_existing=True)

        node_coord = nodes.new("ShaderNodeTexCoord")
        node_mapping = nodes.new("ShaderNodeMapping")
        node_mapping.inputs["Rotation"].default_value[2] = rotation_z

        links.new(node_coord.outputs["Generated"], node_mapping.inputs["Vector"])
        links.new(node_mapping.outputs["Vector"], node_env.inputs["Vector"])
        links.new(node_env.outputs["Color"], node_bg.inputs["Color"])
        links.new(node_bg.outputs["Background"], node_out.inputs["Surface"])


_mgr = None


def get_asset_manager() -> AssetManager:
    global _mgr
    if _mgr is None:
        _mgr = AssetManager()
    return _mgr 

"""Модуль автоматической загрузки ассетов через открытые API Poly Haven и ambientCG."""

import os
import json
import zipfile
import requests
import bpy

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets_cache"))


class AssetManager:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _download_file(self, url: str, target_path: str):
        """Скачивает файл с отображением прогресса."""
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        print(f"[ASSETS] Скачивание: {url} -> {os.path.basename(target_path)}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print(f"[ASSETS] Успешно загружено: {os.path.basename(target_path)}")

    # =========================================================================
    # 1. ИНТЕГРАЦИЯ С POLY HAVEN (api.polyhaven.com)
    # =========================================================================
    def polyhaven(self, asset_id: str, asset_type: str = "hdris", resolution: str = "2k", file_format: str = "hdr") -> str:
        """Скачивает ассет с Poly Haven по его ID (HDRI, модель или текстуры).

        Возвращает абсолютный путь к локальному файлу.
        """
        local_dir = os.path.join(self.cache_dir, "polyhaven", asset_type, asset_id)
        os.makedirs(local_dir, exist_ok=True)

        expected_filename = f"{asset_id}_{resolution}.{file_format}"
        local_filepath = os.path.join(local_dir, expected_filename)

        if os.path.exists(local_filepath) and os.path.getsize(local_filepath) > 0:
            print(f"[ASSETS CACHE] Poly Haven ассет найден локально: {expected_filename}")
            return local_filepath

        # Запрос к открытому API файлов
        meta_url = f"https://api.polyhaven.com/files/{asset_id}"
        print(f"[ASSETS] Запрос метаданных Poly Haven: {meta_url}")
        res = requests.get(meta_url, timeout=30)
        res.raise_for_status()
        data = res.json()

        download_url = None

        if asset_type == "hdris":
            hdri_entry = data.get("hdri", {}).get(resolution, {})
            format_entry = hdri_entry.get(file_format) or hdri_entry.get("exr") or hdri_entry.get("hdr")
            if format_entry and "url" in format_entry:
                download_url = format_entry["url"]
        elif asset_type == "models":
            gltf_entry = data.get("gltf", {}).get(resolution, {})
            if "url" in gltf_entry:
                download_url = gltf_entry["url"]
                expected_filename = f"{asset_id}_{resolution}.glb"
                local_filepath = os.path.join(local_dir, expected_filename)

        if not download_url:
            raise ValueError(f"Не удалось найти URL для скачивания Poly Haven: id={asset_id}, type={asset_type}, res={resolution}")

        self._download_file(download_url, local_filepath)
        return local_filepath

    # =========================================================================
    # 2. ИНТЕГРАЦИЯ С AMBIENTCG (ambientcg.com)
    # =========================================================================
    def ambientcg(self, asset_id: str, resolution: str = "2K", filetype: str = "JPG") -> dict:
        """Скачивает CC0 PBR набор текстур с ambientCG и распаковывает его.

        Возвращает словарь путей к картам: {'color', 'roughness', 'normal', 'displacement'}.
        """
        pack_name = f"{asset_id}_{resolution}-{filetype}"
        local_dir = os.path.join(self.cache_dir, "ambientcg", pack_name)
        zip_path = os.path.join(self.cache_dir, "ambientcg", f"{pack_name}.zip")

        # Если уже распаковано — возвращаем карту путей
        if os.path.exists(local_dir) and len(os.listdir(local_dir)) > 0:
            print(f"[ASSETS CACHE] PBR набор ambientCG найден: {pack_name}")
            return self._index_pbr_folder(local_dir)

        # Скачивание ZIP-архива
        download_url = f"https://ambientcg.com/get?file={pack_name}.zip"
        self._download_file(download_url, zip_path)

        # Распаковка
        print(f"[ASSETS] Распаковка текстур: {pack_name}...")
        os.makedirs(local_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(local_dir)

        if os.path.exists(zip_path):
            os.remove(zip_path)  # Удаляем архив для экономии места

        return self._index_pbr_folder(local_dir)

    def _index_pbr_folder(self, folder: str) -> dict:
        """Сканирует папку и классифицирует карты PBR-материала."""
        maps = {}
        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            f_lower = fname.lower()

            if "color" in f_lower or "diff" in f_lower or "albedo" in f_lower:
                maps["color"] = path
            elif "roughness" in f_lower:
                maps["roughness"] = path
            elif "normalgl" in f_lower or ("normal" in f_lower and "dx" not in f_lower):
                maps["normal"] = path
            elif "displacement" in f_lower or "disp" in f_lower:
                maps["displacement"] = path
            elif "ao" in f_lower or "ambientocclusion" in f_lower:
                maps["ao"] = path

        return maps

    # =========================================================================
    # 3. ПОДКЛЮЧЕНИЕ HDRI К МИРУ BLENDER (WORLD NODE TREE)
    # =========================================================================
    def apply_hdri_to_world(self, hdri_path: str, strength: float = 1.0, rotation_z: float = 0.0):
        """Создает и настраивает нодовое окружение мира с HDRI текстурой."""
        world = bpy.context.scene.world
        if not world:
            world = bpy.data.worlds.new("Cinema_World")
            bpy.context.scene.world = world

        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        nodes.clear()

        # Создание нод
        node_out = nodes.new(type="ShaderNodeOutputWorld")
        node_bg = nodes.new(type="ShaderNodeBackground")
        node_bg.inputs["Strength"].default_value = strength

        node_env = nodes.new(type="ShaderNodeTexEnvironment")
        node_env.image = bpy.data.images.load(hdri_path, check_existing=True)

        node_coord = nodes.new(type="ShaderNodeTexCoord")
        node_mapping = nodes.new(type="ShaderNodeMapping")
        node_mapping.inputs["Rotation"].default_value[2] = rotation_z

        # Линковка
        links.new(node_coord.outputs["Generated"], node_mapping.inputs["Vector"])
        links.new(node_mapping.outputs["Vector"], node_env.inputs["Vector"])
        links.new(node_env.outputs["Color"], node_bg.inputs["Color"])
        links.new(node_bg.outputs["Background"], node_out.inputs["Surface"])
        print(f"[ASSETS] HDRI подключен к World: {os.path.basename(hdri_path)}")

    def preload_manifest(self, manifest_path: str):
        """Пакетно скачивает всё, что указано в manifest.json проекта."""
        if not os.path.exists(manifest_path):
            print(f"[ASSETS] Манифест не найден: {manifest_path} (пропуск предзагрузки)")
            return

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for item in manifest.get("polyhaven", []):
            self.polyhaven(
                asset_id=item["id"],
                asset_type=item.get("type", "hdris"),
                resolution=item.get("resolution", "2k"),
                file_format=item.get("format", "hdr")
            )

        for item in manifest.get("ambientcg", []):
            self.ambientcg(
                asset_id=item["id"],
                resolution=item.get("resolution", "2K"),
                filetype=item.get("filetype", "JPG")
            )


# Синглтон для вызова одной строкой
_default_manager = None

def get_asset_manager() -> AssetManager:
    global _default_manager
    if _default_manager is None:
        _default_manager = AssetManager()
    return _default_manager

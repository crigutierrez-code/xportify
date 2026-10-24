#!/usr/bin/env python3
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "xportify"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"


def cargar_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def guardar_config(cfg: dict):
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def ultimo_directorio():
    cfg = cargar_config()
    d = cfg.get("ultima_carpeta")
    if d and Path(d).exists():
        return d
    return str(Path.home() / "Music" / "Xportify")


def guardar_directorio(d: str):
    cfg = cargar_config()
    cfg["ultima_carpeta"] = d
    guardar_config(cfg)


def calidad_defecto():
    cfg = cargar_config()
    return cfg.get("calidad", 192)


def guardar_calidad(q: int):
    cfg = cargar_config()
    cfg["calidad"] = q
    guardar_config(cfg)


def proveedor_defecto():
    cfg = cargar_config()
    return cfg.get("proveedor", "auto")


def guardar_proveedor(p: str):
    cfg = cargar_config()
    cfg["proveedor"] = p
    guardar_config(cfg)

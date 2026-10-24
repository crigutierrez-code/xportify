#!/usr/bin/env python3
import json
import re
from typing import Dict, List

import httpx

SPOTIFY_RE = re.compile(r"open\.spotify\.com/(?:intl-[a-z-]+/)?(playlist|album|track|artist)/([A-Za-z0-9]+)")
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def es_url_spotify(url: str) -> bool:
    return bool(SPOTIFY_RE.search(url))


def _embed_tracks(tipo: str, spotify_id: str) -> List[Dict[str, str]]:
    url = f"https://open.spotify.com/embed/{tipo}/{spotify_id}"
    r = httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
    r.raise_for_status()
    m = NEXT_DATA_RE.search(r.text)
    if not m:
        raise RuntimeError("Spotify no devolvió la lista esperada. Prueba a exportar con Exportify.")
    data = json.loads(m.group(1))
    entity = (data.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity") or {})
    tracks = entity.get("trackList") or []
    canciones = []
    for t in tracks:
        titulo = (t.get("title") or "").strip()
        if not titulo:
            continue
        artista = (t.get("subtitle") or "").strip()
        canciones.append({"titulo": titulo, "artista": artista, "album": ""})
    if not canciones and entity.get("type") == "track":
        titulo = (entity.get("title") or "").strip()
        if titulo:
            canciones.append({"titulo": titulo, "artista": (entity.get("subtitle") or "").strip(), "album": ""})
    return canciones


def canciones_desde_spotify(url: str) -> List[Dict[str, str]]:
    m = SPOTIFY_RE.search(url)
    if not m:
        raise ValueError("URL de Spotify no reconocida")
    tipo, spotify_id = m.group(1), m.group(2)
    if tipo == "artist":
        raise ValueError("Las URLs de artista no están soportadas todavía. Usa una playlist o álbum.")
    canciones = _embed_tracks(tipo, spotify_id)
    if not canciones:
        raise RuntimeError(
            "No se pudieron leer las canciones de ese enlace.\n"
            "Si es tu lista de 'Me gusta', expórtala con Exportify y carga el CSV."
        )
    return canciones

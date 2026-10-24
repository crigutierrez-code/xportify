#!/usr/bin/env python3
import json
import re
from typing import Dict, List

import httpx

SPOTIFY_RE = re.compile(r"open\.spotify\.com/(?:intl-[a-z-]+/)?(playlist|album|track|artist)/([A-Za-z0-9]+)")
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
EMBED_RE = re.compile(r'<script[^>]+src=["\']([^"\']*embed[^"\']*)["\']', re.S)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def es_url_spotify(url: str) -> bool:
    return bool(SPOTIFY_RE.search(url))


def _extraer_tracks_desde_entity(entity: dict) -> List[Dict[str, str]]:
    tracks = entity.get("trackList") or entity.get("tracks") or []
    canciones = []
    for t in tracks:
        if not isinstance(t, dict):
            continue
        titulo = (t.get("title") or t.get("name") or "").strip()
        if not titulo:
            continue
        artista = (
            t.get("subtitle")
            or t.get("artistName")
            or ", ".join([a.get("name", "") for a in t.get("artists", []) if isinstance(a, dict)])
            or ""
        ).strip()
        album = (t.get("albumName") or t.get("album") or "").strip()
        canciones.append({"titulo": titulo, "artista": artista, "album": album})
    if not canciones and entity.get("type") in ("track", "song"):
        titulo = (entity.get("title") or entity.get("name") or "").strip()
        if titulo:
            artista = (entity.get("subtitle") or "").strip()
            canciones.append({"titulo": titulo, "artista": artista, "album": ""})
    return canciones


def _embed_tracks(tipo: str, spotify_id: str) -> List[Dict[str, str]]:
    url = f"https://open.spotify.com/embed/{tipo}/{spotify_id}"
    r = httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
    r.raise_for_status()
    m = NEXT_DATA_RE.search(r.text)
    if m:
        try:
            data = json.loads(m.group(1))
            state = data.get("props", {}).get("pageProps", {}).get("state") or {}
            entity = (state.get("data", {}).get("entity") or state.get("entity") or {})
            canciones = _extraer_tracks_desde_entity(entity)
            if canciones:
                return canciones
        except Exception:
            pass
    try:
        data = json.loads(r.text)
        for k in ["props", "pageProps", "state", "data"]:
            if isinstance(data, dict) and k in data:
                data = data[k]
        if isinstance(data, dict):
            entity = data.get("entity") or {}
            canciones = _extraer_tracks_desde_entity(entity)
            if canciones:
                return canciones
    except Exception:
        pass
    raise RuntimeError("No se pudieron leer las canciones desde el enlace público.")


def canciones_desde_spotify(url: str) -> List[Dict[str, str]]:
    m = SPOTIFY_RE.search(url)
    if not m:
        raise ValueError("URL de Spotify no reconocida")
    tipo, spotify_id = m.group(1), m.group(2)
    if tipo == "artist":
        raise ValueError("Las URLs de artista no están soportadas. Usa una playlist, álbum o pista.")
    canciones = _embed_tracks(tipo, spotify_id)
    if not canciones:
        raise RuntimeError(
            "No se pudieron leer las canciones de ese enlace.\n\n"
            "Si es tu lista privada de 'Me gusta' (Liked Songs), expórtala con Exportify "
            "desde la pestaña 'Archivo / Texto'."
        )
    return canciones

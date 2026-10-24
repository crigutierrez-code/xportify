#!/usr/bin/env python3
from typing import Dict, List

import yt_dlp

from .spotify import es_url_spotify, canciones_desde_spotify


def _canciones_desde_ytdlp(url: str) -> List[Dict[str, str]]:
    opciones = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "noplaylist": False,
    }
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)

    canciones = []

    def add(entry):
        if not entry:
            return
        titulo = (entry.get("track") or entry.get("title") or "").strip()
        artista = (entry.get("artist") or entry.get("creator") or entry.get("uploader") or "").strip()
        album = (entry.get("album") or "").strip()
        if titulo:
            canciones.append({"titulo": titulo, "artista": artista, "album": album})

    if info.get("_type") == "playlist" or "entries" in info:
        for entry in (info.get("entries") or []):
            add(entry)
    else:
        add(info)
    return canciones


def canciones_desde_url(url: str) -> List[Dict[str, str]]:
    url = url.strip()
    if not url:
        raise ValueError("URL vacía")
    if es_url_spotify(url):
        return canciones_desde_spotify(url)
    canciones = _canciones_desde_ytdlp(url)
    if not canciones:
        raise RuntimeError(
            "No se pudieron extraer canciones de esa URL.\n"
            "Soportamos playlists de YouTube / YouTube Music, SoundCloud, Bandcamp y Spotify (playlist/álbum)."
        )
    return canciones

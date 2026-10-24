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
        "ignoreerrors": True,
    }
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)

    canciones: List[Dict[str, str]] = []

    def add(entry):
        if not entry:
            return
        titulo = (entry.get("track") or entry.get("title") or entry.get("fulltitle") or "").strip()
        if not titulo:
            return
        artista = (
            entry.get("artist")
            or entry.get("creator")
            or entry.get("uploader")
            or entry.get("channel")
            or ""
        ).strip()
        album = (entry.get("album") or "").strip()
        if " - " in titulo and not artista:
            try:
                a, t = titulo.split(" - ", 1)
                if len(a) < 60 and len(t) > 2:
                    artista, titulo = a.strip(), t.strip()
            except Exception:
                pass
        canciones.append({"titulo": titulo, "artista": artista, "album": album})

    if not info:
        return canciones
    if info.get("_type") == "playlist" or "entries" in info:
        for entry in info.get("entries") or []:
            add(entry)
    else:
        add(info)
    return canciones


def canciones_desde_url(url: str) -> List[Dict[str, str]]:
    url = (url or "").strip()
    if not url:
        raise ValueError("URL vacía")
    if not url.startswith(("http://", "https://")):
        raise ValueError("Introduce una URL válida (http/https)")
    if es_url_spotify(url):
        return canciones_desde_spotify(url)
    canciones = _canciones_desde_ytdlp(url)
    if not canciones:
        raise RuntimeError(
            "No se pudieron extraer canciones de ese enlace.\n\n"
            "Soportados: playlists/álbumes de Spotify (públicos), YouTube, YouTube Music, SoundCloud, Bandcamp.\n"
            "Si es tu lista 'Me gusta' de Spotify, usa Exportify para descargar el CSV."
        )
    return canciones

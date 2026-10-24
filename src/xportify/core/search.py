#!/usr/bin/env python3
from typing import Optional

import yt_dlp
from ytmusicapi import YTMusic


class Buscador:
    def __init__(self):
        try:
            self.ytmusic = YTMusic()
        except Exception:
            self.ytmusic = None

    def buscar_youtube_music(self, artista: str, titulo: str) -> Optional[str]:
        if not self.ytmusic:
            return None
        query = f"{artista} {titulo}".strip() if artista else titulo.strip()
        try:
            results = self.ytmusic.search(query, filter="songs")
            if not results:
                return None
            video_id = results[0].get("videoId")
            if not video_id:
                return None
            return f"https://music.youtube.com/watch?v={video_id}"
        except Exception:
            return None

    def buscar_youtube(self, artista: str, titulo: str) -> Optional[str]:
        consulta = f"ytsearch1:{artista} - {titulo} audio" if artista else f"ytsearch1:{titulo} audio"
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(consulta, download=False)
                if info and "entries" in info and info["entries"]:
                    entry = info["entries"][0]
                    return entry.get("webpage_url") or entry.get("url")
        except Exception:
            pass
        return None

    def obtener_url(self, artista: str, titulo: str, preferir: str = "auto") -> Optional[str]:
        if preferir in ("auto", "ytmusic"):
            url = self.buscar_youtube_music(artista, titulo)
            if url:
                return url
        if preferir in ("auto", "youtube"):
            url = self.buscar_youtube(artista, titulo)
            if url:
                return url
        return None

#!/usr/bin/env python3
from pathlib import Path
from typing import Callable, Optional

import yt_dlp
from yt_dlp.utils import sanitize_filename

from .search import Buscador


class Descargador:
    def __init__(self, carpeta_salida: str | Path, calidad: int = 192, preferir: str = "auto"):
        self.carpeta = Path(carpeta_salida).expanduser()
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.calidad = calidad
        self.preferir = preferir
        self.buscador = Buscador()

    def descargar(self, cancion: dict, callback: Optional[Callable[[str], None]] = None) -> str:
        titulo = cancion.get("titulo", "").strip()
        artista = cancion.get("artista", "").strip()
        album = cancion.get("album", "").strip()

        if not titulo:
            raise ValueError("Título vacío")

        base = sanitize_filename(f"{artista} - {titulo}" if artista else titulo)
        destino_mp3 = self.carpeta / f"{base}.mp3"

        if destino_mp3.exists():
            if callback:
                callback("omitida")
            return "omitida"

        url = self.buscador.obtener_url(artista, titulo, self.preferir)
        if not url:
            raise RuntimeError("No se encontró resultado en YouTube/YouTube Music")

        args_meta = ["-metadata", f"title={titulo}"]
        if artista:
            args_meta += ["-metadata", f"artist={artista}"]
        if album:
            args_meta += ["-metadata", f"album={album}"]

        opciones = {
            "format": "bestaudio/best",
            "outtmpl": str(self.carpeta / f"{base}.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": str(self.calidad),
                }
            ],
            "postprocessor_args": {"extractaudio": args_meta},
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        if callback:
            callback("ok")
        return "ok"

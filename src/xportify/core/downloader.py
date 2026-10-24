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
        self.calidad = int(calidad)
        if self.calidad not in (128, 192, 256, 320):
            self.calidad = 192
        self.preferir = preferir if preferir in ("auto", "ytmusic", "youtube") else "auto"
        self.buscador = Buscador()
        self._cancelado = False

    def cancelar(self):
        self._cancelado = True

    def descargar(self, cancion: dict, callback: Optional[Callable[[str], None]] = None) -> str:
        if self._cancelado:
            raise InterruptedError("Descarga cancelada")
        titulo = (cancion.get("titulo") or "").strip()
        artista = (cancion.get("artista") or "").strip()
        album = (cancion.get("album") or "").strip()

        if not titulo:
            raise ValueError("Título vacío")

        nombre_base = f"{artista} - {titulo}" if artista else titulo
        base = sanitize_filename(nombre_base)
        destino_mp3 = self.carpeta / f"{base}.mp3"

        if destino_mp3.exists():
            if callback:
                callback("omitida")
            return "omitida"

        if self._cancelado:
            raise InterruptedError("Descarga cancelada")

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
            "ignoreerrors": False,
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

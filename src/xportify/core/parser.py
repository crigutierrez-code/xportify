#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import List, Dict

import pandas as pd

COLS_TITULO = ["track name", "track", "name", "title", "song", "cancion", "canción", "nombre", "titulo", "título"]
COLS_ARTISTA = ["artist name(s)", "artist names", "artist name", "artist", "artists", "artista", "artistas"]
COLS_ALBUM = ["album name", "album", "álbum"]


def encontrar_columna(df, candidatas):
    mapa = {str(c).strip().lower(): c for c in df.columns}
    for nombre in candidatas:
        if nombre in mapa:
            return mapa[nombre]
    return None


def leer_canciones_desde_archivo(ruta: str | Path) -> List[Dict[str, str]]:
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    if ruta.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(ruta)
    elif ruta.suffix.lower() == ".json":
        df = pd.read_json(ruta)
    else:
        df = pd.read_csv(ruta, encoding="utf-8-sig")

    col_titulo = encontrar_columna(df, COLS_TITULO)
    col_artista = encontrar_columna(df, COLS_ARTISTA)
    col_album = encontrar_columna(df, COLS_ALBUM)

    if col_titulo is None:
        raise ValueError(f"No encontré la columna del título. Columnas disponibles: {list(df.columns)}")

    canciones = []
    for _, fila in df.iterrows():
        titulo = str(fila[col_titulo]).strip()
        if not titulo or titulo.lower() == "nan":
            continue

        artista = ""
        if col_artista is not None and pd.notna(fila[col_artista]):
            artista = str(fila[col_artista]).replace(";", ", ").strip()

        album = ""
        if col_album is not None and pd.notna(fila[col_album]):
            album = str(fila[col_album]).strip()

        canciones.append({"titulo": titulo, "artista": artista, "album": album})
    return canciones


def parsear_texto_manual(texto: str) -> List[Dict[str, str]]:
    canciones = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if " - " in linea:
            partes = linea.split(" - ", 1)
            artista = partes[0].strip()
            titulo = partes[1].strip()
        elif "-" in linea:
            partes = linea.split("-", 1)
            artista = partes[0].strip()
            titulo = partes[1].strip()
        else:
            artista = ""
            titulo = linea
        if titulo:
            canciones.append({"titulo": titulo, "artista": artista, "album": ""})
    return canciones

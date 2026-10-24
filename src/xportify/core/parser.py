#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd


COLS_TITULO = [
    "track name",
    "track",
    "name",
    "title",
    "song",
    "cancion",
    "canción",
    "nombre",
    "titulo",
    "título",
    "trackname",
]
COLS_ARTISTA = [
    "artist name(s)",
    "artist names",
    "artist name",
    "artist",
    "artists",
    "artista",
    "artistas",
    "artistname",
]
COLS_ALBUM = ["album name", "album", "álbum", "albumname", "disc"]


def encontrar_columna(df, candidatas):
    mapa = {str(c).strip().lower().replace("\n", " ").replace("\t", " "): c for c in df.columns}
    for nombre in candidatas:
        if nombre in mapa:
            return mapa[nombre]
    return None


def _leer_csv(path: Path):
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        if df.shape[1] == 1:
            try:
                df = pd.read_csv(path, encoding="utf-8-sig", sep=";")
            except Exception:
                pass
        return df
    except Exception:
        try:
            df = pd.read_csv(path, encoding="latin-1")
            if df.shape[1] == 1:
                try:
                    df = pd.read_csv(path, encoding="latin-1", sep=";")
                except Exception:
                    pass
            return df
        except Exception:
            df = pd.read_csv(path, encoding="utf-8-sig", sep=None, engine="python")
            return df


def leer_canciones_desde_archivo(ruta: str | Path) -> List[Dict[str, str]]:
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    ext = ruta.suffix.lower()
    if ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(ruta)
    elif ext == ".json":
        try:
            df = pd.read_json(ruta)
        except Exception:
            import json

            data = json.loads(ruta.read_text(encoding="utf-8"))
            df = pd.DataFrame(data)
    elif ext == ".tsv":
        df = pd.read_csv(ruta, encoding="utf-8-sig", sep="\t")
    else:
        df = _leer_csv(ruta)

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
            artista = str(fila[col_artista]).replace(";", ", ").replace("|", ", ").strip()

        album = ""
        if col_album is not None and pd.notna(fila[col_album]):
            album = str(fila[col_album]).strip()
            if album.lower() == "nan":
                album = ""

        canciones.append({"titulo": titulo, "artista": artista, "album": album})
    return canciones


def parsear_texto_manual(texto: str) -> List[Dict[str, str]]:
    canciones = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        linea = re.sub(r"^\d+[\.\)]\s+", "", linea)
        if " - " in linea:
            partes = linea.split(" - ", 1)
            artista = partes[0].strip()
            titulo = partes[1].strip()
        elif " – " in linea:
            partes = linea.split(" – ", 1)
            artista = partes[0].strip()
            titulo = partes[1].strip()
        elif " — " in linea:
            partes = linea.split(" — ", 1)
            artista = partes[0].strip()
            titulo = partes[1].strip()
        elif "\t" in linea and linea.count("\t") >= 1:
            partes = [p.strip() for p in linea.split("\t") if p.strip()]
            if len(partes) >= 2:
                artista, titulo = partes[0], partes[1]
            else:
                continue
        elif "-" in linea:
            partes = linea.split("-", 1)
            artista = partes[0].strip()
            titulo = partes[1].strip()
        else:
            artista = ""
            titulo = linea
        titulo = titulo.strip().strip('"').strip("'")
        artista = artista.strip().strip('"').strip("'")
        if titulo and titulo.lower() != "nan":
            canciones.append({"titulo": titulo, "artista": artista, "album": ""})
    return canciones


def exportar_lista(canciones: List[Dict[str, str]], ruta: str | Path):
    ruta = Path(ruta)
    if ruta.suffix.lower() == ".json":
        import json

        ruta.write_text(json.dumps(canciones, ensure_ascii=False, indent=2), encoding="utf-8")
        return ruta
    df = pd.DataFrame(canciones)
    if ruta.suffix.lower() in (".xlsx", ".xls"):
        df.to_excel(ruta, index=False)
    else:
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
    return ruta

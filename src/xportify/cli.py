#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from .core.downloader import Descargador
from .core.parser import leer_canciones_desde_archivo
from .core.sources import canciones_desde_url
from .utils.ffmpeg import aviso_ffmpeg, ffmpeg_disponible


def main():
    parser = argparse.ArgumentParser(description="Xportify CLI: de tu lista a MP3.")
    parser.add_argument("entrada", help="Archivo CSV/Excel/JSON o URL de playlist/álbum")
    parser.add_argument("-o", "--salida", default="musica", help="Carpeta de destino")
    parser.add_argument("--calidad", type=int, default=192, choices=[128, 192, 256, 320])
    parser.add_argument("--proveedor", default="auto", choices=["auto", "ytmusic", "youtube"])
    args = parser.parse_args()

    if not ffmpeg_disponible():
        sys.exit(aviso_ffmpeg())

    if args.entrada.startswith("http://") or args.entrada.startswith("https://"):
        canciones = canciones_desde_url(args.entrada)
    else:
        canciones = leer_canciones_desde_archivo(args.entrada)

    carpeta = Path(args.salida).expanduser()
    descargador = Descargador(carpeta, args.calidad, args.proveedor)
    total = len(canciones)
    print(f"{total} canciones. Guardando en {carpeta}")

    fallidas = []
    for i, c in enumerate(canciones, 1):
        etiqueta = f"{c['artista']} - {c['titulo']}" if c["artista"] else c["titulo"]
        print(f"[{i}/{total}] {etiqueta} ... ", end="", flush=True)
        try:
            estado = descargador.descargar(c)
            print("omitida" if estado == "omitida" else "listo")
        except KeyboardInterrupt:
            print("\nInterrumpido")
            break
        except Exception as e:
            print("ERROR")
            fallidas.append((etiqueta, str(e).splitlines()[0] if str(e) else "error"))

    if fallidas:
        log = carpeta / "fallidas.txt"
        log.write_text("\n".join(f"{n}  ->  {m}" for n, m in fallidas), encoding="utf-8")
        print(f"\n{len(fallidas)} fallidas. Lista en {log}")
    else:
        print("\nTodo descargado sin errores.")

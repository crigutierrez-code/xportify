#!/usr/bin/env python3
import shutil
from pathlib import Path


def ffmpeg_disponible() -> bool:
    return shutil.which("ffmpeg") is not None


def aviso_ffmpeg():
    if ffmpeg_disponible():
        return None
    return (
        "FFmpeg no está instalado.\n\n"
        "Xportify necesita ffmpeg para convertir a MP3.\n\n"
        "Instálalo:\n"
        "  - Arch/Manjaro: sudo pacman -S ffmpeg\n"
        "  - Ubuntu/Debian: sudo apt install ffmpeg\n"
        "  - Fedora: sudo dnf install ffmpeg\n"
        "  - macOS (brew): brew install ffmpeg\n"
        "  - Windows: https://www.gyan.dev/ffmpeg/builds/"
    )

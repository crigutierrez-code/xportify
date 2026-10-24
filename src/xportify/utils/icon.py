#!/usr/bin/env python3
import sys
from pathlib import Path

from PySide6.QtGui import QIcon

def icono_app() -> QIcon:
    base = Path(__file__).resolve().parents[3] / "assets"
    for nombre in ["xportify.png", "xportify-icon-1024.png", "icon.svg"]:
        ruta = base / nombre
        if ruta.exists():
            icono = QIcon(str(ruta))
            if not icono.isNull():
                return icono
    return QIcon()


def _icono_generado() -> QIcon:
    pix = QPixmap(256, 256)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    grad = QLinearGradient(0, 0, 256, 256)
    grad.setColorAt(0, QColor("#22d3ee"))
    grad.setColorAt(1, QColor("#34d399"))
    p.setBrush(QBrush(grad))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(QRectF(16, 16, 224, 224), 52, 52)
    p.setPen(QColor("#0f0f0f"))
    p.end()
    return QIcon(pix)

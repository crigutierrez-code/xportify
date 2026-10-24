#!/usr/bin/env python3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class ListaPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        cab = QHBoxLayout()
        self.lbl_total = QLabel("Sin canciones cargadas")
        self.lbl_total.setStyleSheet("color: #b9b9b9;")
        cab.addWidget(self.lbl_total)
        cab.addStretch()
        self.blimpiar = QPushButton("Limpiar lista")
        self.bexportar = QPushButton("Exportar lista (CSV/JSON)")
        self.bir = QPushButton("Ir a Descarga")
        self.bir.setObjectName("primary")
        cab.addWidget(self.blimpiar)
        cab.addWidget(self.bexportar)
        cab.addWidget(self.bir)
        layout.addLayout(cab)

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["#", "Artista", "Título", "Álbum", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        layout.addWidget(self.tabla)

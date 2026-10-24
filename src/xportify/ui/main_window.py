#!/usr/bin/env python3
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QTextEdit,
    QGroupBox,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QMessageBox,
    QHeaderView,
)

from ..core.parser import leer_canciones_desde_archivo, parsear_texto_manual, exportar_lista
from ..core.downloader import Descargador
from ..core.sources import canciones_desde_url
from ..utils.ffmpeg import aviso_ffmpeg, ffmpeg_disponible
from ..utils.icon import icono_app
from ..utils import config


class WorkerURL(QThread):
    ok = Signal(list)
    fallo = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            self.ok.emit(canciones_desde_url(self.url))
        except Exception as e:
            self.fallo.emit(str(e))


class WorkerDescarga(QThread):
    progreso = Signal(int, int)
    estado_cancion = Signal(int, str, str)
    terminado = Signal(list)

    def __init__(self, canciones, carpeta, calidad, preferir):
        super().__init__()
        self.canciones = canciones
        self.carpeta = carpeta
        self.calidad = calidad
        self.preferir = preferir
        self._stop = False

    def run(self):
        descargador = Descargador(self.carpeta, self.calidad, self.preferir)
        fallidas = []
        total = len(self.canciones)
        for i, cancion in enumerate(self.canciones):
            if self._stop:
                break
            etiqueta = f"{cancion.get('artista')} - {cancion.get('titulo')}" if cancion.get('artista') else cancion.get('titulo')
            self.estado_cancion.emit(i, "buscando", etiqueta)
            try:
                estado = descargador.descargar(cancion)
                if estado == "omitida":
                    self.estado_cancion.emit(i, "omitida", etiqueta)
                else:
                    self.estado_cancion.emit(i, "listo", etiqueta)
            except Exception as e:
                msg = str(e).splitlines()[0] if str(e) else "error desconocido"
                self.estado_cancion.emit(i, "error", etiqueta)
                fallidas.append((etiqueta, msg))
            self.progreso.emit(i + 1, total)
        self.terminado.emit(fallidas)

    def stop(self):
        self._stop = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xportify")
        self.setWindowIcon(icono_app())
        self.setMinimumSize(980, 720)
        self.canciones = []
        self.worker = None
        self.setAcceptDrops(True)

        self.setStyleSheet("""
            QMainWindow { background: #0f0f0f; }
            QWidget { color: #f5f5f5; font-size: 9pt; }
            QTabWidget::pane { border: 1px solid #2a2a2a; border-radius: 10px; background: #151515; }
            QTabBar::tab { background: transparent; padding: 8px 16px; margin-right: 4px; border-radius: 8px; }
            QTabBar::tab:selected { background: #1f1f1f; }
            QTabBar::tab:hover { background: #1a1a1a; }
            QGroupBox { border: 1px solid #2a2a2a; border-radius: 10px; margin-top: 12px; padding: 16px; background: #151515; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #b9b9b9; }
            QPushButton { background: #1f1f1f; border: 1px solid #2f2f2f; border-radius: 9px; padding: 8px 14px; }
            QPushButton:hover { background: #262626; }
            QPushButton:pressed { background: #1a1a1a; }
            QPushButton#primary { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #22d3ee, stop:1 #34d399); color: #0f0f0f; border: none; font-weight: 600; }
            QPushButton#primary:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #38e1f5, stop:1 #4df0ad); }
            QPushButton:disabled { color: #6b6b6b; }
            QLineEdit, QTextEdit, QComboBox, QSpinBox { background: #101010; border: 1px solid #2a2a2a; border-radius: 9px; padding: 7px 10px; }
            QComboBox::drop-down { border: none; }
            QTableWidget { background: #151515; border: 1px solid #2a2a2a; border-radius: 10px; gridline-color: #242424; }
            QHeaderView::section { background: #1a1a1a; border: none; padding: 8px; color: #b9b9b9; }
            QProgressBar { background: #101010; border: 1px solid #2a2a2a; border-radius: 999px; text-align: center; height: 10px; }
            QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #22d3ee, stop:1 #34d399); border-radius: 999px; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        header = QHBoxLayout()
        titulo = QLabel("Xportify")
        titulo.setStyleSheet("font-size: 18pt; font-weight: 600;")
        subtitulo = QLabel("De tu lista a MP3 · Limpio, directo y sin rodeos")
        subtitulo.setStyleSheet("color: #9b9b9b;")
        vheader = QVBoxLayout()
        vheader.addWidget(titulo)
        vheader.addWidget(subtitulo)
        header.addLayout(vheader)
        header.addStretch()
        root.addLayout(header)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self.tab_origen = QWidget()
        self.tabs.addTab(self.tab_origen, "Archivo / Texto")
        self._build_tab_origen()

        self.tab_url = QWidget()
        self.tabs.addTab(self.tab_url, "URL")
        self._build_tab_url()

        self.tab_lista = QWidget()
        self.tabs.addTab(self.tab_lista, "Lista")
        self._build_tab_lista()

        self.tab_descarga = QWidget()
        self.tabs.addTab(self.tab_descarga, "Descarga")
        self._build_tab_descarga()

        try:
            self.carpeta_edit.setText(config.ultimo_directorio())
            q = config.calidad_defecto()
            idx = self.calidad.findData(q)
            if idx>=0: self.calidad.setCurrentIndex(idx)
            pr = config.proveedor_defecto()
            for i in range(self.proveedor.count()):
                if self.proveedor.itemData(i)==pr:
                    self.proveedor.setCurrentIndex(i); break
        except Exception:
            pass
        self.statusBar().showMessage("Listo")
        self._comprobar_ffmpeg()

    def _build_tab_origen(self):
        layout = QVBoxLayout(self.tab_origen)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        grupo_enlaces = QGroupBox("Obtener lista sin complicarte")
        v1 = QVBoxLayout(grupo_enlaces)
        info = QLabel("¿No tienes el CSV/Excel? Exporta tus Me gusta o playlist con uno de estos servicios.")
        info.setStyleSheet("color: #b9b9b9;")
        v1.addWidget(info)
        hlinks = QHBoxLayout()
        b1 = QPushButton("Abrir watsonbox/Exportify (recomendado)")
        b2 = QPushButton("Abrir exportify.net")
        b3 = QPushButton("Abrir Playlistation")
        b1.clicked.connect(lambda: self.abrir("https://watsonbox.github.io/exportify/"))
        b2.clicked.connect(lambda: self.abrir("https://exportify.net/"))
        b3.clicked.connect(lambda: self.abrir("https://playlistation.com/"))
        hlinks.addWidget(b1)
        hlinks.addWidget(b2)
        hlinks.addWidget(b3)
        hlinks.addStretch()
        v1.addLayout(hlinks)
        tip = QLabel("Consejo: exporta 'Liked Songs' para traer todos tus 'Me gusta'.")
        tip.setStyleSheet("color: #9b9b9b;")
        v1.addWidget(tip)
        layout.addWidget(grupo_enlaces)

        grupo_archivo = QGroupBox("Desde archivo CSV / Excel / JSON")
        v2 = QVBoxLayout(grupo_archivo)
        h2 = QHBoxLayout()
        self.archivo_edit = QLineEdit()
        self.archivo_edit.setPlaceholderText("Selecciona un archivo...")
        bsel = QPushButton("Seleccionar archivo")
        bsel.clicked.connect(self.seleccionar_archivo)
        bcargar = QPushButton("Cargar lista")
        bcargar.clicked.connect(self.cargar_desde_archivo)
        h2.addWidget(self.archivo_edit)
        h2.addWidget(bsel)
        h2.addWidget(bcargar)
        v2.addLayout(h2)
        layout.addWidget(grupo_archivo)

        grupo_texto = QGroupBox("Pegar texto (Artista - Canción)")
        v3 = QVBoxLayout(grupo_texto)
        self.texto_edit = QTextEdit()
        self.texto_edit.setPlaceholderText("Ejemplo:\nThe Weeknd - Blinding Lights\nDaft Punk - One More Time")
        bcargar2 = QPushButton("Cargar desde texto")
        bcargar2.clicked.connect(self.cargar_desde_texto)
        v3.addWidget(self.texto_edit)
        v3.addWidget(bcargar2, alignment=Qt.AlignRight)
        layout.addWidget(grupo_texto)

        layout.addStretch()

    def _build_tab_url(self):
        layout = QVBoxLayout(self.tab_url)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        grupo = QGroupBox("Pega un enlace")
        v = QVBoxLayout(grupo)
        info = QLabel("Playlist o álbum de Spotify, playlist de YouTube / YouTube Music, SoundCloud o Bandcamp.")
        info.setStyleSheet("color: #b9b9b9;")
        v.addWidget(info)
        h = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://open.spotify.com/playlist/...")
        self.url_edit.returnPressed.connect(self.cargar_desde_url)
        self.burl = QPushButton("Cargar lista")
        self.burl.setObjectName("primary")
        self.burl.clicked.connect(self.cargar_desde_url)
        h.addWidget(self.url_edit)
        h.addWidget(self.burl)
        v.addLayout(h)
        layout.addWidget(grupo)

        grupo_ayuda = QGroupBox("Notas")
        v2 = QVBoxLayout(grupo_ayuda)
        nota = QLabel(
            "· Funciona con enlaces públicos (playlist, álbum o canción).\n"
            "· Tu lista privada de 'Me gusta' no es accesible por URL: expórtala con Exportify "
            "desde la pestaña anterior.\n"
            "· YouTube Music suele dar mejores coincidencias que YouTube normal."
        )
        nota.setStyleSheet("color: #9b9b9b;")
        nota.setWordWrap(True)
        v2.addWidget(nota)
        layout.addWidget(grupo_ayuda)

        self.lbl_url = QLabel("")
        self.lbl_url.setStyleSheet("color: #9b9b9b;")
        layout.addWidget(self.lbl_url)
        layout.addStretch()

    def cargar_desde_url(self):
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Sin URL", "Pega un enlace primero.")
            return
        self.burl.setEnabled(False)
        self.lbl_url.setText("Leyendo el enlace...")
        self.statusBar().showMessage("Leyendo enlace...")
        self.url_worker = WorkerURL(url)
        self.url_worker.ok.connect(self._url_ok)
        self.url_worker.fallo.connect(self._url_fallo)
        self.url_worker.start()

    def _url_ok(self, canciones):
        self.burl.setEnabled(True)
        self.canciones = canciones
        self.lbl_url.setText(f"{len(canciones)} canciones encontradas")
        self._actualizar_lista()
        self.tabs.setCurrentIndex(2)
        self.statusBar().showMessage(f"Cargadas {len(canciones)} canciones desde URL")

    def _url_fallo(self, mensaje):
        self.burl.setEnabled(True)
        self.lbl_url.setText("No se pudo leer el enlace")
        self.statusBar().showMessage("Error al leer el enlace")
        QMessageBox.critical(self, "Error al leer URL", mensaje)

    def _build_tab_lista(self):
        layout = QVBoxLayout(self.tab_lista)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        cab = QHBoxLayout()
        self.lbl_total = QLabel("Sin canciones cargadas")
        self.lbl_total.setStyleSheet("color: #b9b9b9;")
        cab.addWidget(self.lbl_total)
        cab.addStretch()
        blimp = QPushButton("Limpiar lista")
        blimp.clicked.connect(self.limpiar_lista)
        bexp = QPushButton("Exportar lista (CSV/JSON/Excel)")
        bexp.clicked.connect(self.exportar_lista)
        bir = QPushButton("Ir a Descarga")
        bir.clicked.connect(lambda: self.tabs.setCurrentIndex(3))
        cab.addWidget(blimp)
        cab.addWidget(bexp)
        cab.addWidget(bir)
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

    def _build_tab_descarga(self):
        layout = QVBoxLayout(self.tab_descarga)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        grupo_conf = QGroupBox("Configuración")
        v = QVBoxLayout(grupo_conf)
        h = QHBoxLayout()
        h.addWidget(QLabel("Carpeta de destino"))
        self.carpeta_edit = QLineEdit(str(Path.home() / "Music" / "Xportify"))
        bcarp = QPushButton("Elegir carpeta")
        bcarp.clicked.connect(self.elegir_carpeta)
        babrir = QPushButton("Abrir carpeta")
        babrir.clicked.connect(self.abrir_carpeta)
        h.addWidget(self.carpeta_edit)
        h.addWidget(bcarp)
        h.addWidget(babrir)
        v.addLayout(h)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Calidad MP3 (kbps)"))
        self.calidad = QComboBox()
        for q in [128, 192, 256, 320]:
            self.calidad.addItem(str(q), q)
        self.calidad.setCurrentText("192")
        h2.addWidget(self.calidad)
        h2.addSpacing(24)
        h2.addWidget(QLabel("Proveedor de búsqueda"))
        self.proveedor = QComboBox()
        self.proveedor.addItem("Auto (recomendado)", "auto")
        self.proveedor.addItem("YouTube Music", "ytmusic")
        self.proveedor.addItem("YouTube", "youtube")
        h2.addWidget(self.proveedor)
        h2.addStretch()
        v.addLayout(h2)
        layout.addWidget(grupo_conf)

        grupo_prog = QGroupBox("Progreso")
        vp = QVBoxLayout(grupo_prog)
        self.progreso = QProgressBar()
        self.progreso.setValue(0)
        vp.addWidget(self.progreso)
        self.lbl_prog = QLabel("Esperando para iniciar")
        self.lbl_prog.setStyleSheet("color: #b9b9b9;")
        vp.addWidget(self.lbl_prog)
        hb = QHBoxLayout()
        self.bdescargar = QPushButton("Iniciar descarga")
        self.bdescargar.setObjectName("primary")
        self.bdescargar.clicked.connect(self.iniciar_descarga)
        self.bparar = QPushButton("Detener")
        self.bparar.setEnabled(False)
        self.bparar.clicked.connect(self.detener_descarga)
        hb.addWidget(self.bdescargar)
        hb.addWidget(self.bparar)
        hb.addStretch()
        vp.addLayout(hb)
        layout.addWidget(grupo_prog)

        layout.addStretch()

    def abrir(self, url):
        QDesktopServices.openUrl(url)


    def limpiar_lista(self):
        if self.canciones and not self._descarga_activa():
            reply = QMessageBox.question(self, "Limpiar lista", "¿Eliminar todas las canciones cargadas?")
            if reply != QMessageBox.Yes:
                return
        self.canciones = []
        self.tabla.setRowCount(0)
        self.lbl_total.setText("Sin canciones cargadas")
        self.progreso.setValue(0)
        self.lbl_prog.setText("Esperando para iniciar")
        self.statusBar().showMessage("Lista limpiada")

    def exportar_lista(self):
        if not self.canciones:
            QMessageBox.warning(self, "Sin canciones", "No hay canciones para exportar.")
            return
        ruta, filtro = QFileDialog.getSaveFileName(
            self,
            "Exportar lista",
            str(Path.home() / "xportify_lista.csv"),
            "CSV (*.csv);;JSON (*.json);;Excel (*.xlsx)"
        )
        if not ruta:
            return
        try:
            exportar_lista(self.canciones, ruta)
            QMessageBox.information(self, "Exportado", f"Lista guardada en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _descarga_activa(self):
        return self.worker is not None and self.worker.isRunning()


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                p = url.toLocalFile().lower()
                if p.endswith(('.csv','.xlsx','.xls','.xlsm','.json','.tsv')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            pl = p.lower()
            if pl.endswith(('.csv','.xlsx','.xls','.xlsm','.json','.tsv')):
                self.archivo_edit.setText(p)
                self.tabs.setCurrentIndex(0)
                self.cargar_desde_archivo()
                event.acceptProposedAction()
                return
        event.ignore()

    def closeEvent(self, event):
        if self._descarga_activa():
            reply = QMessageBox.question(
                self,
                "Descarga en curso",
                "Hay una descarga en progreso.\n¿Detenerla y salir?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    self.worker.stop()
                    self.worker.wait(3000)
                except Exception:
                    pass
                event.accept()
            else:
                event.ignore()
            return
        event.accept()

    def _comprobar_ffmpeg(self):
        aviso = aviso_ffmpeg()
        if aviso:
            QMessageBox.warning(self, "FFmpeg requerido", aviso)

    def seleccionar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo",
            str(Path.home()),
            "Archivos soportados (*.csv *.xlsx *.xls *.xlsm *.json);;CSV (*.csv);;Excel (*.xlsx *.xls *.xlsm);;JSON (*.json)"
        )
        if ruta:
            self.archivo_edit.setText(ruta)

    def elegir_carpeta(self):
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.carpeta_edit.text())
        if ruta:
            self.carpeta_edit.setText(ruta)
            Path(ruta).mkdir(parents=True, exist_ok=True)
            try:
                config.guardar_directorio(ruta)
            except Exception:
                pass

    def abrir_carpeta(self):
        ruta = self.carpeta_edit.text().strip()
        if not ruta:
            return
        Path(ruta).mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(f"file://{Path(ruta).resolve()}")

    def cargar_desde_archivo(self):
        ruta = self.archivo_edit.text().strip()
        if not ruta:
            QMessageBox.warning(self, "Sin archivo", "Selecciona un archivo CSV/Excel/JSON primero.")
            return
        try:
            self.canciones = leer_canciones_desde_archivo(ruta)
            self._actualizar_lista()
            self.tabs.setCurrentIndex(2)
            self.statusBar().showMessage(f"Cargadas {len(self.canciones)} canciones")
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar", str(e))

    def cargar_desde_texto(self):
        texto = self.texto_edit.toPlainText()
        if not texto.strip():
            QMessageBox.warning(self, "Sin texto", "Pega al menos una línea con Artista - Canción")
            return
        try:
            self.canciones = parsear_texto_manual(texto)
            if not self.canciones:
                QMessageBox.warning(self, "Vacío", "No se encontraron canciones válidas.")
                return
            self._actualizar_lista()
            self.tabs.setCurrentIndex(2)
            self.statusBar().showMessage(f"Cargadas {len(self.canciones)} canciones")
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar", str(e))

    def _actualizar_lista(self):
        self.tabla.setRowCount(0)
        for i, c in enumerate(self.canciones):
            self.tabla.insertRow(i)
            self.tabla.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.tabla.setItem(i, 1, QTableWidgetItem(c.get("artista", "")))
            self.tabla.setItem(i, 2, QTableWidgetItem(c.get("titulo", "")))
            self.tabla.setItem(i, 3, QTableWidgetItem(c.get("album", "")))
            item = QTableWidgetItem("Pendiente")
            item.setForeground(Qt.gray)
            self.tabla.setItem(i, 4, item)
        self.lbl_total.setText(f"{len(self.canciones)} canciones cargadas")
        self.progreso.setValue(0)
        self.lbl_prog.setText("Listo para descargar")

    def iniciar_descarga(self):
        if getattr(self,'_descarga_activa',lambda: False)():
            QMessageBox.information(self, "Descarga en curso", "Ya hay una descarga en progreso.")
            return
        if not self.canciones:
            QMessageBox.warning(self, "Sin canciones", "Carga canciones desde la pestaña Archivo / Texto o URL primero.")
            return
        if not ffmpeg_disponible():
            QMessageBox.critical(self, "FFmpeg requerido", aviso_ffmpeg())
            return
        carpeta = self.carpeta_edit.text().strip() or str(Path.home() / "Music" / "Xportify")
        self.carpeta_edit.setText(carpeta)
        calidad = self.calidad.currentData()
        preferir = self.proveedor.currentData()
        Path(carpeta).mkdir(parents=True, exist_ok=True)
        try:
            config.guardar_directorio(carpeta)
            config.guardar_calidad(calidad)
            config.guardar_proveedor(preferir)
        except Exception:
            pass

        try:
            self.bdescargar.setEnabled(False)
            self.bparar.setEnabled(True)
        except Exception:
            pass
        try:
            self.tab_origen.setEnabled(False)
            self.tab_url.setEnabled(False)
        except Exception:
            pass
        self.tabs.setCurrentIndex(3)
        self.progreso.setMaximum(len(self.canciones))
        self.progreso.setValue(0)
        try:
            for i in range(self.tabla.rowCount()):
                item = QTableWidgetItem("Pendiente")
                item.setForeground(Qt.gray)
                self.tabla.setItem(i, 4, item)
        except Exception:
            pass
        self.lbl_prog.setText("Iniciando...")

        self.worker = WorkerDescarga(self.canciones, carpeta, calidad, preferir)
        self.worker.progreso.connect(self._on_progreso)
        self.worker.estado_cancion.connect(self._on_estado)
        self.worker.terminado.connect(self._on_terminado)
        self.worker.start()

    def detener_descarga(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.lbl_prog.setText("Deteniendo...")
            self.bparar.setEnabled(False)

    def _bloquear(self, bloquear: bool):
        self.tab_origen.setEnabled(not bloquear)
        self.tab_url.setEnabled(not bloquear)
        try:
            self.bdescargar.setEnabled(not bloquear)
        except Exception:
            pass
        try:
            self.bparar.setEnabled(bloquear)
        except Exception:
            pass

    def _on_progreso(self, actual, total):
        self.progreso.setValue(actual)
        try:
            if actual >=1 and actual <= len(self.canciones):
                c=self.canciones[actual-1]
                et=f"{c.get("artista")+" - " if c.get("artista") else ""}{c.get("titulo","")}"
                self.lbl_prog.setText(f"Progreso: {actual}/{total} · {et}")
            else:
                self.lbl_prog.setText(f"Progreso: {actual}/{total}")
        except Exception:
            self.lbl_prog.setText(f"Progreso: {actual}/{total}")

    def _on_estado(self, idx, estado, etiqueta):
        if idx < 0 or idx >= self.tabla.rowCount():
            return
        col = 4
        if estado == "buscando":
            item = QTableWidgetItem("Buscando")
            item.setForeground(Qt.yellow)
            self.tabla.setItem(idx, col, item)
        elif estado == "descargando":
            item = QTableWidgetItem("Descargando")
            item.setForeground(Qt.cyan)
            self.tabla.setItem(idx, col, item)
        elif estado == "listo":
            item = QTableWidgetItem("Listo")
            item.setForeground(Qt.green)
            self.tabla.setItem(idx, col, item)
        elif estado == "omitida":
            item = QTableWidgetItem("Omitida")
            item.setForeground(Qt.gray)
            self.tabla.setItem(idx, col, item)
        elif estado == "error":
            item = QTableWidgetItem("Error")
            item.setForeground(Qt.red)
            self.tabla.setItem(idx, col, item)

    def _on_terminado(self, fallidas):
        self.bdescargar.setEnabled(True)
        self.bparar.setEnabled(False)
        if fallidas:
            carpeta = self.carpeta_edit.text().strip()
            log = Path(carpeta) / "fallidas.txt"
            try:
                log.write_text("\n".join(f"{n}  ->  {m}" for n, m in fallidas), encoding="utf-8")
                QMessageBox.information(self, "Finalizado con errores", f"{len(fallidas)} canciones fallaron.\nLista guardada en:\n{log}")
            except Exception:
                QMessageBox.information(self, "Finalizado con errores", f"{len(fallidas)} canciones fallaron.")
            self.lbl_prog.setText(f"Finalizado · {len(fallidas)} fallidas")
        else:
            QMessageBox.information(self, "Finalizado", "Todo descargado sin errores.")
            self.lbl_prog.setText("Todo completado")
        try:
            self.tab_origen.setEnabled(True)
            self.tab_url.setEnabled(True)
        except Exception:
            pass
        self.statusBar().showMessage("Descarga finalizada")
        self.worker = None

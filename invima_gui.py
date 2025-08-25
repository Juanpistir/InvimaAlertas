from __future__ import annotations

import sys
import json
from pathlib import Path
from PySide6.QtGui import QFontDatabase, QFont, QPixmap, QPainter, QColor
from typing import Dict

from PySide6.QtCore import Qt, Slot, QUrl, QSize
from PySide6.QtGui import QDesktopServices
from PySide6.QtGui import QIcon
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QTextEdit,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QIcon

import main as invima_main


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invima Reportes - GUI")
        # Central container wrapped later in a scroll area
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # App title (large, iOS-like)
        title = QLabel("Invima Reportes")
        title.setObjectName('titleLabel')
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        # Plantilla
        grid.addWidget(QLabel("Plantilla (xlsx):"), 0, 0)
        self.plantilla_edit = QLineEdit("plantilla.xlsx")
        grid.addWidget(self.plantilla_edit, 0, 1)
        btn_plantilla = QPushButton("Seleccionar...")
        btn_plantilla.clicked.connect(self.select_plantilla)
        grid.addWidget(btn_plantilla, 0, 2)

        # Salida
        grid.addWidget(QLabel("Archivo de salida:"), 1, 0)
        self.salida_edit = QLineEdit("reporte_invima_lleno.xlsx")
        grid.addWidget(self.salida_edit, 1, 1)
        btn_salida = QPushButton("Seleccionar...")
        btn_salida.clicked.connect(self.select_salida)
        grid.addWidget(btn_salida, 1, 2)

        # Filas
        grid.addWidget(QLabel("Fila inicial:"), 2, 0)
        self.fila_spin = QSpinBox()
        self.fila_spin.setRange(1, 1000)
        self.fila_spin.setValue(6)
        grid.addWidget(self.fila_spin, 2, 1)

        grid.addWidget(QLabel("Última fila (datos):"), 3, 0)
        self.ultima_spin = QSpinBox()
        self.ultima_spin.setRange(1, 10000)
        self.ultima_spin.setValue(34)
        grid.addWidget(self.ultima_spin, 3, 1)

        # Datos fijos
        datos_group = QGroupBox("Datos fijos")
        # Center and emphasize the group title like an iOS header
        datos_group.setAlignment(Qt.AlignHCenter)
        datos_group.setFont(QFont(self.font().family(), 10, QFont.Bold))
        datos_layout = QGridLayout()
        datos_layout.setHorizontalSpacing(10)
        datos_layout.setVerticalSpacing(8)
        datos_layout.setContentsMargins(14, 18, 14, 12)
        datos_group.setLayout(datos_layout)

        lbl = QLabel("Medicamento / Dispositivo:")
        lbl.setObjectName('rowLabel')
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        datos_layout.addWidget(lbl, 0, 0)
        try:
            self.apply_card_shadow(lbl)
        except Exception:
            pass
        self.medicamento_edit = QLineEdit("DISPOSITIVO MÉDICO")
        datos_layout.addWidget(self.medicamento_edit, 0, 1)

        lbl = QLabel("Aplica institución:")
        lbl.setObjectName('rowLabel')
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        datos_layout.addWidget(lbl, 1, 0)
        try:
            self.apply_card_shadow(lbl)
        except Exception:
            pass
        self.aplica_edit = QLineEdit("NO")
        datos_layout.addWidget(self.aplica_edit, 1, 1)

        lbl = QLabel("Acciones ejecutadas:")
        lbl.setObjectName('rowLabel')
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        datos_layout.addWidget(lbl, 2, 0)
        try:
            self.apply_card_shadow(lbl)
        except Exception:
            pass
        self.acciones_edit = QLineEdit("N/A")
        datos_layout.addWidget(self.acciones_edit, 2, 1)

        lbl = QLabel("Responsable revisión:")
        lbl.setObjectName('rowLabel')
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        datos_layout.addWidget(lbl, 3, 0)
        try:
            self.apply_card_shadow(lbl)
        except Exception:
            pass
        self.responsable_edit = QLineEdit("")
        datos_layout.addWidget(self.responsable_edit, 3, 1)

        lbl = QLabel("Logotipo (png):")
        lbl.setObjectName('rowLabel')
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        datos_layout.addWidget(lbl, 4, 0)
        try:
            self.apply_card_shadow(lbl)
        except Exception:
            pass
        self.logo_edit = QLineEdit("logotipo.png")
        datos_layout.addWidget(self.logo_edit, 4, 1)
        btn_logo = QPushButton("Seleccionar...")
        btn_logo.clicked.connect(self.select_logo)
        datos_layout.addWidget(btn_logo, 4, 2)

        lbl = QLabel("Anchura imagen (px):")
        lbl.setObjectName('rowLabel')
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        datos_layout.addWidget(lbl, 5, 0)
        try:
            self.apply_card_shadow(lbl)
        except Exception:
            pass
        self.logo_width_spin = QSpinBox()
        self.logo_width_spin.setRange(10, 2000)
        self.logo_width_spin.setValue(240)
        # Make numeric inputs compact so width fits content better
        self.logo_width_spin.setFixedWidth(100)
        datos_layout.addWidget(self.logo_width_spin, 5, 1)

        # Indica si la plantilla ya contiene el logotipo (siempre activado por defecto)
        self.template_has_logo_chk = QCheckBox("La plantilla ya contiene el logotipo")
        self.template_has_logo_chk.setObjectName('rowLabel')
        self.template_has_logo_chk.setChecked(True)
        datos_layout.addWidget(self.template_has_logo_chk, 6, 0, 1, 2)
        try:
            self.apply_card_shadow(self.template_has_logo_chk)
        except Exception:
            pass

        # URL y páginas
        grid.addWidget(QLabel("Base URL:"), 4, 0)
        self.url_edit = QLineEdit(
            "https://app.invima.gov.co/alertas/dispositivos-medicos-invima?field_tipo_de_documento_value=1&field_a_o_value=1"
        )
        grid.addWidget(self.url_edit, 4, 1, 1, 2)

        grid.addWidget(QLabel("Número de páginas:"), 5, 0)
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 1000)
        self.pages_spin.setValue(2)
        self.pages_spin.setFixedWidth(90)
        grid.addWidget(self.pages_spin, 5, 1)

        layout.addLayout(grid)
        layout.addWidget(datos_group)

        # Botones y progreso
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Ejecutar Scraper")
        # mark primary action for styling
        self.run_btn.setProperty('role', 'primary')
        self.run_btn.clicked.connect(self.run_scraper)
        btn_layout.addWidget(self.run_btn)

        self.open_folder_btn = QPushButton("Abrir carpeta")
        self.open_folder_btn.setProperty('role', 'secondary')
        self.open_folder_btn.clicked.connect(self.open_folder)
        btn_layout.addWidget(self.open_folder_btn)

        # Config save/load
        self.save_cfg_btn = QPushButton("Guardar configuración")
        self.save_cfg_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(self.save_cfg_btn)

        self.load_cfg_btn = QPushButton("Cargar configuración")
        self.load_cfg_btn.clicked.connect(self.load_config)
        btn_layout.addWidget(self.load_cfg_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Progreso:"))
        self.progress_text = QTextEdit()
        self.progress_text.setObjectName('progressBox')
        self.progress_text.setReadOnly(True)
        self.progress_text.setFixedHeight(200)
        layout.addWidget(self.progress_text)

        # Apply shadow effects to group and progress for a card-like feeling
        try:
            self.apply_card_shadow(datos_group)
            self.apply_card_shadow(self.progress_text)
        except Exception:
            pass

        # Put central widget inside a scroll area so the UI scrolls when window is small
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(central)
        self.setCentralWidget(scroll)

        # Try to set icons for main buttons if icons exist (render play icon in white)
        self.try_set_icon(self.run_btn, 'play.svg', tint=QColor(255,255,255))
        self.try_set_icon(self.open_folder_btn, 'folder-open.svg')
        self.try_set_icon(self.save_cfg_btn, 'save.svg')
        self.try_set_icon(self.load_cfg_btn, 'download.svg')

    @Slot()
    def select_plantilla(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar plantilla", str(Path.cwd()), "Excel Files (*.xlsx)")
        if path:
            self.plantilla_edit.setText(path)
    
    @Slot()
    def select_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar logotipo", str(Path.cwd()), "Image Files (*.png *.jpg *.jpeg)")
        if path:
            self.logo_edit.setText(path)

    @Slot()
    def select_salida(self):
        # Abrir diálogo de 'Guardar como' para elegir destino del archivo de salida
        default = str(Path.cwd() / self.salida_edit.text())
        path, _ = QFileDialog.getSaveFileName(self, "Seleccionar archivo de salida", default, "Excel Files (*.xlsx)")
        if path:
            # Asegurar extensión .xlsx si el usuario no la añadió
            if not Path(path).suffix:
                path = f"{path}.xlsx"
            self.salida_edit.setText(path)

    @Slot()
    def open_folder(self):
        carpeta = str(Path.cwd())
        QDesktopServices.openUrl(__import__("PySide6.QtCore", fromlist=["QUrl"]).QUrl.fromLocalFile(carpeta))

    def append_progress(self, text: str):
        self.progress_text.append(text)

    def try_set_icon(self, button: QPushButton, icon_name: str, tint: QColor | None = None):
        """Set QIcon from icons/<icon_name> if the file exists. If tint is provided, render SVG tinted to that color."""
        icons_dir = Path(__file__).parent / 'icons'
        svg_path = icons_dir / icon_name
        if not svg_path.exists():
            return
        try:
            if tint is None:
                button.setIcon(QIcon(str(svg_path)))
                button.setIconSize(QSize(20, 20))
                return
            # Render SVG to a pixmap and tint it
            renderer = QSvgRenderer(str(svg_path))
            pix = QPixmap(20, 20)
            pix.fill(Qt.transparent)
            p = QPainter(pix)
            renderer.render(p)
            p.setCompositionMode(QPainter.CompositionMode_SourceIn)
            p.fillRect(pix.rect(), tint)
            p.end()
            button.setIcon(QIcon(pix))
            button.setIconSize(QSize(20, 20))
        except Exception:
            try:
                button.setIcon(QIcon(str(svg_path)))
                button.setIconSize(QSize(20, 20))
            except Exception:
                pass

    def apply_card_shadow(self, widget: QWidget):
        """Apply a subtle drop shadow effect to a widget to emulate card depth."""
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(12)
        effect.setOffset(0, 3)
        effect.setColor(QColor(0, 0, 0, 70))
        widget.setGraphicsEffect(effect)

    @Slot()
    def save_config(self):
        cfg = {
            'base_url': self.url_edit.text().strip(),
            'num_pages': int(self.pages_spin.value()),
            'plantilla_path': self.plantilla_edit.text().strip(),
            'salida_path': self.salida_edit.text().strip(),
            'fila_inicial': int(self.fila_spin.value()),
            'ultima_fila_datos': int(self.ultima_spin.value()),
            'medicamento_dispositivo': self.medicamento_edit.text().strip(),
            'aplica_institucion': self.aplica_edit.text().strip(),
            'acciones_ejecutadas': self.acciones_edit.text().strip(),
            'responsable_revision': self.responsable_edit.text().strip(),
            'image_path': self.logo_edit.text().strip(),
            'image_width_px': int(self.logo_width_spin.value()),
            'template_has_logo': bool(self.template_has_logo_chk.isChecked()),
        }
        try:
            path = Path.cwd() / 'config.json'
            path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
            self.append_progress(f"Configuración guardada en {path}")
            QMessageBox.information(self, "Guardado", f"Configuración guardada en {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {e}")

    @Slot()
    def load_config(self):
        try:
            path = Path.cwd() / 'config.json'
            if not path.exists():
                QMessageBox.warning(self, "No existe", "No se encontró 'config.json' en la carpeta del proyecto.")
                return
            data = json.loads(path.read_text(encoding='utf-8'))
            # Aplicar valores si existen
            self.url_edit.setText(data.get('base_url', self.url_edit.text()))
            self.pages_spin.setValue(int(data.get('num_pages', self.pages_spin.value())))
            self.plantilla_edit.setText(data.get('plantilla_path', self.plantilla_edit.text()))
            self.salida_edit.setText(data.get('salida_path', self.salida_edit.text()))
            self.fila_spin.setValue(int(data.get('fila_inicial', self.fila_spin.value())))
            self.ultima_spin.setValue(int(data.get('ultima_fila_datos', self.ultima_spin.value())))
            self.medicamento_edit.setText(data.get('medicamento_dispositivo', self.medicamento_edit.text()))
            self.aplica_edit.setText(data.get('aplica_institucion', self.aplica_edit.text()))
            self.acciones_edit.setText(data.get('acciones_ejecutadas', self.acciones_edit.text()))
            self.responsable_edit.setText(data.get('responsable_revision', self.responsable_edit.text()))
            self.logo_edit.setText(data.get('image_path', self.logo_edit.text()))
            self.logo_width_spin.setValue(int(data.get('image_width_px', self.logo_width_spin.value())))
            self.template_has_logo_chk.setChecked(bool(data.get('template_has_logo', True)))
            self.append_progress(f"Configuración cargada desde {path}")
            QMessageBox.information(self, "Cargado", f"Configuración cargada desde {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la configuración: {e}")

    @Slot()
    def run_scraper(self):
        config: Dict = {
            'base_url': self.url_edit.text().strip(),
            'num_pages': int(self.pages_spin.value()),
            'plantilla_path': self.plantilla_edit.text().strip(),
            'salida_path': self.salida_edit.text().strip(),
            'fila_inicial': int(self.fila_spin.value()),
            'ultima_fila_datos': int(self.ultima_spin.value()),
            'medicamento_dispositivo': self.medicamento_edit.text().strip(),
            'aplica_institucion': self.aplica_edit.text().strip(),
            'acciones_ejecutadas': self.acciones_edit.text().strip(),
            'responsable_revision': self.responsable_edit.text().strip(),
            'image_path': self.logo_edit.text().strip(),
            'image_width_px': int(self.logo_width_spin.value()),
            'template_has_logo': bool(self.template_has_logo_chk.isChecked()),
        }

        self.progress_text.clear()
        self.run_btn.setEnabled(False)
        try:
            salida = invima_main.run_invima_scraper(config, progress=self.append_progress)
            QMessageBox.information(self, "Terminado", f"Reporte generado: {salida}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo: {e}")
        finally:
            self.run_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    # Cargar tema iOS-like (QSS) si existe
    qss_path = Path(__file__).parent / 'styles' / 'ios_like.qss'
    if qss_path.exists():
        try:
            with qss_path.open('r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
        except Exception:
            pass

    # Intentar registrar una fuente bundled (fonts/Inter-Regular.ttf) si existe
    fonts_dir = Path(__file__).parent / 'fonts'
    inter_path = fonts_dir / 'Inter-Regular.ttf'
    if inter_path.exists():
        try:
            QFontDatabase.addApplicationFont(str(inter_path))
            app.setFont(QFont('Inter', 11))
        except Exception:
            pass
    else:
        # Ajuste de fuente por defecto para look más iOS-like en Windows
        app.setFont(QFont('Segoe UI', 10))
    w = MainWindow()
    w.resize(900, 700)
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

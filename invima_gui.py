from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Dict

from PySide6.QtCore import Qt, Slot, QUrl
from PySide6.QtGui import QDesktopServices
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
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QTextEdit,
)

import main as invima_main


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invima Reportes - GUI")

        central = QWidget()
        layout = QVBoxLayout(central)

        grid = QGridLayout()

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
        datos_layout = QGridLayout()
        datos_group.setLayout(datos_layout)

        datos_layout.addWidget(QLabel("Medicamento / Dispositivo:"), 0, 0)
        self.medicamento_edit = QLineEdit("DISPOSITIVO MÉDICO")
        datos_layout.addWidget(self.medicamento_edit, 0, 1)

        datos_layout.addWidget(QLabel("Aplica institución:"), 1, 0)
        self.aplica_edit = QLineEdit("NO")
        datos_layout.addWidget(self.aplica_edit, 1, 1)

        datos_layout.addWidget(QLabel("Acciones ejecutadas:"), 2, 0)
        self.acciones_edit = QLineEdit("N/A")
        datos_layout.addWidget(self.acciones_edit, 2, 1)

        datos_layout.addWidget(QLabel("Responsable revisión:"), 3, 0)
        self.responsable_edit = QLineEdit("")
        datos_layout.addWidget(self.responsable_edit, 3, 1)

        datos_layout.addWidget(QLabel("Logotipo (png):"), 4, 0)
        self.logo_edit = QLineEdit("logotipo.png")
        datos_layout.addWidget(self.logo_edit, 4, 1)
        btn_logo = QPushButton("Seleccionar...")
        btn_logo.clicked.connect(self.select_logo)
        datos_layout.addWidget(btn_logo, 4, 2)

        datos_layout.addWidget(QLabel("Anchura imagen (px):"), 5, 0)
        self.logo_width_spin = QSpinBox()
        self.logo_width_spin.setRange(10, 2000)
        self.logo_width_spin.setValue(240)
        datos_layout.addWidget(self.logo_width_spin, 5, 1)

        # Indica si la plantilla ya contiene el logotipo (siempre activado por defecto)
        self.template_has_logo_chk = QCheckBox("La plantilla ya contiene el logotipo")
        self.template_has_logo_chk.setChecked(True)
        datos_layout.addWidget(self.template_has_logo_chk, 6, 0, 1, 2)

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
        grid.addWidget(self.pages_spin, 5, 1)

        layout.addLayout(grid)
        layout.addWidget(datos_group)

        # Botones y progreso
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Ejecutar Scraper")
        self.run_btn.clicked.connect(self.run_scraper)
        btn_layout.addWidget(self.run_btn)

        self.open_folder_btn = QPushButton("Abrir carpeta")
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
        self.progress_text.setReadOnly(True)
        self.progress_text.setFixedHeight(200)
        layout.addWidget(self.progress_text)

        self.setCentralWidget(central)

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
    w = MainWindow()
    w.resize(900, 700)
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

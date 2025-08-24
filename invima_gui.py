from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

from PySide6.QtCore import Qt, Slot
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

        # URL y páginas
        grid.addWidget(QLabel("Base URL:"), 4, 0)
        self.url_edit = QLineEdit("https://app.invima.gov.co/alertas/dispositivos-medicos-invima?field_tipo_de_documento_value=1&field_a_o_value=1")
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
    def open_folder(self):
        carpeta = str(Path.cwd())
        QDesktopServices = __import__('PySide6.QtGui', fromlist=['QDesktopServices']).QDesktopServices
        QUrl = __import__('PySide6.QtCore', fromlist=['QUrl']).QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(carpeta))

    def append_progress(self, text: str):
        self.progress_text.append(text)

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

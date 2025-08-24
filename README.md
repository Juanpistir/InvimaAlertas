Insertar un logotipo en el reporte

La aplicación ahora soporta insertar una imagen en el rango `A1:B4` del archivo generado si configuras el campo "Logotipo (png)" en la GUI o añades `image_path` en `config.json`.
Para que la imagen se redimensione correctamente, instala Pillow:

```powershell
python -m pip install pillow
```

Control de anchura: puedes ajustar "Anchura imagen (px)" en la GUI (valor por defecto 240px).
- PySide6 y PyInstaller están en `environment.yml` para reproducibilidad.
InvimaReportes GUI

Instrucciones rápidas:

1) Crear entorno (si no lo hiciste):

```powershell
conda env create -f environment.yml
conda activate InvimaReportes
```

2) Ejecutar la GUI:

```powershell
python .\invima_gui.py
```

3) Empaquetar en un .exe (Windows) con PyInstaller (opcional):

```powershell
conda activate InvimaReportes
pyinstaller --name InvimaReportes --windowed invima_gui.py
```

El ejecutable saldrá en `dist\InvimaReportes\`.

Notas:
- Asegúrate de incluir `plantilla.xlsx` en la misma carpeta o seleccionarla desde la GUI.
- PySide6 y PyInstaller están en `environment.yml` para reproducibilidad.

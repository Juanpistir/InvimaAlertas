import requests
from bs4 import BeautifulSoup
import time
import openpyxl
from typing import Callable, Dict, List, Optional


def scraper_invima(url: str, headers: Dict[str, str]) -> Optional[List[Dict[str, str]]]:
    """Realiza una petición y extrae alertas desde la página dada.

    Retorna lista de dicts con claves: Nombre, RISARH, Fecha. Devuelve [] si no hay filas.
    """
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la petición a {url}: {e}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    scraped_data = []
    filas = soup.find_all("div", class_="alertas-invima-list")
    if not filas:
        return []
    for fila in filas:
        try:
            nombre = fila.find(class_="views-field-title").text.strip()
        except Exception:
            nombre = ""
        try:
            risarh = fila.find(class_="views-field-field-numero-de-id-d-m").text.strip()
        except Exception:
            risarh = ""
        try:
            fecha = fila.find(class_="views-field-field-a-o").text.strip()
        except Exception:
            fecha = ""
        data = {"Nombre": nombre, "RISARH": risarh, "Fecha": fecha}
        scraped_data.append(data)
    return scraped_data


def run_invima_scraper(config: Dict, progress: Optional[Callable[[str], None]] = None) -> str:
    """Ejecuta el scraping y llena la plantilla según `config`.

    Config (valores por defecto razonables):
      - base_url
      - num_pages
      - headers
      - plantilla_path
      - salida_path
      - fila_inicial
      - ultima_fila_datos
      - medicamento_dispositivo
      - aplica_institucion
      - acciones_ejecutadas
      - responsable_revision

    `progress` puede ser una función que recibe strings para mostrar al usuario.
    Retorna la ruta del archivo generado.
    """
    # Valores por defecto
    base_url = config.get("base_url", "https://app.invima.gov.co/alertas/dispositivos-medicos-invima?field_tipo_de_documento_value=1&field_a_o_value=1")
    num_pages = int(config.get("num_pages", 2))
    headers = config.get("headers", {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
    })

    plantilla = config.get("plantilla_path", "plantilla.xlsx")
    salida = config.get("salida_path", "reporte_invima_lleno.xlsx")
    fila_inicial = int(config.get("fila_inicial", 6))
    ultima_fila_datos = int(config.get("ultima_fila_datos", 34))

    medicamento_dispositivo = config.get("medicamento_dispositivo", "DISPOSITIVO MÉDICO")
    aplica_institucion = config.get("aplica_institucion", "NO")
    acciones_ejecutadas = config.get("acciones_ejecutadas", "N/A")
    responsable_revision = config.get("responsable_revision", "")

    todas_las_alertas = []
    if progress:
        progress(f"Iniciando scraping de las primeras {num_pages} páginas...")
    for page_num in range(num_pages):
        url_actual = f"{base_url}&page={page_num}"
        if progress:
            progress(f"Scrapeando página {page_num + 1}: {url_actual}")
        alertas_pagina_actual = scraper_invima(url_actual, headers)
        if alertas_pagina_actual:
            todas_las_alertas.extend(alertas_pagina_actual)
            if progress:
                progress(f"Encontradas {len(alertas_pagina_actual)} alertas en la página {page_num + 1}.")
        else:
            if progress:
                progress("No se encontraron más alertas. Deteniendo.")
            break
        time.sleep(float(config.get("delay", 1)))

    if not todas_las_alertas:
        if progress:
            progress("No se extrajeron alertas.")
        raise RuntimeError("No se extrajeron alertas desde la fuente especificada.")

    # Guardar en Excel
    try:
        if progress:
            progress(f"Cargando la plantilla '{plantilla}'...")
        workbook = openpyxl.load_workbook(plantilla)
        sheet = workbook.active

        espacios_disponibles = ultima_fila_datos - fila_inicial + 1
        if len(todas_las_alertas) > espacios_disponibles:
            alertas_para_escribir = todas_las_alertas[:espacios_disponibles]
            if progress:
                progress(f"Se extrajeron {len(todas_las_alertas)} alertas, pero la plantilla tiene espacio para {espacios_disponibles}. Se escribirán las primeras {espacios_disponibles}.")
        else:
            alertas_para_escribir = todas_las_alertas

        for index, alerta in enumerate(alertas_para_escribir):
            row = fila_inicial + index
            sheet[f'A{row}'] = alerta.get('Fecha', '')
            sheet[f'B{row}'] = alerta.get('RISARH', '')
            sheet[f'C{row}'] = medicamento_dispositivo
            sheet[f'D{row}'] = alerta.get('Nombre', '')
            sheet[f'E{row}'] = aplica_institucion
            sheet[f'F{row}'] = acciones_ejecutadas
            sheet[f'H{row}'] = responsable_revision

        workbook.save(salida)
        if progress:
            progress(f"Reporte guardado en: {salida}")
        return salida

    except FileNotFoundError:
        if progress:
            progress(f"ERROR: No se encontró el archivo de plantilla '{plantilla}'.")
        raise
    except Exception as e:
        if progress:
            progress(f"Error al procesar Excel: {e}")
        raise


if __name__ == '__main__':
    # Comportamiento por defecto cuando se ejecuta directamente (mantener compatibilidad con el script original)
    default_config = {
        'base_url': "https://app.invima.gov.co/alertas/dispositivos-medicos-invima?field_tipo_de_documento_value=1&field_a_o_value=1",
        'num_pages': 2,
        'plantilla_path': 'plantilla.xlsx',
        'salida_path': 'reporte_invima_lleno.xlsx',
        'fila_inicial': 6,
        'ultima_fila_datos': 34,
    }
    try:
        salida = run_invima_scraper(default_config, progress=print)
        print(f"Salida: {salida}")
    except Exception as e:
        print(f"Ejecución fallida: {e}")
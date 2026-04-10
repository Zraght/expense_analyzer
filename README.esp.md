🌐 [English version](README.md)

# expense-tracker

Lo construí originalmente porque seguía exportando mis transacciones bancarias a CSV y luego no hacía nada con ellas. Las abría en Excel, las revisaba un momento y cerraba el archivo. Así que en algún punto decidí escribir algo que procesara los datos de verdad — categorías, tendencias, todo lo que pareciera raro — y produjera algo legible.

Es una herramienta de línea de comandos. Apúntala a un archivo CSV o Excel y ejecuta el flujo completo: lee y limpia los datos, calcula estadísticas por categoría y mes, detecta transacciones sospechosas, genera tres gráficos y escribe un reporte HTML autónomo que puedes abrir sin internet.

```
$ expense-tracker -i data/expenses.csv

  PASO 1 / 3  —  Ingesta de datos
  Registros: 21  |  Período: 01/05/2024 — 03/28/2024  |  Total: $7,679.00

  PASO 2 / 3  —  Análisis y Detección de Anomalías
  [+] $2,400.00 es 2.2x por encima de la media de Comida de $579.83  (Evento de catering)

  PASO 3 / 3  —  Visualizaciones
  [bar]  bar_category_20240408.png
  [pie]  pie_category_20240408.png
  [line] line_monthly_20240408.png
  [html] expense_report_20240408.html
```

---

## Primeros pasos

```bash
git clone https://github.com/Zraght/expense-tracker
cd expense-tracker
pip install -e .

# hay un archivo de ejemplo en data/ si quieres probarlo de inmediato
expense-tracker

# o apúntalo a tu propio archivo
expense-tracker -i ruta/a/gastos.csv -o resultados/

# omite el reporte HTML si solo quieres la salida en terminal + gráficos
expense-tracker --no-report --log-level DEBUG
```

Requiere Python 3.10+.

```bash
# dependencias de desarrollo (pytest, black, ruff, mypy) — opcionales
pip install -e ".[dev]"

python -m pytest tests/
# 73 pasaron
```

---

## Cómo usarlo

```
expense-tracker [-h] [-i INPUT] [-o OUTPUT] [-c CONFIG]
                [--log-level {DEBUG,INFO,WARNING,ERROR}]
                [--show-plots] [--no-report] [--version]
```

| Opción | Qué hace |
|---|---|
| `-i`, `--input` | ruta a tu archivo CSV o Excel |
| `-o`, `--output` | carpeta de salida, por defecto `output/` |
| `-c`, `--config` | ruta a un archivo de configuración personalizado |
| `--log-level` | ponlo en `DEBUG` si algo no se está parseando correctamente |
| `--show-plots` | muestra los gráficos en una ventana (necesita pantalla, obviamente) |
| `--no-report` | omite el reporte HTML, solo guarda los gráficos |

---

## Cómo debe verse tu archivo

Cuatro columnas, nada más:

| Columna | Tipo | Ejemplo |
|---|---|---|
| `Date` | string | `2024-03-15` |
| `Category` | string | `Food` |
| `Amount` | float | `85.50` |
| `Description` | string | `Compras semanales` |

El formato de fecha por defecto es `%Y-%m-%d`. Si tus fechas tienen un formato distinto, eso es configurable. El archivo de ejemplo en `data/expenses_example.csv` es probablemente la forma más rápida de entender qué espera el programa.

---

## Qué hace exactamente

Lee archivos `.csv`, `.xlsx` o `.xls`. Al cargar el archivo, coerciona los tipos, elimina duplicados completos y advierte sobre cualquier cosa que tuvo que omitir (fechas incorrectas, montos no numéricos, ese tipo de cosas).

A partir de ahí calcula:
- gasto total y promedio por mes
- totales, porcentajes y conteo de transacciones por categoría
- las transacciones individuales más altas y más bajas

Luego comprueba si hay anomalías — más sobre eso a continuación.

Finalmente: tres gráficos (barras, pastel, línea), guardados como PNGs a 300 DPI. Y si no pasaste `--no-report`, escribe un archivo HTML autónomo con los gráficos incrustados en base64. Lo hice así para que el archivo se mantenga íntegro si lo mueves o se lo envías a alguien — sin enlaces de imagen rotos.

Los logs se guardan en `logs/expense_tracker.log` con rotación para que no se acumulen.

---

## La parte de detección de anomalías

Resultó ser más útil de lo que esperaba cuando la agregué. Básicamente, para cada categoría, examina todas tus transacciones y marca las que están muy fuera del rango normal para esa categoría específicamente — no en general, sino por categoría. Así que un cargo de $400 en una categoría donde normalmente gastas $40 será marcado, aunque $400 sea completamente normal en otra categoría.

La salida es intencionalmente simple:

```
[+] $2,400.00 es 2.2x por encima de la media de Comida de $579.83
    Fecha: 03/28/2024  |  Evento de catering
```

En la práctica esto detecta tres cosas: errores de ingreso de datos (monto incorrecto), cargos duplicados reales, y excepciones legítimas que quizás quieras revisar de todas formas. Las categorías con menos de 3 transacciones se omiten — no hay suficiente historial para determinar qué es "normal".

El umbral es configurable si el valor por defecto marca demasiado o muy poco.

---

## Configuración

No necesitas un archivo de configuración para ejecutarlo — hay valores por defecto para todo. Pero si quieres ajustar algo, edita `config/config.json`:

```json
{
  "analysis": {
    "anomaly_z_threshold": 2.0
  },
  "visualization": {
    "dpi": 300,
    "show_plots": false
  },
  "output": {
    "export_html": true
  }
}
```

Cualquier clave que omitas simplemente vuelve al valor por defecto. El conjunto completo de valores por defecto está en `utils/config_loader.py` si quieres ver todo lo que se puede ajustar. También puedes sobreescribir la mayoría de las opciones directamente desde la línea de comandos sin tocar el archivo.

---

## Estructura del proyecto

```
expense-tracker/
├── main.py                   # Punto de entrada CLI y orquestador del flujo
├── pyproject.toml            # Configuración de build, dependencias, ajustes de herramientas
├── config/
│   └── config.json           # Configuración editable por el usuario
├── data/
│   └── expenses_example.csv  # Datos de ejemplo
├── modules/
│   ├── reading.py            # Ingesta y limpieza de CSV/Excel
│   ├── analysis.py           # Estadísticas y detección de anomalías
│   ├── visualization.py      # Generación de gráficos (matplotlib/seaborn)
│   └── reporter.py           # Constructor del reporte HTML
├── utils/
│   ├── config_loader.py      # Carga de configuración con fusión profunda de defaults
│   ├── logger.py             # Logging rotativo en archivo y consola
│   └── validators.py         # Validación de DataFrames y rutas
├── tests/
│   ├── conftest.py           # Fixtures compartidos
│   ├── test_analysis.py
│   ├── test_reading.py
│   ├── test_validators.py
│   └── test_config.py
├── logs/
└── output/
```

---

## Por qué lo construí como un proyecto "real"

Honestamente, en parte fue para tener algo que mostrar. Quería construir algo de principio a fin — no un notebook, no un script, sino un CLI instalable de verdad con tests, logging, gestión de configuración y manejo adecuado de errores. El tipo de cosa que le entregarías a alguien más y podría ejecutar sin problemas.

Los patrones aquí son los que usaría en un trabajo real de pipelines de datos:

| Patrón | Dónde |
|---|---|
| Pipeline ETL | `reading.py` → `analysis.py` → `reporter.py` |
| Validación de esquema + contratos de datos | `utils/validators.py`, verificaciones de columnas antes de cualquier procesamiento |
| Detección estadística de anomalías | `detect_anomalies()` — mismo enfoque usado en detección de fraudes y monitoreo de logs |
| Logging estructurado | manejador rotativo, niveles consistentes en todos los módulos |
| Comportamiento dirigido por configuración | JSON con fusión profunda, sin valores hardcodeados, sobreescribible por entorno |
| CLI con códigos de salida | argparse, valor no-cero en caso de fallo, funciona en scripts y CI |
| Empaquetado adecuado | `pyproject.toml`, instalable con `pip install -e .` |
| Cobertura de tests | 73 pruebas unitarias, fixtures compartidos, casos límite, rutas de validación |

---

## Licencia

MIT — ver [LICENSE](LICENSE).
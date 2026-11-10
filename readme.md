# Hotelera Caribe S.A.S. · Sistema de Business Intelligence

Proyecto final de Inteligencia de Negocios (Fundación Universitaria Konrad Lorenz). Diseño e implementación de un sistema de BI para **Hotelera Caribe S.A.S.**, una cadena hotelera **ficticia** de cinco hoteles en Cartagena de Indias, construida sobre datos públicos reales del turismo colombiano.

> **Declaración de datos.** Las cifras internas de la cadena (habitaciones, empleados, tarifas) son inventadas, y las reservas (F3) son datos **sintéticos** generados por el equipo, calibrados con datos reales de Migración Colombia y del DANE. No hay datos personales de personas reales.

## Integrantes y entregas

| Dato | Valor |
|---|---|
| Integrantes | Laura Sofía Franco Mateus (506241128) · Karen Marcela Bayona Romero (506241093) |
| Docente | Leandro Pájaro Fuentes |
| Entrega 1 | 23/10/2026 · Diagnóstico, estrategia y diseño |
| Entrega 2 | 06/11/2026 · Data warehouse, ETL y tablero |
| Entrega final | 17/11/2026 |

---

## El problema

Cada hotel registra las reservas con formatos distintos, calcula la ocupación y la tarifa promedio con definiciones diferentes y guarda el histórico en archivos dispersos. Un analista consolida los informes a mano en unos cinco días hábiles, por lo que el gerente general no tiene evidencia para fijar, con cuatro a seis meses de antelación, las tarifas por tipo de habitación ni la contratación de temporales.

Según el modelo de madurez de BI (BIMM), la cadena está en la **fase 2** (datos accesibles sin BI). El proyecto apunta a la **fase 5** (crecimiento del DW y reporting formal).

---

## Preguntas de negocio

| # | Pregunta | Tipo |
|---|---|---|
| **P0** | ¿Qué ocupación y qué tarifa promedio por tipo de habitación debe esperar la cadena en cada mes de los próximos 12 meses? | BA |
| P1 | ¿Cómo han variado la ocupación y la tarifa promedio por mes y tipo de habitación en los últimos años? | BI |
| P2 | ¿Cuántos visitantes extranjeros se esperan en Cartagena en los próximos meses, por nacionalidad? | BA |
| P3 | ¿Qué temporadas dejan más ingresos por habitación disponible en cada tipo de habitación? | BI |
| P4 | ¿Cuántas habitaciones de cada hotel estarán ocupadas en cada semana de temporada alta? | BA |

---

## Arquitectura

Arquitectura de cinco capas, con gobierno y metadatos como capa transversal. Los diagramas (PNG y archivo editable de draw.io) están en [`docs/diagramas/`](docs/diagramas/).

| Capa | Componentes |
|---|---|
| 1. Fuentes | F1 Migración Colombia (CSV) · F2 DANE, EMA (Excel) · F3 reservas sintéticas (CSV) |
| 2. Integración (ETL) | Pentaho Data Integration (PDI): transformaciones `.ktr` coordinadas por el trabajo `job_carga_dw.kjb` |
| 3. Almacén de datos | MySQL 8, base `hotelera_caribe_dw`, esquema en estrella |
| 4. Usuario final | Power BI Desktop (`.pbix`) y Python (modelo predictivo) |
| 5. Gobierno y metadatos | Diccionarios de datos, reglas de limpieza, conciliación de totales, roles y permisos |

> En la Entrega 1 el almacén se había diseñado sobre PostgreSQL. Para la implementación se usó MySQL 8 por los recursos de los equipos de desarrollo y su compatibilidad con PDI. La estructura lógica del modelo no cambió.

---

## Fuentes de datos

| Fuente | Procedencia | Formato | Registros | Periodo |
|---|---|---|---|---|
| **F1.** Flujos migratorios de extranjeros (tableros) | Migración Colombia · [tableros de visualización](https://www.migracioncolombia.gov.co/planeacion-y-estadistica/observatorio-om3/datos-abiertos/tableros-de-visualizacion) | CSV (UTF-16, tabuladores) | 1.639 filas en 9 archivos | 2023–2025 |
| **F2.** Encuesta Mensual de Alojamiento (EMA) | DANE · [página de la encuesta](https://www.dane.gov.co/index.php/estadisticas-por-tema/servicios/muestra-mensual-de-hoteles-mmh) | Excel (.xlsx) | 36 observaciones mensuales de Cartagena | 2023–2025 |
| **F3.** Reservas de Hotelera Caribe S.A.S. (**sintética**) | Generada con [`datos/generador/generar_reservas.py`](datos/generador/) | CSV | 121.893 filas | 2023–2025 |

- **Alcance de F1:** extranjeros que entran o salen por el Aeropuerto Rafael Núñez de Cartagena, con el mismo filtro en los tres años. Se usa para estudiar la estacionalidad más que el volumen total de visitantes.
- **Alcance de F2:** la EMA publica la ocupación en porcentaje, pero las tarifas solo como índice (base 2019 = 100), no en pesos.
- **F3:** se calibró con la ocupación mensual de Cartagena (F2) y con la estacionalidad y los países de origen de F1. Incluye inconsistencias introducidas a propósito (formatos de fecha, duplicados, nulos, códigos de habitación y tarifas con y sin IVA), documentadas en `datos/generador/inconsistencias_introducidas.md`.
- El detalle de procedencia, fecha de descarga, licencia y pasos de cada fuente está en [`datos/descarga.md`](datos/descarga.md). Los diccionarios, en [`datos/diccionarios/`](datos/diccionarios/).

---

## Modelo dimensional

**Granularidad:** una noche de una reserva confirmada de una habitación de un tipo determinado en un hotel de la cadena, en una fecha específica.

Esquema en estrella con 9 tablas en `hotelera_caribe_dw`:

| Tabla | Tipo | Registros |
|---|---|---|
| `dim_tiempo` | Dimensión | 1.096 |
| `dim_hotel` | Dimensión | 5 |
| `dim_tipoHabitacion` | Dimensión | 3 |
| `dim_canal` | Dimensión | 5 |
| `dim_nacionalidad` | Dimensión | 195 |
| `fact_reserva_noche` | Hechos | 120.092 |
| `fact_capacidad_diaria` | Hechos | 5.475 |
| `fact_llegadas_extranjeros` | Hechos | 1.639 |
| `fact_mercado_destino` | Hechos | 36 |

`dim_tiempo` se llena con el procedimiento almacenado `LlenarDimTiempo`, que genera una fila por día entre el 1 de enero de 2023 y el 31 de diciembre de 2025.

---

## Proceso ETL (Pentaho Data Integration)

Un trabajo principal (`job_carga_dw.kjb`) coordina las transformaciones (`.ktr`) en dos fases principales, garantizando la integridad referencial y la limpieza de datos:

1. **Limpieza y Preparación:** vaciado de tablas de staging y hechos.
2. **Carga de Dimensiones:** poblamiento de `dim_tiempo`, `dim_hotel`, `dim_tipoHabitacion`, `dim_canal` y `dim_nacionalidad`.
3. **Carga de Staging y Hechos:** procesamiento del archivo fuente y carga en `fact_reserva_noche`.

Los scripts de auditoría y conciliación de fuentes están disponibles en [`dw/conciliacion/`](dw/conciliacion/).

---

## Tablero (Power BI)

El archivo `.pbix` ubicado en [`dashboard/`](dashboard/) se conecta directamente al almacén en MySQL. Incluye los indicadores clave de rendimiento (**Tasa de ocupación hotelera**, **RevPAR** e ingresos por canal de venta), dotados de filtros interactivos por tiempo, hotel y canal.

---

## Estructura del repositorio

```
bi-proyecto-equipo506241093/
├── README.md              Descripción general y guía de reproducción
├── .gitignore
├── dashboard/             Tablero de Power BI (.pbix) y capturas de páginas
├── datos/
│   ├── raw/               Fuentes originales (F1, F2) y reservas generadas (F3)
│   ├── muestras/          20 filas de muestra por fuente en CSV
│   ├── diccionarios/      Diccionarios de datos por fuente
│   ├── generador/         Script Python de generación de F3 e informe de inconsistencias
│   └── descarga.md        Guía de obtención de fuentes
├── docs/
│   ├── entregas/          PDFs correspondientes a cada entrega del proyecto
│   └── diagramas/         Arquitectura y esquemas dimensionales (PNG y draw.io)
├── dw/
│   ├── ddl/               Scripts CREATE TABLE y procedimiento LlenarDimTiempo
│   └── conciliacion/      Scripts SQL de validación y conteo por fuente
├── etl/
│   ├── transformaciones/  Archivos .ktr de Pentaho Data Integration
│   └── trabajos/          Trabajo principal .kjb de orquestación ETL
└── modelo/                Notebooks de Python para el modelo predictivo
```

---

## Cómo reproducir

**Requisitos previos:** MySQL 8, Pentaho Data Integration (PDI), Power BI Desktop y (opcional para regenerar F3) Python 3 con `numpy`, `pandas` y `openpyxl`.

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Karen-Bayona/bi-proyecto-equipo506241093.git
   cd bi-proyecto-equipo506241093
   ```

2. **(Opcional) Regenerar F3:** Con los archivos de F1 y F2 ubicados en `datos/raw/`:
   ```bash
   pip install numpy pandas openpyxl
   python datos/generador/generar_reservas.py
   ```

3. **Crear la base de datos y esquemas:** 
   * En MySQL Workbench o DBeaver, crea la base de datos con cotejamiento UTF-8:
     ```sql
     CREATE DATABASE IF NOT EXISTS hotelera_caribe_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     USE hotelera_caribe_dw;
     ```
   * Ejecuta en orden los scripts ubicados en la carpeta [`dw/ddl/`](dw/ddl/): primero las tablas dimensionales, de staging (`stg_reserva`) y de hechos (`fact_reserva_noche`), asegurándote de incluir las columnas adicionales de soporte (`estado_reserva`, `noches_fuente`, `tarifa_total`).

4. **Poblar la dimensión de tiempo:** 
   * Ejecuta el script del procedimiento almacenado `LlenarDimTiempo` (incluido en `dw/ddl/`).
   * Llámalo con el rango de fechas del proyecto ejecutando la siguiente instrucción:
     ```sql
     CALL LlenarDimTiempo('2023-01-01', '2025-12-31');
     ```

5. **Configurar y ejecutar el proceso ETL (Pentaho Data Integration):**
   * **Motor y Versión:** Pentaho Data Integration (Spoon) v9.4.0.0-343.
   * **Parámetros de conexión a MySQL:**
     * **Host:** `localhost`
     * **Puerto:** `3306`
     * **Base de datos:** `hotelera_caribe_dw`
     * **Usuario:** `root` (sin contraseñas almacenadas en los archivos de configuración).
   * **Ubicación de las fuentes:** Asegúrate de que los archivos CSV de entrada (como `F3_reservas_muestra.csv`) se encuentren accesibles en la ruta esperada por las transformaciones (por ejemplo, en la raíz del disco `C:\`).
   * **Orden de ejecución del Job maestro (`etl/trabajos/job_carga_dw.kjb`):**
     1. **`limpia_stg_y_fact`**: Ejecuta las sentencias de limpieza mediante `TRUNCATE TABLE` en las tablas de staging y hechos.
     2. **`carga_dim_tiempo`**: Llama al procedimiento almacenado para asegurar la vigencia del calendario.
     3. **Carga de Dimensiones (`tr_dim_hotel`, `tr_dim_tipo_habitacion`, `tr_dim_canal`, `tr_dim_nacionalidad`)**: Procesa y actualiza las dimensiones de forma secuencial.
     4. **Carga de Staging (`tr_stg_reserva`)**: Procesa, normaliza fechas y carga los datos crudos en la tabla de staging.
     5. **Carga de Hechos (`tr_fact_reserva_noche`)**: Realiza los cruces necesarios y carga la tabla de hechos final hasta alcanzar el nodo de **Success**.
   * Abre Pentaho Spoon, carga `job_carga_dw.kjb`, verifica la conexión y haz clic en **Run** para ejecutar el flujo completo sobre una base limpia.

6. **Validar la carga:** 
   * Ejecuta las consultas de auditoría y conteo contenidas en el script [`dw/conciliacion/conciliacion_fuentes.sql`](dw/conciliacion/) para verificar que los registros de staging coincidan de forma íntegra con las tablas dimensionales y de hechos.

7. **Explorar el tablero en Power BI:** 
   * Abre el archivo `.pbix` ubicado en la carpeta [`dashboard/`](dashboard/).
   * Apunta la fuente de datos hacia tu servidor local de MySQL (`hotelera_caribe_dw`) y haz clic en **Actualizar** para visualizar los indicadores de ocupación, RevPAR y ventas.

---

## Documentos de entrega

- **Entrega 1:** `docs/entregas/BI-Entrega-1-Equipo506241093.pdf`
- **Entrega 2:** `docs/entregas/BI-Entrega-2-Equipo506241093.pdf`
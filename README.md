# BI · Hotelera Caribe S.A.S · Proyecto final (Equipo 506241093)

Proyecto final de Business Intelligence. Diseño de un sistema de BI para **Hotelera Caribe S.A.S**, una cadena hotelera ficticia de cinco hoteles en Cartagena de Indias, construida sobre datos públicos reales del turismo colombiano. Las cifras internas de la cadena son inventadas.

| Dato | Valor |
|---|---|
| Integrantes | Laura Sofia Franco Mateus (506241128) · Karen Marcela Bayona Romero (506241093) |
| Docente | Leandro Pájaro Fuentes |
| Entrega 1 | 23/10/2026 · Diagnóstico, estrategia y diseño |

## Problema

Cada hotel registra las reservas con formatos distintos, calcula la ocupación y la tarifa promedio con definiciones diferentes y guarda el histórico en archivos dispersos. Un analista consolida los informes a mano en unos cinco días hábiles, por lo que el gerente general no tiene evidencia para fijar tarifas por tipo de habitación ni la contratación de temporales con 4 a 6 meses de antelación.

**Pregunta principal (P0):** ¿qué ocupación y qué tarifa promedio por tipo de habitación debe esperar la cadena en cada mes de los próximos 12 meses?

## Resumen de la solución

- **Madurez (BIMM):** fase actual 2 (datos accesibles sin BI); fase objetivo 5 (crecimiento del DW y reporting formal).
- **Arquitectura de cinco capas:** fuentes → ETL con Pentaho PDI → Data Warehouse en PostgreSQL → Python (modelo predictivo) y Power BI (dashboard) → Gerente General, con gobierno de datos y metadatos como capa transversal.
- **Modelo dimensional:** constelación de hechos. Una fila de `fact_reserva_noche` representa una noche de una reserva confirmada de una habitación de un tipo en un hotel, en una fecha. Dimensiones: tiempo, hotel, tipo de habitación, canal y nacionalidad. Hechos adicionales: `fact_capacidad_diaria`, `fact_llegadas_extranjeros` y `fact_mercado_destino`.

## Fuentes de datos

| Fuente | Descripción | Formato |
|---|---|---|
| F1 | Migración Colombia: flujos migratorios de extranjeros, tableros 2023-2025 (9 archivos) | CSV |
| F2 | DANE: Encuesta Mensual de Alojamiento (EMA), 2023-2025 | Excel (.xlsx) |
| F3 | Reservas de Hotelera Caribe S.A.S. (sintética, 121.893 registros, sin datos personales) | CSV |

## Estructura del repositorio

```
.
├── README.md
├── docs/
│   ├── BI-Entrega-1-Equipo506241093.pdf     # documento de la Entrega 1
│   └── diagramas/
│       ├── arquitectura.png                  # diagrama de cinco capas
│       ├── arquitectura.drawio               # editable (draw.io)
│       ├── esquema_dimensional.png           # modelo dimensional
│       └── esquema_dimensional.drawio        # editable (draw.io)
└── datos/
    ├── raw/                                  # F1, F2 y F3 originales
    ├── generador/
    │   ├── generar_reservas.py               # script que genera F3
    │   └── inconsistencias_introducidas.md   # problemas de calidad introducidos a propósito
    ├── muestras/                             # muestra de 20 filas por fuente
    └── diccionarios/                         # diccionario de datos por fuente (Anexo A)
```

Las carpetas `dw/ddl` (scripts `CREATE TABLE`), `dashboard/` (archivo `.pbix`) y `modelo/` (notebooks de Python) se crearán en las siguientes entregas, cuando se construya el DW, el dashboard y el modelo predictivo.

## Cómo regenerar F3

Desde la raíz del repositorio:

```bash
pip install numpy pandas openpyxl
python datos/generador/generar_reservas.py
```

El script lee, desde `datos/raw/`, el anexo de la EMA (`anex-EMA-*.xlsx`) y los CSV de Migración Colombia (comportamiento mensual y país de nacionalidad), y escribe `datos/raw/F3_reservas_hotelera_caribe.csv`, la muestra en `datos/muestras/` y el informe de inconsistencias en `datos/generador/`. Usa una semilla fija, por lo que el resultado es reproducible.

## Licencias y uso

- F1 y F2: información pública del Estado colombiano (Migración Colombia y DANE), de libre consulta y uso académico.
- F3: datos ficticios generados por el equipo, sin personas reales. Uso académico.

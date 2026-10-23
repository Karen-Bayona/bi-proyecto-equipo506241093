# F3 - Inconsistencias introducidas a proposito (datos SINTETICOS)

Reservas generadas: 121,893 filas (incluye 1,801 duplicados). Periodo: 2023-01-01 a 2025-12-31. Semilla: 42.

## 1. Formatos de fecha distintos por zona
Centro Historico y Getsemani: dd/mm/aaaa. Bocagrande: mm-dd-aaaa.
```
id_reserva hotel fecha_reserva fecha_entrada
RES-000001    H1    18/12/2022    01/01/2023
RES-000002    H1    31/12/2022    01/01/2023
RES-000003    H1    09/09/2022    01/01/2023
RES-000004    H1    14/11/2022    01/01/2023
```

## 2. Identificadores duplicados
1,801 filas repetidas exactamente.
```
id_reserva hotel fecha_entrada  tarifa_noche
RES-000087    H4    01-01-2023        504000
RES-000087    H4    01-01-2023        504000
RES-000155    H2    02/01/2023        351000
RES-000155    H2    02/01/2023        351000
```

## 3. Valores nulos
canal: 4,804; nacionalidad: 7,206; num_huespedes: 2,402.
```
id_reserva hotel canal nacionalidad
RES-000004    H1  None       Brasil
RES-000015    H1  None     Colombia
RES-000062    H4  None     Colombia
```

## 4. Codigos de tipo de habitacion inconsistentes
Valores distintos para el mismo tipo: Estándar, STD, SUITE, SUP, Standard, Suite, Superior, estandar, ste, suite, sup., superior.

## 5. Tarifa con y sin IVA (sin columna que lo indique)
Bocagrande (H4, H5) incluye IVA 19 %; Centro y Getsemani (H1-H3) no. Promedio de tarifa_noche por hotel:
```
hotel
H1    454471
H2    433195
H3    438430
H4    407306
H5    391575
```

## Calibracion con la EMA (ocupacion mensual de Cartagena)
```
    mes  ocupacion_cadena_%  ocupacion_EMA_Cartagena_%  diferencia
2023-01                74.9                       76.0        -1.1
2023-02                73.6                       73.7        -0.1
2023-03                72.5                       70.1         2.4
2023-04                62.5                       63.0        -0.5
2023-05                62.0                       61.0         1.0
2023-06                65.7                       66.5        -0.8
2023-07                74.0                       73.2         0.8
2023-08                70.5                       71.8        -1.3
2023-09                65.7                       64.2         1.5
2023-10                59.2                       58.9         0.3
2023-11                67.4                       67.8        -0.4
2023-12                65.0                       65.0         0.0
2024-01                69.2                       70.7        -1.5
2024-02                70.1                       70.2        -0.1
2024-03                66.7                       67.7        -1.0
2024-04                60.8                       61.9        -1.1
2024-05                60.8                       59.8         1.0
2024-06                65.3                       63.6         1.7
2024-07                64.8                       66.4        -1.6
2024-08                69.4                       70.1        -0.7
2024-09                64.0                       64.0         0.0
2024-10                63.1                       63.1         0.0
2024-11                68.0                       69.0        -1.0
2024-12                65.9                       66.0        -0.1
2025-01                74.4                       74.0         0.4
2025-02                73.0                       70.7         2.3
2025-03                66.3                       66.9        -0.6
2025-04                59.9                       59.9         0.0
2025-05                55.7                       56.6        -0.9
2025-06                63.5                       63.5         0.0
2025-07                66.7                       67.4        -0.7
2025-08                69.7                       68.6         1.1
2025-09                63.5                       64.5        -1.0
2025-10                64.0                       63.6         0.4
2025-11                70.3                       67.9         2.4
2025-12                67.0                       67.0         0.0
```
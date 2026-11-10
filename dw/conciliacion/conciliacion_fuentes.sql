-- =====================================================================
-- Proyecto: Hotelera Caribe DW
-- Script de Conciliación de Fuentes (CO1 a CO3)
-- Descripción: Valida el conteo de registros y la integridad entre las
--              fuentes de Staging y las tablas del Modelo Dimensional.
-- =====================================================================

USE hotelera_caribe_dw;

-- ---------------------------------------------------------------------
-- 1. Conciliación General de Staging vs Hechos (Reservas y Ocupación)
-- ---------------------------------------------------------------------
SELECT 
    'Tabla Staging vs Hechos' AS Tipo_Validacion,
    (SELECT COUNT(*) FROM stg_reserva) AS Registros_Staging,
    (SELECT COUNT(*) FROM fact_reserva_noche) AS Registros_Fact_Reserva,
    ((SELECT COUNT(*) FROM stg_reserva) - (SELECT COUNT(*) FROM fact_reserva_noche)) AS Diferencia;

-- ---------------------------------------------------------------------
-- 2. Conciliación desglosada por Fuentes (CO1, CO2, CO3) en Staging
-- ---------------------------------------------------------------------
SELECT 
    fuente AS Fuente_Datos,
    COUNT(*) AS Total_Registros_Staging
FROM stg_reserva
GROUP BY fuente;

-- ---------------------------------------------------------------------
-- 3. Validación de Dimensiones Principales cargadas
-- ---------------------------------------------------------------------
SELECT 'dim_hotel' AS Dimension, COUNT(*) AS Total FROM dim_hotel
UNION ALL
SELECT 'dim_canal' AS Dimension, COUNT(*) AS Total FROM dim_canal
UNION ALL
SELECT 'dim_nacionalidad' AS Dimension, COUNT(*) AS Total FROM dim_nacionalidad
UNION ALL
SELECT 'dim_tipohabitacion' AS Dimension, COUNT(*) AS Total FROM dim_tipohabitacion
UNION ALL
SELECT 'dim_tiempo' AS Dimension, COUNT(*) AS Total FROM dim_tiempo;

-- ---------------------------------------------------------------------
-- 4. Control Financiero (Suma de ingresos en la tabla de hechos)
-- ---------------------------------------------------------------------
SELECT 
    'Control Financiero - Ingresos Totales' AS Métrica,
    SUM(ingreso_noche) AS Total_Ingresos_Fact
FROM fact_reserva_noche;
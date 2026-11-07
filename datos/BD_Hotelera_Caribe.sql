USE hotelera_caribe_dw;

-- 1. Eliminar el procedimiento si ya existía previamente para evitar conflictos
DROP PROCEDURE IF EXISTS LlenarDimTiempo;

-- 2. Crear el procedimiento almacenado para generar las fechas
DELIMITER $$

CREATE PROCEDURE LlenarDimTiempo(IN fecha_inicio DATE, IN fecha_fin DATE)
BEGIN
    DECLARE fecha_actual DATE;
    SET fecha_actual = fecha_inicio;
    
    WHILE fecha_actual <= fecha_fin DO
        INSERT IGNORE INTO dim_tiempo (id_tiempo, fecha, dia_semana, semana, mes, trimestre, anio, temporada, es_festivo)
        VALUES (
            DATE_FORMAT(fecha_actual, '%Y%m%d'),
            fecha_actual,
            CASE DAYOFWEEK(fecha_actual)
                WHEN 1 THEN 'Domingo'
                WHEN 2 THEN 'Lunes'
                WHEN 3 THEN 'Martes'
                WHEN 4 THEN 'Miércoles'
                WHEN 5 THEN 'Jueves'
                WHEN 6 THEN 'Viernes'
                WHEN 7 THEN 'Sábado'
            END,
            WEEK(fecha_actual, 1),
            MONTH(fecha_actual),
            QUARTER(fecha_actual),
            YEAR(fecha_actual),
            CASE 
                WHEN MONTH(fecha_actual) IN (6, 7, 12) THEN 'Alta'
                WHEN MONTH(fecha_actual) IN (1, 4, 10) THEN 'Media'
                ELSE 'Baja'
            END,
            FALSE
        );
        SET fecha_actual = DATE_ADD(fecha_actual, INTERVAL 1 DAY);
    END WHILE;
END$$

DELIMITER ;

-- 3. Ejecutar el procedimiento para poblar desde el 2023 hasta el 2025
CALL LlenarDimTiempo('2023-01-01', '2025-12-31');
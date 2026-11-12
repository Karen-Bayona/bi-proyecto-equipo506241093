-- Extracción de datos para el modelo predictivo de Business Analytics (Entrega 3)
-- Hotelera Caribe S.A.S. - Predicción de volumen de noches ocupadas por hotel, tipo de habitación y mes
SELECT 
    t.anio,
    t.mes,
    h.nombre_hotel AS sede_hotel,
    th.nombre_tipo AS tipo_habitacion,
    SUM(f.noches) AS total_noches_ocupadas,
    AVG(f.tarifa_noche) AS tarifa_promedio_adr,
    SUM(f.ingreso_noche) AS ingresos_totales,
    SUM(f.num_huespedes) AS total_huespedes
FROM 
    fact_reserva_noche f
JOIN 
    dim_tiempo t ON f.id_tiempo = t.id_tiempo
JOIN 
    dim_hotel h ON f.id_hotel = h.id_hotel
JOIN 
    dim_tipohabitacion th ON f.id_tipo_habitacion = th.id_tipo_habitacion
GROUP BY 
    t.anio, t.mes, h.nombre_hotel, th.nombre_tipo
ORDER BY 
    t.anio ASC, t.mes ASC, h.nombre_hotel ASC;
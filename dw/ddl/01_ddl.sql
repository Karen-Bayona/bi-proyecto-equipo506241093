
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `hotelera_caribe_dw`
--
CREATE DATABASE IF NOT EXISTS hotelera_caribe_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hotelera_caribe_dw;
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dim_canal`
--

CREATE TABLE `dim_canal` (
  `id_canal` int(11) NOT NULL,
  `codigo_canal` varchar(30) NOT NULL,
  `nombre_canal` varchar(60) NOT NULL,
  `tipo_canal` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `dim_canal`
--

INSERT INTO `dim_canal` (`id_canal`, `codigo_canal`, `nombre_canal`, `tipo_canal`) VALUES
(-1, 'N/D', 'Desconocido', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dim_hotel`
--

CREATE TABLE `dim_hotel` (
  `id_hotel` int(11) NOT NULL,
  `codigo_hotel` varchar(30) NOT NULL,
  `nombre_hotel` varchar(100) NOT NULL,
  `ciudad` varchar(60) DEFAULT NULL,
  `categoria` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `dim_hotel`
--

INSERT INTO `dim_hotel` (`id_hotel`, `codigo_hotel`, `nombre_hotel`, `ciudad`, `categoria`) VALUES
(-1, 'N/D', 'Desconocido', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dim_nacionalidad`
--

CREATE TABLE `dim_nacionalidad` (
  `id_nacionalidad` int(11) NOT NULL,
  `codigo_pais` varchar(10) NOT NULL,
  `pais` varchar(80) NOT NULL,
  `region` varchar(40) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `dim_nacionalidad`
--

INSERT INTO `dim_nacionalidad` (`id_nacionalidad`, `codigo_pais`, `pais`, `region`) VALUES
(-1, 'N/D', 'Desconocido', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dim_tiempo`
--

CREATE TABLE `dim_tiempo` (
  `id_tiempo` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `dia_semana` varchar(10) NOT NULL,
  `semana` tinyint(4) NOT NULL,
  `mes` tinyint(4) NOT NULL,
  `trimestre` tinyint(4) NOT NULL,
  `anio` smallint(6) NOT NULL,
  `temporada` varchar(10) NOT NULL,
  `es_festivo` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `dim_tiempo`
--

INSERT INTO `dim_tiempo` (`id_tiempo`, `fecha`, `dia_semana`, `semana`, `mes`, `trimestre`, `anio`, `temporada`, `es_festivo`) VALUES
(19000101, '1900-01-01', 'Desconocid', 0, 0, 0, 1900, 'Baja', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dim_tipohabitacion`
--

CREATE TABLE `dim_tipohabitacion` (
  `id_tipo_habitacion` int(11) NOT NULL,
  `codigo_tipo` varchar(30) NOT NULL,
  `nombre_tipo` varchar(60) NOT NULL,
  `capacidad` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `dim_tipohabitacion`
--

INSERT INTO `dim_tipohabitacion` (`id_tipo_habitacion`, `codigo_tipo`, `nombre_tipo`, `capacidad`) VALUES
(-1, 'N/D', 'Desconocido', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `fact_reserva_noche`
--

CREATE TABLE `fact_reserva_noche` (
  `id_hecho` bigint(20) NOT NULL,
  `id_tiempo` int(11) NOT NULL,
  `id_hotel` int(11) NOT NULL,
  `id_tipo_habitacion` int(11) NOT NULL,
  `id_canal` int(11) NOT NULL,
  `id_nacionalidad` int(11) NOT NULL,
  `id_reserva` varchar(40) NOT NULL,
  `tarifa_noche` decimal(12,2) DEFAULT NULL,
  `ingreso_noche` decimal(12,2) DEFAULT NULL,
  `num_huespedes` tinyint(4) DEFAULT NULL,
  `noches` tinyint(4) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `stg_reserva`
--

CREATE TABLE `stg_reserva` (
  `id_stg` bigint(20) NOT NULL,
  `fuente` varchar(20) NOT NULL,
  `id_reserva` varchar(40) DEFAULT NULL,
  `codigo_hotel` varchar(30) DEFAULT NULL,
  `codigo_tipo` varchar(30) DEFAULT NULL,
  `codigo_canal` varchar(30) DEFAULT NULL,
  `codigo_pais` varchar(10) DEFAULT NULL,
  `fecha_llegada` date DEFAULT NULL,
  `fecha_salida` date DEFAULT NULL,
  `tarifa_noche` decimal(12,2) DEFAULT NULL,
  `num_huespedes` tinyint(4) DEFAULT NULL,
  `estado` varchar(12) NOT NULL,
  `motivo` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `dim_canal`
--
ALTER TABLE `dim_canal`
  ADD PRIMARY KEY (`id_canal`),
  ADD UNIQUE KEY `codigo_canal` (`codigo_canal`);

--
-- Indices de la tabla `dim_hotel`
--
ALTER TABLE `dim_hotel`
  ADD PRIMARY KEY (`id_hotel`),
  ADD UNIQUE KEY `codigo_hotel` (`codigo_hotel`);

--
-- Indices de la tabla `dim_nacionalidad`
--
ALTER TABLE `dim_nacionalidad`
  ADD PRIMARY KEY (`id_nacionalidad`),
  ADD UNIQUE KEY `codigo_pais` (`codigo_pais`);

--
-- Indices de la tabla `dim_tiempo`
--
ALTER TABLE `dim_tiempo`
  ADD PRIMARY KEY (`id_tiempo`),
  ADD UNIQUE KEY `fecha` (`fecha`);

--
-- Indices de la tabla `dim_tipohabitacion`
--
ALTER TABLE `dim_tipohabitacion`
  ADD PRIMARY KEY (`id_tipo_habitacion`),
  ADD UNIQUE KEY `codigo_tipo` (`codigo_tipo`);

--
-- Indices de la tabla `fact_reserva_noche`
--
ALTER TABLE `fact_reserva_noche`
  ADD PRIMARY KEY (`id_hecho`),
  ADD KEY `fk_f_tiempo` (`id_tiempo`),
  ADD KEY `fk_f_hotel` (`id_hotel`),
  ADD KEY `fk_f_tipo` (`id_tipo_habitacion`),
  ADD KEY `fk_f_canal` (`id_canal`),
  ADD KEY `fk_f_nac` (`id_nacionalidad`);

--
-- Indices de la tabla `stg_reserva`
--
ALTER TABLE `stg_reserva`
  ADD PRIMARY KEY (`id_stg`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `dim_canal`
--
ALTER TABLE `dim_canal`
  MODIFY `id_canal` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `dim_hotel`
--
ALTER TABLE `dim_hotel`
  MODIFY `id_hotel` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `dim_nacionalidad`
--
ALTER TABLE `dim_nacionalidad`
  MODIFY `id_nacionalidad` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `dim_tipohabitacion`
--
ALTER TABLE `dim_tipohabitacion`
  MODIFY `id_tipo_habitacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `fact_reserva_noche`
--
ALTER TABLE `fact_reserva_noche`
  MODIFY `id_hecho` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `stg_reserva`
--
ALTER TABLE `stg_reserva`
  MODIFY `id_stg` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `fact_reserva_noche`
--
ALTER TABLE `fact_reserva_noche`
  ADD CONSTRAINT `fk_f_canal` FOREIGN KEY (`id_canal`) REFERENCES `dim_canal` (`id_canal`),
  ADD CONSTRAINT `fk_f_hotel` FOREIGN KEY (`id_hotel`) REFERENCES `dim_hotel` (`id_hotel`),
  ADD CONSTRAINT `fk_f_nac` FOREIGN KEY (`id_nacionalidad`) REFERENCES `dim_nacionalidad` (`id_nacionalidad`),
  ADD CONSTRAINT `fk_f_tiempo` FOREIGN KEY (`id_tiempo`) REFERENCES `dim_tiempo` (`id_tiempo`),
  ADD CONSTRAINT `fk_f_tipo` FOREIGN KEY (`id_tipo_habitacion`) REFERENCES `dim_tipohabitacion` (`id_tipo_habitacion`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

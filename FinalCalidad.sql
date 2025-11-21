-- --------------------------------------------------------
-- Host:                         localhost
-- Versión del servidor:         8.0.43 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.12.0.7122
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para bd_hotel_san_eduardo
CREATE DATABASE IF NOT EXISTS `bd_hotel_san_eduardo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `bd_hotel_san_eduardo`;

-- Volcando estructura para tabla bd_hotel_san_eduardo.actividad
CREATE TABLE IF NOT EXISTS `actividad` (
  `id_actividad` int NOT NULL AUTO_INCREMENT,
  `accion` varchar(50) NOT NULL,
  `id_reserva` int DEFAULT NULL,
  `id_habitacion` int DEFAULT NULL,
  `nuevo_estado_hab` varchar(50) DEFAULT NULL,
  `fecha_hora` datetime NOT NULL,
  PRIMARY KEY (`id_actividad`),
  KEY `fk_actividad_reserva` (`id_reserva`),
  KEY `fk_actividad_habitacion` (`id_habitacion`),
  CONSTRAINT `fk_actividad_habitacion` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`) ON DELETE SET NULL,
  CONSTRAINT `fk_actividad_reserva` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.actividad: ~19 rows (aproximadamente)
INSERT INTO `actividad` (`id_actividad`, `accion`, `id_reserva`, `id_habitacion`, `nuevo_estado_hab`, `fecha_hora`) VALUES
	(1, 'Check-in', NULL, NULL, 'Ocupada', '2025-10-21 01:08:45'),
	(2, 'Check-out', NULL, NULL, 'En Limpieza', '2025-10-21 01:08:52'),
	(3, 'Check-in', NULL, NULL, 'Ocupada', '2025-10-31 08:21:57'),
	(4, 'Check-out', NULL, NULL, 'En Limpieza', '2025-10-31 08:26:01'),
	(5, 'Limpieza OK', NULL, NULL, 'Disponible', '2025-10-31 08:27:19'),
	(6, 'Limpieza OK', NULL, NULL, 'Disponible', '2025-10-31 08:27:23'),
	(7, 'Check-in', NULL, NULL, 'Ocupada', '2025-10-31 08:27:30'),
	(8, 'Check-in', NULL, NULL, 'Ocupada', '2025-11-04 09:54:13'),
	(9, 'Check-out', NULL, NULL, 'En Limpieza', '2025-11-04 09:54:33'),
	(10, 'Limpieza OK', NULL, NULL, 'Disponible', '2025-11-04 09:56:53'),
	(11, 'Check-in', NULL, NULL, 'Ocupada', '2025-11-07 02:16:29'),
	(12, 'Check-out', NULL, NULL, 'En Limpieza', '2025-11-07 02:16:45'),
	(13, 'Limpieza OK', NULL, NULL, 'Disponible', '2025-11-07 02:16:54'),
	(14, 'Check-in', NULL, NULL, 'Ocupada', '2025-11-11 11:49:06'),
	(15, 'Check-out', NULL, NULL, 'En Limpieza', '2025-11-11 11:49:10'),
	(16, 'Limpieza OK', NULL, NULL, 'Disponible', '2025-11-11 11:49:37'),
	(17, 'Check-in', NULL, NULL, 'Ocupada', '2025-11-21 00:00:57'),
	(18, 'Check-out', NULL, NULL, 'En Limpieza', '2025-11-21 00:01:13'),
	(19, 'Check-in', 87, 16, 'Ocupada', '2025-11-21 01:46:18');

-- Volcando estructura para tabla bd_hotel_san_eduardo.check_in
CREATE TABLE IF NOT EXISTS `check_in` (
  `id_checkin` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  PRIMARY KEY (`id_checkin`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `check_in_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.check_in: ~1 rows (aproximadamente)
INSERT INTO `check_in` (`id_checkin`, `id_reserva`, `fecha`, `hora`) VALUES
	(2, 87, '2025-11-21', '01:46:18');

-- Volcando estructura para tabla bd_hotel_san_eduardo.check_out
CREATE TABLE IF NOT EXISTS `check_out` (
  `id_checkout` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `total_factura` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_checkout`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `check_out_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.check_out: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.clientes
CREATE TABLE IF NOT EXISTS `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `tipo_documento` enum('DNI','Pasaporte','CE') NOT NULL DEFAULT 'DNI',
  `num_documento` varchar(20) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `nacionalidad` varchar(60) DEFAULT 'Perú',
  `direccion` varchar(150) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `num_documento` (`num_documento`),
  UNIQUE KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `fk_cliente_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3412 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.clientes: ~9 rows (aproximadamente)
INSERT INTO `clientes` (`id_cliente`, `tipo_documento`, `num_documento`, `nombres`, `apellidos`, `nacionalidad`, `direccion`, `telefono`, `correo`, `id_usuario`) VALUES
	(1, 'CE', '66666666666666666666', 'Anghelo Jamir', 'Merino Mayra', 'Pakistán', 'Husares de Junin 868', '+51942030088', 'jamir_anghelo@hotmail.com', 1),
	(2, 'Pasaporte', '111111111111', 'Jamir', 'Casa', 'España', 'Carlos Castañeda 637', '+1111111111111', 'jamir@lsp.com', 3),
	(3, 'CE', '111111112', 'LILIANA', 'MAYRA', 'Estados Unidos', 'Carlos Castañeda 637', '+1111111111111111', 'lorena@lsp.com', 4),
	(4, 'CE', '123456789', 'Jose', 'Fiestas', 'Venezuela', 'San Pucta 123', '+58123456789', 'josefiestas@gmail.com', 5),
	(5, 'DNI', '16712223', 'Lorena', 'Merino', 'Perú', 'Carlos Castañeda 637', '+51971868785', 'lorena_yjl@hotmail.com', 6),
	(6, 'DNI', '72318704', 'Jamir', 'Merino Mayra', 'Perú', 'Carlos Castañeda 640', '+51942030088', 'jamir@gmail.com', 7),
	(7, 'DNI', '72318705', 'Jamir', 'Merino Mayra', 'España', 'Husares de Junin 868', '+51942030088', 'jamir_merino@hotmail.com', 8),
	(8, 'DNI', '72318703', 'Isis', 'Dulcemaria', 'Perú', '', '', '', 9),
	(9, 'DNI', '73242600', 'Maguiña', 'sanchez rosmer', 'Perú', NULL, NULL, NULL, NULL);

-- Volcando estructura para tabla bd_hotel_san_eduardo.contenido_dinamico
CREATE TABLE IF NOT EXISTS `contenido_dinamico` (
  `id_contenido` int NOT NULL AUTO_INCREMENT,
  `clave` varchar(50) NOT NULL,
  `titulo` varchar(255) DEFAULT NULL,
  `contenido` text,
  `ultima_modificacion` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_contenido`),
  UNIQUE KEY `clave` (`clave`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.contenido_dinamico: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.facturacion
CREATE TABLE IF NOT EXISTS `facturacion` (
  `id_factura` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `id_tipo_pago` int NOT NULL,
  `id_usuario` int DEFAULT NULL,
  `fecha_emision` date NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `estado` varchar(30) DEFAULT 'Pagado',
  `comprobante_pago` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_factura`),
  KEY `id_reserva` (`id_reserva`),
  KEY `id_tipo_pago` (`id_tipo_pago`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `facturacion_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`),
  CONSTRAINT `facturacion_ibfk_2` FOREIGN KEY (`id_tipo_pago`) REFERENCES `tipo_pago` (`id_tipo_pago`),
  CONSTRAINT `facturacion_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.facturacion: ~1 rows (aproximadamente)
INSERT INTO `facturacion` (`id_factura`, `id_reserva`, `id_tipo_pago`, `id_usuario`, `fecha_emision`, `total`, `estado`, `comprobante_pago`) VALUES
	(53, 87, 2, 7, '2025-11-21', 480.00, 'Pagado', NULL);

-- Volcando estructura para tabla bd_hotel_san_eduardo.habitaciones
CREATE TABLE IF NOT EXISTS `habitaciones` (
  `id_habitacion` int NOT NULL AUTO_INCREMENT,
  `numero` varchar(20) NOT NULL,
  `id_tipo` int NOT NULL,
  `estado` varchar(30) DEFAULT 'Disponible',
  `imagen` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_habitacion`),
  UNIQUE KEY `numero` (`numero`),
  KEY `id_tipo` (`id_tipo`),
  CONSTRAINT `habitaciones_ibfk_1` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_habitacion` (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.habitaciones: ~9 rows (aproximadamente)
INSERT INTO `habitaciones` (`id_habitacion`, `numero`, `id_tipo`, `estado`, `imagen`) VALUES
	(15, '101', 9, 'Disponible', 'img/habitaciones/h1individual.jpg'),
	(16, '201', 2, 'Ocupada', 'img/habitaciones/habitaciondoble.jpg'),
	(17, '301', 1, 'Disponible', 'img/habitaciones/hestandar.jpg'),
	(18, '401', 3, 'Disponible', 'img/habitaciones/familiar.jpg'),
	(19, '501', 5, 'Disponible', 'img/habitaciones/dobledoscamas.jpg'),
	(20, '601', 7, 'Disponible', 'img/habitaciones/dobleestanjdar.jpg'),
	(21, '701', 4, 'Disponible', 'img/habitaciones/estandar.jpg'),
	(22, '801', 6, 'Disponible', 'img/habitaciones/triple.png'),
	(23, '901', 8, 'Disponible', 'img/habitaciones/suite.jpg');

-- Volcando estructura para tabla bd_hotel_san_eduardo.historial_notificaciones
CREATE TABLE IF NOT EXISTS `historial_notificaciones` (
  `id_notificacion` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `tipo` varchar(50) NOT NULL,
  `correo_destino` varchar(150) NOT NULL,
  `asunto` varchar(150) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_envio` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_notificacion`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `historial_notificaciones_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.historial_notificaciones: ~33 rows (aproximadamente)
INSERT INTO `historial_notificaciones` (`id_notificacion`, `id_usuario`, `tipo`, `correo_destino`, `asunto`, `estado`, `fecha_envio`) VALUES
	(1, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmacion - Hotel San Eduardo', 'Enviado', '2025-10-21 01:39:06'),
	(2, 6, 'confirmacion', 'jamir.merino.17@hotmail.com', 'Confirmación de Reserva #3 • Hotel San Eduardo', 'Enviado', '2025-10-21 01:40:15'),
	(3, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #3 • Hotel San Eduardo', 'Enviado', '2025-10-21 01:40:17'),
	(4, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #4 • Hotel San Eduardo', 'Enviado', '2025-10-31 08:19:40'),
	(5, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #5 • Hotel San Eduardo', 'Enviado', '2025-11-04 09:50:13'),
	(6, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #6 • Hotel San Eduardo', 'Enviado', '2025-11-04 11:43:41'),
	(7, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #7 • Hotel San Eduardo', 'Enviado', '2025-11-06 00:51:45'),
	(8, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #8 • Hotel San Eduardo', 'Enviado', '2025-11-06 16:04:17'),
	(9, 6, 'confirmacion', 'anghelojamircko@hotmail.com', 'Confirmación de Reserva #8 • Hotel San Eduardo', 'Enviado', '2025-11-06 16:04:20'),
	(10, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #11 • Hotel San Eduardo', 'Enviado', '2025-11-06 21:01:03'),
	(11, 6, 'confirmacion', 'lorena_yjl@hotmail.com', 'Confirmación de Reserva #24 • Hotel San Eduardo', 'Enviado', '2025-11-06 22:07:31'),
	(12, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #36 • Hotel San Eduardo', 'Enviado', '2025-11-07 21:44:33'),
	(13, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #36 • Hotel San Eduardo', 'Enviado', '2025-11-07 22:38:25'),
	(14, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #36 • Hotel San Eduardo', 'Enviado', '2025-11-07 22:40:02'),
	(15, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #38 • Hotel San Eduardo', 'Enviado', '2025-11-07 23:18:00'),
	(16, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #40 • Hotel San Eduardo', 'Enviado', '2025-11-07 23:25:29'),
	(17, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #39 • Hotel San Eduardo', 'Enviado', '2025-11-07 23:28:12'),
	(18, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #42 • Hotel San Eduardo', 'Enviado', '2025-11-08 00:04:53'),
	(19, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva de Servicios #43 • Hotel San Eduardo', 'Enviado', '2025-11-08 00:13:40'),
	(20, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva de Servicios #44 • Hotel San Eduardo', 'Enviado', '2025-11-08 00:19:41'),
	(21, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #45 • Hotel San Eduardo', 'Enviado', '2025-11-08 00:41:17'),
	(22, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #46 • Hotel San Eduardo', 'Enviado', '2025-11-08 00:45:40'),
	(23, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #47 • Hotel San Eduardo', 'Enviado', '2025-11-08 00:47:59'),
	(24, 8, 'cancelacion', 'jamir_merino@hotmail.com', 'Cancelación de reserva #47 • Hotel San Eduardo', 'Enviado', '2025-11-08 00:48:27'),
	(25, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #48 • Hotel San Eduardo', 'Enviado', '2025-11-09 23:23:59'),
	(26, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #49 • Hotel San Eduardo', 'Enviado', '2025-11-13 21:49:27'),
	(27, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #49 • Hotel San Eduardo', 'Enviado', '2025-11-18 23:23:03'),
	(28, 8, 'cancelacion', 'jamir_merino@hotmail.com', 'Cancelación de reserva #49 • Hotel San Eduardo', 'Enviado', '2025-11-19 00:21:13'),
	(29, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #50 • Hotel San Eduardo', 'Enviado', '2025-11-20 23:44:48'),
	(30, 8, 'confirmacion', 'jamir_merino@hotmail.com', 'Confirmación de Reserva #51 • Hotel San Eduardo', 'Enviado', '2025-11-20 23:46:18'),
	(31, 7, 'confirmacion', 'jamir@gmail.com', 'Confirmación de Reserva #85 • Hotel San Eduardo', 'Enviado', '2025-11-21 01:03:54'),
	(32, 7, 'confirmacion', 'jamir@gmail.com', 'Confirmación de Reserva #86 • Hotel San Eduardo', 'Enviado', '2025-11-21 01:07:20'),
	(33, 7, 'confirmacion', 'jamir@gmail.com', 'Confirmación de Reserva #87 • Hotel San Eduardo', 'Enviado', '2025-11-21 01:45:08');

-- Volcando estructura para tabla bd_hotel_san_eduardo.imagenes_habitacion
CREATE TABLE IF NOT EXISTS `imagenes_habitacion` (
  `id_imagen` int NOT NULL AUTO_INCREMENT,
  `id_habitacion` int NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  PRIMARY KEY (`id_imagen`),
  KEY `id_habitacion` (`id_habitacion`),
  CONSTRAINT `imagenes_habitacion_ibfk_1` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.imagenes_habitacion: ~10 rows (aproximadamente)
INSERT INTO `imagenes_habitacion` (`id_imagen`, `id_habitacion`, `ruta_imagen`) VALUES
	(41, 15, 'img/habitaciones/h1individual.jpg'),
	(42, 16, 'img/habitaciones/habitaciondoble.jpg'),
	(43, 17, 'img/habitaciones/hestandar.jpg'),
	(44, 16, 'img/habitaciones/habitaciondoble.jpg'),
	(45, 18, 'img/habitaciones/familiar.jpg'),
	(46, 19, 'img/habitaciones/dobledoscamas.jpg'),
	(47, 20, 'img/habitaciones/dobleestanjdar.jpg'),
	(48, 21, 'img/habitaciones/estandar.jpg'),
	(51, 22, 'img/habitaciones/triple.png'),
	(52, 23, 'img/habitaciones/suite.jpg');

-- Volcando estructura para tabla bd_hotel_san_eduardo.incidencias
CREATE TABLE IF NOT EXISTS `incidencias` (
  `id_incidencia` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int DEFAULT NULL,
  `id_habitacion` int DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  `descripcion` text NOT NULL,
  `fecha_reporte` datetime DEFAULT CURRENT_TIMESTAMP,
  `prioridad` enum('Baja','Media','Alta') DEFAULT 'Media',
  `estado` enum('Pendiente','En proceso','Resuelta') DEFAULT 'Pendiente',
  PRIMARY KEY (`id_incidencia`),
  KEY `id_reserva` (`id_reserva`),
  KEY `id_habitacion` (`id_habitacion`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `incidencias_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`),
  CONSTRAINT `incidencias_ibfk_2` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`),
  CONSTRAINT `incidencias_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.incidencias: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.mensajes_contacto
CREATE TABLE IF NOT EXISTS `mensajes_contacto` (
  `id_mensaje` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `mensaje` text NOT NULL,
  `fecha_envio` datetime DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('Pendiente','Leído','Respondido') DEFAULT 'Pendiente',
  PRIMARY KEY (`id_mensaje`)
) ENGINE=InnoDB AUTO_INCREMENT=3372 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.mensajes_contacto: ~1 rows (aproximadamente)
INSERT INTO `mensajes_contacto` (`id_mensaje`, `nombre`, `correo`, `mensaje`, `fecha_envio`, `estado`) VALUES
	(1, 'Jamir Merino', 'jamir_merino@hotmail.com', 'hola me gusta la pagina', '2025-11-07 11:20:53', 'Pendiente');

-- Volcando estructura para tabla bd_hotel_san_eduardo.promociones
CREATE TABLE IF NOT EXISTS `promociones` (
  `id_promocion` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `tipo_descuento` enum('Porcentaje','Monto fijo') DEFAULT 'Porcentaje',
  `valor_descuento` decimal(10,2) NOT NULL,
  `estado` enum('Activa','Inactiva') DEFAULT 'Activa',
  PRIMARY KEY (`id_promocion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.promociones: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.promocion_habitacion
CREATE TABLE IF NOT EXISTS `promocion_habitacion` (
  `id_promocion` int NOT NULL,
  `id_habitacion` int NOT NULL,
  PRIMARY KEY (`id_promocion`,`id_habitacion`),
  KEY `id_habitacion` (`id_habitacion`),
  CONSTRAINT `promocion_habitacion_ibfk_1` FOREIGN KEY (`id_promocion`) REFERENCES `promociones` (`id_promocion`),
  CONSTRAINT `promocion_habitacion_ibfk_2` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.promocion_habitacion: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.recuperacion
CREATE TABLE IF NOT EXISTS `recuperacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `expiracion` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `recuperacion_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.recuperacion: ~1 rows (aproximadamente)
INSERT INTO `recuperacion` (`id`, `usuario_id`, `token`, `expiracion`) VALUES
	(3, 8, '6P5CSSAOgefyjBY4Ut-BnuVhIfyNiRr5gxuP4bV8aV8', '2025-11-20 23:00:13');

-- Volcando estructura para tabla bd_hotel_san_eduardo.reportes
CREATE TABLE IF NOT EXISTS `reportes` (
  `id_reporte` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `id_reserva` int DEFAULT NULL,
  `tipo` varchar(50) NOT NULL,
  `fecha_generacion` date NOT NULL,
  `contenido` text,
  PRIMARY KEY (`id_reporte`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `reportes_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `reportes_ibfk_2` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.reportes: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.reservas
CREATE TABLE IF NOT EXISTS `reservas` (
  `id_reserva` int NOT NULL AUTO_INCREMENT,
  `codigo_confirmacion` varchar(50) DEFAULT NULL,
  `id_cliente` int NOT NULL,
  `id_habitacion` int DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  `fecha_reserva` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_entrada` date NOT NULL,
  `fecha_salida` date NOT NULL,
  `num_huespedes` int DEFAULT '1',
  `estado` varchar(30) DEFAULT 'Activa',
  `motivo_cancelacion` varchar(255) DEFAULT NULL,
  `fecha_cancelacion` datetime DEFAULT NULL,
  `noches` int DEFAULT '0',
  `total` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id_reserva`),
  UNIQUE KEY `codigo_confirmacion` (`codigo_confirmacion`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_habitacion` (`id_habitacion`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `reservas_ibfk_2` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`),
  CONSTRAINT `reservas_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.reservas: ~1 rows (aproximadamente)
INSERT INTO `reservas` (`id_reserva`, `codigo_confirmacion`, `id_cliente`, `id_habitacion`, `id_usuario`, `fecha_reserva`, `fecha_entrada`, `fecha_salida`, `num_huespedes`, `estado`, `motivo_cancelacion`, `fecha_cancelacion`, `noches`, `total`) VALUES
	(87, NULL, 6, 16, 7, '2025-11-21 01:45:06', '2025-11-21', '2025-11-25', 1, 'Activa', NULL, NULL, 4, 480.00);

-- Volcando estructura para tabla bd_hotel_san_eduardo.reserva_servicio
CREATE TABLE IF NOT EXISTS `reserva_servicio` (
  `id_reserva_servicio` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int DEFAULT NULL,
  `id_cliente` int DEFAULT NULL,
  `id_servicio` int NOT NULL,
  `fecha_uso` date DEFAULT NULL,
  `hora_uso` time DEFAULT NULL,
  `cantidad` int DEFAULT '1',
  `estado` varchar(20) DEFAULT 'Pendiente',
  `origen` enum('Vinculado','Independiente') DEFAULT 'Independiente',
  `subtotal` decimal(10,2) NOT NULL DEFAULT '0.00',
  `fecha` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  PRIMARY KEY (`id_reserva_servicio`),
  KEY `fk_reservaservicio_reserva` (`id_reserva`),
  KEY `fk_reservaservicio_cliente` (`id_cliente`),
  KEY `fk_reservaservicio_servicio` (`id_servicio`),
  CONSTRAINT `fk_reservaservicio_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE SET NULL,
  CONSTRAINT `fk_reservaservicio_reserva` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`) ON DELETE SET NULL,
  CONSTRAINT `fk_reservaservicio_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.reserva_servicio: ~33 rows (aproximadamente)
INSERT INTO `reserva_servicio` (`id_reserva_servicio`, `id_reserva`, `id_cliente`, `id_servicio`, `fecha_uso`, `hora_uso`, `cantidad`, `estado`, `origen`, `subtotal`, `fecha`, `hora`) VALUES
	(1, NULL, NULL, 1, NULL, NULL, 1, 'Pendiente', 'Independiente', 80.00, NULL, NULL),
	(2, NULL, NULL, 2, NULL, NULL, 1, 'Pendiente', 'Independiente', 25.00, NULL, NULL),
	(3, NULL, NULL, 3, NULL, NULL, 1, 'Pendiente', 'Independiente', 50.00, NULL, NULL),
	(4, NULL, NULL, 4, NULL, NULL, 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(5, NULL, NULL, 5, NULL, NULL, 1, 'Pendiente', 'Independiente', 30.00, NULL, NULL),
	(6, NULL, NULL, 1, NULL, NULL, 1, 'Pendiente', 'Independiente', 80.00, NULL, NULL),
	(7, NULL, NULL, 2, NULL, NULL, 1, 'Pendiente', 'Independiente', 25.00, NULL, NULL),
	(8, NULL, NULL, 3, NULL, NULL, 1, 'Pendiente', 'Independiente', 50.00, NULL, NULL),
	(9, NULL, NULL, 4, NULL, NULL, 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(10, NULL, NULL, 5, NULL, NULL, 1, 'Pendiente', 'Independiente', 30.00, NULL, NULL),
	(16, NULL, 6, 1, NULL, NULL, 1, 'Pendiente', 'Independiente', 80.00, '2025-11-06', '06:00:00'),
	(17, NULL, 6, 1, NULL, NULL, 1, 'Pendiente', 'Independiente', 80.00, '2025-11-06', '06:00:00'),
	(18, NULL, NULL, 4, NULL, NULL, 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(19, NULL, NULL, 2, NULL, NULL, 1, 'Pendiente', 'Independiente', 25.00, NULL, NULL),
	(20, NULL, 6, 4, '2025-11-06', '13:00:00', 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(21, NULL, 6, 6, '2025-11-06', '13:00:00', 1, 'Pendiente', 'Independiente', 90.00, NULL, NULL),
	(22, NULL, 6, 8, '2025-11-06', '13:00:00', 1, 'Pendiente', 'Independiente', 40.00, NULL, NULL),
	(23, NULL, NULL, 4, NULL, NULL, 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(24, NULL, NULL, 4, NULL, NULL, 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(25, NULL, NULL, 4, NULL, NULL, 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(26, NULL, NULL, 8, NULL, NULL, 1, 'Pendiente', 'Independiente', 40.00, NULL, NULL),
	(27, NULL, NULL, 4, NULL, NULL, 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(28, NULL, NULL, 9, NULL, NULL, 1, 'Pendiente', 'Independiente', 25.00, NULL, NULL),
	(29, NULL, NULL, 10, NULL, NULL, 1, 'Pendiente', 'Independiente', 30.00, NULL, NULL),
	(30, NULL, 7, 4, '2025-11-10', '09:00:00', 1, 'Cancelado', 'Vinculado', 20.00, NULL, NULL),
	(31, NULL, 7, 4, '2025-11-08', '06:30:00', 1, 'Cancelado', 'Vinculado', 20.00, NULL, NULL),
	(32, NULL, 7, 9, '2025-11-09', '07:30:00', 1, 'Cancelado', 'Vinculado', 25.00, NULL, NULL),
	(33, NULL, 7, 6, '2025-11-08', '06:30:00', 1, 'Cancelado', 'Vinculado', 90.00, NULL, NULL),
	(34, NULL, 7, 4, '2025-11-14', '07:00:00', 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(35, NULL, 7, 6, '2025-11-12', '07:00:00', 1, 'Pendiente', 'Independiente', 90.00, NULL, NULL),
	(36, NULL, 7, 4, '2025-11-13', '08:00:00', 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(37, NULL, 7, 4, '2025-11-08', '09:00:00', 1, 'Pendiente', 'Independiente', 20.00, NULL, NULL),
	(38, NULL, 7, 4, '2025-11-19', '06:00:00', 1, 'Cancelado', 'Vinculado', 20.00, NULL, NULL);

-- Volcando estructura para tabla bd_hotel_san_eduardo.roles
CREATE TABLE IF NOT EXISTS `roles` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.roles: ~4 rows (aproximadamente)
INSERT INTO `roles` (`id_rol`, `nombre_rol`) VALUES
	(1, 'Administrador'),
	(2, 'Recepcionista'),
	(3, 'Cliente'),
	(4, 'Mantenimiento');

-- Volcando estructura para tabla bd_hotel_san_eduardo.servicios
CREATE TABLE IF NOT EXISTS `servicios` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `estado` tinyint DEFAULT '1',
  `tipo_disponibilidad` enum('multiple','unico') DEFAULT 'unico',
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.servicios: ~16 rows (aproximadamente)
INSERT INTO `servicios` (`id_servicio`, `nombre`, `descripcion`, `precio`, `estado`, `tipo_disponibilidad`) VALUES
	(1, 'Spa', 'Acceso al spa con sauna y jacuzzi', 80.00, 0, 'unico'),
	(2, 'Piscina', 'Uso de piscina con toallas incluidas', 25.00, 0, 'multiple'),
	(3, 'Coworking', 'Acceso a sala coworking por día', 50.00, 0, 'unico'),
	(4, 'Lavandería', 'Servicio de lavado y planchado', 20.00, 1, 'unico'),
	(5, 'Desayuno buffet', 'Desayuno completo en el restaurante', 30.00, 0, 'unico'),
	(6, 'Spa y masajes relajantes', 'Sesión de spa con masajes y aromaterapia.', 90.00, 1, 'unico'),
	(7, 'Sauna y jacuzzi', 'Acceso por 30 minutos al sauna seco y jacuzzi.', 60.00, 1, 'unico'),
	(8, 'Gimnasio', 'Uso libre del gimnasio con entrenador disponible.', 40.00, 1, 'unico'),
	(9, 'Piscina', 'Acceso a la piscina por el día, incluye toalla.', 25.00, 1, 'multiple'),
	(10, 'Desayuno buffet', 'Desayuno completo en el restaurante.', 30.00, 1, 'multiple'),
	(11, 'Almuerzo ejecutivo', 'Menú del día con bebida y postre.', 40.00, 1, 'multiple'),
	(12, 'Cena gourmet', 'Cena especial con entrada, plato fuerte y vino.', 55.00, 1, 'multiple'),
	(13, 'Servicio de bar', 'Acceso al bar con carta de cócteles y snacks.', 35.00, 1, 'multiple'),
	(14, 'Sala de coworking', 'Espacio equipado para trabajo remoto por día.', 50.00, 1, 'unico'),
	(15, 'Salón de conferencias o reuniones', 'Alquiler por hora del salón con proyector.', 150.00, 1, 'unico'),
	(16, 'Tour local', 'Recorrido guiado por los principales atractivos de Chiclayo.', 120.00, 1, 'multiple');

-- Volcando estructura para tabla bd_hotel_san_eduardo.servicio_reservado
CREATE TABLE IF NOT EXISTS `servicio_reservado` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_servicio` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'Ocupado',
  PRIMARY KEY (`id`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `servicio_reservado_ibfk_1` FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.servicio_reservado: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.tipo_habitacion
CREATE TABLE IF NOT EXISTS `tipo_habitacion` (
  `id_tipo` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `capacidad` int DEFAULT NULL,
  `precio_base` decimal(10,2) NOT NULL,
  `comodidades` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.tipo_habitacion: ~9 rows (aproximadamente)
INSERT INTO `tipo_habitacion` (`id_tipo`, `nombre`, `descripcion`, `capacidad`, `precio_base`, `comodidades`) VALUES
	(1, 'Estandar', 'Habitación con una cama individual', 1, 80.00, 'WiFi, TV Cable'),
	(2, 'Doble', 'Habitación con dos camas', 2, 120.00, 'WiFi, Aire Acondicionado, Desayuno'),
	(3, 'Familiar', 'Habitación amplia para 4 personas', 4, 180.00, 'WiFi, TV Cable, Aire Acondicionado, Desayuno, Minibar'),
	(4, 'Habitación Estándar', 'Habitación con una cama doble y ambiente acogedor para una persona.', 1, 120.00, 'WiFi gratuito, Baño privado, Tv de Pantalla Plana'),
	(5, 'Habitación Doble - 2 camas', 'Habitación con dos camas y sala de estar ideal para familias o grupos.', 4, 280.00, 'WiFi gratuito, Baño privado, Tv de Pantalla Plana, Sala de estar'),
	(6, 'Habitación Triple', 'Habitación amplia con tres camas y terraza privada.', 5, 450.00, 'WiFi gratuito, Baño privado, Tv de Pantalla Plana, Terraza privada'),
	(7, 'Habitación Doble Estándar', 'Habitación con cama doble, vista a un patio interior y espacio cómodo para grupos.', 6, 550.00, 'WiFi gratuito, Baño privado, Tv de Pantalla Plana, Vistas a un patio interior'),
	(8, 'Suite Presidencial', 'Suite de lujo con jacuzzi, aire acondicionado y piscina privada.', 6, 450.00, 'Aire acondicionado, Jacuzzi, Piscina, Tv de Pantalla Plana con Cable'),
	(9, 'Habitación Individual', 'Habitación sencilla con una cama individual, ideal para viajeros.', 1, 80.00, 'WiFi gratuito, Una cama sencilla');

-- Volcando estructura para tabla bd_hotel_san_eduardo.tipo_pago
CREATE TABLE IF NOT EXISTS `tipo_pago` (
  `id_tipo_pago` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`id_tipo_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.tipo_pago: ~4 rows (aproximadamente)
INSERT INTO `tipo_pago` (`id_tipo_pago`, `descripcion`) VALUES
	(1, 'Transferencia bancaria'),
	(2, 'Tarjeta de credito/debito'),
	(3, 'Yape'),
	(4, 'Plin');

-- Volcando estructura para tabla bd_hotel_san_eduardo.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `dni` varchar(12) DEFAULT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `estado` tinyint DEFAULT '1',
  `id_rol` int NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `correo` (`correo`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=3412 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.usuarios: ~8 rows (aproximadamente)
INSERT INTO `usuarios` (`id_usuario`, `dni`, `nombres`, `apellidos`, `correo`, `password_hash`, `telefono`, `estado`, `id_rol`) VALUES
	(1, '00000000', 'Anghelo Jamir', 'Merino Mayra', 'jamir_anghelo@hotmail.com', '$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+51942030088', 1, 1),
	(3, NULL, 'Jamir', 'Casa', 'jamir@lsp.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+1111111111111', 1, 3),
	(4, NULL, 'LILIANA', 'MAYRA', 'lorena@lsp.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+1111111111111111', 1, 3),
	(5, NULL, 'Jose', 'Fiestas', 'josefiestas@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+58123456789', 1, 3),
	(6, '16712223', 'Lorena', 'Merino', 'lorena_yjl@hotmail.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+51971868785', 1, 3),
	(7, '72318704', 'Jamir', 'Merino Mayra', 'jamir@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+51942030088', 1, 2),
	(8, '72318705', 'Jamir', 'Merino Mayra', 'jamir_merino@hotmail.com', '$argon2id$v=19$m=65536,t=3,p=4$sCuxQ29bn++odGShDO06Kg$ww5OdRxnAhSX5Y6UMeU3I5lf5+IDHP1KVv4UXhnZR0Y', '+51942030088', 1, 3),
	(9, '72318703', 'Isis', 'Dulcemaria', '', '', '', 1, 3);

-- Volcando estructura para tabla bd_hotel_san_eduardo.valoraciones
CREATE TABLE IF NOT EXISTS `valoraciones` (
  `id_valoracion` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int NOT NULL,
  `id_reserva` int DEFAULT NULL,
  `puntuacion` int NOT NULL,
  `comentario` text,
  `fecha_valoracion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_valoracion`),
  KEY `fk_valoracion_cliente` (`id_cliente`),
  KEY `fk_valoracion_reserva` (`id_reserva`),
  CONSTRAINT `fk_valoracion_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE CASCADE,
  CONSTRAINT `fk_valoracion_reserva` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.valoraciones: ~1 rows (aproximadamente)
INSERT INTO `valoraciones` (`id_valoracion`, `id_cliente`, `id_reserva`, `puntuacion`, `comentario`, `fecha_valoracion`) VALUES
	(1, 7, NULL, 5, 'Buena estadia', '2025-11-18 23:24:23');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

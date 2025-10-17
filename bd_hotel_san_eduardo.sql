-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.42 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.8.0.6908
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

-- Volcando estructura para tabla bd_hotel_san_eduardo.check_in
CREATE TABLE IF NOT EXISTS `check_in` (
  `id_checkin` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  PRIMARY KEY (`id_checkin`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `check_in_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.check_in: ~0 rows (aproximadamente)

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.clientes: ~6 rows (aproximadamente)
INSERT INTO `clientes` (`id_cliente`, `tipo_documento`, `num_documento`, `nombres`, `apellidos`, `nacionalidad`, `direccion`, `telefono`, `correo`, `id_usuario`) VALUES
	(1, 'CE', '66666666666666666666', 'Anghelo Jamir', 'Merino Mayra', 'Pakistán', 'Husares de Junin 868', '+51942030088', 'jamir_merino@hotmail.com', 1),
	(2, 'Pasaporte', '111111111111', 'Jamir', 'Casa', 'España', 'Carlos Castañeda 637', '+1111111111111', 'jamir@lsp.com', 3),
	(3, 'CE', '111111112', 'LILIANA', 'MAYRA', 'Estados Unidos', 'Carlos Castañeda 637', '+1111111111111111', 'lorena@lsp.com', 4),
	(4, 'CE', '123456789', 'Jose', 'Fiestas', 'Venezuela', 'San Pucta 123', '+58123456789', 'josefiestas@gmail.com', 5),
	(5, 'DNI', '16712223', 'Liliana', 'Mayra', 'Perú', 'Carlos Castañeda 637', '+51971868785', 'lorena_yjl@hotmail.com', 6),
	(6, 'DNI', '72318705', 'Jamir', 'Merino Mayra', 'Perú', 'Carlos Castañeda 640', '+51942030088', 'jamir@gmail.com', 7);

-- Volcando estructura para tabla bd_hotel_san_eduardo.facturacion
CREATE TABLE IF NOT EXISTS `facturacion` (
  `id_factura` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `id_tipo_pago` int NOT NULL,
  `id_usuario` int DEFAULT NULL,
  `fecha_emision` date NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `estado` varchar(30) DEFAULT 'Pagado',
  PRIMARY KEY (`id_factura`),
  KEY `id_reserva` (`id_reserva`),
  KEY `id_tipo_pago` (`id_tipo_pago`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `facturacion_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`),
  CONSTRAINT `facturacion_ibfk_2` FOREIGN KEY (`id_tipo_pago`) REFERENCES `tipo_pago` (`id_tipo_pago`),
  CONSTRAINT `facturacion_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.facturacion: ~0 rows (aproximadamente)

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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.habitaciones: ~6 rows (aproximadamente)
INSERT INTO `habitaciones` (`id_habitacion`, `numero`, `id_tipo`, `estado`, `imagen`) VALUES
	(1, '101', 1, 'Disponible', 'static/img/habitaciones/individual_1.jpg'),
	(2, '102', 1, 'Disponible', 'static/img/habitaciones/individual_2.jpg'),
	(3, '201', 2, 'Disponible', 'static/img/habitaciones/doble_1.jpg'),
	(4, '202', 2, 'Disponible', 'static/img/habitaciones/doble_2.jpg'),
	(5, '301', 3, 'Disponible', 'static/img/habitaciones/familiar_1.jpg'),
	(6, '302', 3, 'Disponible', 'static/img/habitaciones/familiar_2.jpg');

-- Volcando estructura para tabla bd_hotel_san_eduardo.imagenes_habitacion
CREATE TABLE IF NOT EXISTS `imagenes_habitacion` (
  `id_imagen` int NOT NULL AUTO_INCREMENT,
  `id_habitacion` int NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  PRIMARY KEY (`id_imagen`),
  KEY `id_habitacion` (`id_habitacion`),
  CONSTRAINT `imagenes_habitacion_ibfk_1` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.imagenes_habitacion: ~9 rows (aproximadamente)
INSERT INTO `imagenes_habitacion` (`id_imagen`, `id_habitacion`, `ruta_imagen`) VALUES
	(19, 1, 'static/img/habitaciones/individual_1.jpg'),
	(20, 1, 'static/img/habitaciones/individual_2.jpg'),
	(21, 1, 'static/img/habitaciones/individual_3.jpg'),
	(22, 3, 'static/img/habitaciones/doble_1.jpg'),
	(23, 3, 'static/img/habitaciones/doble_2.jpg'),
	(24, 3, 'static/img/habitaciones/doble_3.jpg'),
	(25, 5, 'static/img/habitaciones/familiar_1.jpg'),
	(26, 5, 'static/img/habitaciones/familiar_2.jpg'),
	(27, 5, 'static/img/habitaciones/familiar_3.jpg');

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.mensajes_contacto: ~0 rows (aproximadamente)

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
  `id_cliente` int NOT NULL,
  `id_habitacion` int NOT NULL,
  `id_usuario` int DEFAULT NULL,
  `fecha_entrada` date NOT NULL,
  `fecha_salida` date NOT NULL,
  `num_huespedes` int DEFAULT '1',
  `estado` varchar(30) DEFAULT 'Activa',
  PRIMARY KEY (`id_reserva`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_habitacion` (`id_habitacion`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `reservas_ibfk_2` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`),
  CONSTRAINT `reservas_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.reservas: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.reserva_servicio
CREATE TABLE IF NOT EXISTS `reserva_servicio` (
  `id_reserva` int NOT NULL,
  `id_servicio` int NOT NULL,
  `cantidad` int DEFAULT '1',
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_reserva`,`id_servicio`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `reserva_servicio_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`),
  CONSTRAINT `reserva_servicio_ibfk_2` FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.reserva_servicio: ~0 rows (aproximadamente)

-- Volcando estructura para tabla bd_hotel_san_eduardo.roles
CREATE TABLE IF NOT EXISTS `roles` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.roles: ~3 rows (aproximadamente)
INSERT INTO `roles` (`id_rol`, `nombre_rol`) VALUES
	(1, 'Administrador'),
	(2, 'Recepcionista'),
	(3, 'Cliente');

-- Volcando estructura para tabla bd_hotel_san_eduardo.servicios
CREATE TABLE IF NOT EXISTS `servicios` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `estado` tinyint DEFAULT '1',
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.servicios: ~5 rows (aproximadamente)
INSERT INTO `servicios` (`id_servicio`, `nombre`, `descripcion`, `precio`, `estado`) VALUES
	(1, 'Spa', 'Acceso al spa con sauna y jacuzzi', 80.00, 1),
	(2, 'Piscina', 'Uso de piscina con toallas incluidas', 25.00, 1),
	(3, 'Coworking', 'Acceso a sala coworking por día', 50.00, 1),
	(4, 'Lavandería', 'Servicio de lavado y planchado', 20.00, 1),
	(5, 'Desayuno buffet', 'Desayuno completo en el restaurante', 30.00, 1);

-- Volcando estructura para tabla bd_hotel_san_eduardo.tipo_habitacion
CREATE TABLE IF NOT EXISTS `tipo_habitacion` (
  `id_tipo` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `capacidad` int DEFAULT NULL,
  `precio_base` decimal(10,2) NOT NULL,
  `comodidades` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.tipo_habitacion: ~3 rows (aproximadamente)
INSERT INTO `tipo_habitacion` (`id_tipo`, `nombre`, `descripcion`, `capacidad`, `precio_base`, `comodidades`) VALUES
	(1, 'Individual', 'Habitación con una cama individual', 1, 80.00, 'WiFi, TV Cable'),
	(2, 'Doble', 'Habitación con dos camas o matrimonial', 2, 120.00, 'WiFi, Aire Acondicionado, Desayuno'),
	(3, 'Familiar', 'Habitación amplia para 4 personas', 4, 180.00, 'WiFi, TV Cable, Aire Acondicionado, Desayuno, Minibar');

-- Volcando estructura para tabla bd_hotel_san_eduardo.tipo_pago
CREATE TABLE IF NOT EXISTS `tipo_pago` (
  `id_tipo_pago` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`id_tipo_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.tipo_pago: ~4 rows (aproximadamente)
INSERT INTO `tipo_pago` (`id_tipo_pago`, `descripcion`) VALUES
	(1, 'Efectivo'),
	(2, 'Tarjeta'),
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla bd_hotel_san_eduardo.usuarios: ~6 rows (aproximadamente)
INSERT INTO `usuarios` (`id_usuario`, `dni`, `nombres`, `apellidos`, `correo`, `password_hash`, `telefono`, `estado`, `id_rol`) VALUES
	(1, '00000000', 'Anghelo Jamir', 'Merino Mayra', 'jamir_merino@hotmail.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+51942030088', 1, 3),
	(3, NULL, 'Jamir', 'Casa', 'jamir@lsp.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+1111111111111', 1, 3),
	(4, NULL, 'LILIANA', 'MAYRA', 'lorena@lsp.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+1111111111111111', 1, 3),
	(5, NULL, 'Jose', 'Fiestas', 'josefiestas@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+58123456789', 1, 3),
	(6, '16712223', 'Liliana', 'Mayra', 'lorena_yjl@hotmail.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+51971868785', 1, 3),
	(7, '72318705', 'Jamir', 'Merino Mayra', 'jamir@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM', '+51942030088', 1, 3);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

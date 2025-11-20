/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `bd_hotel_san_eduardo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `bd_hotel_san_eduardo`;
DROP TABLE IF EXISTS `actividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actividad` (
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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `check_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `check_in` (
  `id_checkin` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  PRIMARY KEY (`id_checkin`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `check_in_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `check_out`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `check_out` (
  `id_checkout` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `total_factura` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_checkout`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `check_out_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
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
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `facturacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion` (
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
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `habitaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `habitaciones` (
  `id_habitacion` int NOT NULL AUTO_INCREMENT,
  `numero` varchar(20) NOT NULL,
  `id_tipo` int NOT NULL,
  `estado` varchar(30) DEFAULT 'Disponible',
  `imagen` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_habitacion`),
  UNIQUE KEY `numero` (`numero`),
  KEY `id_tipo` (`id_tipo`),
  CONSTRAINT `habitaciones_ibfk_1` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_habitacion` (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `historial_notificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_notificaciones` (
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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `imagenes_habitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imagenes_habitacion` (
  `id_imagen` int NOT NULL AUTO_INCREMENT,
  `id_habitacion` int NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  PRIMARY KEY (`id_imagen`),
  KEY `id_habitacion` (`id_habitacion`),
  CONSTRAINT `imagenes_habitacion_ibfk_1` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `incidencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `incidencias` (
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
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `mensajes_contacto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mensajes_contacto` (
  `id_mensaje` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `mensaje` text NOT NULL,
  `fecha_envio` datetime DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('Pendiente','Leído','Respondido') DEFAULT 'Pendiente',
  PRIMARY KEY (`id_mensaje`)
) ENGINE=InnoDB AUTO_INCREMENT=3372 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `promocion_habitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promocion_habitacion` (
  `id_promocion` int NOT NULL,
  `id_habitacion` int NOT NULL,
  PRIMARY KEY (`id_promocion`,`id_habitacion`),
  KEY `id_habitacion` (`id_habitacion`),
  CONSTRAINT `promocion_habitacion_ibfk_1` FOREIGN KEY (`id_promocion`) REFERENCES `promociones` (`id_promocion`),
  CONSTRAINT `promocion_habitacion_ibfk_2` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `promociones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promociones` (
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
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `recuperacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recuperacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `expiracion` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `recuperacion_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `reportes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reportes` (
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
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `reserva_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reserva_servicio` (
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
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `reservas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservas` (
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
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `servicio_reservado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicio_reservado` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_servicio` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'Ocupado',
  PRIMARY KEY (`id`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `servicio_reservado_ibfk_1` FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicios` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `estado` tinyint DEFAULT '1',
  `tipo_disponibilidad` enum('multiple','unico') DEFAULT 'unico',
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `tipo_habitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_habitacion` (
  `id_tipo` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `capacidad` int DEFAULT NULL,
  `precio_base` decimal(10,2) NOT NULL,
  `comodidades` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `tipo_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_pago` (
  `id_tipo_pago` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`id_tipo_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
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
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `valoraciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `valoraciones` (
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
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


-- =========================
--  DATA SECTION (INSERTs)
-- =========================

/*!40014 SET FOREIGN_KEY_CHECKS=0 */;
/*!40014 SET UNIQUE_CHECKS=0 */;
/*!40101 SET SQL_NOTES=0 */;
USE `bd_hotel_san_eduardo`;


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

/*!40000 ALTER TABLE `actividad` DISABLE KEYS */;
INSERT INTO `actividad` VALUES (1,'Check-in',2,5,'Ocupada','2025-10-21 01:08:45'),(2,'Check-out',2,5,'En Limpieza','2025-10-21 01:08:52'),(3,'Check-in',4,1,'Ocupada','2025-10-31 08:21:57'),(4,'Check-out',4,1,'En Limpieza','2025-10-31 08:26:01'),(5,'Limpieza OK',NULL,5,'Disponible','2025-10-31 08:27:19'),(6,'Limpieza OK',NULL,1,'Disponible','2025-10-31 08:27:23'),(7,'Check-in',3,1,'Ocupada','2025-10-31 08:27:30'),(8,'Check-in',5,3,'Ocupada','2025-11-04 09:54:13'),(9,'Check-out',5,3,'En Limpieza','2025-11-04 09:54:33'),(10,'Limpieza OK',NULL,3,'Disponible','2025-11-04 09:56:53'),(11,'Check-in',30,3,'Ocupada','2025-11-07 02:16:29'),(12,'Check-out',30,3,'En Limpieza','2025-11-07 02:16:45'),(13,'Limpieza OK',NULL,3,'Disponible','2025-11-07 02:16:54'),(14,'Check-in',48,1,'Ocupada','2025-11-11 11:49:06'),(15,'Check-out',48,1,'En Limpieza','2025-11-11 11:49:10'),(16,'Limpieza OK',NULL,1,'Disponible','2025-11-11 11:49:37');
/*!40000 ALTER TABLE `actividad` ENABLE KEYS */;

/*!40000 ALTER TABLE `check_in` DISABLE KEYS */;
/*!40000 ALTER TABLE `check_in` ENABLE KEYS */;

/*!40000 ALTER TABLE `check_out` DISABLE KEYS */;
/*!40000 ALTER TABLE `check_out` ENABLE KEYS */;

/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (1,'CE','66666666666666666666','Anghelo Jamir','Merino Mayra','Pakistán','Husares de Junin 868','+51942030088','jamir_anghelo@hotmail.com',1),(2,'Pasaporte','111111111111','Jamir','Casa','España','Carlos Castañeda 637','+1111111111111','jamir@lsp.com',3),(3,'CE','111111112','LILIANA','MAYRA','Estados Unidos','Carlos Castañeda 637','+1111111111111111','lorena@lsp.com',4),(4,'CE','123456789','Jose','Fiestas','Venezuela','San Pucta 123','+58123456789','josefiestas@gmail.com',5),(5,'DNI','16712223','Lorena','Merino','Perú','Carlos Castañeda 637','+51971868785','lorena_yjl@hotmail.com',6),(6,'DNI','72318704','Jamir','Merino Mayra','Perú','Carlos Castañeda 640','+51942030088','jamir@gmail.com',7),(7,'DNI','72318705','Jamir','Merino Mayra','España','Husares de Junin 868','+51942030088','jamir_merino@hotmail.com',8),(8,'DNI','72318703','Isis','Dulcemaria','Perú','','','',9),(9,'DNI','73242600','Maguiña','sanchez rosmer','Perú',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;

/*!40000 ALTER TABLE `facturacion` DISABLE KEYS */;
INSERT INTO `facturacion` VALUES (1,1,4,7,'2025-10-16',160.00,'Pagado','67283a6ab49e7.jpeg'),(2,2,3,7,'2025-10-16',745.00,'Pagado','IMG_0672.png'),(3,3,1,6,'2025-10-21',365.00,'Pagado',NULL),(4,4,2,6,'2025-10-31',80.00,'Pagado',NULL),(5,5,2,6,'2025-11-04',480.00,'Pagado',NULL),(6,6,2,6,'2025-11-04',720.00,'Pagado',NULL),(7,7,2,6,'2025-11-06',205.00,'Pagado',NULL),(8,8,2,6,'2025-11-06',80.00,'Pagado',NULL),(9,9,1,6,'2025-11-06',20.00,'Pagado',NULL),(10,10,1,6,'2025-11-06',20.00,'Pagado',NULL),(11,11,1,6,'2025-11-06',80.00,'Pagado',NULL),(12,12,1,6,'2025-11-06',0.00,'Pagado','static\\img\\comprobantes\\zalzar.png'),(13,13,1,6,'2025-11-06',0.00,'Pagado','static\\img\\comprobantes\\zalzar.png'),(14,14,1,6,'2025-11-06',0.00,'Pagado','static\\img\\comprobantes\\zalzar.png'),(15,15,1,6,'2025-11-06',0.00,'Pagado','static\\img\\comprobantes\\logo.jpg'),(16,16,1,6,'2025-11-06',80.00,'Pagado','static\\img\\comprobantes\\unnamed_1.jpg'),(17,17,1,6,'2025-11-06',80.00,'Pagado','static\\img\\comprobantes\\1-4.jpg'),(18,18,1,6,'2025-11-06',720.00,'Pagado','static\\img\\comprobantes\\zalzar.png'),(19,19,1,6,'2025-11-06',80.00,'Pagado','static\\img\\comprobantes\\2.png'),(20,20,1,6,'2025-11-06',120.00,'Pagado','static\\img\\comprobantes\\Imagen_de_WhatsApp_2025-09-20_a_las_21.48.53_b4281512.jpg'),(21,21,1,6,'2025-11-06',1260.00,'Pagado','static\\img\\comprobantes\\logo.jpg'),(22,22,1,6,'2025-11-06',1260.00,'Pagado','static\\img\\comprobantes\\Copia_de_Diagrama_en_blanco.png'),(23,23,1,6,'2025-11-06',180.00,'Pagado','static\\img\\comprobantes\\zalzar.png'),(24,24,2,6,'2025-11-06',540.00,'Pagado',NULL),(25,29,1,6,'2025-11-07',480.00,'Pagado','static\\img\\comprobantes\\kaosbn.jpg'),(26,31,1,6,'2025-11-07',80.00,'Pagado','static\\img\\comprobantes\\Captura_de_pantalla_2025-11-07_013645.png'),(27,32,1,6,'2025-11-07',20.00,'Pagado',NULL),(28,33,2,6,'2025-11-07',80.00,'Pagado',NULL),(29,34,1,6,'2025-11-07',115.00,'Pagado',NULL),(30,36,2,8,'2025-11-07',540.00,'Anulado',NULL),(31,36,1,8,'2025-11-07',20.00,'Anulado',NULL),(32,36,1,8,'2025-11-07',20.00,'Anulado',NULL),(33,36,1,8,'2025-11-07',25.00,'Anulado',NULL),(34,37,1,8,'2025-11-07',180.00,'Anulado','static\\img\\comprobantes\\logo_-_copia.jpg'),(35,38,2,8,'2025-11-07',540.00,'Anulado',NULL),(36,39,3,8,'2025-11-07',540.00,'Anulado','static\\img\\comprobantes\\logo_-_copia.jpg'),(37,40,1,8,'2025-11-07',540.00,'Anulado','static\\img\\comprobantes\\logo_-_copia.jpg'),(38,39,1,8,'2025-11-07',90.00,'Anulado',NULL),(39,41,1,8,'2025-11-08',20.00,'Pagado',NULL),(40,42,1,8,'2025-11-08',90.00,'Pagado',NULL),(41,43,1,8,'2025-11-08',20.00,'Pagado',NULL),(42,44,1,8,'2025-11-08',20.00,'Pagado',NULL),(43,45,1,8,'2025-11-08',80.00,'Anulado','static\\img\\comprobantes\\logo_-_copia.jpg'),(44,46,1,8,'2025-11-08',120.00,'Anulado','static\\img\\comprobantes\\logo_-_copia.jpg'),(45,47,1,8,'2025-11-08',80.00,'Anulado','static\\img\\comprobantes\\logo_-_copia.jpg'),(46,48,1,8,'2025-11-09',160.00,'Pagado','static\\img\\comprobantes\\logo_-_copia.jpg'),(47,49,1,8,'2025-11-13',1080.00,'Anulado',NULL),(48,49,1,8,'2025-11-18',20.00,'Anulado',NULL);
/*!40000 ALTER TABLE `facturacion` ENABLE KEYS */;

/*!40000 ALTER TABLE `habitaciones` DISABLE KEYS */;
INSERT INTO `habitaciones` VALUES (1,'101',1,'Disponible','static/img/habitaciones/individual_1.jpg'),(2,'102',1,'Disponible','static/img/habitaciones/individual_2.jpg'),(3,'201',2,'Disponible','static/img/habitaciones/doble_1.jpg'),(4,'202',2,'Disponible','static/img/habitaciones/doble_2.jpg'),(5,'301',3,'Disponible','static/img/habitaciones/familiar_1.jpg'),(6,'302',3,'Disponible','static/img/habitaciones/familiar_2.jpg'),(7,'104',2,'Disponible','img/habitaciones/Sala-de-reuniones-scaled.jpg'),(10,'103',3,'Disponible','img/habitaciones/default.jpg');
/*!40000 ALTER TABLE `habitaciones` ENABLE KEYS */;

/*!40000 ALTER TABLE `historial_notificaciones` DISABLE KEYS */;
INSERT INTO `historial_notificaciones` VALUES (1,6,'confirmacion','lorena_yjl@hotmail.com','Confirmacion - Hotel San Eduardo','Enviado','2025-10-21 01:39:06'),(2,6,'confirmacion','jamir.merino.17@hotmail.com','Confirmación de Reserva #3 • Hotel San Eduardo','Enviado','2025-10-21 01:40:15'),(3,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #3 • Hotel San Eduardo','Enviado','2025-10-21 01:40:17'),(4,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #4 • Hotel San Eduardo','Enviado','2025-10-31 08:19:40'),(5,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #5 • Hotel San Eduardo','Enviado','2025-11-04 09:50:13'),(6,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #6 • Hotel San Eduardo','Enviado','2025-11-04 11:43:41'),(7,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #7 • Hotel San Eduardo','Enviado','2025-11-06 00:51:45'),(8,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #8 • Hotel San Eduardo','Enviado','2025-11-06 16:04:17'),(9,6,'confirmacion','anghelojamircko@hotmail.com','Confirmación de Reserva #8 • Hotel San Eduardo','Enviado','2025-11-06 16:04:20'),(10,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #11 • Hotel San Eduardo','Enviado','2025-11-06 21:01:03'),(11,6,'confirmacion','lorena_yjl@hotmail.com','Confirmación de Reserva #24 • Hotel San Eduardo','Enviado','2025-11-06 22:07:31'),(12,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #36 • Hotel San Eduardo','Enviado','2025-11-07 21:44:33'),(13,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #36 • Hotel San Eduardo','Enviado','2025-11-07 22:38:25'),(14,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #36 • Hotel San Eduardo','Enviado','2025-11-07 22:40:02'),(15,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #38 • Hotel San Eduardo','Enviado','2025-11-07 23:18:00'),(16,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #40 • Hotel San Eduardo','Enviado','2025-11-07 23:25:29'),(17,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #39 • Hotel San Eduardo','Enviado','2025-11-07 23:28:12'),(18,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #42 • Hotel San Eduardo','Enviado','2025-11-08 00:04:53'),(19,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva de Servicios #43 • Hotel San Eduardo','Enviado','2025-11-08 00:13:40'),(20,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva de Servicios #44 • Hotel San Eduardo','Enviado','2025-11-08 00:19:41'),(21,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #45 • Hotel San Eduardo','Enviado','2025-11-08 00:41:17'),(22,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #46 • Hotel San Eduardo','Enviado','2025-11-08 00:45:40'),(23,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #47 • Hotel San Eduardo','Enviado','2025-11-08 00:47:59'),(24,8,'cancelacion','jamir_merino@hotmail.com','Cancelación de reserva #47 • Hotel San Eduardo','Enviado','2025-11-08 00:48:27'),(25,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #48 • Hotel San Eduardo','Enviado','2025-11-09 23:23:59'),(26,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #49 • Hotel San Eduardo','Enviado','2025-11-13 21:49:27'),(27,8,'confirmacion','jamir_merino@hotmail.com','Confirmación de Reserva #49 • Hotel San Eduardo','Enviado','2025-11-18 23:23:03'),(28,8,'cancelacion','jamir_merino@hotmail.com','Cancelación de reserva #49 • Hotel San Eduardo','Enviado','2025-11-19 00:21:13');
/*!40000 ALTER TABLE `historial_notificaciones` ENABLE KEYS */;

/*!40000 ALTER TABLE `imagenes_habitacion` DISABLE KEYS */;
INSERT INTO `imagenes_habitacion` VALUES (19,1,'static/img/habitaciones/individual_1.jpg'),(20,1,'static/img/habitaciones/individual_2.jpg'),(21,1,'static/img/habitaciones/individual_3.jpg'),(22,3,'static/img/habitaciones/doble_1.jpg'),(23,3,'static/img/habitaciones/doble_2.jpg'),(24,3,'static/img/habitaciones/doble_3.jpg'),(25,5,'static/img/habitaciones/familiar_1.jpg'),(26,5,'static/img/habitaciones/familiar_2.jpg'),(27,5,'static/img/habitaciones/familiar_3.jpg'),(28,7,'img/habitaciones/Sala-de-reuniones-scaled.jpg'),(29,7,'img/habitaciones/3010.jpg'),(30,7,'img/habitaciones/media_x5gdi2kk_e-learning_skills-and-techniques_essential-bar-skills_speed-and-efficiency_split_bartender-at-bar-with-cockta.jpg'),(31,10,'img/habitaciones/default.jpg'),(32,10,'img/habitaciones/32537213-42f4-4389-b1f6-fadff7fb7c7c.jpg'),(33,10,'img/habitaciones/67283a6ab49e7.jpeg');
/*!40000 ALTER TABLE `imagenes_habitacion` ENABLE KEYS */;

/*!40000 ALTER TABLE `incidencias` DISABLE KEYS */;
/*!40000 ALTER TABLE `incidencias` ENABLE KEYS */;

/*!40000 ALTER TABLE `mensajes_contacto` DISABLE KEYS */;
INSERT INTO `mensajes_contacto` VALUES (1,'Jamir Merino','jamir_merino@hotmail.com','hola me gusta la pagina','2025-11-07 11:20:53','Pendiente');
/*!40000 ALTER TABLE `mensajes_contacto` ENABLE KEYS */;

/*!40000 ALTER TABLE `promocion_habitacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `promocion_habitacion` ENABLE KEYS */;

/*!40000 ALTER TABLE `promociones` DISABLE KEYS */;
/*!40000 ALTER TABLE `promociones` ENABLE KEYS */;

/*!40000 ALTER TABLE `recuperacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `recuperacion` ENABLE KEYS */;

/*!40000 ALTER TABLE `reportes` DISABLE KEYS */;
/*!40000 ALTER TABLE `reportes` ENABLE KEYS */;

/*!40000 ALTER TABLE `reserva_servicio` DISABLE KEYS */;
INSERT INTO `reserva_servicio` VALUES (1,2,NULL,1,NULL,NULL,1,'Pendiente','Independiente',80.00,NULL,NULL),(2,2,NULL,2,NULL,NULL,1,'Pendiente','Independiente',25.00,NULL,NULL),(3,2,NULL,3,NULL,NULL,1,'Pendiente','Independiente',50.00,NULL,NULL),(4,2,NULL,4,NULL,NULL,1,'Pendiente','Independiente',20.00,NULL,NULL),(5,2,NULL,5,NULL,NULL,1,'Pendiente','Independiente',30.00,NULL,NULL),(6,3,NULL,1,NULL,NULL,1,'Pendiente','Independiente',80.00,NULL,NULL),(7,3,NULL,2,NULL,NULL,1,'Pendiente','Independiente',25.00,NULL,NULL),(8,3,NULL,3,NULL,NULL,1,'Pendiente','Independiente',50.00,NULL,NULL),(9,3,NULL,4,NULL,NULL,1,'Pendiente','Independiente',20.00,NULL,NULL),(10,3,NULL,5,NULL,NULL,1,'Pendiente','Independiente',30.00,NULL,NULL),(16,NULL,6,1,NULL,NULL,1,'Pendiente','Independiente',80.00,'2025-11-06','06:00:00'),(17,NULL,6,1,NULL,NULL,1,'Pendiente','Independiente',80.00,'2025-11-06','06:00:00'),(18,7,NULL,4,NULL,NULL,1,'Pendiente','Independiente',20.00,NULL,NULL),(19,7,NULL,2,NULL,NULL,1,'Pendiente','Independiente',25.00,NULL,NULL),(20,NULL,6,4,'2025-11-06','13:00:00',1,'Pendiente','Independiente',20.00,NULL,NULL),(21,NULL,6,6,'2025-11-06','13:00:00',1,'Pendiente','Independiente',90.00,NULL,NULL),(22,NULL,6,8,'2025-11-06','13:00:00',1,'Pendiente','Independiente',40.00,NULL,NULL),(23,9,NULL,4,NULL,NULL,1,'Pendiente','Independiente',20.00,NULL,NULL),(24,10,NULL,4,NULL,NULL,1,'Pendiente','Independiente',20.00,NULL,NULL),(25,32,NULL,4,NULL,NULL,1,'Pendiente','Independiente',20.00,NULL,NULL),(26,34,NULL,8,NULL,NULL,1,'Pendiente','Independiente',40.00,NULL,NULL),(27,34,NULL,4,NULL,NULL,1,'Pendiente','Independiente',20.00,NULL,NULL),(28,34,NULL,9,NULL,NULL,1,'Pendiente','Independiente',25.00,NULL,NULL),(29,34,NULL,10,NULL,NULL,1,'Pendiente','Independiente',30.00,NULL,NULL),(30,36,7,4,'2025-11-10','09:00:00',1,'Cancelado','Vinculado',20.00,NULL,NULL),(31,36,7,4,'2025-11-08','06:30:00',1,'Cancelado','Vinculado',20.00,NULL,NULL),(32,36,7,9,'2025-11-09','07:30:00',1,'Cancelado','Vinculado',25.00,NULL,NULL),(33,39,7,6,'2025-11-08','06:30:00',1,'Cancelado','Vinculado',90.00,NULL,NULL),(34,41,7,4,'2025-11-14','07:00:00',1,'Pendiente','Independiente',20.00,NULL,NULL),(35,42,7,6,'2025-11-12','07:00:00',1,'Pendiente','Independiente',90.00,NULL,NULL),(36,43,7,4,'2025-11-13','08:00:00',1,'Pendiente','Independiente',20.00,NULL,NULL),(37,44,7,4,'2025-11-08','09:00:00',1,'Pendiente','Independiente',20.00,NULL,NULL),(38,49,7,4,'2025-11-19','06:00:00',1,'Cancelado','Vinculado',20.00,NULL,NULL);
/*!40000 ALTER TABLE `reserva_servicio` ENABLE KEYS */;

/*!40000 ALTER TABLE `reservas` DISABLE KEYS */;
INSERT INTO `reservas` VALUES (1,NULL,6,1,7,'2025-10-17 04:52:52','2025-10-16','2025-10-18',1,'Cancelada','Cancelado por el cliente','2025-10-17 00:01:25',0,0.00),(2,NULL,6,5,7,'2025-10-17 04:52:52','2025-10-16','2025-10-19',1,'Finalizada',NULL,NULL,0,0.00),(3,NULL,5,1,6,'2025-10-21 01:40:13','2025-10-22','2025-10-24',1,'Cancelada','Cancelado por el cliente','2025-10-31 08:28:35',0,0.00),(4,NULL,5,1,6,'2025-10-31 08:19:37','2025-10-31','2025-11-01',1,'Finalizada',NULL,NULL,0,0.00),(5,NULL,5,3,6,'2025-11-04 09:50:11','2025-11-05','2025-11-09',1,'Finalizada',NULL,NULL,0,0.00),(6,NULL,5,3,6,'2025-11-04 11:43:39','2025-11-05','2025-11-11',1,'Finalizada',NULL,NULL,0,0.00),(7,NULL,5,2,6,'2025-11-06 00:51:42','2025-11-06','2025-11-08',1,'Finalizada',NULL,NULL,0,0.00),(8,NULL,5,1,6,'2025-11-06 16:04:15','2025-11-07','2025-11-08',1,'Finalizada',NULL,NULL,0,0.00),(9,NULL,5,NULL,6,'2025-11-06 16:17:38','2025-11-06','2025-11-06',1,'Finalizada',NULL,NULL,0,0.00),(10,NULL,5,NULL,6,'2025-11-06 16:39:20','2025-11-06','2025-11-06',1,'Finalizada',NULL,NULL,0,0.00),(11,NULL,5,1,6,'2025-11-06 21:01:00','2025-11-06','2025-11-07',1,'Finalizada',NULL,NULL,0,0.00),(12,NULL,6,1,6,'2025-11-06 21:11:21','2025-11-06','2025-11-07',1,'Finalizada',NULL,NULL,0,0.00),(13,NULL,6,1,6,'2025-11-06 21:12:58','2025-11-06','2025-11-07',1,'Finalizada',NULL,NULL,0,0.00),(14,NULL,6,1,6,'2025-11-06 21:13:15','2025-11-06','2025-11-07',1,'Finalizada',NULL,NULL,0,0.00),(15,NULL,6,1,6,'2025-11-06 21:23:01','2025-11-06','2025-11-07',1,'Finalizada',NULL,NULL,0,0.00),(16,NULL,6,1,6,'2025-11-06 21:26:37','2025-11-06','2025-11-07',1,'Finalizada',NULL,NULL,0,0.00),(17,NULL,6,1,6,'2025-11-06 21:31:35','2025-11-06','2025-11-07',1,'Finalizada',NULL,NULL,0,0.00),(18,NULL,6,1,6,'2025-11-06 21:33:14','2025-11-06','2025-11-15',1,'Finalizada',NULL,NULL,0,0.00),(19,NULL,5,1,6,'2025-11-06 21:42:50','2025-11-06','2025-11-07',1,'Cancelada','Cancelado por el cliente','2025-11-06 21:51:09',0,0.00),(20,NULL,5,3,6,'2025-11-06 21:43:37','2025-11-07','2025-11-08',1,'Cancelada','Cancelado por el cliente','2025-11-06 21:51:07',0,0.00),(21,NULL,5,6,6,'2025-11-06 21:46:11','2025-11-13','2025-11-20',1,'Cancelada','Cancelado por el cliente','2025-11-06 21:48:24',0,0.00),(22,NULL,5,6,6,'2025-11-06 21:49:05','2025-11-13','2025-11-20',1,'Cancelada','Cancelado por el cliente','2025-11-06 21:51:04',0,0.00),(23,NULL,5,6,6,'2025-11-06 21:51:32','2025-11-07','2025-11-08',1,'Finalizada',NULL,NULL,0,0.00),(24,NULL,5,5,6,'2025-11-06 22:07:28','2025-11-07','2025-11-10',1,'Finalizada',NULL,NULL,0,0.00),(25,NULL,1,6,7,'2025-11-07 00:31:07','2025-11-07','2025-11-10',1,'Finalizada',NULL,NULL,0,0.00),(26,NULL,1,6,7,'2025-11-07 00:31:07','2025-11-07','2025-11-10',1,'Finalizada',NULL,NULL,0,0.00),(27,NULL,8,2,7,'2025-11-07 01:41:28','2025-11-08','2025-11-09',1,'Finalizada',NULL,NULL,0,0.00),(28,NULL,8,3,7,'2025-11-07 01:56:29','2025-11-07','2025-11-10',1,'Finalizada',NULL,NULL,0,0.00),(29,NULL,5,4,6,'2025-11-07 02:11:28','2025-11-07','2025-11-11',1,'Finalizada',NULL,NULL,4,480.00),(30,NULL,8,3,7,'2025-11-07 02:12:34','2025-11-07','2025-11-10',1,'Finalizada',NULL,NULL,3,360.00),(31,NULL,5,1,6,'2025-11-07 02:23:56','2025-11-08','2025-11-09',1,'Cancelada','Cancelado por el cliente','2025-11-07 11:27:21',1,80.00),(32,NULL,5,NULL,6,'2025-11-07 02:39:43','2025-11-08','2025-11-08',1,'Cancelada',NULL,NULL,0,0.00),(33,NULL,5,2,6,'2025-11-07 11:10:05','2025-11-07','2025-11-08',1,'Cancelada',NULL,NULL,1,80.00),(34,NULL,5,NULL,6,'2025-11-07 11:19:03','2025-11-07','2025-11-07',1,'Cancelada',NULL,NULL,0,0.00),(35,'CHAT-066388B6',9,1,NULL,'2025-11-07 11:44:20','2025-11-08','2025-11-09',1,'Cancelada',NULL,NULL,0,0.00),(36,NULL,7,5,8,'2025-11-07 21:43:26','2025-11-08','2025-11-11',1,'Cancelada','Cancelado por el cliente','2025-11-07 22:55:29',3,540.00),(37,NULL,7,5,8,'2025-11-07 23:12:55','2025-11-08','2025-11-09',1,'Cancelada','Cancelado por el cliente','2025-11-07 23:19:19',1,180.00),(38,NULL,7,6,8,'2025-11-07 23:17:58','2025-11-08','2025-11-11',1,'Cancelada','Cancelado por el cliente','2025-11-07 23:19:22',3,540.00),(39,NULL,7,5,8,'2025-11-07 23:20:12','2025-11-08','2025-11-11',1,'Cancelada','Cancelado por el cliente','2025-11-08 00:01:36',3,540.00),(40,NULL,7,6,8,'2025-11-07 23:25:27','2025-11-08','2025-11-11',1,'Cancelada','Cancelado por el cliente','2025-11-08 00:01:54',3,540.00),(41,NULL,7,NULL,8,'2025-11-08 00:02:27','2025-11-14','2025-11-14',1,'Activa',NULL,NULL,0,0.00),(42,NULL,7,NULL,8,'2025-11-08 00:04:50','2025-11-12','2025-11-12',1,'Activa',NULL,NULL,0,0.00),(43,NULL,7,NULL,8,'2025-11-08 00:13:37','2025-11-13','2025-11-13',1,'Activa',NULL,NULL,0,0.00),(44,NULL,7,NULL,8,'2025-11-08 00:19:38','2025-11-08','2025-11-08',1,'Activa',NULL,NULL,0,0.00),(45,NULL,7,1,8,'2025-11-08 00:41:15','2025-11-09','2025-11-10',1,'Cancelada','Cancelado por el cliente','2025-11-08 00:41:40',1,80.00),(46,NULL,7,3,8,'2025-11-08 00:45:38','2025-11-08','2025-11-09',1,'Cancelada','Cancelado por el cliente','2025-11-08 00:46:05',1,120.00),(47,NULL,7,1,8,'2025-11-08 00:47:56','2025-11-09','2025-11-10',1,'Cancelada','Cancelado por el cliente','2025-11-08 00:48:25',1,80.00),(48,NULL,7,1,8,'2025-11-09 23:23:57','2025-11-10','2025-11-12',1,'Finalizada',NULL,NULL,2,160.00),(49,NULL,7,5,8,'2025-11-13 21:49:24','2025-11-14','2025-11-20',1,'Cancelada','Cancelado por el cliente','2025-11-19 00:21:10',6,1080.00);
/*!40000 ALTER TABLE `reservas` ENABLE KEYS */;

/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador'),(2,'Recepcionista'),(3,'Cliente'),(4,'Mantenimiento');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;

/*!40000 ALTER TABLE `servicio_reservado` DISABLE KEYS */;
/*!40000 ALTER TABLE `servicio_reservado` ENABLE KEYS */;

/*!40000 ALTER TABLE `servicios` DISABLE KEYS */;
INSERT INTO `servicios` VALUES (1,'Spa','Acceso al spa con sauna y jacuzzi',80.00,0,'unico'),(2,'Piscina','Uso de piscina con toallas incluidas',25.00,0,'multiple'),(3,'Coworking','Acceso a sala coworking por día',50.00,0,'unico'),(4,'Lavandería','Servicio de lavado y planchado',20.00,1,'unico'),(5,'Desayuno buffet','Desayuno completo en el restaurante',30.00,0,'unico'),(6,'Spa y masajes relajantes','Sesión de spa con masajes y aromaterapia.',90.00,1,'unico'),(7,'Sauna y jacuzzi','Acceso por 30 minutos al sauna seco y jacuzzi.',60.00,1,'unico'),(8,'Gimnasio','Uso libre del gimnasio con entrenador disponible.',40.00,1,'unico'),(9,'Piscina','Acceso a la piscina por el día, incluye toalla.',25.00,1,'multiple'),(10,'Desayuno buffet','Desayuno completo en el restaurante.',30.00,1,'multiple'),(11,'Almuerzo ejecutivo','Menú del día con bebida y postre.',40.00,1,'multiple'),(12,'Cena gourmet','Cena especial con entrada, plato fuerte y vino.',55.00,1,'multiple'),(13,'Servicio de bar','Acceso al bar con carta de cócteles y snacks.',35.00,1,'multiple'),(14,'Sala de coworking','Espacio equipado para trabajo remoto por día.',50.00,1,'unico'),(15,'Salón de conferencias o reuniones','Alquiler por hora del salón con proyector.',150.00,1,'unico'),(16,'Tour local','Recorrido guiado por los principales atractivos de Chiclayo.',120.00,1,'multiple');
/*!40000 ALTER TABLE `servicios` ENABLE KEYS */;

/*!40000 ALTER TABLE `tipo_habitacion` DISABLE KEYS */;
INSERT INTO `tipo_habitacion` VALUES (1,'Individual','Habitación con una cama individual',1,80.00,'WiFi, TV Cable'),(2,'Doble','Habitación con dos camas o matrimonial',2,120.00,'WiFi, Aire Acondicionado, Desayuno'),(3,'Familiar','Habitación amplia para 4 personas',4,180.00,'WiFi, TV Cable, Aire Acondicionado, Desayuno, Minibar');
/*!40000 ALTER TABLE `tipo_habitacion` ENABLE KEYS */;

/*!40000 ALTER TABLE `tipo_pago` DISABLE KEYS */;
INSERT INTO `tipo_pago` VALUES (1,'Transferencia bancaria'),(2,'Tarjeta de credito/debito'),(3,'Yape'),(4,'Plin');
/*!40000 ALTER TABLE `tipo_pago` ENABLE KEYS */;

/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'00000000','Anghelo Jamir','Merino Mayra','jamir_anghelo@hotmail.com','$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM','+51942030088',1,4),(3,NULL,'Jamir','Casa','jamir@lsp.com','$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM','+1111111111111',1,3),(4,NULL,'LILIANA','MAYRA','lorena@lsp.com','$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM','+1111111111111111',1,3),(5,NULL,'Jose','Fiestas','josefiestas@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM','+58123456789',1,3),(6,'16712223','Lorena','Merino','lorena_yjl@hotmail.com','$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM','+51971868785',1,3),(7,'72318704','Jamir','Merino Mayra','jamir@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$zZXEbH6c5A27baHq+T9elA$mhSVUX8lbBaHzVbSFhv/3xD8AB1+S87ZIdaROKitIuM','+51942030088',1,1),(8,'72318705','Jamir','Merino Mayra','jamir_merino@hotmail.com','$argon2id$v=19$m=65536,t=3,p=4$sCuxQ29bn++odGShDO06Kg$ww5OdRxnAhSX5Y6UMeU3I5lf5+IDHP1KVv4UXhnZR0Y','+51942030088',1,3),(9,'72318703','Isis','Dulcemaria','','','',1,3);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;

/*!40000 ALTER TABLE `valoraciones` DISABLE KEYS */;
INSERT INTO `valoraciones` VALUES (1,7,48,5,'Buena estadia','2025-11-18 23:24:23');
/*!40000 ALTER TABLE `valoraciones` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


-- =========================
--  END DATA SECTION
-- =========================

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


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

CREATE DATABASE IF NOT EXISTS /*!32312 IF NOT EXISTS*/ `proyectomoviles` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `proyectomoviles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `calificaciones` (
  `id_calificacion` int NOT NULL AUTO_INCREMENT,
  `viaje_id` int DEFAULT NULL,
  `evaluador_id` int DEFAULT NULL,
  `evaluado_id` int DEFAULT NULL,
  `rol_evaluador` varchar(20) DEFAULT NULL COMMENT 'Pasajero o Conductor',
  `puntuacion` int DEFAULT NULL,
  `comentario` text,
  `fecha_calificacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_calificacion`),
  KEY `viaje_id` (`viaje_id`),
  KEY `evaluador_id` (`evaluador_id`),
  KEY `evaluado_id` (`evaluado_id`),
  CONSTRAINT `calificaciones_ibfk_1` FOREIGN KEY (`viaje_id`) REFERENCES `viajes` (`id`),
  CONSTRAINT `calificaciones_ibfk_2` FOREIGN KEY (`evaluador_id`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `calificaciones_ibfk_3` FOREIGN KEY (`evaluado_id`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `calificaciones_chk_1` CHECK ((`puntuacion` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `calificaciones` VALUES (1,5,1,2,'Pasajero',5,'Excelente conductor, muy puntual.','2025-06-24 12:33:28'),(2,6,1,2,'Pasajero',4,'Buen servicio, pero la música estaba algo alta.','2025-06-24 12:33:28'),(3,7,1,2,'Pasajero',1,'Muy amable y responsable.','2025-06-24 12:33:28'),(4,5,2,1,'Conductor',5,'Pasajero respetuoso y puntual.','2025-06-24 12:33:28'),(5,5,2,1,'Conductor',4,'Todo bien, aunque se demoró un poco en llegar al punto de encuentro.','2025-06-24 12:33:28'),(6,7,2,1,'Conductor',5,'Muy educado, lo llevaría de nuevo.','2025-06-24 12:33:28'),(7,5,2,1,'Conductor',5,'Pasajero respetuoso y puntual.','2025-06-28 20:42:54'),(8,5,2,1,'Conductor',4,'Todo bien, aunque se demoró un poco en llegar al punto de encuentro.','2025-06-28 20:42:54'),(9,7,2,1,'Conductor',5,'Muy educado, lo llevaría de nuevo.','2025-06-28 20:42:54'),(18,5,3,2,'Conductor',5,'Excelente comportamiento','2025-06-29 00:04:28'),(26,5,4,2,'Conductor',4,'Buen pasajero','2025-06-29 00:06:57'),(27,5,5,2,'Conductor',4,'Fue puntual','2025-06-29 00:07:06'),(29,6,11,2,'Conductor',3,'Podría mejorar la comunicación','2025-06-29 00:07:47'),(30,6,7,2,'Conductor',5,'Muy respetuoso','2025-06-29 00:07:47'),(31,7,8,2,'Conductor',4,'Sin inconvenientes','2025-06-29 00:07:47'),(32,7,9,2,'Conductor',5,'Recomiendo al pasajero','2025-06-29 00:07:47'),(33,8,10,2,'Conductor',5,'Excelente trato','2025-06-29 00:07:47'),(50,9,2,1,'Pasajero',3,'dzsfbc','2025-07-01 02:52:06'),(51,9,10,1,'Pasajero',NULL,NULL,'2025-07-01 02:42:30'),(52,9,11,1,'Pasajero',NULL,NULL,'2025-07-01 02:42:30'),(53,20,2,1,'Pasajero',4,'gaaa','2025-07-02 00:22:28'),(54,20,3,1,'Pasajero',3,'adasdas','2025-07-02 00:22:45');
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `chats` (
  `id_chat` int NOT NULL AUTO_INCREMENT,
  `viaje_id` int DEFAULT NULL,
  `conductor_id` int DEFAULT NULL,
  `pasajero_id` int DEFAULT NULL,
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_chat`),
  KEY `conductor_id` (`conductor_id`),
  KEY `pasajero_id` (`pasajero_id`),
  KEY `viaje_id` (`viaje_id`),
  CONSTRAINT `chats_ibfk_1` FOREIGN KEY (`conductor_id`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `chats_ibfk_2` FOREIGN KEY (`pasajero_id`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `chats_ibfk_3` FOREIGN KEY (`viaje_id`) REFERENCES `viajes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `chats` VALUES (7,21,1,2,'2025-07-02 03:54:22'),(8,21,1,3,'2025-07-02 05:07:54');
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `mensajes` (
  `id_mensaje` int NOT NULL AUTO_INCREMENT,
  `id_chat` int NOT NULL,
  `emisor_id` int NOT NULL,
  `mensaje` text,
  `tipo` enum('texto','imagen','audio') DEFAULT 'texto',
  `url_archivo` varchar(255) DEFAULT NULL,
  `enviado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mensaje`),
  KEY `id_chat` (`id_chat`),
  KEY `emisor_id` (`emisor_id`),
  CONSTRAINT `mensajes_ibfk_1` FOREIGN KEY (`id_chat`) REFERENCES `chats` (`id_chat`),
  CONSTRAINT `mensajes_ibfk_2` FOREIGN KEY (`emisor_id`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `mensajes` VALUES (11,7,2,'Hola vrocito','texto',NULL,'2025-07-02 05:02:10'),(12,7,2,'Odio a plis y a toda su familia de muertos','texto',NULL,'2025-07-02 05:02:24'),(13,7,2,'GAAAAAAAAAA','texto',NULL,'2025-07-02 05:02:28'),(14,8,3,'Miedo','texto',NULL,'2025-07-02 05:08:04'),(15,7,1,'Vrocito','texto',NULL,'2025-07-02 05:24:19'),(16,7,1,'GAAA','texto',NULL,'2025-07-02 05:24:23'),(17,7,1,'CAMILA SIALER PUTA GAAA','texto',NULL,'2025-07-02 05:25:44'),(18,7,1,'bena','texto',NULL,'2025-07-02 05:40:39'),(19,7,1,'vreo','texto',NULL,'2025-07-02 06:24:17');
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `reservas` (
  `id_reserva` int NOT NULL AUTO_INCREMENT,
  `viaje_id` int DEFAULT NULL,
  `pasajero_id` int DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL COMMENT 'Pendiente, Confirmada, Cancelada',
  `fecha_reserva` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `qr_token` varchar(255) DEFAULT NULL,
  `confirmado_qr` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_reserva`),
  KEY `viaje_id` (`viaje_id`),
  KEY `pasajero_id` (`pasajero_id`),
  CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`viaje_id`) REFERENCES `viajes` (`id`),
  CONSTRAINT `reservas_ibfk_2` FOREIGN KEY (`pasajero_id`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `reservas` VALUES (33,5,1,'Finalizado','2025-06-22 18:40:50','XYZ',0),(34,5,1,'Finalizado','2025-06-22 18:50:16','XYZ',0),(35,5,1,'Finalizado','2025-06-22 18:50:43','XYZ',0),(36,5,1,'Finalizado','2025-06-22 18:52:56','XYZ',0),(37,5,1,'Cancelada','2025-06-22 18:57:39','XYZ',0),(38,6,1,'Cancelada','2025-06-23 03:31:30','XYZ',0),(39,5,1,'Cancelada','2025-06-23 03:41:10','XYZ',0),(40,5,1,'Cancelada','2025-06-23 04:09:05','XYZ',0),(41,6,1,'Cancelada','2025-06-23 04:19:54','XYZ',0),(42,5,1,'Cancelada','2025-06-23 04:27:16','XYZ',0),(43,5,1,'Cancelada','2025-06-23 04:27:40','XYZ',0),(44,5,1,'Cancelada','2025-06-23 04:28:58','XYZ',0),(45,5,1,'Cancelada','2025-06-23 04:31:23','XYZ',0),(46,5,1,'Cancelada','2025-06-23 05:09:33','XYZ',0),(47,5,1,'Cancelada','2025-06-23 05:22:35','XYZ',0),(48,6,1,'Cancelada','2025-06-23 05:30:54','XYZ',0),(49,7,1,'Cancelada','2025-06-23 05:49:41','XYZ',0),(50,5,1,'Cancelada','2025-06-24 13:38:36','XYZ',0),(51,6,1,'Cancelada','2025-06-24 13:39:49','RESERVA-XYZ-20250625-114910',0),(52,6,1,'Cancelada','2025-06-24 15:46:23','9009663e-b35b-4e4a-94bc-50a0ac7d09b7',0),(53,5,1,'Cancelada','2025-06-25 19:37:04','ba67cda1-2447-455c-8ede-b60e4d13d700',0),(54,6,1,'Finalizado','2025-06-25 19:41:23','5fd775ab-5722-4480-aa2a-539f3c6576c',0),(56,8,2,'Finalizado','2025-06-29 00:36:39','217a4070-96ea-4ede-8234-bd8d6f35db60',1),(57,8,4,'Finalizado','2025-06-29 16:47:15','941c1fac-c061-4bf7-9cb3-fe0fb55a1194',0),(58,8,10,'Finalizado','2025-06-29 17:33:19','2b34c5f1-9f0d-4261-839c-f18f5fed7a75',0),(59,8,10,'Finalizado','2025-06-29 17:47:05','f8e7b20a-9d29-498e-80bd-db2783aa3123',0),(60,8,10,'Finalizado','2025-06-29 17:49:27','7dbe5bba-e022-4c16-8e3d-d8827e8605f8',0),(61,8,10,'Finalizado','2025-06-29 17:50:32','3ce882ea-98b0-4192-88ff-d25df9a50024',0),(71,9,2,'Finalizado','2025-07-01 01:42:25','c2c49adb-f78e-41bd-a620-4e7fb2bf1532',1),(72,9,2,'Finalizado','2025-07-01 02:27:56','4423835b-5142-460b-a484-9fd2457dbcac',1),(74,9,10,'Finalizado','2025-07-01 02:33:06','029833f5-4f76-4b74-acf5-1a22d1a4121a',1),(75,9,11,'Finalizado','2025-07-01 02:34:44','d1a9593b-ccb3-4dae-85e0-6386c889ea15',1),(82,20,2,'Finalizado','2025-07-02 00:18:20','585c06f6-5634-4c66-9231-ae30c94dd602',1),(83,20,3,'Finalizado','2025-07-02 00:18:38','3d764b28-adb8-4913-b37c-b5a703eab7f4',1),(84,21,2,'Cancelada','2025-07-02 02:03:05','e25e257c-1cb8-4d4f-bd9e-d21d5a6e5a9b',0),(85,21,3,'Cancelada','2025-07-02 05:06:54','6463b8b8-e801-4b34-946f-0964657e28e3',0);
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `tipo_usuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `des_tipo` varchar(50) DEFAULT NULL COMMENT 'Pasajero, Conductor, Ambos',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `tipo_usuario` VALUES (1,'Pasajero'),(2,'Conductor'),(3,'Ambos');
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `usuario_fcm` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `dispositivo` varchar(100) NOT NULL,
  `token` text NOT NULL,
  `fecha_hora_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `usuario_fcm_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `usuario_fcm` VALUES (5,1,'Samsung Galaxy A21s de Angel','f43egfvKRxOkz64z3Jr5YL:APA91bEFwSyW96V0lmt2GTUFmsQ0Q2Py3i63H7k2nY0HDW1lYoO5_CBgqsYiW7Le8BjP-23WzyRMECmRz0Sav1r8d_89WB-G59B09jpzj_f_xuAcOIzogKI','2025-06-25 23:09:55',1),(6,1,'Lenovo Tab M10 Plus 3rd Gen','f_Ja-5M2QwKZzH6y-t7arb:APA91bFd3FqmGLPgtALiokRl-ahlrnp5zaX4kGCkKspg8IDsHr1EGKx3Nh2IirXoqzhpZEUC6c8nOdfg5u86EgG8IHSmWLxxML4_aDTJCkO26DlQHUYeNN4','2025-06-26 20:07:03',1),(7,2,'Samsung Galaxy A21s de Angel','f43egfvKRxOkz64z3Jr5YL:APA91bEFwSyW96V0lmt2GTUFmsQ0Q2Py3i63H7k2nY0HDW1lYoO5_CBgqsYiW7Le8BjP-23WzyRMECmRz0Sav1r8d_89WB-G59B09jpzj_f_xuAcOIzogKI','2025-06-28 23:37:43',1),(8,4,'Samsung Galaxy A21s de Angel','f43egfvKRxOkz64z3Jr5YL:APA91bEFwSyW96V0lmt2GTUFmsQ0Q2Py3i63H7k2nY0HDW1lYoO5_CBgqsYiW7Le8BjP-23WzyRMECmRz0Sav1r8d_89WB-G59B09jpzj_f_xuAcOIzogKI','2025-06-29 16:47:10',1),(9,10,'Samsung Galaxy A21s de Angel','f43egfvKRxOkz64z3Jr5YL:APA91bEFwSyW96V0lmt2GTUFmsQ0Q2Py3i63H7k2nY0HDW1lYoO5_CBgqsYiW7Le8BjP-23WzyRMECmRz0Sav1r8d_89WB-G59B09jpzj_f_xuAcOIzogKI','2025-06-29 17:31:27',1),(10,11,'Samsung Galaxy A21s de Angel','f43egfvKRxOkz64z3Jr5YL:APA91bEFwSyW96V0lmt2GTUFmsQ0Q2Py3i63H7k2nY0HDW1lYoO5_CBgqsYiW7Le8BjP-23WzyRMECmRz0Sav1r8d_89WB-G59B09jpzj_f_xuAcOIzogKI','2025-07-01 02:34:40',1),(11,3,'Samsung Galaxy A21s de Angel','f43egfvKRxOkz64z3Jr5YL:APA91bEFwSyW96V0lmt2GTUFmsQ0Q2Py3i63H7k2nY0HDW1lYoO5_CBgqsYiW7Le8BjP-23WzyRMECmRz0Sav1r8d_89WB-G59B09jpzj_f_xuAcOIzogKI','2025-07-02 00:18:33',1),(12,16,'Galaxy Note10+','cTuqMp-SRoKQDKzITvSf9d:APA91bHfKRoxb-3tAZiiZLlu9g86S4xQ_0vXDpl8YrRBuhqBHhigHBYG0hIqKqo4vP962BgJrIR1KmZs8m5HZFJaOM7nguPb4iADV2toPv_ZmBSeQnbSxEk','2025-07-03 17:55:02',1),(13,1,'Galaxy Note10+','cTuqMp-SRoKQDKzITvSf9d:APA91bHfKRoxb-3tAZiiZLlu9g86S4xQ_0vXDpl8YrRBuhqBHhigHBYG0hIqKqo4vP962BgJrIR1KmZs8m5HZFJaOM7nguPb4iADV2toPv_ZmBSeQnbSxEk','2025-07-03 17:59:50',1);
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `contraseña` varchar(255) DEFAULT NULL,
  `tipo_usuario` int DEFAULT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `latitud` double DEFAULT NULL,
  `longitud` double DEFAULT NULL,
  `estado` tinyint(1) DEFAULT '1',
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `validado` tinyint(1) DEFAULT '0',
  `direccion` varchar(255) DEFAULT NULL,
  `admin` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_usuario`),
  KEY `tipo_usuario` (`tipo_usuario`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`tipo_usuario`) REFERENCES `tipo_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `usuarios` VALUES (1,'Angel','angelmontenegro122003@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$DhuQucaekZr1yu11XfTSzQ$+72Neob1Licd0LMxPmTp9DdVMdVGbsNIwigVp73uIxo',1,'968633311','xd.png',-6.767053711423482,-79.8493471913728,1,'2025-06-11 14:13:24',1,'Yurimaguas 165',0),(2,'Carlos Pérez','carlos@example.com','$argon2id$v=19$m=65536,t=3,p=4$DhuQucaekZr1yu11XfTSzQ$+72Neob1Licd0LMxPmTp9DdVMdVGbsNIwigVp73uIxo',1,'912345678','Screenshot_20250504-130510_Binance.jpg',-6.7732,-79.845,1,'2025-06-11 14:13:24',1,'Los trambos 277',0),(3,'Lucía Gómez','lucia@example.com','$argon2id$v=19$m=65536,t=3,p=4$DhuQucaekZr1yu11XfTSzQ$+72Neob1Licd0LMxPmTp9DdVMdVGbsNIwigVp73uIxo',2,'956789432','lucia.jpg',-6.772,-79.8415,1,'2025-06-11 14:13:24',1,NULL,0),(4,'Ricardo','ricardoherrerac8gmail.com','$argon2id$v=19$m=65536,t=3,p=4$DhuQucaekZr1yu11XfTSzQ$+72Neob1Licd0LMxPmTp9DdVMdVGbsNIwigVp73uIxo',1,'945674347','xd.png',-6.7715,-79.8409,1,'2025-06-13 23:59:12',1,'Mierda 123',0),(5,'Papoi','angel1210yt@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$sz0olPSsAzOof5V21//zCA$Has75HbKkXo+ZedHu17DIpahXQkT5HsG/wb0JM3lpuk',1,'968567234',NULL,-6.7715,-79.8409,1,'2025-06-16 02:17:06',1,NULL,0),(7,'Fernando','fernando@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$TGfxtMpAmoImWWRrK7uuAw$0oktKuV1puWFfi3Owz1Pz9eV9nWVbWYixXainkgnhig',2,'354837745','xd.png',47.92076625579733,106.89958533341867,1,'2025-06-16 04:54:00',1,NULL,0),(8,'hispenw','mierda@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$BgYrgaDUS/DPoMfRsU3MMg$ZbmU4fpmPLrknIM2Tw7K8cg6d0LOvgalcIzU9nsaEx0',2,'645945615','xd.png',-6.7715,-79.8409,1,'2025-06-16 15:14:07',1,NULL,0),(9,'Jamir','jamir_merino@hotmail.com','$argon2id$v=19$m=65536,t=3,p=4$DhuQucaekZr1yu11XfTSzQ$+72Neob1Licd0LMxPmTp9DdVMdVGbsNIwigVp73uIxo',2,'942030088','Screenshot_20250504-130510_Binance.jpg',-6.756072982172424,-79.8391642794013,1,'2025-06-16 15:27:26',1,'Atahualpa, José Leonardo Ortiz, Chiclayo, Lambayeque, 14009, Perú',1),(10,'Luis','santamaria@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$LbZ8f20q0rnHBZ48N9E2eA$VUlItGJuLsiynYwW2BAV2A8qERaOYU8MBf9tZUE0Y7Q',1,'938838838','Screenshot_20250616-165011_PapoiMovil.jpg',-6.775169834290604,-79.83582593500614,1,'2025-06-18 14:27:48',1,'Morrope',0),(11,'viruela','richicabro@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$x5BtM4gCdLU183NeUS2P+g$b7BoCqOquv7Nm0dhhbSVQDzXB86uwnnquibvKaWiza4',1,'736736736','Screenshot_20250616-165011_PapoiMovil.jpg',-6.7714572640235025,-79.83867712318897,1,'2025-06-21 06:36:51',1,'Plaza de Armas, Avenida San José, Chiclayo, Lambayeque, 14001, Perú',0),(12,'aaa','a@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$sFVjIiFNVwhnIAGdgXGlXQ$c7L8ddozLvNJCqN375a68fnME8o0PXBshZ+Yf5uHWWo',1,'378378764','Screenshot_20250616-165007_PapoiMovil.jpg',-6.759902201581069,-79.83485732227564,1,'2025-06-21 06:56:06',1,'Calle Los Libertadores, José Leonardo Ortiz, Chiclayo, Lambayeque, 14001, Perú',0),(13,'prueba ubi','pruebaubi@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$n249EuFc7i6WzrALknfKew$TZHRvjLxordpZ4FnqOPLlmxbCaMWK4gj+uUBvKoBexw',1,'888777663','Screenshot_20250504-130510_Binance.jpg',-6.777817990436348,-79.87987652420998,1,'2025-06-23 05:32:22',1,'Universidad de San Martín de Porres, Avenida La Pradera, Pueblo Joven El Trebol, Pimentel, Chiclayo, Lambayeque, 14009, Perú',0),(14,'pruebaxd','pruebaxd@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$FoAli9sbYP+y6Zny7n/IZw$bIwwa4VJlcD7OjG7lySnCgtnqzKb/cQ+JQL+H9TBRFk',1,'645645645','images_1.jpeg',-6.7728632564653335,-79.83731959015131,1,'2025-07-02 14:58:53',0,'640, Calle 7 de Enero, Chiclayo, Lambayeque, 14001, Perú',0),(15,'Administrador','administrador@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$FoAli9sbYP+y6Zny7n/IZw$bIwwa4VJlcD7OjG7lySnCgtnqzKb/cQ+JQL+H9TBRFk',1,'999999999',NULL,NULL,NULL,1,'2025-07-02 15:00:04',1,NULL,1),(16,'Isis','isis@hotmail.com','$argon2id$v=19$m=65536,t=3,p=4$DhuQucaekZr1yu11XfTSzQ$+72Neob1Licd0LMxPmTp9DdVMdVGbsNIwigVp73uIxo',1,'987654321','IMG-20250627-WA0002.jpg',-6.763366152384141,-79.83741749078035,1,'2025-07-03 17:50:49',1,'Agua Viva, 188, Calle Cois, Chiclayo, Lambayeque, 14001, Perú',0);
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `vehiculos` (
  `id_vehiculo` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `marca` varchar(50) DEFAULT NULL,
  `modelo` varchar(50) DEFAULT NULL,
  `placa` varchar(20) DEFAULT NULL,
  `color` varchar(30) DEFAULT NULL,
  `validado` tinyint(1) DEFAULT '0',
  `asientos` int DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_vehiculo`),
  UNIQUE KEY `placa` (`placa`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `vehiculos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `vehiculos` VALUES (1,7,'Toyota','Yaris','ABC-123','Gris',1,4,'gaa.png'),(2,2,'Hyundai','Accent','XYZ-456','Negro',1,4,'gaa.png'),(4,1,'Toyota','Yaris','ABC-444','Gris',1,4,'gaa.png'),(5,11,'Richi','Richi','BDC-233','Marron mierda',1,10,'gaa.png'),(6,13,'carro','carro','333NNN','verde',1,4,'gaa.png'),(7,9,'Toyota','Yaria','M4Y-202','Gris',1,4,'IMG-20250627-WA0000.jpg');
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `viajes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vehiculo_id` int DEFAULT NULL,
  `punto_partida` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `destino` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `lat_partida` double DEFAULT NULL,
  `lng_partida` double DEFAULT NULL,
  `lat_destino` double DEFAULT NULL,
  `lng_destino` double DEFAULT NULL,
  `fecha_hora_salida` timestamp NULL DEFAULT NULL,
  `asientos_disponibles` int DEFAULT NULL,
  `restricciones` varchar(255) DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL COMMENT 'Activo, Finalizado, Cancelado',
  PRIMARY KEY (`id`),
  KEY `vehiculo_id` (`vehiculo_id`),
  CONSTRAINT `viajes_ibfk_1` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id_vehiculo`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `viajes` VALUES (5,2,'Universidad de San Martín de Porres, Avenida La Pradera, Pueblo Joven El Trebol, Pimentel, Chiclayo, Lambayeque, 14009, Perú','USAT',-6.7732,-79.845,-6.760361421400738,-79.86303878679222,'2025-06-23 15:30:39',3,'Ninguna','Cancelado'),(6,2,'Universidad de San Martín de Porres, Avenida La Pradera, Pueblo Joven El Trebol, Pimentel, Chiclayo, Lambayeque, 14009, Perú','USAT',-6.7732,-79.845,-6.760361421400738,-79.86303878679222,'2025-06-25 16:49:10',4,'a','Cancelado'),(7,6,'Universidad de San Martín de Porres, Avenida La Pradera, Pueblo Joven El Trebol, Pimentel, Chiclayo, Lambayeque, 14009, Perú','USAT',-6.777817990436348,-79.87987652420998,-6.760361421400738,-79.86303878679222,'2025-06-24 23:30:44',3,'aaa','Activo'),(8,4,'Yurimaguas 165','USAT',-6.767053711423482,-79.8493471913728,-6.760361421400738,-79.86303878679222,'2025-06-30 20:43:06',0,'aaa','Finalizado'),(9,4,'Yurimaguas 165','USAT',-6.767053711423482,-79.8493471913728,-6.760361421400738,-79.86303878679222,'2025-07-01 07:30:00',2,'Nada','Finalizado'),(20,4,'Yurimaguas 165','USAT',-6.767053711423482,-79.8493471913728,-6.760361421400738,-79.86303878679222,'2025-07-02 00:50:57',2,'nada','Finalizado'),(21,4,'Yurimaguas 165','USAT',-6.767053711423482,-79.8493471913728,-6.760361421400738,-79.86303878679222,'2025-07-04 02:30:12',2,'aa','Cancelado'),(22,7,'Yurimaguas 165','USAT',-6.7715,-79.8409,-6.760361421400738,-79.86303878679222,'2025-07-03 06:40:00',4,NULL,'Activo');
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


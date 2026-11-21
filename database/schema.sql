CREATE DATABASE IF NOT EXISTS veterinaria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE veterinaria_db;

CREATE TABLE clientes (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, nombres VARCHAR(100) NOT NULL, apellidos VARCHAR(100) NOT NULL,
  dni VARCHAR(20) NOT NULL UNIQUE, telefono VARCHAR(30) NOT NULL, correo VARCHAR(150), direccion VARCHAR(255),
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX idx_clientes_nombre (apellidos, nombres)
) ENGINE=InnoDB;
CREATE TABLE veterinarios (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, nombres VARCHAR(100) NOT NULL, apellidos VARCHAR(100) NOT NULL,
  dni VARCHAR(20) NOT NULL UNIQUE, telefono VARCHAR(30) NOT NULL, correo VARCHAR(150), especialidad VARCHAR(120) NOT NULL,
  estado ENUM('activo','inactivo') NOT NULL DEFAULT 'activo', INDEX idx_veterinarios_estado (estado)
) ENGINE=InnoDB;
CREATE TABLE servicios (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(120) NOT NULL UNIQUE, descripcion TEXT, precio DECIMAL(10,2) NOT NULL,
  duracion_minutos SMALLINT UNSIGNED NOT NULL, estado ENUM('activo','inactivo') NOT NULL DEFAULT 'activo'
) ENGINE=InnoDB;
CREATE TABLE mascotas (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, cliente_id INT UNSIGNED NOT NULL, nombre VARCHAR(100) NOT NULL, especie VARCHAR(60) NOT NULL,
  raza VARCHAR(100), sexo ENUM('Macho','Hembra') NOT NULL, fecha_nacimiento DATE, peso DECIMAL(6,2), color VARCHAR(80), observaciones TEXT,
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT fk_mascota_cliente FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
  INDEX idx_mascotas_nombre(nombre), INDEX idx_mascotas_cliente(cliente_id)
) ENGINE=InnoDB;
CREATE TABLE citas (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, mascota_id INT UNSIGNED NOT NULL, veterinario_id INT UNSIGNED NOT NULL, servicio_id INT UNSIGNED NOT NULL,
  fecha DATE NOT NULL, hora TIME NOT NULL, motivo TEXT NOT NULL, observaciones TEXT, estado ENUM('Pendiente','Confirmada','En atención','Completada','Cancelada') NOT NULL DEFAULT 'Pendiente',
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT fk_cita_mascota FOREIGN KEY(mascota_id) REFERENCES mascotas(id) ON DELETE RESTRICT,
  CONSTRAINT fk_cita_veterinario FOREIGN KEY(veterinario_id) REFERENCES veterinarios(id) ON DELETE RESTRICT,
  CONSTRAINT fk_cita_servicio FOREIGN KEY(servicio_id) REFERENCES servicios(id) ON DELETE RESTRICT,
  UNIQUE KEY uq_veterinario_horario(veterinario_id, fecha, hora), INDEX idx_citas_fecha(fecha), INDEX idx_citas_estado(estado)
) ENGINE=InnoDB;
CREATE TABLE historial_clinico (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, mascota_id INT UNSIGNED NOT NULL, veterinario_id INT UNSIGNED NOT NULL, fecha_atencion DATE NOT NULL,
  motivo_consulta TEXT NOT NULL, diagnostico TEXT, tratamiento TEXT, observaciones TEXT,
  CONSTRAINT fk_historial_mascota FOREIGN KEY(mascota_id) REFERENCES mascotas(id) ON DELETE CASCADE,
  CONSTRAINT fk_historial_veterinario FOREIGN KEY(veterinario_id) REFERENCES veterinarios(id) ON DELETE RESTRICT, INDEX idx_historial_mascota(mascota_id)
) ENGINE=InnoDB;
CREATE TABLE vacunas (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, mascota_id INT UNSIGNED NOT NULL, veterinario_id INT UNSIGNED, nombre_vacuna VARCHAR(120) NOT NULL,
  fecha_aplicacion DATE NOT NULL, proxima_dosis DATE, observaciones TEXT,
  CONSTRAINT fk_vacuna_mascota FOREIGN KEY(mascota_id) REFERENCES mascotas(id) ON DELETE CASCADE,
  CONSTRAINT fk_vacuna_veterinario FOREIGN KEY(veterinario_id) REFERENCES veterinarios(id) ON DELETE SET NULL, INDEX idx_vacunas_proxima(proxima_dosis)
) ENGINE=InnoDB;

CREATE DATABASE IF NOT EXISTS ecotech_db
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ecotech_db;

CREATE TABLE IF NOT EXISTS departamento (
    id_departamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_gerente INT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(30) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    fecha_inicio_contrato DATE NOT NULL,
    salario DECIMAL(12,2) NOT NULL,
    id_departamento INT NULL,
    CONSTRAINT fk_empleado_departamento
        FOREIGN KEY (id_departamento)
        REFERENCES departamento(id_departamento)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS proyecto (
    id_proyecto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500) NOT NULL,
    fecha_inicio DATE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS empleado_proyecto (
    id_empleado INT NOT NULL,
    id_proyecto INT NOT NULL,
    PRIMARY KEY (id_empleado, id_proyecto),
    FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado)
        ON DELETE CASCADE,
    FOREIGN KEY (id_proyecto)
        REFERENCES proyecto(id_proyecto)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS registro_tiempo (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    id_proyecto INT NOT NULL,
    fecha DATE NOT NULL,
    horas_trabajadas DECIMAL(5,2) NOT NULL,
    descripcion_trabajo VARCHAR(500) NOT NULL,
    FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado)
        ON DELETE CASCADE,
    FOREIGN KEY (id_proyecto)
        REFERENCES proyecto(id_proyecto)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL UNIQUE,
    nombre_usuario VARCHAR(40) NOT NULL UNIQUE,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin','empleado') NOT NULL DEFAULT 'empleado',
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;


-- Historial local de observaciones recibidas desde APIs externas.
CREATE TABLE IF NOT EXISTS indicador_api (
    id_indicador BIGINT AUTO_INCREMENT PRIMARY KEY,
    fuente VARCHAR(80) NOT NULL,
    codigo VARCHAR(40) NOT NULL,
    fecha DATE NOT NULL,
    valor DECIMAL(18,6) NOT NULL,
    unidad VARCHAR(30) NOT NULL,
    verificado_en VARCHAR(40) NOT NULL,
    UNIQUE KEY uq_indicador_observacion (fuente, codigo, fecha)
) ENGINE=InnoDB;

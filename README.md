# MiTiendaMateo

En Workbench, o por consola, crear una base de datos con el nombre kioscomateo:

CREATE DATABASE kioscomateo;

Cambiar a la nueva base de datos para poder trabajar con ella:

USE kioscomateo;

Para verificar que se creó correctamente la BD:

SHOW DATABASES;

Crear las tablas con los comandos:

CREATE TABLE Marcas (
  ID_Marca INT AUTO_INCREMENT PRIMARY KEY,
  Nombre_Marca VARCHAR(50) NOT NULL UNIQUE,
  Borrado_Marca BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_M DATETIME DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE Provincias (
  ID_Provincia INT AUTO_INCREMENT PRIMARY KEY,
  Nombre_Provincia VARCHAR(50) NOT NULL UNIQUE,
  Borrado_Provincia BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_P DATETIME DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE Locales_Comerciales (
  ID_Loc_Com INT AUTO_INCREMENT PRIMARY KEY,
  ID_Provincia INT NOT NULL,
  Nombre_Loc_Com VARCHAR(100) NOT NULL,
  Cod_Postal_Loc_Com INT,
  Telefono_Loc_Com VARCHAR(30),
  Direccion_Loc_Com VARCHAR(100),
  Borrado_Loc_Com BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_LC DATETIME DEFAULT NULL,
  UNIQUE (ID_Provincia, Nombre_Loc_Com),
  CONSTRAINT fk_lc_prov FOREIGN KEY (ID_Provincia) REFERENCES Provincias(ID_Provincia)
) ENGINE=InnoDB;

CREATE TABLE Empleados (
  ID_Empleado INT AUTO_INCREMENT PRIMARY KEY,
  DNI_Emp BIGINT NOT NULL UNIQUE,
  Apellido_Emp VARCHAR(80) NOT NULL,
  Nombre_Emp VARCHAR(80) NOT NULL,
  Email_Emp VARCHAR(150) NOT NULL UNIQUE,
  Usuario_Emp VARCHAR(50) UNIQUE,
  Telefono_Emp VARCHAR(20),
  Domicilio_Emp VARCHAR(200),
  Fecha_Alta_Emp DATE NOT NULL,
  Fecha_Baja_Emp DATE,
  Contrasena_Emp VARCHAR(255) NOT NULL,
  Borrado_Emp BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_E DATETIME DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE EmpleadosXLocCom (
  ID_Empleado INT,
  ID_Loc_Com INT,
  Turno_ExLC VARCHAR(20) NOT NULL,
  Horas_Trabajadas INT NOT NULL,
  PRIMARY KEY (ID_Empleado, ID_Loc_Com),
  CONSTRAINT fk_exlc_emp FOREIGN KEY (ID_Empleado) REFERENCES Empleados(ID_Empleado),
  CONSTRAINT fk_exlc_lc FOREIGN KEY (ID_Loc_Com) REFERENCES Locales_Comerciales(ID_Loc_Com)
) ENGINE=InnoDB;

CREATE TABLE Billeteras_Virtuales (
  ID_BV INT AUTO_INCREMENT PRIMARY KEY,
  Nombre_BV VARCHAR(100) NOT NULL,
  Usuario_BV VARCHAR(100) NOT NULL UNIQUE,
  Contrasena_BV VARCHAR(255) NOT NULL,
  CBU_BV VARCHAR(22) UNIQUE,
  FH_Alta_BV DATETIME NOT NULL,
  FH_Baja_BV DATETIME NULL,
  Saldo_BV DECIMAL(12,2),
  Borrado_BV BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_BV DATETIME DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE Proveedores (
  ID_Proveedor INT AUTO_INCREMENT PRIMARY KEY,
  Cuit_Prov CHAR(15) NOT NULL UNIQUE,
  Nombre_Prov VARCHAR(150) NOT NULL,
  Telefono_Prov VARCHAR(20),
  Email_Prov VARCHAR(150),
  Direccion_Prov VARCHAR(100),
  Borrado_Prov BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_Prov DATETIME DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE Productos (
  ID_Producto INT AUTO_INCREMENT PRIMARY KEY,
  Nombre_Producto VARCHAR(150),
  Precio_Unit_Prod DECIMAL(10,2),
  Fecha_Venc_Prod DATE,
  Borrado_Prod BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_Prod DATETIME DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE ProveedoresXLocCom (
  ID_Proveedor INT,
  ID_Loc_Com INT,
  FH_Ultima_Visita DATETIME,
  Borrado_PxLC BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_PxLC DATETIME DEFAULT NULL,
  PRIMARY KEY (ID_Proveedor, ID_Loc_Com),
  CONSTRAINT fk_pxlc_proveedor FOREIGN KEY (ID_Proveedor) REFERENCES Proveedores(ID_Proveedor),
  CONSTRAINT fk_pxlc_loccom FOREIGN KEY (ID_Loc_Com) REFERENCES Locales_Comerciales(ID_Loc_Com)
) ENGINE=InnoDB;

CREATE TABLE ProveedoresXProductos (
  ID_Proveedor INT,
  ID_Producto INT,
  Costo_Compra DECIMAL(10,2),
  Borrado_PvXPr BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_PvXPr DATETIME DEFAULT NULL,
  PRIMARY KEY (ID_Proveedor, ID_Producto),
  CONSTRAINT fk_pvxpr_proveedor FOREIGN KEY (ID_Proveedor) REFERENCES Proveedores(ID_Proveedor),
  CONSTRAINT fk_pvxpr_prod FOREIGN KEY (ID_Producto) REFERENCES Productos(ID_Producto)
) ENGINE=InnoDB;

CREATE TABLE Stock (
  ID_Producto INT,
  ID_Loc_Com INT,
  Stock_PxLC INT NOT NULL,
  Stock_Min_PxLC INT NOT NULL DEFAULT 0,
  Borrado_PxLC BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_PxLC DATETIME DEFAULT NULL,
  PRIMARY KEY (ID_Producto, ID_Loc_Com),
  CONSTRAINT fk_prxlc_prod FOREIGN KEY (ID_Producto) REFERENCES Productos(ID_Producto),
  CONSTRAINT fk_prxlc_loccom FOREIGN KEY (ID_Loc_Com) REFERENCES Locales_Comerciales(ID_Loc_Com)
) ENGINE=InnoDB;

CREATE TABLE Cajas (
    ID_Caja INT AUTO_INCREMENT PRIMARY KEY,
    ID_Loc_Com INT NOT NULL,
    Numero_Caja INT NOT NULL,
    Borrado_Caja BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_Caja DATETIME DEFAULT NULL,
    UNIQUE (ID_Loc_Com, Numero_Caja),
    CONSTRAINT fk_caja_loccom FOREIGN KEY (ID_Loc_Com) REFERENCES Locales_Comerciales(ID_Loc_Com)
) ENGINE=InnoDB;

CREATE TABLE Arqueos_Caja (
    ID_Arqueo INT AUTO_INCREMENT PRIMARY KEY,
    ID_Caja INT NOT NULL,
    ID_Empleado_Apertura INT NOT NULL,
    ID_Empleado_Cierre INT,
    FH_Apertura DATETIME NOT NULL,
    FH_Cierre DATETIME,
    Saldo_Apertura DECIMAL(12, 2) NOT NULL,
    Saldo_Cierre DECIMAL(12, 2),
    Monto_Sistema DECIMAL(12, 2),
    Diferencia DECIMAL(12, 2),
    Abierto_Arqueo BOOLEAN,
    Borrado_Arqueo BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_Arqueo DATETIME DEFAULT NULL,
    CONSTRAINT fk_arqueo_caja FOREIGN KEY (ID_Caja) REFERENCES Cajas(ID_Caja),
    CONSTRAINT fk_arqueo_emp_ap FOREIGN KEY (ID_Empleado_Apertura) REFERENCES Empleados(ID_Empleado),
    CONSTRAINT fk_arqueo_emp_ci FOREIGN KEY (ID_Empleado_Cierre) REFERENCES Empleados(ID_Empleado)
) ENGINE=InnoDB;

CREATE TABLE Ventas (
  ID_Venta INT AUTO_INCREMENT PRIMARY KEY,
  ID_Loc_Com INT NOT NULL,
  ID_Caja INT,
  ID_Empleado INT,
  FH_Venta DATETIME NOT NULL,
  Total_Venta DECIMAL(10, 2) NOT NULL,
  Borrado_Venta BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_Venta DATETIME DEFAULT NULL,
  CONSTRAINT fk_ventas_lc FOREIGN KEY (ID_Loc_Com) REFERENCES Locales_Comerciales(ID_Loc_Com),
  CONSTRAINT fk_ventas_empleado FOREIGN KEY (ID_Empleado) REFERENCES Empleados(ID_Empleado),
  CONSTRAINT fk_ventas_caja FOREIGN KEY (ID_Caja) REFERENCES Cajas(ID_Caja)
) ENGINE=InnoDB;

CREATE TABLE Detalle_Ventas (
  ID_Venta INT,
  ID_Producto INT,
  Cantidad INT NOT NULL,
  Subtotal DECIMAL(10, 2) NOT NULL,
  Borrado_DV BOOLEAN NOT NULL DEFAULT FALSE,
  FH_Borrado_DV DATETIME DEFAULT NULL,
  PRIMARY KEY (ID_Venta, ID_Producto),
  CONSTRAINT fk_dv_venta FOREIGN KEY (ID_Venta) REFERENCES Ventas(ID_Venta),
  CONSTRAINT fk_dv_prod FOREIGN KEY (ID_Producto) REFERENCES Productos(ID_Producto)
) ENGINE=InnoDB;

CREATE TABLE Pedidos_Proveedor (
    ID_Pedido_Prov INT AUTO_INCREMENT PRIMARY KEY,
    ID_Loc_Com INT NOT NULL,
    ID_Proveedor INT NOT NULL,
    ID_Empleado INT,
    FH_Pedido_Prov DATETIME NOT NULL,
    Estado_Pedido_Prov VARCHAR(50) NOT NULL,
    Total_Estimado DECIMAL(10, 2),
    Borrado_Ped_Prov BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_Ped_Prov DATETIME DEFAULT NULL,
    CONSTRAINT fk_pedprov_loccom FOREIGN KEY (ID_Loc_Com) REFERENCES Locales_Comerciales(ID_Loc_Com),
    CONSTRAINT fk_pedprov_proveedor FOREIGN KEY (ID_Proveedor) REFERENCES Proveedores(ID_Proveedor),
    CONSTRAINT fk_pedprov_empleado FOREIGN KEY (ID_Empleado) REFERENCES Empleados(ID_Empleado)
) ENGINE=InnoDB;

CREATE TABLE Detalle_Pedidos_Proveedor (
    ID_Pedido_Prov INT NOT NULL,
    ID_Producto INT NOT NULL,
    Cantidad_Solicitada INT NOT NULL,
    Costo_Est_Unit DECIMAL(10, 2),
    Subtotal_Est DECIMAL(10, 2),
    Borrado_Det_Ped_Prov BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_Det_Ped_Prov DATETIME DEFAULT NULL,
    PRIMARY KEY (ID_Pedido_Prov, ID_Producto),
    CONSTRAINT fk_detpedprov_pedprov FOREIGN KEY (ID_Pedido_Prov) REFERENCES Pedidos_Proveedor(ID_Pedido_Prov),
    CONSTRAINT fk_detpedprov_prod FOREIGN KEY (ID_Producto) REFERENCES Productos(ID_Producto)
) ENGINE=InnoDB;

CREATE TABLE Compras (
    ID_Compra INT AUTO_INCREMENT PRIMARY KEY,
    ID_Proveedor INT NOT NULL,
    ID_Loc_Com INT NOT NULL,
    ID_Empleado INT,
    ID_Pedido_Prov INT NULL,
    FH_Compra DATETIME NOT NULL,
    Total_Compra DECIMAL(10, 2) NOT NULL,
    Borrado_Compra BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_Compra DATETIME DEFAULT NULL,
    CONSTRAINT fk_compras_proveedor FOREIGN KEY (ID_Proveedor) REFERENCES Proveedores(ID_Proveedor),
    CONSTRAINT fk_compras_loccom FOREIGN KEY (ID_Loc_Com) REFERENCES Locales_Comerciales(ID_Loc_Com),
    CONSTRAINT fk_compras_empleado FOREIGN KEY (ID_Empleado) REFERENCES Empleados(ID_Empleado),
    CONSTRAINT fk_compras_pedidoprov FOREIGN KEY (ID_Pedido_Prov) REFERENCES Pedidos_Proveedor(ID_Pedido_Prov)
) ENGINE=InnoDB;

CREATE TABLE Detalle_Compras (
    ID_Compra INT NOT NULL,
    ID_Producto INT NOT NULL,
    Cantidad_DC INT NOT NULL,
    Precio_Unitario_DC DECIMAL(10, 2) NOT NULL,
    Borrado_Det_Comp BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_Det_Comp DATETIME DEFAULT NULL,
    PRIMARY KEY (ID_Compra, ID_Producto),
    CONSTRAINT fk_detcomp_compra FOREIGN KEY (ID_Compra) REFERENCES Compras(ID_Compra),
    CONSTRAINT fk_detcomp_prod FOREIGN KEY (ID_Producto) REFERENCES Productos(ID_Producto)
) ENGINE=InnoDB;

CREATE TABLE Pagos_Ventas (
    ID_Pago_Venta INT AUTO_INCREMENT PRIMARY KEY,
    ID_Venta INT NOT NULL,
    ID_BV INT NOT NULL,
    Monto DECIMAL(10, 2) NOT NULL,
    FH_Pago_Venta DATETIME NOT NULL,
    Borrado_PV BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_PV DATETIME DEFAULT NULL,
    CONSTRAINT fk_pagosventa_venta FOREIGN KEY (ID_Venta) REFERENCES Ventas(ID_Venta),
    CONSTRAINT fk_pagosventa_bv FOREIGN KEY (ID_BV) REFERENCES Billeteras_Virtuales(ID_BV)
) ENGINE=InnoDB;

CREATE TABLE Pagos_Compras (
    ID_Pago_Compra INT AUTO_INCREMENT PRIMARY KEY,
    ID_Compra INT NOT NULL,
    ID_BV INT NOT NULL,
    Monto DECIMAL(10, 2) NOT NULL,
    FH_Pago_Compra DATETIME NOT NULL,
    Borrado_PC BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_PC DATETIME DEFAULT NULL,
    CONSTRAINT fk_pagoscompra_compra FOREIGN KEY (ID_Compra) REFERENCES Compras(ID_Compra),
    CONSTRAINT fk_pagoscompra_bv FOREIGN KEY (ID_BV) REFERENCES Billeteras_Virtuales(ID_BV)
) ENGINE=InnoDB;

CREATE TABLE Incidencias_Compras (
    ID_Incidencia INT AUTO_INCREMENT PRIMARY KEY,
    ID_Compra INT NOT NULL,
    ID_Producto INT NOT NULL,
    Tipo_Problema VARCHAR(50) NOT NULL,
    Cantidad_Reportada INT NOT NULL,
    Descripcion_Incidencia TEXT,
    FH_Reporte DATETIME NOT NULL,
    CONSTRAINT fk_inc_compra FOREIGN KEY (ID_Compra) REFERENCES Compras(ID_Compra),
    CONSTRAINT fk_inc_producto FOREIGN KEY (ID_Producto) REFERENCES Productos(ID_Producto)
) ENGINE=InnoDB;

CREATE TABLE Movimientos_Financieros (
    ID_Movimiento INT AUTO_INCREMENT PRIMARY KEY,
    ID_Caja INT,
    ID_BV INT,
    Tipo_Movimiento VARCHAR(20) NOT NULL, -- 'Ingreso' o 'Egreso'
    Concepto VARCHAR(200) NOT NULL,
    Monto DECIMAL(12, 2) NOT NULL,
    FH_Movimiento DATETIME NOT NULL,
    Borrado_Movimiento BOOLEAN NOT NULL DEFAULT FALSE,
    FH_Borrado_Movimiento DATETIME DEFAULT NULL,
    CONSTRAINT fk_mov_caja FOREIGN KEY (ID_Caja) REFERENCES Cajas(ID_Caja),
    CONSTRAINT fk_mov_bv FOREIGN KEY (ID_BV) REFERENCES Billeteras_Virtuales(ID_BV)
) ENGINE=InnoDB;

CREATE TABLE Auditoria (
  ID_Auditoria INT AUTO_INCREMENT PRIMARY KEY,
  ID_Usuario INT,
  Nombre_Tabla VARCHAR(50) NOT NULL,
  ID_Registro INT NOT NULL,
  Accion_Auditoria ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  Datos_Anteriores JSON,
  Datos_Nuevos JSON,
  FH_Accion DATETIME NOT NULL,
  CONSTRAINT fk_auditoria_usuario FOREIGN KEY (ID_Usuario) REFERENCES Empleados(ID_Empleado)
) ENGINE=InnoDB;

Verificar si se crearon bien las tablas con:

SHOW TABLES;

Ejecutar el comando inspectdb para traducir las tablas, atributos, claves y relaciones de la BD en código entendible por Django. Dicha traducción aparecerá en la consola:

python manage.py inspectdb

Con el código generado por inspectdb, se deben ubicar cada entidad en los diferentes models.py de cada app, según corresponda.

Este proyecto queda definido por las siguientes apps models:

a_central
	Provincias, Locales_Comerciales, Empleados, EmpleadosXLocCom, Auditoria, Billeteras_Virtuales, Marcas, Proveedores, Productos

a_cajas
	Cajas, Arqueos_Caja, Pagos_Compras, Pagos_Ventas, Movimientos_Financieros

a_compras
	Compras, Detalle_Compras, Pedidos_Proveedor, Detalle_Pedidos_Proveedor, Incidencias_Compras

a_stock
	ProveedoresXLocCom, ProveedoresXProductos, Stock

a_ventas
	Ventas, Detalle_Ventas

Se debe seguir un orden, respetando primero las tablas que son independientes y luego las que poseen claves foráneas.


*****************
***** Migraciones
*****************


Para crear un archivo de migración de cada app, ejecutar:

python manage.py makemigrations

Para migrar. En caso que las tablas ya existan en la BD, ejecutar:

python manage.py migrate --fake-initial

Si las tablas no existen en la BD, ejecutar:

python manage.py migrate


*******************************
***** Creación del superusuario
*******************************


python manage.py createsuperuser

superusuario Django: adminpp2


***************************************************************
***** Registro de roles en el panel de administración de Django
***************************************************************


Con el superusuario logueado, en la sección Authentication and Authorization / Groups.

Se crea el rol "Encargado" con todos los permisos y acciones disponibles.

Se crea el rol "Cajero" que va a tener sólo:

Can add venta, Can change venta, Can view venta
Can add detalles ventas, Can view detalles ventas
Can change cajas, Can view cajas
Can add arqueos caja, Can change arqueos caja, Can view arqueos caja
Can view producto
Can view stock
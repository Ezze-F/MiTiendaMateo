# MiTiendaMateo

En Workbench, o por consola, crear una base de datos con el nombre kioscomateo:

CREATE DATABASE kioscomateo;

Cambiar a la nueva base de datos para poder trabajar con ella:

USE kioscomateo;

Para verificar que se creó correctamente la BD:

SHOW DATABASES;

Crear las tablas con los comandos:

create table Roles(ID_Roles int not null, Nombre_Rol varchar(50), Descripcion_Rol varchar(100), primary key(ID_Roles));
create table Empleados(Legajo_Nro int not null, Dni_Emp varchar(20) not null, Apellido_Emp varchar(50), Nombre_Emp varchar(50), Email_Emp varchar(100), Telefono_Emp varchar(50), Domicilio_Emp varchar(100), Fecha_Alta datetime default null, Fecha_Baja datetime, primary key(Legajo_Nro));
create table Proveedores(Cuit_Pv int not null, Nombre_Pv varchar(50), Telefono_Pv varchar(50), Email_Pv varchar(100), Direccion_Pv varchar(100), Habilitado enum('SI','NO'), primary key(Cuit_Pv));
create table Provincias(ID_Provincias int not null, Nombre_Provincia varchar(50), ZonaGeog varchar(20), primary key(ID_Provincias));
create table Productos(ID_Productos int not null, Nombre_Producto varchar(50), Precio_Unitario decimal(10,2), Fecha_Elaboracion date, Fecha_Vencimiento date, Cant_Stock int, primary key(ID_Productos));
create table Pedidos_Provisorios(ID_Pedprov int not null, Cantidad_Prov int, Total_Costo decimal(10,2), primary key(ID_Pedprov));
create table Usuarios(ID_Usuarios int not null, Legajo_Nro int not null, Contrasena varchar(100), primary key(ID_Usuarios), constraint FK_Usuarios_Empleados foreign key(Legajo_Nro) references Empleados(Legajo_Nro));
create table UsuariosXRoles(ID_Usuarios int not null, ID_Roles int not null, Fecha_Asignacion datetime, Fecha_Desvinculacion datetime, primary key(ID_Usuarios, ID_Roles), constraint FK_UsuariosXR_Usuarios foreign key(ID_Usuarios) references Usuarios(ID_Usuarios), constraint FK_UsuariosXR_Roles foreign key(ID_Roles) references Roles(ID_Roles));
create table Codigos_Postales(ID_Postal int not null, ID_Provincias int not null, Localidad varchar(100), Barrio varchar(50), primary key(ID_Postal), constraint FK_CP_Provincias foreign key(ID_Provincias) references Provincias(ID_Provincias));
create table Locales_Comerciales(ID_Loc_Com int not null, ID_Postal int not null, Nombre_Loc_Com varchar(50), Telefono_Loc_Com varchar(20), Email_Loc_Com varchar(50), Nombre_Calle varchar(100), Nro_Calle int, primary key(ID_Loc_Com), constraint FK_LocCom_CodigosPostales foreign key(ID_Postal) references Codigos_Postales(ID_Postal));
create table UsuariosXLocCom(ID_Usuarios int not null, ID_Loc_Com int not null, Fecha_Inicio datetime, Observaciones varchar(200), primary key(ID_Usuarios, ID_Loc_Com), constraint FK_UsuariosXL_Usuarios foreign key(ID_Usuarios) references Usuarios(ID_Usuarios), constraint FK_UsuariosXL_LocCom foreign key(ID_Loc_Com) references Locales_Comerciales(ID_Loc_Com));
create table EmpleadosXLocCom(Legajo_Nro int not null, ID_Loc_Com int not null, Turno varchar(20), Horas_Trabajadas int, primary key(Legajo_Nro, ID_Loc_Com), constraint FK_EmplXL_LocCom foreign key(ID_Loc_Com) references Locales_Comerciales(ID_Loc_Com), constraint FK_EmplXL_Empleados foreign key(Legajo_Nro) references Empleados(Legajo_Nro));
create table Cajas(ID_Cajas int not null, Legajo_Nro int not null, ID_Loc_Com int not null, Fecha_Apertura_Cj date, Hora_Apertura_Cj time, Fecha_Cierre_Cj date, Hora_Cierre_Cj time, Monto_Inicial_Cj decimal(10,2), Monto_Final_Cj decimal(10,2), Total_Venta_Efectivo decimal(10,2), Total_Ventas_BV decimal(10,2), Total_Egreso_Efectivo decimal(10,2), Total_Egreso_BV decimal(10,2), primary key(ID_Cajas), constraint FK_Cajas_Empleados foreign key(Legajo_Nro) references Empleados(Legajo_Nro), constraint FK_Cajas_LocCom foreign key(ID_Loc_Com) references Locales_Comerciales(ID_Loc_Com));
create table Reportes_Cierres(ID_RC int not null, ID_Cajas int not null, Fecha_RC date, Hora_RC time, Monto_Efectivo decimal(10,2), Monto_BV decimal(10,2), Ruta_Ubi_Arch_RC varchar(500), primary key(ID_RC), constraint FK_RC_Cajas foreign key(ID_Cajas) references Cajas(ID_Cajas));
create table Reportes_Aperturas(ID_RA int not null, ID_Cajas int not null, Fecha_RA date, Hora_RA time, Monto_Efectivo_RA decimal(10,2), Monto_BV_RA decimal(10,2), Ruta_Ubi_Arch_RA varchar(500), primary key(ID_RA), constraint FK_RA_Cajas foreign key(ID_Cajas) references Cajas(ID_Cajas));
create table Billeteras_Virtuales(ID_BV int not null, ID_Cajas int not null, Nombre_BV varchar(50), Usuario_BV varchar(50), Contrasena_BV varchar(50), CVU_BV varchar(20), Fecha_Alta_BV date, Hora_Alta_BV time, Fecha_Baja_BV date, Hora_Baja_BV time, Saldo_BV decimal(10,2), primary key(ID_BV), constraint FK_BV_Cajas foreign key(ID_Cajas) references Cajas(ID_Cajas));
create table BilleteraVirtualesXCajas(ID_Cajas int not null, ID_BV int not null, Veces_Utilizada_Compra int, Veces_Utilizada_Venta int, primary key (ID_Cajas, ID_BV), constraint fk_BVXCaja foreign key (ID_Cajas) references Cajas(ID_Cajas), constraint fk_BVXC foreign key (ID_BV) references Billeteras_Virtuales(ID_BV));
create table Compras_Canceladas(ID_CC int not null, ID_Cajas int not null, Fecha_CC date, Hora_CC time, Monto_CC decimal(10,2), Descripcion varchar(500), primary key(ID_CC), constraint FK_CC_Cajas foreign key(ID_Cajas) references Cajas(ID_Cajas));
create table Ventas_Canceladas(ID_VC int not null, ID_Cajas int not null, Fecha_VC date, Hora_VC time, Monto_VC decimal(10,2), primary key(ID_VC), constraint FK_VC_Cajas foreign key(ID_Cajas) references Cajas(ID_Cajas));
create table Compras(ID_Compras int not null, Cuit_Pv int not null, ID_Cajas int not null, ID_Loc_Com int not null, Fecha_Com date, Hora_Com time, Monto_Total decimal(10,2), Ruta_Arch_Fact varchar(500), primary key(ID_Compras), constraint FK_Compras_Prov foreign key(Cuit_Pv) references Proveedores(Cuit_Pv), constraint FK_Compras_Cajas foreign key(ID_Cajas) references Cajas(ID_Cajas), constraint FK_Compras_LocCom foreign key(ID_Loc_Com) references Locales_Comerciales(ID_Loc_Com));
create table Reporte_Inconsistencia_Pedidos(ID_RIP int not null, ID_Compras int not null, Fecha_RIP date, Hora_RIP time, Ruta_Ubi_Arch_RIP varchar(500), Descripcion varchar(200), primary key(ID_RIP), constraint FK_RIP_Compras foreign key(ID_Compras) references Compras(ID_Compras));
create table Ventas(ID_Ventas int not null, ID_Cajas int not null, Fecha_Venta date, Hora_Venta time, Monto_Final decimal(10,2), primary key(ID_Ventas), constraint FK_Ventas_Cajas foreign key(ID_Cajas) references Cajas(ID_Cajas));
create table Detalle_Ventas(ID_Ventas int not null, ID_Productos int not null, Cantidad_Producto int, Precio_Unitario decimal(10,2), Monto_Final decimal(10,2), primary key(ID_Ventas, ID_Productos), constraint FK_DV_Ventas foreign key(ID_Ventas) references Ventas(ID_Ventas), constraint FK_DV_Productos foreign key(ID_Productos) references Productos(ID_Productos));
create table Detalle_Compras(ID_Compras int not null, ID_Productos int not null, Precio_Unitario decimal(10,2), Cantidad_Producto int, primary key(ID_Compras, ID_Productos), constraint FK_DC_Compras foreign key(ID_Compras) references Compras(ID_Compras), constraint FK_DC_Productos foreign key(ID_Productos) references Productos(ID_Productos));
create table ProveedoresXProductos(Cuit_Pv int not null, ID_Productos int not null, Ultima_Entrega date, Observacion varchar(500), primary key(Cuit_Pv, ID_Productos), constraint FK_PXP_Prov foreign key(Cuit_Pv) references Proveedores(Cuit_Pv), constraint FK_PXP_Productos foreign key(ID_Productos) references Productos(ID_Productos));
create table Pedidos_Confirmados(ID_PedConf int not null, Cuit_Pv int not null, primary key(ID_PedConf), constraint FK_PConf_Prov foreign key(Cuit_Pv) references Proveedores(Cuit_Pv));
create table Pedidos_ConfXProductos(ID_PedConf int not null, ID_Productos int not null, Observaciones varchar(100), primary key(ID_PedConf, ID_Productos), constraint FK_PCXP_PConf foreign key(ID_PedConf) references Pedidos_Confirmados(ID_PedConf), constraint FK_PCXP_Productos foreign key(ID_Productos) references Productos(ID_Productos));
create table Pedidos_ProvXProductos(ID_Pedprov int not null, ID_Productos int not null, Descripcion varchar(100), primary key(ID_Pedprov, ID_Productos), constraint FK_PProvXP_PProv foreign key(ID_Pedprov) references Pedidos_Provisorios(ID_Pedprov), constraint FK_PProvXP_Productos foreign key(ID_Productos) references Productos(ID_Productos));
create table ProductoXLocCom (ID_Productos int not null, ID_Loc_Com int not null, Observaciones varchar(100), primary key(ID_Productos, ID_Loc_Com), constraint FK_LocComXProductos foreign key(ID_Productos) references Productos(ID_Productos), constraint FK_LocComXProd foreign key (ID_Loc_Com) references Locales_Comerciales(ID_Loc_Com));
create table Reportes_Stock(ID_RST int not null, ID_Productos int not null, Fecha_RS date, Hora_RS time, Ruta_Ubi_Arch_RS varchar(500), Descripcion varchar(100), primary key(ID_RST), constraint FK_RS_Prodcutos foreign key(ID_Productos) references Productos(ID_Productos));
create table ProveedoresXLocCom(Cuit_Pv int not null, ID_Loc_Com int not null, Fecha_Ultima_Visita date, Hora_Ultima_Visita time, primary key(Cuit_Pv, ID_Loc_Com), constraint FK_PXL_Prov foreign key(Cuit_Pv) references Proveedores(Cuit_Pv), constraint FK_PXL_LocCom foreign key(ID_Loc_Com) references Locales_Comerciales(ID_Loc_Com));

Verificar si se crearon bien las tablas con:

SHOW TABLES;

Ejecutar el comando inspectdb para traducir las tablas, atributos, claves y relaciones de la BD en código entendible por Django. Dicha traducción aparecerá en la consola:

python manage.py inspectdb

Con el código generado por inspectdb, se deben ubicar cada entidad en los diferentes models.py de cada app, según corresponda.

Este proyecto queda definido por las siguientes apps models:

a_billeteras_v (Billeterasvirtualesxcajas, BilleterasVirtuales)
a_caja (Cajas, ReportesAperturas, ReportesCierres)
a_compras (Compras, ComprasCanceladas, DetalleCompras, ReporteIncosnsistenciaPedidos)
a_empleados (Empleados, Empleadosxloccom, Roles, Usuarios, Usuariosxloccom, Usuariosxroles)
a_productos (Productos, Productosxloccom, ReportesStock)
a_proveedores (Proveedores, PedidosConfxproductos, PedidosConfirmados, PedidosProvxproductos, PedidosProvisorios, Proveedoresxloccom, Proveedoresxproductos)
a_sucursales (CodigosPostales, LocalesComerciales, Provincias)
a_ventas (Ventas, DetalleVentas, VentasCanceladas)

Se debe seguir un orden, respetando primero las tablas que son independientes y luego las que poseen claves foráneas.

Para crear un archivo de migración de cada app, ejecutar:

python manage.py makemigrations

Para migrar. En caso que las tablas ya existan en la BD, ejecutar:

python manage.py migrate --fake-initial

Si las tablas no existen en la BD, ejecutar:

python manage.py migrate

Numeración de apps a codificar:

1) Productos
2) Proveedores
3) Compras
4) Ventas
5) Caja
6) Billeteras virtuales
7) Sucursales
8) Empleados

Desarrollo de la app Productos:
25/08/2025 - Creación de urls.py, forms.py y carpeta templates.




***** Restruccturación de las apps del proyecto

a_central
	Roles, Provincias, Sucursales,
Empleados, Auditorías

a_stock
	Marcas, Proveedores, Productos, Stock_Sucursales, Proveedores_Productos

a_cajas
	Cajas, Movimientos_Cajas, Billeteras_Virtuales

a_ventas
	Ventas, Detalles_Ventas

a_compras
	Compras, Detalles_Compras

***** Creación del superusuario

superusuario Django: adminpp2
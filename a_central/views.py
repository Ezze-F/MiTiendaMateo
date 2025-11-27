from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET 
from django.db import IntegrityError, transaction # Importar transaction para atomicidad
from django.utils import timezone
from datetime import date
import logging 

# Importaciones clave para autenticación y roles
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

from .models import Empleados, Provincias, Marcas, Proveedores, LocalesComerciales, Productos, BilleterasVirtuales
from .forms import EmpleadoRegistroForm, ProvinciaForm, MarcaForm, ProveedorRegistroForm, LocalComercialRegistroForm, ProductoRegistroForm, BilleteraRegistroForm, BilleteraModificacionForm
from a_stock.models import Proveedoresxloccom
from a_stock.models import Proveedoresxproductos
from a_stock.models import Stock

# Configuración de logging para ver errores en la consola
logger = logging.getLogger(__name__)

# Función auxiliar para extraer mensajes de error del formulario
def _form_errors_to_dict(form):
    """Convierte los errores de un formulario en un diccionario plano para JsonResponse."""
    errors = {}
    for field, field_errors in form.errors.items():
        # Tomamos el primer error de cada campo para un mensaje conciso
        errors[field] = field_errors[0]
    # Si hay errores no relacionados con campos (ej. en clean general), los incluimos
    if '__all__' in form.errors:
         errors['non_field_errors'] = form.errors['__all__'][0]
    return errors

# ===============================================
# EMPLEADOS
# ===============================================

def _serialize_empleados(queryset, is_deleted_view):
    """
    Serializa un queryset de Empleados al formato requerido por DataTables,
    manejando las diferencias entre vistas de empleados activos e inactivos.
    """
    data = []
    for emp in queryset:
        dni_str = str(emp.dni_emp)

        # Intentamos obtener el username del usuario vinculado
        username = ''
        if emp.usuario_emp:
            username = emp.usuario_emp
        elif hasattr(emp, 'user_auth') and emp.user_auth:
            username = getattr(emp.user_auth, 'username', '') or ''

        empleado_data = {
            'id_empleado': emp.id_empleado,
            'dni_emp': dni_str,
            'apellido_emp': emp.apellido_emp,
            'nombre_emp': emp.nombre_emp,
            'usuario_emp': username,  # <<--- aseguramos que siempre esté presente
        }

        if not is_deleted_view:
            empleado_data.update({
                'email_emp': emp.email_emp,
                'telefono_emp': emp.telefono_emp if emp.telefono_emp else '',
                'domicilio_emp': emp.domicilio_emp if emp.domicilio_emp else '',
                'fecha_alta_emp': emp.fecha_alta_emp.strftime('%Y-%m-%d') if emp.fecha_alta_emp else '',
                'rol_emp': emp.get_rol(),
            })
        else:
            empleado_data.update({
                'fh_borrado_e': emp.fh_borrado_e.strftime('%Y-%m-%d %H:%M') if emp.fh_borrado_e else '',
            })

        data.append(empleado_data)
    return data


# --- VISTA PRINCIPAL EMPLEADOS (No modificada) ---
def listar_empleados(request):
    """Renderiza la plantilla principal de gestión de empleados y envía los roles."""
    roles = Group.objects.all().order_by('name')
    context = {
        'roles': roles,
    }
    return render(request, 'a_central/empleados/listar_empleados.html', context)


# --- API - LISTADO DE EMPLEADOS DISPONIBLES (Uso del Manager por defecto) ---
def empleados_disponibles_api(request):
    """Devuelve los datos de empleados activos para DataTables."""
    if request.method == 'GET':
        try:
            # Empleados.objects usa por defecto el EmpleadoManager (solo activos)
            empleados = Empleados.objects.select_related('user_auth').prefetch_related('user_auth__groups').order_by('id_empleado')
            data = _serialize_empleados(empleados, is_deleted_view=False)
            return JsonResponse({'data': data})
        except Exception as e:
            logger.error(f"Error al serializar empleados disponibles: {e}", exc_info=True)
            return JsonResponse({'error': 'Error interno al obtener empleados disponibles.'}, status=500)


# --- API - LISTADO DE EMPLEADOS ELIMINADOS (Uso del Manager all_objects) ---
def empleados_eliminados_api(request):
    """Devuelve los datos de empleados inactivos/eliminados para DataTables."""
    if request.method == 'GET':
        try:
            # Usamos el manager all_objects y filtramos por borrado_emp=True
            empleados = Empleados.all_objects.filter(borrado_emp=True).select_related('user_auth').order_by('-id_empleado')
            data = _serialize_empleados(empleados, is_deleted_view=True)
            return JsonResponse({'data': data})
        except Exception as e:
            logger.error(f"Error al serializar empleados eliminados: {e}", exc_info=True)
            return JsonResponse({'error': 'Error interno al obtener empleados eliminados.'}, status=500)


# --- OPERACIONES CRUD EMPLEADOS ---
# ... (registrar_empleado y modificar_empleado no modificados, pues se usan Managers en la validación del form) ...

@require_POST
def registrar_empleado(request):
    """
    Vista para registrar un nuevo empleado y crear su usuario asociado en el sistema de autenticación.
    Todos los campos son obligatorios y el inicio de sesión se hará solo por 'usuario_emp'.
    """
    form = EmpleadoRegistroForm(request.POST)

    if not form.is_valid():
        errors = dict(form.errors.items())
        return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors})

    data = form.cleaned_data
    username_final = data['usuario_emp']  # Siempre obligatorio

    try:
        with transaction.atomic():
            # Crear usuario Django
            user = User.objects.create_user(
                username=username_final,
                email=data['email_emp'],
                password=data['contrasena_emp'],
                first_name=data['nombre_emp'],
                last_name=data['apellido_emp'],
            )
            user.is_active = True
            user.save()

            # Asignar rol (grupo)
            rol_seleccionado = data['id_rol']
            user.groups.add(rol_seleccionado)

            # Crear registro en Empleados
            Empleados.all_objects.create( # Uso all_objects para asegurar la creación aunque el manager por defecto filtre
                user_auth=user,
                dni_emp=data['dni_emp'],
                apellido_emp=data['apellido_emp'],
                nombre_emp=data['nombre_emp'],
                email_emp=data['email_emp'],
                usuario_emp=username_final,
                contrasena_emp=user.password,
                telefono_emp=data['telefono_emp'],
                domicilio_emp=data['domicilio_emp'],
                fecha_alta_emp=date.today(),
                borrado_emp=False,
            )

        return JsonResponse({'success': True, 'message': 'Empleado y Usuario registrados exitosamente.'})

    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'Error de integridad en la base de datos (DNI/Email duplicado).'})
    except Exception as e:
        logger.error(f"Error al registrar empleado: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'})
        
@require_POST
def modificar_empleado(request, empleado_id):
    # Lógica de modificación de empleado (Uso all_objects para encontrarlo si está borrado lógicamente, aunque en principio solo se debería modificar uno activo)
    # Mejor usar Empleados.objects para buscar solo entre los activos para la modificación
    try:
        # get_object_or_404 usa Empleados.objects (solo activos)
        empleado = get_object_or_404(Empleados, pk=empleado_id)
        dni = request.POST.get('dni_emp')
        apellido = request.POST.get('apellido_emp')
        nombre = request.POST.get('nombre_emp')
        email = request.POST.get('email_emp')
        telefono = request.POST.get('telefono_emp')
        domicilio = request.POST.get('domicilio_emp')
        usuario_emp = request.POST.get('usuario_emp')
        id_rol_str = request.POST.get('id_rol')

        # --- Validación de Unicidad para Modificación ---
        # Usamos all_objects para buscar unicidad en TODO el historial, activos e inactivos
        if Empleados.all_objects.exclude(pk=empleado_id).filter(dni_emp=dni).exists():
             raise IntegrityError('El DNI ya está registrado por otro empleado (activo o inactivo).')
        if Empleados.all_objects.exclude(pk=empleado_id).filter(email_emp=email).exists():
             raise IntegrityError('El Email ya está registrado por otro empleado (activo o inactivo).')
        
        if empleado.user_auth:
            # El campo email y username del User debe ser único
            if User.objects.exclude(pk=empleado.user_auth.pk).filter(email=email).exists():
                 raise IntegrityError('El Email ya está registrado en el sistema de usuarios (User).')
            
            # El campo usuario_emp es el username del User, y debe ser único.
            username_to_check = usuario_emp if usuario_emp else str(dni)
            if User.objects.exclude(pk=empleado.user_auth.pk).filter(username=username_to_check).exists():
                raise IntegrityError('El nombre de Usuario ya está en uso por otro usuario.')

        # --- Fin Validación ---
        
        with transaction.atomic():
            # Actualizar campos del Empleado
            empleado.dni_emp = dni
            empleado.apellido_emp = apellido
            empleado.nombre_emp = nombre
            empleado.email_emp = email
            empleado.usuario_emp = usuario_emp if usuario_emp else str(dni)
            empleado.telefono_emp = telefono if telefono else None
            empleado.domicilio_emp = domicilio if domicilio else None
            empleado.save()

            # Actualizar el Usuario de Django si existe (Sincronización)
            if empleado.user_auth:
                empleado.user_auth.email = email
                empleado.user_auth.username = empleado.usuario_emp 
                empleado.user_auth.first_name = nombre
                empleado.user_auth.last_name = apellido
                
                if id_rol_str and id_rol_str.isdigit():
                    rol_seleccionado = Group.objects.get(pk=int(id_rol_str))
                    empleado.user_auth.groups.clear()
                    empleado.user_auth.groups.add(rol_seleccionado)
                
                empleado.user_auth.save()


        return JsonResponse({'success': True})

    except Empleados.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado o ya eliminado.'})
    except Group.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'El Rol seleccionado no es válido o no existe.'})
    except IntegrityError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        logger.error(f"Error al modificar empleado {empleado_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def borrar_empleado(request, empleado_id):
    """Realiza el borrado lógico de un empleado activo."""
    try:
        # Usamos all_objects para asegurar que podemos encontrarlo aunque el manager por defecto lo excluya si por alguna razón está mal.
        # Filtramos explícitamente por borrado_emp=False para garantizar que no se borre dos veces.
        empleado = Empleados.all_objects.get(pk=empleado_id, borrado_emp=False) 
        
        # Usamos el nuevo método del modelo
        if empleado.borrar_logico():
            return JsonResponse({'success': True, 'message': 'Empleado borrado lógicamente exitosamente.'})
        else:
            # Esto no debería pasar si filtramos por borrado_emp=False, pero es una buena práctica.
            return JsonResponse({'success': False, 'error': 'El empleado ya estaba borrado.'})

    except Empleados.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado o ya está dado de baja.'})
    except Exception as e:
        logger.error(f"Error al borrar empleado {empleado_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def recuperar_empleado(request, empleado_id):
    """Restaura un empleado previamente borrado lógicamente."""
    try:
        # Usamos all_objects y filtramos por borrado_emp=True para encontrar el registro a restaurar
        empleado = Empleados.all_objects.get(pk=empleado_id, borrado_emp=True) 
        
        # Usamos el nuevo método del modelo
        if empleado.restaurar():
            return JsonResponse({'success': True, 'message': 'Empleado restaurado exitosamente.'})
        else:
            # Esto no debería pasar si filtramos por borrado_emp=True.
            return JsonResponse({'success': False, 'error': 'El empleado ya estaba activo.'})

    except Empleados.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado o ya está activo.'})
    except Exception as e:
        logger.error(f"Error al recuperar empleado {empleado_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


# ===============================================
# PROVINCIAS
# ===============================================

def _serialize_provincias(queryset, is_deleted_view):
    """Serializa un queryset de Provincias para DataTables."""
    data = []
    for prov in queryset:
        provincia_data = {
            'id_provincia': prov.id_provincia,
            'nombre_provincia': prov.nombre_provincia,
        }
        
        if is_deleted_view:
            provincia_data.update({
                'fh_borrado_p': prov.fh_borrado_p.strftime('%Y-%m-%d %H:%M') if prov.fh_borrado_p else 'N/A',
            })
            
        data.append(provincia_data)
    return data

def listar_provincias(request):
    """Renderiza la plantilla principal de gestión de provincias."""
    # No se necesita contexto por ahora, pero se mantiene la estructura.
    return render(request, 'a_central/provincias/listar_provincias.html', {})

@require_GET
def provincias_disponibles_api(request):
    """Devuelve los datos de provincias activas para DataTables (Usa ProvinciaManager)."""
    try:
        # Provincias.objects usa el ProvinciaManager por defecto (solo activas)
        provincias = Provincias.objects.order_by('nombre_provincia')
        data = _serialize_provincias(provincias, is_deleted_view=False)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al serializar provincias disponibles: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener provincias disponibles.'}, status=500)

@require_GET
def provincias_eliminadas_api(request):
    """Devuelve los datos de provincias eliminadas para DataTables (Usa ProvinciaAllObjectsManager)."""
    try:
        # Usamos all_objects y filtramos por borrado_provincia=True
        provincias = Provincias.all_objects.filter(borrado_provincia=True).order_by('-fh_borrado_p')
        data = _serialize_provincias(provincias, is_deleted_view=True)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al serializar provincias eliminadas: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener provincias eliminadas.'}, status=500)

@require_POST
def registrar_provincia(request):
    """Vista para registrar una nueva provincia."""
    form = ProvinciaForm(request.POST)

    if form.is_valid():
        try:
            with transaction.atomic():
                provincia = form.save(commit=False)
                provincia.borrado_provincia = False
                provincia.save()
            return JsonResponse({'success': True, 'message': 'Provincia registrada exitosamente.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Error de integridad: El nombre de provincia ya existe.'}, status=400)
        except Exception as e:
            logger.error(f"Error al registrar provincia: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)
    else:
        # Devuelve errores de validación del formulario
        errors = _form_errors_to_dict(form)
        return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors}, status=400)

@require_POST
def modificar_provincia(request, provincia_id):
    """Vista para modificar una provincia existente."""
    provincia = get_object_or_404(Provincias.all_objects, pk=provincia_id)
    # Si usamos ProvinciaForm(request.POST, instance=provincia), la validación del clean_nombre_provincia
    # ya manejará si la provincia está borrada lógicamente o no, chequeando la unicidad.
    form = ProvinciaForm(request.POST, instance=provincia)

    if form.is_valid():
        try:
            with transaction.atomic():
                form.save()
            return JsonResponse({'success': True, 'message': 'Provincia modificada exitosamente.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Error de integridad: El nombre de provincia ya existe.'}, status=400)
        except Exception as e:
            logger.error(f"Error al modificar provincia {provincia_id}: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)
    else:
        errors = _form_errors_to_dict(form)
        return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors}, status=400)

@require_POST
def borrar_provincia(request, provincia_id):
    """Realiza el borrado lógico de una provincia activa."""
    try:
        # Usamos all_objects para asegurar que podemos encontrarla y verificamos que no esté borrada
        provincia = Provincias.all_objects.get(pk=provincia_id, borrado_provincia=False) 
        
        if provincia.borrar_logico():
            return JsonResponse({'success': True, 'message': 'Provincia borrada lógicamente.'})
        
    except Provincias.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Provincia no encontrada o ya está dada de baja.'}, status=404)
    except Exception as e:
        logger.error(f"Error al borrar provincia {provincia_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
def recuperar_provincia(request, provincia_id):
    """Restaura una provincia previamente borrada lógicamente."""
    try:
        # Usamos all_objects y filtramos por borrado_provincia=True
        provincia = Provincias.all_objects.get(pk=provincia_id, borrado_provincia=True) 
        
        if provincia.restaurar():
            return JsonResponse({'success': True, 'message': 'Provincia restaurada exitosamente.'})
        
    except Provincias.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Provincia no encontrada o ya está activa.'}, status=404)
    except Exception as e:
        logger.error(f"Error al recuperar provincia {provincia_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ===============================================
# MARCAS
# ===============================================

def _serialize_marcas(queryset, is_deleted_view):
    """Serializa un queryset de Marcas para DataTables."""
    data = []
    for marca in queryset:
        marca_data = {
            'id_marca': marca.id_marca,
            'nombre_marca': marca.nombre_marca,
        }

        if is_deleted_view:
            marca_data.update({
                'fh_borrado_m': marca.fh_borrado_m.strftime('%Y-%m-%d %H:%M') if marca.fh_borrado_m else 'N/A',
            })

        data.append(marca_data)
    return data


def listar_marcas(request):
    """Renderiza la plantilla principal de gestión de marcas."""
    return render(request, 'a_central/marcas/listar_marcas.html', {})


@require_GET
def marcas_disponibles_api(request):
    """Devuelve los datos de marcas activas (usando MarcaManager)."""
    try:
        marcas = Marcas.objects.order_by('nombre_marca')
        data = _serialize_marcas(marcas, is_deleted_view=False)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al serializar marcas disponibles: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener marcas disponibles.'}, status=500)


@require_GET
def marcas_eliminadas_api(request):
    """Devuelve los datos de marcas eliminadas (usando MarcaAllObjectsManager)."""
    try:
        marcas = Marcas.all_objects.filter(borrado_marca=True).order_by('-fh_borrado_m')
        data = _serialize_marcas(marcas, is_deleted_view=True)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al serializar marcas eliminadas: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener marcas eliminadas.'}, status=500)


@require_POST
def registrar_marca(request):
    """Registra una nueva marca."""
    form = MarcaForm(request.POST)

    if form.is_valid():
        try:
            with transaction.atomic():
                marca = form.save(commit=False)
                marca.borrado_marca = False
                marca.save()
            return JsonResponse({'success': True, 'message': 'Marca registrada exitosamente.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Error de integridad: El nombre de marca ya existe.'}, status=400)
        except Exception as e:
            logger.error(f"Error al registrar marca: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)
    else:
        errors = _form_errors_to_dict(form)
        return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors}, status=400)


@require_POST
def modificar_marca(request, marca_id):
    """Modifica una marca existente."""
    marca = get_object_or_404(Marcas.all_objects, pk=marca_id)
    form = MarcaForm(request.POST, instance=marca)

    if form.is_valid():
        try:
            with transaction.atomic():
                form.save()
            return JsonResponse({'success': True, 'message': 'Marca modificada exitosamente.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Error de integridad: El nombre de marca ya existe.'}, status=400)
        except Exception as e:
            logger.error(f"Error al modificar marca {marca_id}: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)
    else:
        errors = _form_errors_to_dict(form)
        return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors}, status=400)


@require_POST
def borrar_marca(request, marca_id):
    """Realiza el borrado lógico de una marca activa."""
    try:
        marca = Marcas.all_objects.get(pk=marca_id, borrado_marca=False)

        if marca.borrar_logico():
            return JsonResponse({'success': True, 'message': 'Marca borrada lógicamente.'})

    except Marcas.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Marca no encontrada o ya está dada de baja.'}, status=404)
    except Exception as e:
        logger.error(f"Error al borrar marca {marca_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def recuperar_marca(request, marca_id):
    """Restaura una marca previamente borrada lógicamente."""
    try:
        marca = Marcas.all_objects.get(pk=marca_id, borrado_marca=True)

        if marca.restaurar():
            return JsonResponse({'success': True, 'message': 'Marca restaurada exitosamente.'})

    except Marcas.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Marca no encontrada o ya está activa.'}, status=404)
    except Exception as e:
        logger.error(f"Error al recuperar marca {marca_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ===============================================
# PROVEEDORES
# ===============================================

def _serialize_proveedores(queryset, is_deleted_view):
    """Serializa proveedores para DataTables."""
    data = []
    for prov in queryset:
        proveedor_data = {
            'id_proveedor': prov.id_proveedor,
            'cuit_prov': prov.cuit_prov,
            'nombre_prov': prov.nombre_prov,
            'telefono_prov': prov.telefono_prov or '',
            'email_prov': prov.email_prov or '',
            'direccion_prov': prov.direccion_prov or '',
            'fecha_alta_prov': prov.fecha_alta_prov.strftime('%Y-%m-%d'), 
        }

        if is_deleted_view:
            proveedor_data.update({
                'fh_borrado_prov': prov.fh_borrado_prov.strftime('%Y-%m-%d %H:%M') if prov.fh_borrado_prov else ''
            })

        data.append(proveedor_data)
    return data

def listar_proveedores(request):
    """Renderiza la página principal de proveedores."""
    locales = LocalesComerciales.objects.all().order_by('nombre_loc_com')
    productos = Productos.objects.filter(borrado_prod=False).order_by('nombre_producto')
    
    context = {
        'locales_comerciales': locales,
        'productos': productos,  # <-- esto es nuevo
    }
    
    # El return debe estar al final, después de definir el contexto.
    return render(request, 'a_central/proveedores/listar_proveedores.html', context)

@require_GET
def proveedores_disponibles_api(request):
    """Devuelve proveedores activos."""
    try:
        proveedores = Proveedores.objects.all().order_by('id_proveedor')
        data = _serialize_proveedores(proveedores, is_deleted_view=False)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar proveedores: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener proveedores.'}, status=500)


@require_GET
def proveedores_eliminados_api(request):
    """Devuelve proveedores borrados lógicamente."""
    try:
        proveedores = Proveedores.all_objects.filter(borrado_prov=True).order_by('-id_proveedor')
        data = _serialize_proveedores(proveedores, is_deleted_view=True)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar proveedores eliminados: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener proveedores eliminados.'}, status=500)

import json

@require_POST
def registrar_proveedor(request):
    """Crea un nuevo proveedor con locales y productos de forma segura usando el formulario."""
    form = ProveedorRegistroForm(request.POST)

    if not form.is_valid():
        # Convierte los errores del formulario en un dict simple
        if not form.is_valid():
            print("Errores del form:", form.errors)  # <- te muestra qué campo falla
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors})

    data = form.cleaned_data
    locales_seleccionados = data.get('locales_comerciales', [])
    productos_seleccionados = data.get('productos_vendidos', [])
    precios = request.POST.getlist('costo_compra')  # vienen como lista, ya validados en el form

    try:
        with transaction.atomic():
            # Crear proveedor
            nuevo_proveedor = Proveedores.all_objects.create(
                cuit_prov=data['cuit_prov'],
                nombre_prov=data['nombre_prov'],
                telefono_prov=data.get('telefono_prov'),
                email_prov=data.get('email_prov'),
                direccion_prov=data.get('direccion_prov'),
                borrado_prov=False
            )
            logger.info(f"Proveedor creado: {nuevo_proveedor.id_proveedor} - {nuevo_proveedor.nombre_prov}")

            # Asociar locales comerciales
            if locales_seleccionados:
                relaciones_locales = [
                    Proveedoresxloccom(id_proveedor=nuevo_proveedor, id_loc_com=local)
                    for local in locales_seleccionados
                ]
                Proveedoresxloccom.objects.bulk_create(relaciones_locales)
                logger.info(f"Locales asociados: {locales_seleccionados}")

            # Asociar productos con su costo
            relaciones_productos = [
                Proveedoresxproductos(
                    id_proveedor=nuevo_proveedor,
                    id_producto=producto,
                    costo_compra=float(precio),
                    borrado_pvxpr=False
                )
                for producto, precio in zip(productos_seleccionados, precios)
            ]
            if relaciones_productos:
                Proveedoresxproductos.objects.bulk_create(relaciones_productos)
                logger.info(f"Productos asociados: {[p.nombre_producto for p in productos_seleccionados]}")

        return JsonResponse({'success': True, 'message': 'Proveedor registrado exitosamente.'})

    except IntegrityError as e:
        logger.error(f"Error de integridad al registrar proveedor: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Error de integridad: {str(e)}'})

    except Exception as e:
        logger.error(f"Error al registrar proveedor: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'})

@require_POST
def modificar_proveedor(request, proveedor_id):
    """Edita los datos de un proveedor incluyendo productos."""
    try:
        proveedor = get_object_or_404(Proveedores, pk=proveedor_id)
        
        # Validaciones de unicidad
        cuit = request.POST.get('cuit_prov')
        email = request.POST.get('email_prov')
        
        if Proveedores.all_objects.exclude(pk=proveedor_id).filter(cuit_prov=cuit).exists():
            return JsonResponse({'success': False, 'error': 'El CUIT ya está registrado por otro proveedor.'})
        
        if email and Proveedores.all_objects.exclude(pk=proveedor_id).filter(email_prov=email).exists():
            return JsonResponse({'success': False, 'error': 'El Email ya está registrado por otro proveedor.'})

        with transaction.atomic():
            # Actualizar datos básicos del proveedor
            proveedor.cuit_prov = cuit
            proveedor.nombre_prov = request.POST.get('nombre_prov')
            proveedor.telefono_prov = request.POST.get('telefono_prov') or None
            proveedor.email_prov = email or None
            proveedor.direccion_prov = request.POST.get('direccion_prov') or None
            proveedor.save()

            # Manejar locales comerciales (tu lógica existente)
            locales_ids_nuevos = [int(lid) for lid in request.POST.getlist('locales_comerciales') if lid.isdigit()]
            
            locales_actuales = Proveedoresxloccom.objects.filter(
                id_proveedor=proveedor
            ).values_list('id_loc_com', flat=True)
            locales_ids_actuales = set(locales_actuales)
            locales_ids_nuevos_set = set(locales_ids_nuevos)

            # Locales a añadir
            locales_a_añadir_ids = locales_ids_nuevos_set.difference(locales_ids_actuales)
            if locales_a_añadir_ids:
                locales_a_añadir = LocalesComerciales.objects.filter(pk__in=locales_a_añadir_ids)
                relaciones_a_crear = [
                    Proveedoresxloccom(id_proveedor=proveedor, id_loc_com=local)
                    for local in locales_a_añadir
                ]
                Proveedoresxloccom.objects.bulk_create(relaciones_a_crear)
            
            # Locales a eliminar
            locales_a_eliminar_ids = locales_ids_actuales.difference(locales_ids_nuevos_set)
            if locales_a_eliminar_ids:
                Proveedoresxloccom.objects.filter(
                    id_proveedor=proveedor, 
                    id_loc_com__in=locales_a_eliminar_ids
                ).delete()

            # === CORRECCIÓN PRINCIPAL: Manejar productos ===
            productos_data = []
            productos_recibidos_ids = set()  # Para trackear qué productos vienen del frontend
            
            for key, value in request.POST.items():
                if key.startswith('productos[') and key.endswith('][producto_id]'):
                    index = key.split('[')[1].split(']')[0]
                    producto_id = value
                    costo_compra = request.POST.get(f'productos[{index}][costo_compra]')
                    id_prov_prod = request.POST.get(f'productos[{index}][id_prov_prod]')
                    
                    if producto_id and costo_compra:
                        productos_data.append({
                            'producto_id': producto_id,
                            'costo_compra': costo_compra,
                            'id_prov_prod': id_prov_prod
                        })
                        if id_prov_prod:  # Si es un producto existente, agregar a la lista de recibidos
                            productos_recibidos_ids.add(int(id_prov_prod))

            # Obtener todos los productos actuales del proveedor
            productos_actuales = Proveedoresxproductos.objects.filter(
                id_proveedor=proveedor, 
                borrado_pvxpr=False
            )
            
            # Identificar productos a eliminar (están en la BD pero no vinieron del frontend)
            productos_a_eliminar = productos_actuales.exclude(id_prov_prod__in=productos_recibidos_ids)
            if productos_a_eliminar.exists():
                # Borrado lógico de los productos eliminados
                productos_a_eliminar.update(borrado_pvxpr=True)
                logger.info(f"Productos eliminados: {[p.id_prov_prod for p in productos_a_eliminar]}")

            # Actualizar productos existentes y agregar nuevos
            productos_actuales_dict = {p.id_prov_prod: p for p in productos_actuales}
            
            for producto_info in productos_data:
                if producto_info['id_prov_prod']:  # Producto existente
                    producto_obj = productos_actuales_dict.get(int(producto_info['id_prov_prod']))
                    if producto_obj:
                        producto_obj.costo_compra = producto_info['costo_compra']
                        producto_obj.borrado_pvxpr = False  # Por si estaba marcado como borrado
                        producto_obj.save()
                else:  # Nuevo producto
                    Proveedoresxproductos.objects.create(
                        id_proveedor=proveedor,
                        id_producto_id=producto_info['producto_id'],
                        costo_compra=producto_info['costo_compra'],
                        borrado_pvxpr=False
                    )

            logger.info(f"Proveedor {proveedor_id} modificado exitosamente")

        return JsonResponse({'success': True, 'message': 'Proveedor modificado exitosamente.'})

    except Exception as e:
        logger.error(f"Error al modificar proveedor {proveedor_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})
    
@require_GET
def cargar_datos_proveedor(request, proveedor_id):
    """Cargar datos del proveedor para edición"""
    try:
        proveedor = get_object_or_404(Proveedores, pk=proveedor_id)
        
        # Obtener locales actuales del proveedor
        locales_actuales = Proveedoresxloccom.objects.filter(
            id_proveedor=proveedor
        ).values_list('id_loc_com', flat=True)
        
        # Obtener productos actuales del proveedor
        productos_actuales = Proveedoresxproductos.objects.filter(
            id_proveedor=proveedor, 
            borrado_pvxpr=False
        ).values('id_prov_prod', 'id_producto', 'costo_compra')
        
        # Datos para el template
        data = {
            'proveedor': {
                'id_proveedor': proveedor.id_proveedor,
                'cuit_prov': proveedor.cuit_prov,
                'nombre_prov': proveedor.nombre_prov,
                'email_prov': proveedor.email_prov,
                'telefono_prov': proveedor.telefono_prov,
                'direccion_prov': proveedor.direccion_prov,
            },
            'locales_actuales': list(locales_actuales),
            'locales_comerciales': list(LocalesComerciales.objects.all().values('id_loc_com', 'nombre_loc_com')),
            'productos_actuales': list(productos_actuales),
            'productos_disponibles': list(Productos.objects.filter(borrado_prod=False).values('id_producto', 'nombre_producto')),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error al cargar datos del proveedor {proveedor_id}: {e}", exc_info=True)
        return JsonResponse({'error': 'Error al cargar datos'}, status=500)

@require_POST
def borrar_proveedor(request, proveedor_id):
    """Borrado lógico de proveedor."""
    try:
        proveedor = Proveedores.all_objects.get(pk=proveedor_id, borrado_prov=False)
        if proveedor.borrar_logico():
            return JsonResponse({'success': True, 'message': 'Proveedor eliminado correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'El proveedor ya estaba eliminado.'})
    except Proveedores.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Proveedor no encontrado o ya eliminado.'})
    except Exception as e:
        logger.error(f"Error al borrar proveedor {proveedor_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def recuperar_proveedor(request, proveedor_id):
    """Restaurar proveedor borrado lógicamente."""
    try:
        proveedor = Proveedores.all_objects.get(pk=proveedor_id, borrado_prov=True)
        if proveedor.restaurar():
            return JsonResponse({'success': True, 'message': 'Proveedor restaurado correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'El proveedor ya estaba activo.'})
    except Proveedores.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Proveedor no encontrado o ya activo.'})
    except Exception as e:
        logger.error(f"Error al restaurar proveedor {proveedor_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


# ===============================================
# LOCALES COMERCIALES
# ===============================================

def _serialize_locales(queryset, is_deleted_view):
    """Serializa locales comerciales para DataTables."""
    data = []
    for loc in queryset:
        local_data = {
            'id_loc_com': loc.id_loc_com,
            'nombre_loc_com': loc.nombre_loc_com,
            'provincia_nombre': loc.id_provincia.nombre_provincia,
            'cod_postal_loc_com': loc.cod_postal_loc_com or '',
            'telefono_loc_com': loc.telefono_loc_com or '',
            'direccion_loc_com': loc.direccion_loc_com or '',
            'fecha_alta_loc_com': loc.fecha_alta_loc_com.strftime('%Y-%m-%d'),
        }

        if is_deleted_view:
            local_data.update({
                'fh_borrado_lc': loc.fh_borrado_lc.strftime('%Y-%m-%d %H:%M') if loc.fh_borrado_lc else ''
            })

        data.append(local_data)
    return data

def listar_locales(request):
    """Renderiza la página principal de locales comerciales."""
    form = LocalComercialRegistroForm()
    provincias = Provincias.objects.all() # Para el select de modificación/registro
    return render(request, 'a_central/locales/listar_locales.html', {'form': form, 'provincias': provincias})


@require_GET
def locales_disponibles_api(request):
    """Devuelve locales activos."""
    try:
        locales = LocalesComerciales.objects.select_related('id_provincia').all().order_by('id_loc_com')
        data = _serialize_locales(locales, is_deleted_view=False)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar locales disponibles: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener locales.'}, status=500)


@require_GET
def locales_eliminados_api(request):
    """Devuelve locales borrados lógicamente."""
    try:
        locales = LocalesComerciales.all_objects.select_related('id_provincia').filter(borrado_loc_com=True).order_by('-id_loc_com')
        data = _serialize_locales(locales, is_deleted_view=True)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar locales eliminados: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener locales eliminados.'}, status=500)

@require_POST
def registrar_local(request):
    """Crea un nuevo local comercial."""
    form = LocalComercialRegistroForm(request.POST)

    if not form.is_valid():
        errors = _form_errors_to_dict(form)
        return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors})

    data = form.cleaned_data
    try:
        with transaction.atomic():
            LocalesComerciales.all_objects.create(
                id_provincia=data['id_provincia'],
                nombre_loc_com=data['nombre_loc_com'],
                cod_postal_loc_com=data.get('cod_postal_loc_com'),
                telefono_loc_com=data.get('telefono_loc_com'),
                direccion_loc_com=data.get('direccion_loc_com'),
                borrado_loc_com=False
            )
        return JsonResponse({'success': True, 'message': 'Local Comercial registrado exitosamente.'})
    except IntegrityError as e:
        # Esto debería ser manejado por la validación del formulario (clean), pero es un fallback
        return JsonResponse({'success': False, 'error': f'Error de integridad: {str(e)}'})
    except Exception as e:
        logger.error(f"Error al registrar local: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def modificar_local(request, local_id):
    """Edita los datos de un local comercial."""
    try:
        local = get_object_or_404(LocalesComerciales, pk=local_id)
        
        # Simular el formulario para validación
        form = LocalComercialRegistroForm(request.POST)
        form.is_valid() # Carga los datos, pero las validaciones de unicidad fallarán para el propio objeto

        # Obtener datos manualmente para la edición
        id_provincia = request.POST.get('id_provincia')
        nombre = request.POST.get('nombre_loc_com')

        # 1. Validación de unicidad manual (Excluir el local actual)
        if LocalesComerciales.all_objects.exclude(pk=local_id).filter(
            id_provincia_id=id_provincia, 
            nombre_loc_com=nombre
        ).exists():
            raise IntegrityError('Ya existe un local comercial con este nombre en la provincia seleccionada.')
        
        # 2. Actualización de datos
        with transaction.atomic():
            local.id_provincia_id = id_provincia
            local.nombre_loc_com = nombre
            local.cod_postal_loc_com = request.POST.get('cod_postal_loc_com') or None
            local.telefono_loc_com = request.POST.get('telefono_loc_com') or None
            local.direccion_loc_com = request.POST.get('direccion_loc_com') or None
            local.save()

        return JsonResponse({'success': True, 'message': 'Local Comercial modificado exitosamente.'})

    except IntegrityError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        logger.error(f"Error al modificar local {local_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def borrar_local(request, local_id):
    """Borrado lógico de local comercial."""
    try:
        local = LocalesComerciales.all_objects.get(pk=local_id, borrado_loc_com=False)
        if local.borrar_logico():
            return JsonResponse({'success': True, 'message': 'Local Comercial eliminado correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'El local ya estaba eliminado.'})
    except LocalesComerciales.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Local Comercial no encontrado o ya eliminado.'})
    except Exception as e:
        logger.error(f"Error al borrar local {local_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def recuperar_local(request, local_id):
    """Restaurar local comercial borrado lógicamente."""
    try:
        local = LocalesComerciales.all_objects.get(pk=local_id, borrado_loc_com=True)
        if local.restaurar():
            return JsonResponse({'success': True, 'message': 'Local Comercial restaurado correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'El local ya estaba activo.'})
    except LocalesComerciales.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Local Comercial no encontrado o ya activo.'})
    except Exception as e:
        logger.error(f"Error al restaurar local {local_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


# ===============================================
# PRODUCTOS
# ===============================================

def _serialize_productos(queryset, is_deleted_view):
    """Serializa productos para DataTables."""
    data = []
    for prod in queryset:
        # Formatear el precio_unit_prod como string (ej. "150.50")
        precio_formato = f"{prod.precio_unit_prod:.2f}" if prod.precio_unit_prod is not None else '0.00'
        
        # Obtener el nombre de la marca
        nombre_marca = prod.id_marca.nombre_marca if prod.id_marca else 'Sin Marca'

        stock = Stock.objects.filter(id_producto=prod.id_producto).first()
        producto_data = {
            'id_producto': prod.id_producto,
            'nombre_producto': prod.nombre_producto or 'N/A',
            'id_marca': prod.id_marca_id, # Para el modal de edición
            'nombre_marca': nombre_marca,
            'precio_unit_prod': precio_formato,
            'fecha_alta_prod': prod.fecha_alta_prod.strftime('%Y-%m-%d'),
            "id_loc_com": stock.id_loc_com_id,
            "stock_min_pxlc": stock.stock_min_pxlc,

        }

        if is_deleted_view:
            producto_data.update({
                'fh_borrado_prod': prod.fh_borrado_prod.strftime('%Y-%m-%d %H:%M') if prod.fh_borrado_prod else ''
            })

        data.append(producto_data)
    return data

from a_central.models import LocalesComerciales

def listar_productos(request):
    """Renderiza la página principal de productos."""
    form = ProductoRegistroForm()
    marcas = Marcas.objects.all()  # Para el select de marca
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)  # Para el select de locales

    return render(request, 'a_central/productos/listar_productos.html', {
        'form': form,
        'marcas': marcas,
        'locales': locales,  # ✅ Necesario para poblar el combo del modal
    })


@require_GET
def productos_disponibles_api(request):
    """Devuelve productos activos."""
    try:
        # Usamos select_related para traer la marca en la misma consulta
        productos = Productos.objects.select_related('id_marca').all().order_by('id_producto')
        data = _serialize_productos(productos, is_deleted_view=False)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar productos disponibles: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener productos.'}, status=500)


@require_GET
def productos_eliminados_api(request):
    """Devuelve productos borrados lógicamente."""
    try:
        productos = Productos.all_objects.select_related('id_marca').filter(borrado_prod=True).order_by('-id_producto')
        data = _serialize_productos(productos, is_deleted_view=True)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar productos eliminados: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener productos eliminados.'}, status=500)

from django.db import transaction, IntegrityError
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import logging
from a_central.models import Productos, LocalesComerciales
from a_stock.models import Stock
from .forms import ProductoRegistroForm  # tu formulario existente

logger = logging.getLogger(__name__)

@require_POST
def registrar_producto(request):
    """Crea un nuevo producto y su registro de stock inicial."""
    form = ProductoRegistroForm(request.POST)

    if not form.is_valid():
        errors = _form_errors_to_dict(form)
        return JsonResponse({
            'success': False,
            'error': 'Error de validación',
            'details': errors
        })

    data = form.cleaned_data
    try:
        with transaction.atomic():
            # 1️⃣ Crear el producto
            producto = Productos.all_objects.create(
                nombre_producto=data['nombre_producto'],
                id_marca=data['id_marca'],
                precio_unit_prod=data['precio_unit_prod'],
                tipo_unidad=data['tipo_unidad'],
                cantidad_por_pack=data.get('cantidad_por_pack'),
                borrado_prod=False
            )

            # 2️⃣ Obtener datos del formulario del modal
            id_loc_com = request.POST.get('id_loc_com')
            stock_min_pxlc = int(request.POST.get('stock_min_pxlc', 0))

            # 3️⃣ Crear stock automáticamente
            if id_loc_com:
                Stock.objects.create(
                    id_producto=producto,
                    id_loc_com_id=id_loc_com,
                    stock_pxlc=0,
                    stock_min_pxlc=stock_min_pxlc,
                    borrado_pxlc=False
                )

        return JsonResponse({
            'success': True,
            'message': 'Producto y stock registrados exitosamente.'
        })

    except IntegrityError as e:
        return JsonResponse({
            'success': False,
            'error': f'Error de integridad: {str(e)}'
        })

    except Exception as e:
        logger.error(f"Error al registrar producto: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
def modificar_producto(request, producto_id):
    """Edita los datos de un producto."""
    try:
        producto = get_object_or_404(Productos.all_objects, pk=producto_id)
        
        nombre = request.POST.get('nombre_producto')
        id_marca = request.POST.get('id_marca')
        precio = request.POST.get('precio_unit_prod')
        stock_minimo = request.POST.get('stock_min_pxlc')
        
        # 1. Validación de unicidad manual (Excluir el producto actual)
        if Productos.all_objects.exclude(pk=producto_id).filter(nombre_producto__iexact=nombre).exists():
            raise IntegrityError('Ya existe otro producto con el mismo nombre.')
        
        # 2. Actualización de datos
        with transaction.atomic():
            producto.nombre_producto = nombre
            producto.id_marca_id = id_marca if id_marca else None
            producto.precio_unit_prod = precio
            producto.save()

            # 🔥 🔥 Actualizar stock mínimo
            stock = Stock.objects.filter(id_producto=producto, borrado_pxlc=False).first()
            if stock:
                stock.stock_min_pxlc = stock_minimo
                stock.save()

        return JsonResponse({'success': True, 'message': 'Producto modificado exitosamente.'})

    except IntegrityError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        logger.error(f"Error al modificar producto {producto_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})

@require_GET
def obtener_stock_minimo(request, producto_id, id_loc_com):
    stock = Stock.objects.get(id_producto=producto_id, id_loc_com=id_loc_com)
    return JsonResponse({'stock_minimo': stock.stock_min_pxlc})

@require_POST
def borrar_producto(request, producto_id):
    """Borrado lógico de producto."""
    try:
        producto = Productos.all_objects.get(pk=producto_id, borrado_prod=False)
        if producto.borrar_logico():
            return JsonResponse({'success': True, 'message': 'Producto eliminado correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'El producto ya estaba eliminado.'})
    except Productos.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado o ya eliminado.'})
    except Exception as e:
        logger.error(f"Error al borrar producto {producto_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def recuperar_producto(request, producto_id):
    """Restaurar producto borrado lógicamente."""
    try:
        producto = Productos.all_objects.get(pk=producto_id, borrado_prod=True)
        if producto.restaurar():
            return JsonResponse({'success': True, 'message': 'Producto restaurado correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'El producto ya estaba activo.'})
    except Productos.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado o ya activo.'})
    except Exception as e:
        logger.error(f"Error al restaurar producto {producto_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})

# ===============================================
# BILLETERAS VIRTUALES
# ===============================================

def _serialize_billeteras(queryset, is_deleted_view):
    """Serializa billeteras virtuales para DataTables."""
    data = []
    for bv in queryset:
        saldo_formato = f"{bv.saldo_bv:.2f}" if bv.saldo_bv is not None else '0.00'
        
        billetera_data = {
            'id_bv': bv.id_bv,
            'nombre_bv': bv.nombre_bv,
            'usuario_bv': bv.usuario_bv,
            'cbu_bv': bv.cbu_bv or 'N/A',
            'saldo_bv': saldo_formato,
            'fh_alta_bv': bv.fh_alta_bv.strftime('%Y-%m-%d %H:%M'),
            # No exponemos la contraseña
        }

        if is_deleted_view:
            billetera_data.update({
                'fh_borrado_bv': bv.fh_borrado_bv.strftime('%Y-%m-%d %H:%M') if bv.fh_borrado_bv else ''
            })
        else:
             # Necesario para el modal de edición
            billetera_data.update({
                'contrasena_bv_hash': bv.contrasena_bv, # Se mantiene el hash/texto original
            })


        data.append(billetera_data)
    return data

def listar_billeteras(request):
    """Renderiza la página principal de billeteras virtuales."""
    form = BilleteraRegistroForm()
    return render(request, 'a_central/billeteras/listar_billeteras.html', {'form': form})


@require_GET
def billeteras_disponibles_api(request):
    """Devuelve billeteras virtuales activas."""
    try:
        billeteras = BilleterasVirtuales.objects.all().order_by('id_bv')
        data = _serialize_billeteras(billeteras, is_deleted_view=False)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar billeteras disponibles: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener billeteras.'}, status=500)


@require_GET
def billeteras_eliminadas_api(request):
    """Devuelve billeteras virtuales borradas lógicamente."""
    try:
        billeteras = BilleterasVirtuales.all_objects.filter(borrado_bv=True).order_by('-id_bv')
        data = _serialize_billeteras(billeteras, is_deleted_view=True)
        return JsonResponse({'data': data})
    except Exception as e:
        logger.error(f"Error al listar billeteras eliminadas: {e}", exc_info=True)
        return JsonResponse({'error': 'Error interno al obtener billeteras eliminadas.'}, status=500)


@require_POST
def registrar_billetera(request):
    """Crea una nueva billetera virtual."""
    # Usamos la Opción 2 del form para facilitar la inserción de la contraseña sin hashing
    form = BilleteraRegistroForm(request.POST) 

    if not form.is_valid():
        errors = _form_errors_to_dict(form)
        return JsonResponse({'success': False, 'error': 'Error de validación', 'details': errors})

    data = form.cleaned_data
    try:
        # Nota: La contraseña se guarda sin hash por simplicidad. Usar make_password() en producción.
        with transaction.atomic():
            BilleterasVirtuales.all_objects.create(
                nombre_bv=data['nombre_bv'],
                usuario_bv=data['usuario_bv'],
                contrasena_bv=data['contrasena_bv'], # Sin hashing
                cbu_bv=data.get('cbu_bv'),
                saldo_bv=data.get('saldo_bv') or 0.00,
                fh_alta_bv=timezone.now(),
                borrado_bv=False
            )
        return JsonResponse({'success': True, 'message': 'Billetera Virtual registrada exitosamente.'})
    except IntegrityError as e:
        return JsonResponse({'success': False, 'error': f'Error de integridad: Ya existe un registro con ese Usuario o CBU/CVU.'})
    except Exception as e:
        logger.error(f"Error al registrar billetera virtual: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def modificar_billetera(request, billetera_id):
    """Edita los datos de una billetera virtual."""
    try:
        billetera = get_object_or_404(BilleterasVirtuales.all_objects, pk=billetera_id)
        
        nombre = request.POST.get('nombre_bv')
        usuario = request.POST.get('usuario_bv')
        cbu = request.POST.get('cbu_bv')
        saldo = request.POST.get('saldo_bv')
        nueva_contrasena = request.POST.get('nueva_contrasena_bv')

        # 1. Validación de unicidad de usuario (Excluir el objeto actual)
        if BilleterasVirtuales.all_objects.exclude(pk=billetera_id).filter(usuario_bv__iexact=usuario).exists():
            raise IntegrityError('Ya existe otra billetera con el mismo nombre de usuario.')
        
        # 2. Validación de unicidad de CBU
        if cbu and BilleterasVirtuales.all_objects.exclude(pk=billetera_id).filter(cbu_bv=cbu).exists():
             raise IntegrityError('Ya existe otra billetera con el mismo CBU/CVU.')
        
        # 3. Actualización de datos
        with transaction.atomic():
            billetera.nombre_bv = nombre
            billetera.usuario_bv = usuario
            billetera.cbu_bv = cbu if cbu else None
            billetera.saldo_bv = saldo

            # Actualizar contraseña solo si se proporciona una nueva
            if nueva_contrasena:
                # Nota: La contraseña se guarda sin hash. Usar make_password() en producción.
                billetera.contrasena_bv = nueva_contrasena 

            billetera.save()

        return JsonResponse({'success': True, 'message': 'Billetera Virtual modificada exitosamente.'})

    except IntegrityError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        logger.error(f"Error al modificar billetera virtual {billetera_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def borrar_billetera(request, billetera_id):
    """Borrado lógico de billetera virtual."""
    try:
        billetera = BilleterasVirtuales.all_objects.get(pk=billetera_id, borrado_bv=False)
        if billetera.borrar_logico():
            return JsonResponse({'success': True, 'message': 'Billetera Virtual eliminada correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'La billetera ya estaba eliminada.'})
    except BilleterasVirtuales.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Billetera Virtual no encontrada o ya eliminada.'})
    except Exception as e:
        logger.error(f"Error al borrar billetera virtual {billetera_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def recuperar_billetera(request, billetera_id):
    """Restaurar billetera virtual borrada lógicamente."""
    try:
        billetera = BilleterasVirtuales.all_objects.get(pk=billetera_id, borrado_bv=True)
        if billetera.restaurar():
            return JsonResponse({'success': True, 'message': 'Billetera Virtual restaurada correctamente.'})
        else:
            return JsonResponse({'success': False, 'error': 'La billetera ya estaba activa.'})
    except BilleterasVirtuales.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Billetera Virtual no encontrada o ya activa.'})
    except Exception as e:
        logger.error(f"Error al restaurar billetera virtual {billetera_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})
    
from a_stock.models import Stock
from a_central.models import LocalesComerciales

try:
    Stock.objects.create(
        id_producto=producto,
        id_loc_com=local_default,
        stock_pxlc=0,
        stock_min_pxlc=0
    )
except Exception as e:
    print(f"No se pudo crear stock inicial: {e}")

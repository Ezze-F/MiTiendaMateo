from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import IntegrityError, transaction # Importar transaction para atomicidad
from django.utils import timezone
from datetime import date
import logging 

# Importaciones clave para autenticación y roles
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

# ASUMO LA EXISTENCIA DE ESTOS MODELOS (AJUSTAR SEGÚN TU PROYECTO)
# Nota: La importación de Provincias es crucial aquí
from .models import Empleados, Provincias 
from .forms import EmpleadoRegistroForm, ProvinciaForm

# Configuración de logging para ver errores en la consola
logger = logging.getLogger(__name__)


# ===============================================
# FUNCIONES AUXILIARES DE SERIALIZACIÓN
# ===============================================

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

def _serialize_empleados(queryset, is_deleted_view):
    """
    Serializa un queryset de Empleados al formato requerido por DataTables, 
    manejando las diferencias entre vistas de empleados activos e inactivos.
    """
    data = []
    for emp in queryset:
        dni_str = str(emp.dni_emp) 
        
        empleado_data = {
            'id_empleado': emp.id_empleado,
            'dni_emp': dni_str, 
            'apellido_emp': emp.apellido_emp,
            'nombre_emp': emp.nombre_emp,
        }
        
        if not is_deleted_view:
            empleado_data.update({
                'email_emp': emp.email_emp,
                'telefono_emp': emp.telefono_emp if emp.telefono_emp else 'N/A', 
                'domicilio_emp': emp.domicilio_emp if emp.domicilio_emp else 'N/A', 
                'fecha_alta_emp': emp.fecha_alta_emp.strftime('%Y-%m-%d') if emp.fecha_alta_emp else 'N/A', 
                'rol_emp': emp.get_rol(), 
            })
        else:
            empleado_data.update({
                'fh_borrado_e': emp.fh_borrado_e.strftime('%Y-%m-%d %H:%M') if emp.fh_borrado_e else 'N/A',
            })
            
        data.append(empleado_data)
    return data


def _serialize_provincias(queryset, is_deleted_view):
    """
    Serializa un queryset de Provincias al formato requerido por DataTables, 
    usando los campos exactos del modelo (id_provincia, nombre_provincia, fh_borrado_p).
    """
    data = []
    for prov in queryset:
        provincia_data = {
            'id_provincia': prov.id_provincia,
            'nombre_provincia': prov.nombre_provincia,
        }

        if is_deleted_view:
            fecha_borrado = prov.fh_borrado_p
            
            # AJUSTE FINAL: Si fecha_borrado es None o si no es un datetime, devolvemos 'N/A'.
            if fecha_borrado and isinstance(fecha_borrado, (timezone.datetime, date)):
                try:
                    # Aseguramos que el objeto sea de tipo datetime y tenga zona horaria
                    if not timezone.is_aware(fecha_borrado):
                        # Convertir a aware (asumiendo que era naive pero debería ser de zona)
                        fecha_borrado = timezone.make_aware(fecha_borrado)
                    
                    # Convertir a la zona horaria local para mostrar
                    fecha_local = timezone.localtime(fecha_borrado)
                    
                    # Formato seguro
                    fecha_formateada = fecha_local.strftime('%d-%m-%Y %H:%M:%S')
                except Exception as e:
                    # En caso de error de zona horaria o formato inesperado
                    logger.error(f"Error al formatear fecha {prov.id_provincia}: {e}", exc_info=True)
                    fecha_formateada = 'N/A' # Devolvemos 'N/A' si hay un error de procesamiento

            else:
                # Si el campo es NULL en la BD
                fecha_formateada = 'N/A'

            provincia_data.update({
                'fh_borrado_p': fecha_formateada,
            })
            
        data.append(provincia_data)
    return data


# ===============================================
# VISTAS DE EMPLEADOS (Se mantiene el código anterior)
# ===============================================

# --- VISTA PRINCIPAL EMPLEADOS ---
def listar_empleados(request):
    """Renderiza la plantilla principal de gestión de empleados y envía los roles."""
    roles = Group.objects.all().order_by('name')
    context = {
        'roles': roles,
    }
    return render(request, 'a_central/empleados/listar_empleados.html', context)


# --- API - LISTADO DE EMPLEADOS DISPONIBLES ---
def empleados_disponibles_api(request):
    """Devuelve los datos de empleados activos para DataTables."""
    if request.method == 'GET':
        try:
            empleados = Empleados.objects.filter(borrado_emp=False).select_related('user_auth').prefetch_related('user_auth__groups').order_by('id_empleado')
            data = _serialize_empleados(empleados, is_deleted_view=False)
            return JsonResponse({'data': data})
        except Exception as e:
            logger.error(f"Error al serializar empleados disponibles: {e}", exc_info=True)
            return JsonResponse({'error': 'Error interno al obtener empleados disponibles.'}, status=500)


# --- API - LISTADO DE EMPLEADOS ELIMINADOS ---
def empleados_eliminados_api(request):
    """Devuelve los datos de empleados inactivos/eliminados para DataTables."""
    if request.method == 'GET':
        try:
            empleados = Empleados.objects.filter(borrado_emp=True).select_related('user_auth').order_by('-id_empleado')
            data = _serialize_empleados(empleados, is_deleted_view=True)
            return JsonResponse({'data': data})
        except Exception as e:
            logger.error(f"Error al serializar empleados eliminados: {e}", exc_info=True)
            return JsonResponse({'error': 'Error interno al obtener empleados eliminados.'}, status=500)


# --- OPERACIONES CRUD EMPLEADOS ---
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
            Empleados.objects.create(
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
    # Lógica de modificación de empleado (no modificada)
    try:
        empleado = Empleados.objects.get(pk=empleado_id, borrado_emp=False)
        dni = request.POST.get('dni_emp')
        apellido = request.POST.get('apellido_emp')
        nombre = request.POST.get('nombre_emp')
        email = request.POST.get('email_emp')
        telefono = request.POST.get('telefono_emp')
        domicilio = request.POST.get('domicilio_emp')
        usuario_emp = request.POST.get('usuario_emp')
        id_rol_str = request.POST.get('id_rol')

        # --- Validación de Unicidad para Modificación ---
        if Empleados.objects.exclude(pk=empleado_id).filter(dni_emp=dni).exists():
             raise IntegrityError('El DNI ya está registrado por otro empleado.')
        if Empleados.objects.exclude(pk=empleado_id).filter(email_emp=email).exists():
             raise IntegrityError('El Email ya está registrado por otro empleado.')
        
        if empleado.user_auth:
            if User.objects.exclude(pk=empleado.user_auth.pk).filter(email=email).exists():
                 raise IntegrityError('El Email ya está registrado en el sistema de usuarios (User).')
            if User.objects.exclude(pk=empleado.user_auth.pk).filter(username=str(dni)).exists():
                 raise IntegrityError('El DNI (como nombre de usuario) ya está registrado en el sistema de usuarios (User).')
        
        username_to_check = usuario_emp if usuario_emp else str(dni)
        if empleado.user_auth and User.objects.exclude(pk=empleado.user_auth.pk).filter(username=username_to_check).exists():
            raise IntegrityError('El nombre de Usuario ya está en uso por otro empleado.')

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
    # Lógica de borrado lógico de empleado (no modificada)
    try:
        empleado = Empleados.objects.get(pk=empleado_id, borrado_emp=False)
        empleado.borrado_emp = True
        empleado.fecha_baja_emp = date.today()
        empleado.fh_borrado_e = timezone.now() 
        empleado.save()

        if empleado.user_auth:
            empleado.user_auth.is_active = False
            empleado.user_auth.save()

        return JsonResponse({'success': True})

    except Empleados.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado o ya está dado de baja.'})
    except Exception as e:
        logger.error(f"Error al borrar empleado {empleado_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def recuperar_empleado(request, empleado_id):
    # Lógica de recuperación de empleado (no modificada)
    try:
        empleado = Empleados.objects.get(pk=empleado_id, borrado_emp=True)
        empleado.borrado_emp = False
        empleado.fecha_baja_emp = None 
        empleado.fh_borrado_e = None   
        empleado.save()
        
        if empleado.user_auth:
            empleado.user_auth.is_active = True
            empleado.user_auth.save()

        return JsonResponse({'success': True})

    except Empleados.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado o ya está activo.'})
    except Exception as e:
        logger.error(f"Error al recuperar empleado {empleado_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


# ===============================================
# VISTAS DE PROVINCIAS (Ajustadas al nuevo modelo)
# ===============================================

# --- VISTA PRINCIPAL PROVINCIAS ---
def listar_provincias(request):
    """Renderiza la plantilla principal de gestión de provincias."""
    return render(request, 'a_central/provincias/listar_provincias.html')

# --- API - LISTADO DE PROVINCIAS ACTIVAS ---
def provincias_activas_api(request):
    """Devuelve los datos de provincias activas (borrado_provincia=False) para DataTables."""
    if request.method == 'GET':
        try:
            # Filtra por borrado_provincia=False
            provincias = Provincias.objects.filter(borrado_provincia=False).order_by('nombre_provincia')
            data = _serialize_provincias(provincias, is_deleted_view=False)
            return JsonResponse({'data': data})
        except Exception as e:
            logger.error(f"Error al serializar provincias activas: {e}", exc_info=True)
            return JsonResponse({'error': 'Error interno al obtener provincias activas.'}, status=500)

# --- API - LISTADO DE PROVINCIAS ELIMINADAS ---
def provincias_eliminadas_api(request):
    """Devuelve los datos de provincias eliminadas (borrado_provincia=True) para DataTables."""
    if request.method == 'GET':
        try:
            # Filtra por borrado_provincia=True
            provincias = Provincias.objects.filter(borrado_provincia=True).order_by('-id_provincia')
            data = _serialize_provincias(provincias, is_deleted_view=True)
            return JsonResponse({'data': data})
        except Exception as e:
            logger.error(f"Error al serializar provincias eliminadas: {e}", exc_info=True)
            return JsonResponse({'error': 'Error interno al obtener provincias eliminadas.'}, status=500)


# --- CRUD - REGISTRAR PROVINCIA ---
@require_POST
def registrar_provincia(request):
    """
    Maneja el registro de una nueva provincia usando ProvinciaForm 
    para la validación y estandarización de datos.
    """
    form = ProvinciaForm(request.POST)

    if form.is_valid():
        try:
            nombre_limpio = form.cleaned_data['nombre_provincia']
            
            provincia_existente_borrada = Provincias.objects.filter(
                nombre_provincia__iexact=nombre_limpio, 
                borrado_provincia=True
            ).first()
            
            if provincia_existente_borrada:
                # Usamos el método restore() del modelo
                provincia_existente_borrada.nombre_provincia = nombre_limpio # Se asegura el casing
                provincia_existente_borrada.restore() 
                return JsonResponse({'success': True, 'message': f'Provincia "{nombre_limpio}" recuperada exitosamente.'})
            else:
                form.save()
                return JsonResponse({'success': True, 'message': f'Provincia "{nombre_limpio}" registrada exitosamente.'})

        except Exception as e:
            logger.error(f"Error al registrar/recuperar provincia: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado al guardar: {str(e)}'})
    else:
        return JsonResponse({
            'success': False, 
            'error': 'Error de validación en el formulario.',
            'errors': _form_errors_to_dict(form) 
        }, status=400) 


# --- CRUD - MODIFICAR PROVINCIA ---
@require_POST
def modificar_provincia(request, provincia_id):
    """
    Maneja la modificación de una provincia existente.
    """
    try:
        provincia_instancia = Provincias.objects.get(pk=provincia_id, borrado_provincia=False)
    except Provincias.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Provincia no encontrada o eliminada.'}, status=404)

    form = ProvinciaForm(request.POST, instance=provincia_instancia)

    if form.is_valid():
        try:
            form.save()
            nombre_limpio = form.cleaned_data['nombre_provincia']
            return JsonResponse({'success': True, 'message': f'Provincia "{nombre_limpio}" modificada exitosamente.'})
        except Exception as e:
            logger.error(f"Error al modificar provincia {provincia_id}: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)
    else:
        return JsonResponse({
            'success': False, 
            'error': 'Error de validación en el formulario.',
            'errors': _form_errors_to_dict(form)
        }, status=400)


# --- CRUD - BORRAR PROVINCIA (Baja lógica) (¡FUNCIÓN MEJORADA!) ---
@require_POST
def borrar_provincia(request, provincia_id):
    """Realiza la baja lógica (eliminación) de una provincia utilizando soft_delete()."""
    try:
        # Nos aseguramos de borrar solo provincias activas
        provincia = Provincias.objects.get(pk=provincia_id, borrado_provincia=False)
        
        # MEJORA: Usamos el método soft_delete del modelo.
        provincia.soft_delete()

        return JsonResponse({'success': True, 'message': f'Provincia "{provincia.nombre_provincia}" borrada exitosamente.'})

    except Provincias.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Provincia no encontrada o ya está dada de baja.'}, status=404)
    except Exception as e:
        logger.error(f"Error al borrar provincia {provincia_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# --- CRUD - RECUPERAR PROVINCIA (¡FUNCIÓN MEJORADA!) ---
@require_POST
def recuperar_provincia(request, provincia_id):
    """Realiza la restauración (alta) de una provincia dado de baja utilizando restore()."""
    try:
        # Nos aseguramos de recuperar solo provincias eliminadas
        provincia = Provincias.objects.get(pk=provincia_id, borrado_provincia=True)
        
        # MEJORA: Usamos el método restore del modelo.
        provincia.restore()

        return JsonResponse({'success': True, 'message': f'Provincia "{provincia.nombre_provincia}" recuperada exitosamente.'})

    except Provincias.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Provincia no encontrada o ya está activa.'}, status=404)
    except Exception as e:
        logger.error(f"Error al recuperar provincia {provincia_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
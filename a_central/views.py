import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Roles, Provincias, Sucursales, Empleados
from django.views.decorators.csrf import csrf_exempt


# -------------------------------------------------------------------
# Vistas para el modelo Roles
# -------------------------------------------------------------------

# Vista principal
def listar_roles(request):
    # renderiza el template que incluye data-url para los endpoints
    return render(request, "a_central/roles/listar_roles.html")


# Endpoints para DataTables (GET)
def roles_disponibles_data(request):
    """
    Vista que devuelve los roles disponibles en formato JSON para DataTables.
    """
    roles = Roles.objects.all().values('id_rol', 'nombre_rol', 'descripcion_rol')
    data = []  # <--- ERROR CORREGIDO: Inicialización de la lista
    for rol in roles:
        data.append({
            'id': rol['id_rol'],
            'nombre': rol['nombre_rol'],
            'descripcion': rol['descripcion_rol']
        })
    return JsonResponse({'data': data})


def roles_eliminados_data(request):
    """
    Vista que devuelve los roles eliminados en formato JSON para DataTables.
    """
    roles = Roles.borrados.all().values('id_rol', 'nombre_rol', 'descripcion_rol', 'fecha_borrado')
    data = []  # <--- ERROR CORREGIDO: Inicialización de la lista
    for rol in roles:
        data.append({
            'id': rol['id_rol'],
            'nombre': rol['nombre_rol'],
            'descripcion': rol['descripcion_rol'],
            'fecha_borrado': rol['fecha_borrado'].strftime('%Y-%m-%d %H:%M:%S') if rol['fecha_borrado'] else ''
        })
    return JsonResponse({'data': data})


# CRUD: registrar, editar, eliminar, restaurar
# Todos esperan POST y JSON o form-encoded.
@require_http_methods(["POST"])
def registrar_rol(request):
    try:
        if request.content_type == "application/json":
            payload = json.loads(request.body)
        else:
            # form-encoded
            payload = request.POST
        nombre = payload.get("nombre_rol")
        descripcion = payload.get("descripcion_rol", "")

        if not nombre:
            return JsonResponse({"success": False, "error": "El nombre es obligatorio."}, status=400)

        # Evitar duplicados activos (opcional)
        if Roles.all_objects.filter(nombre_rol=nombre, borrado_logico=False).exists():
            return JsonResponse({"success": False, "error": "Ya existe un rol con ese nombre."}, status=400)

        rol = Roles.all_objects.create(
            nombre_rol=nombre,
            descripcion_rol=descripcion
        )
        return JsonResponse({"success": True, "id": rol.id_rol})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def modificar_rol(request, rol_id):
    try:
        if request.content_type == "application/json":
            payload = json.loads(request.body)
        else:
            payload = request.POST
        nombre = payload.get("nombre_rol")
        descripcion = payload.get("descripcion_rol", "")

        rol = get_object_or_404(Roles.all_objects, pk=rol_id)
        if nombre:
            # evitar colisiones con otro rol activo
            if Roles.all_objects.filter(nombre_rol=nombre, borrado_logico=False).exclude(pk=rol_id).exists():
                return JsonResponse({"success": False, "error": "Ya existe otro rol con ese nombre."}, status=400)
            rol.nombre_rol = nombre
        rol.descripcion_rol = descripcion
        rol.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def borrar_rol(request, rol_id):
    """
    Vista para el borrado lógico de un rol.
    """
    try:
        rol = get_object_or_404(Roles, pk=rol_id)
        rol.eliminacion()
        return JsonResponse({"success": True})
    except Exception as e:
        print(f"Error al intentar borrar el rol: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def recuperar_rol(request, rol_id):
    try:
        rol = get_object_or_404(Roles.borrados, pk=rol_id)
        rol.restauracion()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



# -------------------------------------------------------------------
# Vistas para el modelo Provincias
# -------------------------------------------------------------------

def provincias_list(request):
    provincias = Provincias.objects.filter(borrado_logico=False)
    return render(request, 'a_central/provincias/provincias_list.html', {'provincias': provincias})

def provincia_create(request):
    if request.method == 'POST':
        nombre_provincia = request.POST.get('nombre_provincia')
        Provincias.objects.create(nombre_provincia=nombre_provincia)
        return redirect(reverse('provincias_list'))
    return render(request, 'a_central/provincias/provincia_form.html')

def provincia_update(request, pk):
    provincia = get_object_or_404(Provincias, pk=pk)
    if request.method == 'POST':
        provincia.nombre_provincia = request.POST.get('nombre_provincia')
        provincia.save()
        return redirect(reverse('provincias_list'))
    return render(request, 'a_central/provincias/provincia_form.html', {'provincia': provincia})

def provincia_delete(request, pk):
    provincia = get_object_or_404(Provincias, pk=pk)
    if request.method == 'POST':
        provincia.borrado_logico = True
        provincia.save()
        return redirect(reverse('provincias_list'))
    return render(request, 'a_central/provincias/provincia_confirm_delete.html', {'provincia': provincia})


# -------------------------------------------------------------------
# Vistas para el modelo Sucursales
# -------------------------------------------------------------------


def sucursales_list(request):
    sucursales = Sucursales.objects.filter(borrado_logico=False)
    return render(request, 'a_central/sucursales/sucursales_list.html', {'sucursales': sucursales})

def sucursal_create(request):
    if request.method == 'POST':
        nombre_sucursal = request.POST.get('nombre_sucursal')
        cod_postal_suc = request.POST.get('cod_postal_suc')
        telefono_suc = request.POST.get('telefono_suc')
        direccion_suc = request.POST.get('direccion_suc')
        id_provincia = request.POST.get('id_provincia')
        provincia = get_object_or_404(Provincias, pk=id_provincia)
        Sucursales.objects.create(nombre_sucursal=nombre_sucursal, cod_postal_suc=cod_postal_suc, telefono_suc=telefono_suc, direccion_suc=direccion_suc, id_provincia=provincia)
        return redirect(reverse('sucursales_list'))
    provincias = Provincias.objects.filter(borrado_logico=False)
    return render(request, 'a_central/sucursales/sucursal_form.html', {'provincias': provincias})

def sucursal_update(request, pk):
    sucursal = get_object_or_404(Sucursales, pk=pk)
    if request.method == 'POST':
        sucursal.nombre_sucursal = request.POST.get('nombre_sucursal')
        sucursal.cod_postal_suc = request.POST.get('cod_postal_suc')
        sucursal.telefono_suc = request.POST.get('telefono_suc')
        sucursal.direccion_suc = request.POST.get('direccion_suc')
        id_provincia = request.POST.get('id_provincia')
        provincia = get_object_or_404(Provincias, pk=id_provincia)
        sucursal.id_provincia = provincia
        sucursal.save()
        return redirect(reverse('sucursales_list'))
    provincias = Provincias.objects.filter(borrado_logico=False)
    return render(request, 'a_central/sucursales/sucursal_form.html', {'sucursal': sucursal, 'provincias': provincias})

def sucursal_delete(request, pk):
    sucursal = get_object_or_404(Sucursales, pk=pk)
    if request.method == 'POST':
        sucursal.borrado_logico = True
        sucursal.save()
        return redirect(reverse('sucursales_list'))
    return render(request, 'a_central/sucursales/sucursal_confirm_delete.html', {'sucursal': sucursal})


# -------------------------------------------------------------------
# Vistas para el modelo Empleados
# -------------------------------------------------------------------


def empleados_list(request):
    empleados = Empleados.objects.filter(borrado_logico=False)
    return render(request, 'a_central/empleados/empleados_list.html', {'empleados': empleados})

def empleado_create(request):
    if request.method == 'POST':
        legajo_nro_empleado = request.POST.get('legajo_nro_empleado')
        dni_empleado = request.POST.get('dni_empleado')
        apellido_empleado = request.POST.get('apellido_empleado')
        nombre_empleado = request.POST.get('nombre_empleado')
        email_empleado = request.POST.get('email_empleado')
        telefono_empleado = request.POST.get('telefono_empleado')
        domicilio_empleado = request.POST.get('domicilio_empleado')
        fecha_baja = request.POST.get('fecha_baja')
        contrasena_empleado = request.POST.get('contrasena_empleado')
        id_rol = request.POST.get('id_rol')
        id_sucursal = request.POST.get('id_sucursal')
        
        rol = get_object_or_404(Roles, pk=id_rol)
        sucursal = get_object_or_404(Sucursales, pk=id_sucursal)

        Empleados.objects.create(
            legajo_nro_empleado=legajo_nro_empleado,
            dni_empleado=dni_empleado,
            apellido_empleado=apellido_empleado,
            nombre_empleado=nombre_empleado,
            email_empleado=email_empleado,
            telefono_empleado=telefono_empleado,
            domicilio_empleado=domicilio_empleado,
            fecha_baja=fecha_baja if fecha_baja else None,
            contrasena_empleado=contrasena_empleado,
            id_rol=rol,
            id_sucursal=sucursal
        )
        return redirect(reverse('empleados_list'))
    roles = Roles.objects.filter(borrado_logico=False)
    sucursales = Sucursales.objects.filter(borrado_logico=False)
    return render(request, 'a_central/empleados/empleado_form.html', {'roles': roles, 'sucursales': sucursales})

def empleado_update(request, pk):
    empleado = get_object_or_404(Empleados, pk=pk)
    if request.method == 'POST':
        empleado.dni_empleado = request.POST.get('dni_empleado')
        empleado.apellido_empleado = request.POST.get('apellido_empleado')
        empleado.nombre_empleado = request.POST.get('nombre_empleado')
        empleado.email_empleado = request.POST.get('email_empleado')
        empleado.telefono_empleado = request.POST.get('telefono_empleado')
        empleado.domicilio_empleado = request.POST.get('domicilio_empleado')
        fecha_baja = request.POST.get('fecha_baja')
        empleado.fecha_baja = fecha_baja if fecha_baja else None
        empleado.contrasena_empleado = request.POST.get('contrasena_empleado')
        id_rol = request.POST.get('id_rol')
        id_sucursal = request.POST.get('id_sucursal')
        
        rol = get_object_or_404(Roles, pk=id_rol)
        sucursal = get_object_or_404(Sucursales, pk=id_sucursal)
        empleado.id_rol = rol
        empleado.id_sucursal = sucursal
        empleado.save()
        return redirect(reverse('empleados_list'))
    roles = Roles.objects.filter(borrado_logico=False)
    sucursales = Sucursales.objects.filter(borrado_logico=False)
    return render(request, 'a_central/empleados/empleado_form.html', {'empleado': empleado, 'roles': roles, 'sucursales': sucursales})

def empleado_delete(request, pk):
    empleado = get_object_or_404(Empleados, pk=pk)
    if request.method == 'POST':
        empleado.borrado_logico = True
        empleado.save()
        return redirect(reverse('empleados_list'))
    return render(request, 'a_central/empleados/empleado_confirm_delete.html', {'empleado': empleado})

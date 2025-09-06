from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Roles
from .forms import RolForm

# Create your views here.

# Listar roles
def listar_roles(request):
    roles_disponibles = Roles.objects.filter(borrado_logico=False)
    roles_eliminados = Roles.objects.filter(borrado_logico=True)
    return render(request, "a_roles/listado_roles.html", {
        "roles_disponibles": roles_disponibles,
        "roles_eliminados": roles_eliminados
    })

# Registrar rol
def registrar_rol(request):
    data = {}
    if request.method == "POST":
        form = RolForm(request.POST)
        if form.is_valid():
            rol = form.save(commit=False)
            rol.borrado_logico = False
            rol.save()
            data["form_is_valid"] = True
            roles_disponibles = Roles.objects.filter(borrado_logico=False)
            data["html_roles_disponibles"] = render_to_string("a_roles/partials/tabla_roles_disponibles.html", {
                "roles_disponibles": roles_disponibles
            })
            roles_eliminados = Roles.objects.filter(borrado_logico=True)
            data["html_roles_eliminados"] = render_to_string("a_roles/partials/tabla_roles_eliminados.html", {
                "roles_eliminados": roles_eliminados
            })
        else:
            data["form_is_valid"] = False
    else:
        form = RolForm()
    context = {"form": form}
    data["html_form"] = render_to_string("a_roles/partials/rol_form.html", context, request=request)
    return JsonResponse(data)

# Modificar rol
def modificar_rol(request, pk):
    rol = get_object_or_404(Roles, pk=pk)
    data = {}
    if request.method == "POST":
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            form.save()
            data["form_is_valid"] = True
            roles_disponibles = Roles.objects.filter(borrado_logico=False)
            data["html_roles_disponibles"] = render_to_string("a_roles/partials/tabla_roles_disponibles.html", {
                "roles_disponibles": roles_disponibles
            })
            roles_eliminados = Roles.objects.filter(borrado_logico=True)
            data["html_roles_eliminados"] = render_to_string("a_roles/partials/tabla_roles_eliminados.html", {
                "roles_eliminados": roles_eliminados
            })
        else:
            data["form_is_valid"] = False
    else:
        form = RolForm(instance=rol)
    context = {"form": form}
    data["html_form"] = render_to_string("a_roles/partials/rol_form.html", context, request=request)
    return JsonResponse(data)

# Eliminar rol (borrado lógico)
def eliminar_rol(request, pk):
    rol = get_object_or_404(Roles, pk=pk)
    data = {}
    if request.method == "POST":
        rol.borrado_logico = True
        rol.save()
        data["form_is_valid"] = True
        roles_disponibles = Roles.objects.filter(borrado_logico=False)
        data["html_roles_disponibles"] = render_to_string("a_roles/partials/tabla_roles_disponibles.html", {
            "roles_disponibles": roles_disponibles
        })
        roles_eliminados = Roles.objects.filter(borrado_logico=True)
        data["html_roles_eliminados"] = render_to_string("a_roles/partials/tabla_roles_eliminados.html", {
            "roles_eliminados": roles_eliminados
        })
    else:
        context = {"rol": rol}
        data["html_form"] = render_to_string("a_roles/partials/rol_confirm_delete.html", context, request=request)
    return JsonResponse(data)

# Recuperar rol
def recuperar_rol(request, pk):
    rol = get_object_or_404(Roles, pk=pk)
    data = {}
    if request.method == "POST":
        rol.borrado_logico = False
        rol.save()
        data["form_is_valid"] = True
        roles_disponibles = Roles.objects.filter(borrado_logico=False)
        data["html_roles_disponibles"] = render_to_string("a_roles/partials/tabla_roles_disponibles.html", {
            "roles_disponibles": roles_disponibles
        })
        roles_eliminados = Roles.objects.filter(borrado_logico=True)
        data["html_roles_eliminados"] = render_to_string("a_roles/partials/tabla_roles_eliminados.html", {
            "roles_eliminados": roles_eliminados
        })
    else:
        context = {"rol": rol}
        data["html_form"] = render_to_string("a_roles/partials/rol_confirm_recover.html", context, request=request)
    return JsonResponse(data)

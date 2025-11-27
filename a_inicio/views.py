from django.shortcuts import render

def pagina_inicio(request):
    return render(request, 'a_inicio/inicio.html')

def terminos_y_condiciones(request):
    return render(request, 'a_inicio/terminos_condiciones.html')
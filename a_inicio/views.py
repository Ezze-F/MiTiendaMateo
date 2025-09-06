from django.shortcuts import render

def pagina_inicio(request):
    return render(request, 'a_inicio/inicio.html')
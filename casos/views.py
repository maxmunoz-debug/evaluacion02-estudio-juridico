from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Caso
from .forms import ClienteForm

def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'casos/clientes/lista.html', {'clientes': clientes})

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'casos/clientes/formulario.html', {'form': form, 'accion': 'Nuevo Cliente'})

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'casos/clientes/formulario.html', {'form': form, 'accion': 'Editar Cliente'})

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')
    return render(request, 'casos/clientes/eliminar.html', {'cliente': cliente})


def lista_casos(request):
    casos = Caso.objects.all().prefetch_related('abogados')
    return render(request, 'casos/lista_casos.html', {'casos': casos})

def detalle_caso(request, caso_id):
    # Usa get_object_or_404 para responder con error 404 si el caso no existe 
    caso = get_object_or_404(Caso, id=caso_id)
    return render(request, 'casos/detalle_caso.html', {'caso': caso})
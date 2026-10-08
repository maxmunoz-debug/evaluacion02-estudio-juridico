from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Caso
from .forms import ClienteForm
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal
from .models import EstadoCaso, Pago, Expediente

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
    # Pregunta 4: Filtro por estado y cookie 'ultimo_estado'
    casos = Caso.objects.all().prefetch_related('abogados', 'pagos', 'estado')
    estados = EstadoCaso.objects.all()
    
    estado_id = request.GET.get('estado')
    
    if estado_id:
        # Si envían el filtro por URL, filtramos y guardaremos la cookie
        casos = casos.filter(estado_id=estado_id)
    else:
        # Si no envían filtro, revisamos si hay una cookie guardada de antes
        estado_cookie = request.COOKIES.get('ultimo_estado')
        if estado_cookie:
            estado_id = estado_cookie
            casos = casos.filter(estado_id=estado_id)

    response = render(request, 'casos/lista_casos.html', {'casos': casos, 'estados': estados, 'estado_actual': estado_id})
    
    # Si filtraron por URL, guardamos el estado en la cookie
    if request.GET.get('estado'):
        response.set_cookie('ultimo_estado', request.GET.get('estado'))
        
    return response

def detalle_caso(request, caso_id):
    caso = get_object_or_404(Caso, id=caso_id)
    mensaje_error = None
    mensaje_exito = None

    if request.method == 'POST':
        # Pregunta 4: Subir documento al expediente (enctype="multipart/form-data")
        if 'subir_doc' in request.POST:
            exp_id = request.POST.get('expediente_id')
            archivo = request.FILES.get('documento')
            if exp_id and archivo:
                expediente = get_object_or_404(Expediente, id=exp_id)
                expediente.documento = archivo
                expediente.save()
                mensaje_exito = "Documento subido correctamente."

        # Pregunta 4: Registrar un pago
        elif 'registrar_pago' in request.POST:
            monto_str = request.POST.get('monto')
            desc = request.POST.get('descripcion')
            try:
                monto = Decimal(monto_str)
                nuevo_pago = Pago(caso=caso, monto=monto, fecha=date.today(), descripcion=desc)
                # Ejecutamos el clean() que programamos en la Pregunta 1
                nuevo_pago.clean() 
                nuevo_pago.save()
                mensaje_exito = "Pago registrado correctamente."
            except ValidationError as e:
                # Si el caso está cancelado/terminado, clean() lanza este error
                mensaje_error = e.messages[0] if isinstance(e.messages, list) else e.message
            except Exception:
                mensaje_error = "Error al procesar el monto."

    return render(request, 'casos/detalle_caso.html', {
        'caso': caso, 
        'mensaje_error': mensaje_error,
        'mensaje_exito': mensaje_exito
    })

def api_caso(request, caso_id):
    # Pregunta 4: Devolver JSON (JsonResponse)
    caso = get_object_or_404(Caso, id=caso_id)
    datos = {
        'codigo': caso.codigo,
        'cliente': caso.cliente.nombres,
        'estado': caso.estado.nombre,
        'abogados': [a.get_full_name() or a.username for a in caso.abogados.all()],
        'numero_expedientes': caso.expedientes.count(),
        'total_pagado': float(caso.total_pagado())
    }
    return JsonResponse(datos)
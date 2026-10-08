from django.urls import path
from . import views

urlpatterns = [
    # Mantenedor de clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:cliente_id>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    
    # Rutas de casos
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/<int:caso_id>/', views.detalle_caso, name='detalle_caso'),
]
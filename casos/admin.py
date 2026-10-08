from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Cliente, EstadoCaso, Caso, Expediente, Pago, PerfilAbogado


# ---------- Usuarios con su PerfilAbogado (uno a uno) ----------
class PerfilAbogadoInline(admin.StackedInline):
    model = PerfilAbogado
    can_delete = False
    verbose_name_plural = 'Perfil de abogado'


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilAbogadoInline]
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'is_staff', 'colegiatura')
    list_filter = ('is_staff', 'is_superuser', 'groups')

    @admin.display(description='Colegiatura')
    def colegiatura(self, obj):
        return obj.perfil.numero_colegiatura if hasattr(obj, 'perfil') else '-'


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)


# ---------- Cliente ----------
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'documento', 'telefono', 'correo', 'cantidad_casos')
    search_fields = ('nombres', 'documento', 'correo')
    list_filter = ('casos__estado',)

    @admin.display(description='N° casos')
    def cantidad_casos(self, obj):
        return obj.casos.count()


# ---------- EstadoCaso ----------
@admin.register(EstadoCaso)
class EstadoCasoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'permite_pagos')
    search_fields = ('nombre',)
    list_filter = ('permite_pagos',)


# ---------- Caso con Expedientes y Pagos en línea ----------
class ExpedienteInline(admin.TabularInline):
    model = Expediente
    extra = 1


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'cliente', 'estado',
                    'fecha_inicio', 'total_pagado')
    search_fields = ('codigo', 'titulo', 'cliente__nombres', 'cliente__documento')
    list_filter = ('estado', 'abogados', 'fecha_inicio')
    filter_horizontal = ('abogados',)
    inlines = [ExpedienteInline, PagoInline]
    date_hierarchy = 'fecha_inicio'


# ---------- Expediente ----------
@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'juzgado', 'fecha_presentacion', 'caso')
    search_fields = ('numero', 'juzgado', 'caso__codigo')
    list_filter = ('juzgado', 'fecha_presentacion')
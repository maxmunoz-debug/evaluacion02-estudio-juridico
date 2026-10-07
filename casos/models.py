from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class Cliente(models.Model):
    nombres = models.CharField(max_length=150)
    documento = models.CharField('DNI o RUC', max_length=11, unique=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    correo = models.EmailField(blank=True)

    class Meta:
        ordering = ['nombres']

    def __str__(self):
        return f'{self.nombres} ({self.documento})'


class EstadoCaso(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    permite_pagos = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Estado de caso'
        verbose_name_plural = 'Estados de caso'

    def __str__(self):
        return self.nombre


class Caso(models.Model):
    codigo = models.CharField('Código', max_length=20, unique=True)
    titulo = models.CharField('Título', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    fecha_inicio = models.DateField()

    # Uno a muchos: un cliente tiene muchos casos
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name='casos'
    )
    # Uno a muchos: un estado se aplica a muchos casos
    estado = models.ForeignKey(
        EstadoCaso, on_delete=models.PROTECT, related_name='casos'
    )
    # Muchos a muchos: un caso tiene varios abogados y un abogado revisa muchos casos
    abogados = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='casos_asignados', blank=True
    )

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'

    def total_pagado(self):
        total = self.pagos.aggregate(total=Sum('monto'))['total']
        return total or Decimal('0.00')
    total_pagado.short_description = 'Total pagado'


class Expediente(models.Model):
    numero = models.CharField('Número', max_length=50, unique=True)
    juzgado = models.CharField(max_length=150)
    fecha_presentacion = models.DateField('Fecha de presentación')
    caso = models.ForeignKey(
        Caso, on_delete=models.CASCADE, related_name='expedientes'
    )

    def __str__(self):
        return f'Exp. {self.numero} ({self.juzgado})'


class Pago(models.Model):
    caso = models.ForeignKey(
        Caso, on_delete=models.PROTECT, related_name='pagos'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.CharField('Descripción', max_length=200, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'S/ {self.monto} - {self.caso.codigo} ({self.fecha})'

    def clean(self):
        # Regla de negocio: solo se paga si el estado del caso lo permite
        if self.caso_id and not self.caso.estado.permite_pagos:
            raise ValidationError(
                f'No se pueden registrar pagos: el caso está en estado '
                f'"{self.caso.estado}".'
            )
        if self.monto is not None and self.monto <= 0:
            raise ValidationError({'monto': 'El monto debe ser mayor que cero.'})


class PerfilAbogado(models.Model):
    # Uno a uno: cada usuario abogado tiene un solo perfil
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil'
    )
    numero_colegiatura = models.CharField('N° de colegiatura', max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Perfil de abogado'
        verbose_name_plural = 'Perfiles de abogado'

    def __str__(self):
        return f'{self.usuario.get_full_name() or self.usuario.username} - CAL {self.numero_colegiatura}'
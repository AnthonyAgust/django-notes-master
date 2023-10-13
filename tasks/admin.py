from django.contrib import admin
from .models import Task

# MOSTRAR FECHA DE CREACION
class TaskAdmin(admin.ModelAdmin):
  readonly_fields = ('created', )

# MOSTRAR EL PANEL DE TAREAS
admin.site.register(Task, TaskAdmin)
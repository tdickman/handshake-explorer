from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Name)
admin.site.register(models.Block)
admin.site.register(models.Event)

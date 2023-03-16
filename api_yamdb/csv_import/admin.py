from django.contrib import admin
from .models import Anyimport

from import_export import resources
from import_export.admin import ImportExportModelAdmin


class ImportResource(resources.ModelResource):

    class Meta:
        model = Anyimport


class ImportforAdmin(ImportExportModelAdmin):
    resource_classes = [ImportResource]


admin.site.register(Anyimport, ImportforAdmin)

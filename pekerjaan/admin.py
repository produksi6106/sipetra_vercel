from django.contrib import admin
from .models import Mitra, TimKegiatan, BebanHonor, PekerjaanMitra

admin.site.register(PekerjaanMitra)
admin.site.register(Mitra)
admin.site.register(TimKegiatan)
admin.site.register(BebanHonor)
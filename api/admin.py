from django.contrib import admin
from .models import Profile, QrCode, ReliefGoods

admin.site.register(Profile)
admin.site.register(QrCode)
admin.site.register(ReliefGoods)
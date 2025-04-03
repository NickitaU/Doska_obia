from django.contrib import admin
from .models import Category, Advertisement, Response


admin.site.register(Response)
admin.site.register(Advertisement)
admin.site.register(Category)

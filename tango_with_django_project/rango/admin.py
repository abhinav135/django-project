from django.contrib import admin
from rango.models import Category, Page, PageAdmin,CategoryAdmin
from rango.models import UserProfile
# Add in this class to customise the Admin Interface
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

# Register your models here.

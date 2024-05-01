from django.contrib import admin

from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','Title','category','Balance', 'price', 'pdf','Status','premium')
    list_filter = ('name',"price",'premium','created')
    search_fields = ('price','category')
    
    list_editable = ('pdf','Balance','price','Status',"category",'premium','Title')
    prepopulated_fields ={'slug': ('name',)}
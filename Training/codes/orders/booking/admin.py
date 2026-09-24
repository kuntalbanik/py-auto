from django.contrib import admin
from booking.models import Orders, UploadedFile
from django.utils.html import format_html


# Register your models here.
# admin.site.register(Orders)
# admin.site.register(UploadedFile)
@admin.register(Orders)
class OrderModelAdmin(admin.ModelAdmin):

    list_display = ('customer_name', 'division', 'unit_or_spares', 'model', 'so_number', 'order_date', 'value', 'booking_account')
    search_fields = ('customer_name','so_number',)

@admin.register(UploadedFile)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('order', 'open_file_link')
    # search_fields = ('',)

    @admin.display(description='Uploaded File')
    def open_file_link(self, obj):
        # Make sure 'my_file' matches the exact name of your FileField/ImageField
        if obj.file:
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',obj.file.url, obj.title)
        return "No File"
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.html import format_html

# Create your models here.

def validate_file_size(value):
    limit = 3 * 1024 * 1024  # 3 MB in bytes
    if value.size > limit:
        raise ValidationError("File size cannot exceed 3 MB.")

class Orders(models.Model):
    customer_name = models.CharField(max_length=255)
    cbg_or_non_cbg = models.CharField(max_length=15)
    division = models.CharField(max_length=20)
    unit_or_spares = models.CharField(max_length=15)
    model = models.CharField(max_length=20, null=True)
    model_ref = models.CharField(max_length=15, null=True)
    area = models.CharField(max_length=20)
    qty = models.IntegerField()
    value = models.FloatField(max_length=16)
    landed_cost = models.FloatField(max_length=16, null=True)
    po_value = models.FloatField(max_length=16, null=True)
    so_number = models.CharField(max_length=16)
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True)
    sales_commission = models.CharField(max_length=12)
    direct_or_buynsell = models.CharField(max_length=8)
    month = models.CharField(max_length=9)
    year = models.CharField(max_length=8)
    booking_account = models.CharField(max_length=40)
    # file = models.FileField(upload_to='uploads/%Y/%m/%d/', validators=[validate_file_size])

    def __str__(self):
        # This displays the actual file name instead of "<UploadedFile object>"
        return f"{self.customer_name} - {self.division} - {self.so_number} - {self.model}"

    class Meta:
         db_table = 'orders'
         verbose_name = "Order"
         verbose_name_plural = "Orders"
        #  ordering = ['-created_at']

class UploadedFile(models.Model):
    """The child model handling the actual multiple files via Foreign Key"""
    order = models.ForeignKey(
        Orders, 
        on_delete=models.CASCADE, 
        related_name='file'
    )
    title = models.CharField(max_length=80)
    file = models.FileField(upload_to='uploads/', validators=[validate_file_size])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            # This displays the actual file name instead of "<UploadedFile object>"
            return f"{self.order} - {self.uploaded_at}"
    # def __order__(self):
    #      return f"{self.order}"

    # def show_content(self):
    #     return format_html(self.content)


# ==========================================================
# class OrdersForm(forms.ModelForm):
#     class Meta:
#         model = Orders
#         fields = ['customer_name','cbg_or_non_cbg','division','order_type','model',
#                   'model_ref','area','qty','value','landed_cost','po_value',
#                   'so_number','order_date','expected_delivery_date','sales_commission',
#                   'direct_or_buynsell','month','year','booking_account','files']
#         widgets = {
#             'files':forms.FileInput(attrs={'class': 'form-control', 'multiple': True}),
#         }
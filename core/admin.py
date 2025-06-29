from django.contrib import admin
from .models import (
    PurchaseOrders, 
    PurchaseOrderItems,
    JobOrders, 
    Locations, 
    Roasters, 
    GreenBeanLots,
    MqttDevice,
    Farms,
    BeanVarietals
)

# This defines the "inline" view for PurchaseOrderItems
class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItems
    # 'extra' means it will show 1 empty slot for a new item by default.
    extra = 1 

# This defines the custom admin view for PurchaseOrders
class PurchaseOrderAdmin(admin.ModelAdmin):
    # This tells the admin to include the PurchaseOrderItemInline 
    # on the "Add/Change Purchase Order" page.
    inlines = [PurchaseOrderItemInline]
    
    # This customizes the list view of all purchase orders
    list_display = ('po_number', 'supplier_name', 'status', 'order_date')
    list_filter = ('status',)
    search_fields = ('po_number', 'supplier_name')

# --- Main Registration ---

# We unregister the default PurchaseOrders admin and re-register it with our custom class.
# Note: A model can only be registered once.
# admin.site.unregister(PurchaseOrders) # This might be needed if you get an error
admin.site.register(PurchaseOrders, PurchaseOrderAdmin)

# Register the other models as before
admin.site.register(JobOrders)
admin.site.register(Locations)
admin.site.register(Roasters)
admin.site.register(GreenBeanLots)
admin.site.register(MqttDevice)
admin.site.register(Farms)
admin.site.register(BeanVarietals)
#admin.site.register(PurchaseOrderItems) # We can keep this for viewing all items at once


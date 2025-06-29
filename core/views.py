from django.shortcuts import render, redirect
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages # 1. ADD THIS IMPORT
from django.http import JsonResponse
from django.core.serializers import serialize
from django.shortcuts import render, get_object_or_404
import json

from .models import (
    PurchaseOrders, 
    PurchaseOrderItems, 
    Consumables, 
    BeanVarietals, 
    AssociatedImages,
    MqttDevice,
    GreenBeanLots,
)

# [RECOMMENDATION] Add this new view for the dashboard page.
@login_required
def dashboard_view(request):
    """
    This view renders the main navigation page for a logged-in user.
    """
    # We can pass the user's information to the template for a personalized greeting.
    context = {
        'user': request.user
    }
    return render(request, 'core/dashboard.html', context)

# Add this function to core/views.py

@login_required
def live_label_view(request):
    """
    This view renders the HMI page that will display the live QR code label.
    """
    return render(request, 'core/hmi_live_label.html')

@login_required
def create_purchase_order(request):
    """
    This view handles the original purchase order form.
    To simplify things, it will just redirect to the more advanced GCB form for now.
    """
    return redirect('create_gcb_purchase_order')


@login_required
def create_gcb_purchase_order(request):
    """
    This view handles the creation of a Purchase Order specifically for Green Coffee Beans,
    now using the logged-in user automatically.
    """
    if request.method == 'POST':
        try:
            with transaction.atomic():
                po_data = request.POST

                new_po = PurchaseOrders.objects.create(
                    po_number=po_data.get('po_number'),
                    supplier_name=po_data.get('supplier_name'),
                    order_date=po_data.get('order_date'),
                    ordered_by_user=request.user,
                    status='Pending'
                )

                fs = FileSystemStorage()
                content_type = ContentType.objects.get_for_model(PurchaseOrders)

                if 'signed_po_scan' in request.FILES:
                    signed_po_file = request.FILES['signed_po_scan']
                    filename = fs.save(signed_po_file.name, signed_po_file)
                    AssociatedImages.objects.create(
                        image_url=fs.url(filename),
                        description=f"Signed PO Scan for {new_po.po_number}",
                        content_type=content_type,
                        object_id=new_po.po_id
                    )

                if 'supplier_photo' in request.FILES:
                    supplier_photo_file = request.FILES['supplier_photo']
                    filename = fs.save(supplier_photo_file.name, supplier_photo_file)
                    AssociatedImages.objects.create(
                        image_url=fs.url(filename),
                        description=f"Supplier Acceptance Photo for {new_po.po_number}",
                        content_type=content_type,
                        object_id=new_po.po_id
                    )

                line_items_json = request.POST.get('line_items_json', '[]')
                line_items = json.loads(line_items_json)
                
                total_amount = 0
                for item in line_items:
                    unit_price = float(item.get('unitPrice', 0))
                    quantity = float(item.get('quantity', 0))
                    total_amount += unit_price * quantity
                    
                    bean_varietal = BeanVarietals.objects.get(pk=item.get('itemId'))
                    
                    attributes_list = item.get('customAttributes', [])
                    attributes_dict = {attr['key']: attr['value'] for attr in attributes_list if attr['key']}

                    PurchaseOrderItems.objects.create(
                        po=new_po,
                        item_type='Green Bean',
                        bean_varietal=bean_varietal,
                        quantity_ordered=quantity,
                        unit_price_at_order=unit_price,
                        custom_attributes=attributes_dict
                    )
                
                new_po.total_amount = total_amount
                new_po.save()

                messages.success(request, 'GCB PO Successful!')

            return redirect('create_gcb_purchase_order')
    
        except Exception as e:
            context = { 'error_message': f"An error occurred: {e}", 'bean_varietals': BeanVarietals.objects.all() }
            return render(request, 'core/create_gcb_purchase_order.html', context)
    else:
        context = { 'bean_varietals': BeanVarietals.objects.all(), 'today_date': timezone.now().strftime('%Y-%m-%d') }
        return render(request, 'core/create_gcb_purchase_order.html', context)
    
    # View to list all registered MQTT devices
class MqttDeviceListView(LoginRequiredMixin, ListView):
    model = MqttDevice
    template_name = 'core/hmi_device_list.html' # We will create this new template
    context_object_name = 'devices'

# View to create a new MQTT device
class MqttDeviceCreateView(LoginRequiredMixin, CreateView):
    model = MqttDevice
    template_name = 'core/hmi_device_form.html' # A form for adding/editing
    fields = ['device_id', 'topic', 'device_type', 'description'] # Fields to show in the form
    success_url = reverse_lazy('device_list') # Redirect here after successful creation

# View to update an existing MQTT device
class MqttDeviceUpdateView(LoginRequiredMixin, UpdateView):
    model = MqttDevice
    template_name = 'core/hmi_device_form.html'
    fields = ['topic', 'device_type', 'description'] # device_id is the key, so it's not editable
    success_url = reverse_lazy('device_list')

# View to delete an MQTT device
class MqttDeviceDeleteView(LoginRequiredMixin, DeleteView):
    model = MqttDevice
    template_name = 'core/hmi_device_confirm_delete.html' # A confirmation page
    success_url = reverse_lazy('device_list')

@login_required
def get_latest_lot_api(request):
    """
    This API endpoint now includes a full, scannable URL
    in its response data for the QR code.
    """
    try:
        latest_lot = GreenBeanLots.objects.order_by('-arrival_date').first()
        
        if latest_lot:
            # Build the full URL for the detail page
            lot_url = request.build_absolute_uri(
                reverse('lot_detail', args=[latest_lot.lot_identifier])
            )
            
            data = {
                'lot_identifier': latest_lot.lot_identifier,
                'bean_name': latest_lot.bean_varietal.name if latest_lot.bean_varietal else 'N/A',
                'weight_kg': latest_lot.current_stock_kg,
                'supplier': latest_lot.supplier_name,
                'arrival_date': latest_lot.arrival_date.strftime('%Y-%m-%d'),
                'qr_code_url': lot_url # [NEW] Add the full URL to the payload
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'No lots found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def lot_detail_view(request, lot_identifier):
    """
    This view displays the details for a single GreenBeanLot,
    identified by its unique lot_identifier. This is the page
    the QR code will link to.
    """
    lot = get_object_or_404(GreenBeanLots, lot_identifier=lot_identifier)
    context = {
        'lot': lot
    }
    return render(request, 'core/lot_detail.html', context)

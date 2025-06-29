from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# --- All imports are now consolidated in this single block ---

class AuthenticationLogs(models.Model):
    class AuthMethod(models.TextChoices):
        PASSWORD = 'Password', 'Password'
        QR_CODE = 'QR Code', 'QR Code'
        BIOMETRIC = 'Biometric', 'Biometric'
        SYSTEM = 'System', 'System'

    class AuthStatus(models.TextChoices):
        SUCCESS = 'Success', 'Success'
        FAILURE = 'Failure', 'Failure'

    auth_log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    roaster = models.ForeignKey('Roasters', on_delete=models.PROTECT, blank=True, null=True)
    timestamp = models.DateTimeField()
    auth_method = models.CharField(max_length=20, choices=AuthMethod.choices)
    status = models.CharField(max_length=10, choices=AuthStatus.choices)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'authentication_logs'
        unique_together = (('auth_log_id', 'timestamp'),)
        verbose_name_plural = "Authentication logs"


class BeanVarietals(models.Model):
    varietal_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    farm = models.ForeignKey('Farms', on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'bean_varietals'
        verbose_name_plural = "Bean varietals"


class Blends(models.Model):
    blend_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'blends'
        verbose_name_plural = "Blends"


class Consumables(models.Model):
    consumable_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    unit_of_measure = models.CharField(max_length=50)
    current_stock_level = models.FloatField(blank=True, null=True)
    reorder_point = models.FloatField(blank=True, null=True)
    unit_cost = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'consumables'
        verbose_name_plural = "Consumables"


class CuppingAttributeScores(models.Model):
    score_id = models.AutoField(primary_key=True)
    evaluation = models.ForeignKey('CuppingEvaluations', on_delete=models.PROTECT)
    attribute_name = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    attribute_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.evaluation} - {self.attribute_name}"

    class Meta:
        db_table = 'cupping_attribute_scores'
        verbose_name_plural = "Cupping attribute scores"


class CuppingEvaluations(models.Model):
    evaluation_id = models.AutoField(primary_key=True)
    roast_batch = models.ForeignKey('RoastBatches', on_delete=models.PROTECT)
    evaluator_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evaluation_date = models.DateTimeField()
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    evaluation_location = models.ForeignKey('Locations', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"Evaluation for {self.roast_batch} on {self.evaluation_date.strftime('%Y-%m-%d')}"

    class Meta:
        db_table = 'cupping_evaluations'
        verbose_name_plural = "Cupping evaluations"


class Customers(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    branding_code = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'customers'
        verbose_name_plural = "Customers"


class DeliveryManifestItems(models.Model):
    class ItemStatus(models.TextChoices):
        LOADED = 'Loaded', 'Loaded'
        DELIVERED = 'Delivered', 'Delivered'
        RETURNED = 'Returned', 'Returned'
        DAMAGED = 'Damaged', 'Damaged'

    manifest_item_id = models.AutoField(primary_key=True)
    manifest = models.ForeignKey('DeliveryManifests', on_delete=models.PROTECT)
    packaged_item = models.ForeignKey('PackagedProducts', on_delete=models.PROTECT)
    quantity = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.LOADED
    )

    class Meta:
        db_table = 'delivery_manifest_items'
        unique_together = (('manifest', 'packaged_item'),)
        verbose_name_plural = "Delivery manifest items"


class DeliveryManifests(models.Model):
    class DeliveryType(models.TextChoices):
        INTERNAL = 'Internal', 'Internal Fleet'
        THIRD_PARTY = 'Third Party', 'Third-Party Courier'
        PICKUP = 'Pickup', 'Customer Pickup'

    class ManifestStatus(models.TextChoices):
        DISPATCHED = 'Dispatched', 'Dispatched'
        IN_TRANSIT = 'In Transit', 'In Transit'
        DELIVERED = 'Delivered', 'Delivered'
        DELAYED = 'Delayed', 'Delayed'

    manifest_id = models.AutoField(primary_key=True)
    manifest_number = models.CharField(max_length=50, unique=True)
    delivery_rider_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    delivery_type = models.CharField(max_length=20, choices=DeliveryType.choices)
    dispatch_date = models.DateTimeField()
    actual_delivery_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=ManifestStatus.choices,
        default=ManifestStatus.DISPATCHED
    )
    notes = models.TextField(blank=True, null=True)
    delivery_partner = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.manifest_number

    class Meta:
        db_table = 'delivery_manifests'
        verbose_name_plural = "Delivery manifests"


class DeliveryReceipts(models.Model):
    dr_id = models.AutoField(primary_key=True)
    dr_number = models.CharField(max_length=50, unique=True)
    delivery_date = models.DateTimeField()
    transaction_location = models.ForeignKey('Locations', on_delete=models.PROTECT)
    transaction_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    notes = models.TextField(blank=True, null=True)
    po = models.ForeignKey('PurchaseOrders', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.dr_number

    class Meta:
        db_table = 'delivery_receipts'
        verbose_name_plural = "Delivery receipts"


class Farms(models.Model):
    farm_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'farms'
        verbose_name_plural = "Farms"


class FinalProducts(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    roast_profile = models.ForeignKey('RoastProfiles', on_delete=models.PROTECT, blank=True, null=True)
    blend = models.ForeignKey(Blends, on_delete=models.PROTECT, blank=True, null=True)
    packaging_material = models.ForeignKey('PackagingMaterials', on_delete=models.PROTECT, blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)
    weight_grams_per_unit = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'final_products'
        verbose_name_plural = "Final products"


class GreenBeanLots(models.Model):
    class QualityGrade(models.TextChoices):
        SPECIALTY = 'Specialty', 'Specialty Grade'
        PREMIUM = 'Premium', 'Premium Grade'
        COMMERCIAL = 'Commercial', 'Commercial Grade'
        OFF_GRADE = 'Off-Grade', 'Off-Grade'

    lot_id = models.AutoField(primary_key=True)
    lot_identifier = models.CharField(max_length=50, unique=True)
    bean_varietal = models.ForeignKey('BeanVarietals', on_delete=models.PROTECT)
    supplier_name = models.CharField(max_length=255, blank=True, null=True)
    purchase_order = models.ForeignKey('PurchaseOrders', on_delete=models.PROTECT, blank=True, null=True)
    arrival_date = models.DateTimeField()
    initial_weight_kg = models.FloatField()
    current_stock_kg = models.FloatField()
    quality_grade = models.CharField(
        max_length=20,
        choices=QualityGrade.choices,
        blank=True, 
        null=True
    )
    moisture_content_percent = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    custom_attributes = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.lot_identifier

    class Meta:
        db_table = 'green_bean_lots'
        verbose_name_plural = "Green bean lots"


class GreenBeanProcessingLog(models.Model):
    class LogEventType(models.TextChoices):
        DRYING_BED = 'Drying Cherries', 'Drying Cherries'
        DRYING_GCB = 'Drying GCB', 'Drying GCB'
        DEHULLING = 'Dehulling', 'Dehulling'
        DEPULPING = 'Depulping', 'Depulping'
        STORAGED = 'Storaged', 'Sealed and Stored'
        ROAST_USAGE = 'Roast Usage', 'Used in Roast Batch'

    log_event_id = models.AutoField(primary_key=True)
    green_bean_lot = models.ForeignKey('GreenBeanLots', on_delete=models.PROTECT, blank=True, null=True)
    roast_batch = models.ForeignKey('RoastBatches', on_delete=models.PROTECT, blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=LogEventType.choices)
    timestamp = models.DateTimeField()
    storage_zone = models.ForeignKey('StorageZones', on_delete=models.PROTECT)
    operator_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    weight_change_kg = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    job = models.ForeignKey('JobOrders', on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        db_table = 'green_bean_processing_log'
        verbose_name_plural = "Green bean processing logs"


class JobOrders(models.Model):
    class JobType(models.TextChoices):
        ROASTING = 'Roasting', 'Roasting'
        BLENDING = 'Blending', 'Blending'
        PACKAGING = 'Packaging', 'Packaging'
        GRINDING = 'Grinding', 'Grinding'

    class JobStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        IN_PROGRESS = 'In Progress', 'In Progress'
        ON_HOLD = 'On Hold', 'On Hold'
        COMPLETED = 'Completed', 'Completed'

    job_id = models.AutoField(primary_key=True)
    job_identifier = models.CharField(max_length=50, unique=True)
    job_type = models.CharField(max_length=20, choices=JobType.choices)
    request_date = models.DateTimeField()
    requested_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    target_quantity_kg = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.PENDING
    )
    production_path_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.job_identifier

    class Meta:
        db_table = 'job_orders'
        verbose_name_plural = "Job orders"


class Locations(models.Model):
    class LocationType(models.TextChoices):
        HUB = 'Hub', 'Hub'
        SPOKE = 'Spoke', 'Spoke'
        ROASTERY = 'Roastery', 'Roastery'
        WAREHOUSE = 'Warehouse', 'Warehouse'
        MOBILE_UNIT = 'Mobile Unit', 'Mobile Unit'

    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=LocationType.choices)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'locations'
        verbose_name_plural = "Locations"


class MachineHealthLogs(models.Model):
    class TestResult(models.TextChoices):
        PASS = 'Pass', 'Pass'
        FAIL = 'Fail', 'Fail'
        WARNING = 'Warning', 'Warning'
        SKIPPED = 'Skipped', 'Skipped'

    health_log_id = models.AutoField(primary_key=True)
    roaster = models.ForeignKey('Roasters', on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    subsystem_name = models.CharField(max_length=100)
    test_result = models.CharField(max_length=20, choices=TestResult.choices)
    failure_details = models.TextField(blank=True, null=True)
    status_code = models.CharField(max_length=50, blank=True, null=True)
    alarm_triggered = models.BooleanField(blank=True, null=True)
    operator_action_suggestion = models.TextField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'machine_health_logs'
        unique_together = (('health_log_id', 'timestamp'),)
        verbose_name_plural = "Machine health logs"


class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    topic = models.CharField(max_length=255)
    payload = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Message on {self.topic} at {self.timestamp}"

    class Meta:
        db_table = 'messages'
        verbose_name_plural = "Messages"


class MobileUnitLocationHistory(models.Model):
    location_history_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Locations, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    battery_level = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'mobile_unit_location_history'
        unique_together = (('location_history_id', 'timestamp'),)
        verbose_name_plural = "Mobile unit location history"


class MqttDevice(models.Model):
    class DeviceType(models.TextChoices):
        PLATFORM_SCALE = 'SCALE', 'Platform Scale (Additive)'
        SUBTRACTIVE_DOSER = 'DOSER', 'Subtractive Doser'
        TELEMETRY = 'TELEMETRY', 'Roaster Telemetry'

    device_id = models.CharField(max_length=100, primary_key=True, help_text="A unique identifier for the device, e.g., 'platform_scale_100kg'")
    topic = models.CharField(max_length=255, unique=True, help_text="The full MQTT topic this device publishes to.")
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.device_id

    class Meta:
        verbose_name_plural = "MQTT devices"


class PackagedProducts(models.Model):
    packaged_item_id = models.AutoField(primary_key=True)
    packaged_item_qr_code = models.CharField(max_length=255, unique=True)
    final_product = models.ForeignKey(FinalProducts, on_delete=models.PROTECT)
    roast_batch = models.ForeignKey('RoastBatches', on_delete=models.PROTECT)
    dr = models.ForeignKey(DeliveryReceipts, on_delete=models.PROTECT, blank=True, null=True)
    packaging_date = models.DateTimeField()
    packaged_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    packaging_location = models.ForeignKey(Locations, on_delete=models.PROTECT, blank=True, null=True)
    best_before_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.packaged_item_qr_code

    class Meta:
        db_table = 'packaged_products'
        verbose_name_plural = "Packaged products"


class PackagingMaterials(models.Model):
    material_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100)
    size_grams = models.IntegerField(blank=True, null=True)
    cost_per_unit = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.type} ({self.size_grams}g)"

    class Meta:
        db_table = 'packaging_materials'
        verbose_name_plural = "Packaging materials"


class PurchaseOrderItems(models.Model):
    po_item_id = models.AutoField(primary_key=True)
    po = models.ForeignKey('PurchaseOrders', on_delete=models.PROTECT)
    consumable = models.ForeignKey('Consumables', on_delete=models.PROTECT, blank=True, null=True)
    bean_varietal = models.ForeignKey('BeanVarietals', on_delete=models.PROTECT, blank=True, null=True)
    item_type = models.CharField(max_length=20, default='Consumable')
    quantity_ordered = models.FloatField()
    quantity_received = models.FloatField(blank=True, null=True, default=0)
    unit_price_at_order = models.FloatField(blank=True, null=True)
    custom_attributes = models.JSONField(blank=True, null=True)

    def __str__(self):
        item_name = self.bean_varietal or self.consumable
        return f"Item for PO {self.po.po_number}: {item_name}"

    class Meta:
        db_table = 'purchase_order_items'
        verbose_name_plural = "Purchase order items"


class PurchaseOrders(models.Model):
    class PoStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        APPROVED = 'Approved', 'Approved'
        COMPLETED = 'Completed', 'Completed'
        CANCELLED = 'Cancelled', 'Cancelled'

    class PaymentMethod(models.TextChoices):
        CASH = 'Cash', 'Cash'
        BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer'
        CREDIT_CARD = 'Credit Card', 'Credit Card'
        TERMS = 'Net Terms', 'Net Terms'
        GCASH = 'GCash', 'GCash'

    po_id = models.AutoField(primary_key=True)
    po_number = models.CharField(max_length=50, unique=True)
    supplier_name = models.CharField(max_length=255)
    order_date = models.DateTimeField()
    expected_delivery_date = models.DateTimeField(blank=True, null=True)
    actual_delivery_date = models.DateTimeField(blank=True, null=True)
    total_amount = models.FloatField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=PoStatus.choices,
        default=PoStatus.PENDING
    )
    ordered_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True, 
        null=True
    )

    def __str__(self):
        return self.po_number

    class Meta:
        db_table = 'purchase_orders'
        verbose_name_plural = "Purchase orders"


class RoastBatches(models.Model):
    batch_id = models.AutoField(primary_key=True)
    batch_identifier = models.CharField(max_length=50, unique=True)
    roaster = models.ForeignKey('Roasters', on_delete=models.PROTECT)
    roast_profile = models.ForeignKey('RoastProfiles', on_delete=models.PROTECT)
    operator_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    roast_location = models.ForeignKey(Locations, on_delete=models.PROTECT, blank=True, null=True)
    green_bean_lot = models.ForeignKey(GreenBeanLots, on_delete=models.PROTECT)
    job = models.ForeignKey(JobOrders, on_delete=models.PROTECT, blank=True, null=True)
    timestamp_start = models.DateTimeField()
    timestamp_end = models.DateTimeField()
    initial_green_weight_grams = models.FloatField(blank=True, null=True)
    final_roasted_weight_grams = models.FloatField(blank=True, null=True)
    roast_duration_minutes = models.FloatField(blank=True, null=True)
    shrinkage_percent = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.batch_identifier

    class Meta:
        db_table = 'roast_batches'
        verbose_name_plural = "Roast batches"


class RoastProfiles(models.Model):
    profile_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    target_temp_c = models.FloatField(blank=True, null=True)
    target_duration_minutes = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roast_profiles'
        verbose_name_plural = "Roast profiles"


class RoastedCoffeeBins(models.Model):
    class BinStatus(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        ALLOCATED = 'Allocated', 'Allocated to Job'
        EMPTY = 'Empty', 'Empty'

    bin_id = models.AutoField(primary_key=True)
    bin_qr_code = models.CharField(max_length=255, unique=True)
    roast_batch = models.ForeignKey('RoastBatches', on_delete=models.PROTECT)
    job = models.ForeignKey(JobOrders, on_delete=models.PROTECT, blank=True, null=True)
    packaging_material = models.ForeignKey('PackagingMaterials', on_delete=models.PROTECT, blank=True, null=True)
    net_weight_kg = models.FloatField()
    fill_date = models.DateTimeField()
    current_storage_zone = models.ForeignKey('StorageZones', on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=BinStatus.choices,
        default=BinStatus.AVAILABLE,
        blank=True,
        null=True
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.bin_qr_code

    class Meta:
        db_table = 'roasted_coffee_bins'
        verbose_name_plural = "Roasted coffee bins"


class RoasterTelemetryLogs(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    roaster = models.ForeignKey('Roasters', on_delete=models.PROTECT)
    batch = models.ForeignKey(RoastBatches, on_delete=models.PROTECT, blank=True, null=True)
    timestamp = models.DateTimeField()
    temperature_bean_probe = models.FloatField(blank=True, null=True)
    temperature_environment = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'roaster_telemetry_logs'
        unique_together = (('log_id', 'timestamp'),)
        verbose_name_plural = "Roaster telemetry logs"


class Roasters(models.Model):
    roaster_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    capacity_grams = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Locations, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roasters'
        verbose_name_plural = "Roasters"


class StorageZones(models.Model):
    zone_id = models.AutoField(primary_key=True)
    zone_identifier = models.CharField(max_length=50, unique=True)
    location = models.ForeignKey(Locations, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, blank=True, null=True)
    zone_type = models.CharField(max_length=50, blank=True, null=True)
    capacity_kg = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.zone_identifier

    class Meta:
        db_table = 'storage_zones'
        verbose_name_plural = "Storage zones"


class AssociatedImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_url = models.TextField()
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.description} for {self.content_object}"

    class Meta:
        verbose_name_plural = "Associated Images"
# --- Recommended update for: backend/core/management/commands/subscribe_mqtt.py ---

import paho.mqtt.client as mqtt
import json
import ssl
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from core.models import MqttDevice, GreenBeanLots, GreenBeanProcessingLog, PurchaseOrders

# This on_message function now includes more robust logic and error handling
def on_message(client, userdata, msg):
    print(f"\n--- New Message Received ---")
    print(f"Topic: '{msg.topic}'")
    print(f"Payload: {msg.payload.decode()}")
    
    try:
        # Look up the device in our database using the incoming topic
        device = MqttDevice.objects.get(topic=msg.topic)
        data = json.loads(msg.payload.decode())

        # Route to the correct logic based on the registered device type
        if device.device_type == MqttDevice.DeviceType.PLATFORM_SCALE:
            with transaction.atomic():
                po_number = data.get("po_number")
                weight_received = float(data.get("weight_received_kg", 0))
                new_lot_identifier = data.get("new_lot_identifier")

                # Find the corresponding Purchase Order
                po = PurchaseOrders.objects.get(po_number=po_number)
                print(f"Found Purchase Order: {po.po_number}")

                # [ROBUSTNESS CHECK 1] Ensure the PO has line items.
                first_item = po.purchaseorderitems_set.first()
                if not first_item:
                    print(f"ERROR: Purchase Order {po_number} has no line items. Cannot create lot.")
                    return # Stop processing this message

                # [ROBUSTNESS CHECK 2] Ensure the line item has a bean varietal.
                if not first_item.bean_varietal:
                    print(f"ERROR: Line item for PO {po_number} has no bean varietal assigned. Cannot create lot.")
                    return # Stop processing this message
                
                # Create a new GreenBeanLot for this delivery
                new_lot = GreenBeanLots.objects.create(
                    lot_identifier=new_lot_identifier,
                    bean_varietal=first_item.bean_varietal,
                    supplier_name=po.supplier_name,
                    purchase_order=po,
                    initial_weight_kg=weight_received,
                    current_stock_kg=weight_received,
                    arrival_date=po.actual_delivery_date or timezone.now()
                )
                print(f"SUCCESS: Created new GreenBeanLot {new_lot.lot_identifier} with {weight_received}kg.")
                
                # Update the Purchase Order status
                po.status = PurchaseOrders.PoStatus.COMPLETED
                po.save()
                print(f"PO {po_number} marked as COMPLETED.")

        elif device.device_type == MqttDevice.DeviceType.SUBTRACTIVE_DOSER:
            # ... (Logic for the subtractive doser would go here) ...
            print(f"Processing SUBTRACTIVE event from device: {device.device_id}")
            pass
        
    except PurchaseOrders.DoesNotExist:
        print(f"ERROR: Purchase Order '{data.get('po_number')}' not found in the database.")
    except MqttDevice.DoesNotExist:
        print(f"ERROR: No device registered for topic '{msg.topic}'. Message ignored.")
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode incoming JSON payload: {msg.payload.decode()}")
    except Exception as e:
        print(f"FATAL ERROR processing message from topic {msg.topic}: {e}")

# The Command class and on_connect function remain the same
class Command(BaseCommand):
    help = 'Starts the dynamic MQTT subscriber.'

    def handle(self, *args, **kwargs):
        mqtt_settings = settings.MQTT_SETTINGS
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=mqtt_settings['CLIENT_ID'])
        client.username_pw_set(mqtt_settings['USERNAME'], mqtt_settings['PASSWORD'])
        client.on_connect = on_connect
        client.on_message = on_message
        client.tls_set(tls_version=ssl.PROTOCOL_TLS)

        self.stdout.write("Connecting to MQTT broker with settings from settings.py...")
        client.connect(mqtt_settings['BROKER_HOST'], mqtt_settings['BROKER_PORT'])
        client.loop_forever()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected successfully to HiveMQ Broker!")
        topic = settings.MQTT_SETTINGS['TOPIC_ROOT']
        client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")
    else:
        print(f"Failed to connect, return code {rc}\n")
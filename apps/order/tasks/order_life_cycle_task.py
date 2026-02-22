# tasks.py

import logging
import time

from celery import shared_task
from django.db import transaction

from apps.order.models.choices import OrderStatus
from apps.order.models.order_model import Order, OrderHistory

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def simulate_order_lifecycle(self, order_id: str):
    try:
        order = Order.objects.filter(id=order_id).first()
        if not order:
            logger.warning(f"WARNING:-------->> Order {order_id} not found.")
            return

        # Step 1: Wait 5 seconds → Mark as executed
        time.sleep(5)

        with transaction.atomic():
            order.status = OrderStatus.EXECUTED.value
            order.save(update_fields=["status"])
            logger.info(f"INFO------>> Order {order.order_id} executed.")

            order_history = OrderHistory.objects.create(
                order=order,
                status=OrderStatus.EXECUTED.value,
                description={"message": "Order executed"},
            )
            order_history.save()
            logger.info(f"INFO------>> Order history {order_history.id} created.")
        # Step 2: Wait another 5 seconds → Mark as closed
        time.sleep(5)

        with transaction.atomic():
            order.status = OrderStatus.CLOSED.value
            order.save(update_fields=["status"])
            logger.info(f"INFO------>> Order {order.order_id} closed.")

            order_history = OrderHistory.objects.create(
                order=order,
                status=OrderStatus.CLOSED.value,
                description={"message": "Order closed"},
            )
            order_history.save()
            logger.info(f"INFO------>> Order history {order_history.id} created.")

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found.")

    except Exception as exc:
        logger.error(f"Error processing order {order_id}: {str(exc)}")
        raise exc

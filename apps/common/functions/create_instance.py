import logging

from django.db import models

logger = logging.getLogger(__name__)


def create_instance(model: type[models.Model], validated_data: dict) -> models.Model:
    try:
        m2m_data: dict[str, list] = {}

        # Extract Many-to-Many fields from validated_data
        # M2M fields must be set AFTER the instance is created
        for field in model._meta.many_to_many:
            if field.name in validated_data:
                m2m_data[field.name] = validated_data.pop(field.name)

        # Create the model instance with remaining (non-M2M) fields
        instance = model.objects.create(**validated_data)

        # Assign M2M relationships
        for field_name, value in m2m_data.items():
            getattr(instance, field_name).set(value)

        # Explicit save for clarity and future extensibility
        instance.save()

        return instance

    except Exception as e:
        # Log full stack trace for debugging and monitoring
        logger.exception(
            "ERROR:------------>> create_instance failed for model=%s | error=%s",
            model.__name__,
            str(e),
        )
        raise

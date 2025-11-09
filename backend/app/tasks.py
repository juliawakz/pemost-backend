from datetime import date

from app.models.plantation import Plantation
from project.celery import app


@app.task
def update_matured_plantations():
    """
    Celery task to check all plantations whose notification_end_date has passed
    and update their is_matured status to True.

    This task runs daily at midnight.
    """
    today = date.today()

    # Find all plantations that have reached maturity but are not marked as matured
    plantations_to_update = Plantation.objects.filter(
        notification_end_date__lte=today,
        is_matured=False,
        is_archived=False
    )

    # Count for logging
    count = plantations_to_update.count()

    # Update all matching plantations
    updated = plantations_to_update.update(is_matured=True)

    return {
        'success': True,
        'message': f'Successfully updated {updated} plantation(s) to matured status',
        'count': count
    }

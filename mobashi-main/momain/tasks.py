from django.conf import settings
import logging
import traceback
from huey import crontab, signals
from huey.contrib import djhuey as huey
from django.core.mail import mail_admins

from .exceptions import HandledError
from .models import School, Campaign, Cascho, Stage
from .syncing import sinc_school, sinc_campaign, sinc_cascho
from .harvesting import harvest
from .routing import actual_routing


logger = logging.getLogger('huey')


def ignore_silent_error(record):
    """
    This is needed to use the retry system of Huey, that only works with unhandled exceptions,
    without having them to clutter the logs with unuseful tracebacks,
    but at the same time with logging relevant information, if any
    """
    if record.exc_info:
        exc_type, exc_value = record.exc_info[:2]
        if isinstance(exc_value, HandledError):
            if exc_value.__cause__:
                logger.error(exc_value.__cause__)
            return False
    return True


logger.addFilter(ignore_silent_error)


@huey.signal(signals.SIGNAL_ERROR)
def task_error(signal, task, exc):
    """
    If specified task reached maximum retries, send an EMail to Admin,
    with details and traceback
    """
    if task.retries > 0:
        return
    subject = f'Task [{task.name}] failed'
    message = f"""Task ID: {task.id}
Args: {task.args}
Kwargs: {task.kwargs}
Exception: {exc}
{traceback.format_exc()}"""
    mail_admins(subject, message)


# Get Harvesting config
config = (settings.HARVESTING_TASK or {})
retries = config.get('RETRIES', 0)
retry_delay = config.get('RETRY_DELAY', 0)

# Only define this task as periodic if a configuration is actually present,
# otherwise it would only be manually runnable
kwargs = {k.lower(): v for k, v in config.get('CRONTAB', {}).items() if v}
if kwargs:
    @huey.db_periodic_task(crontab(**kwargs), retries=retries, retry_delay=retry_delay)
    def async_harvest():
        harvest()
else:
    @huey.db_task(retries=retries, retry_delay=retry_delay)
    def async_harvest():
        harvest()


# Get Syncing config
config = (settings.SYNCING_TASK or {})
retries = config.get('RETRIES', 0)
retry_delay = config.get('RETRY_DELAY', 0)


@huey.db_task(retries=retries, retry_delay=retry_delay)
def async_tosurv_school(pk, created):
    sinc_school(School.objects.get(pk=pk), created)


@huey.db_task(retries=retries, retry_delay=retry_delay)
def async_tosurv_campaign(pk, created):
    sinc_campaign(Campaign.objects.get(pk=pk), created)


@huey.db_task(retries=retries, retry_delay=retry_delay)
def async_tosurv_cascho(campaign_uuid, school_uuid, add_school):
    sinc_cascho(campaign_uuid, school_uuid, add_school)


# Get Routing config
config = (settings.ROUTING_TASK or {})
retries = config.get('RETRIES', 0)
retry_delay = config.get('RETRY_DELAY', 0)


@huey.db_task(retries=retries, retry_delay=retry_delay)
def async_actual_routing(pk):
    actual_routing(Stage.objects.get(pk=pk))

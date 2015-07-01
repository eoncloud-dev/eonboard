import logging
import time
import traceback
from django.conf import settings

from cloud_utils import create_rc_by_volume
from biz.volume.settings import VOLUME_STATE_CREATING, VOLUME_STATE_AVAILABLE, VOLUME_STATE_ERROR, VOLUME_STATE_ERROR_DELETING
from api import cinder
from celery import app


LOG = logging.getLogger("cloud.tasks")


def volume_create(volume):
    rc = create_rc_by_volume(volume)
    try:
        volume = cinder.volume_create(rc, size=volume.size, name="Volume-%04d" % volume.id,
                                      description="",
                                      volume_type=None)
        return volume
    except Exception as e:
        LOG.exception(e)
        return False


def volume_get(volume):
    rc = create_rc_by_volume(volume)
    try:
        volume = cinder.volume_get(rc, volume.volume_id)
        return volume
    except Exception as e:
        LOG.exception(e)
        return False


def volume_delete(volume):
    rc = create_rc_by_volume(volume)
    try:
        volume = cinder.volume_delete(rc, volume.volume_id)
        return volume
    except Exception as e:
        LOG.exception(e)
        return False


@app.task
def volume_create_task(volume, **kwargs):
    if not volume:
        return
    LOG.info('begin to start create volume:[%s][%s]' % (volume.id, volume.name))
    # create volume
    cinder = volume_create(volume)
    if not cinder:
        LOG.info('cinder create error volume:[%s][%s]' % (volume.id, volume.name))
        return

    volume.volume_id = cinder.id
    volume.status = VOLUME_STATE_CREATING
    volume.save()

    count = 0
    while True:
        time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
        vol = volume_get(volume)
        st = vol.status.upper()
        LOG.info('cinder status rsync volume:[%s][%s][status: %s]' % (volume.id, volume.name, st))
        if st == "AVAILABLE":
            volume.status = VOLUME_STATE_AVAILABLE
            volume.save()
            break
        elif st == "ERROR":
            volume.status = VOLUME_STATE_ERROR
            volume.save()
            break
        elif st == "CREATING":
            pass
        count += 1
        if count > settings.MAX_COUNT_SYNC * 2:
            break


@app.task
def volume_delete_action_task(volume, **kwargs):
    if not volume:
        return
    LOG.info('begin to delete volume:[%s][%s]' % (volume.id, volume.name))
    cinder = volume_get(volume)
    if cinder:
        volume_delete(volume)
        count = 0
        while True:
            time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
            vol = volume_get(volume)
            LOG.info('cinder status rsync volume:[%s][%s]' % (volume.id, volume.name))
            if vol is False:
                volume.deleted = True
                volume.volume_id = None
                volume.save()
                break
            elif vol.status.upper() == 'ERROR-DELETING':
                volume.status = VOLUME_STATE_ERROR_DELETING
                volume.save()
                break
            count += 1
            if count > settings.MAX_COUNT_SYNC * 2:
                break
    else:
        volume.deleted = True
        volume.save()

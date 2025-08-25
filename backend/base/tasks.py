import logging
import subprocess

from project import app

logger = logging.getLogger(__file__)


@app.task()
def backupmediafiles():
    """Backup media and db files"""
    backup_script = "backup.sh"

    subprocess.call(["bash", backup_script])

    logger.info("Backing up db and media files ")

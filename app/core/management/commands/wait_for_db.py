"""Wait for the database to become available."""
import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Pause command execution until the default database is reachable."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        database = connections["default"]

        while True:
            try:
                database.cursor()
            except OperationalError:
                self.stdout.write("Database unavailable, retrying in 1 second...")
                time.sleep(1)
            else:
                break

        self.stdout.write(self.style.SUCCESS("Database available."))


import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from crops.models import Crop
from tqdm import tqdm

User = get_user_model()


class Command(BaseCommand):
    help = "Load crops from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        # Get or create system superuser for created_by/updated_by fields
        system_user = User.objects.filter(
            is_superuser=True
        ).first()

        created_crops = 0
        existing_crops = 0
        updated_crops = 0
        skipped_rows = 0

        # Count rows for tqdm
        with open(csv_file, newline="", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in tqdm(reader, total=total_rows, desc="Importing crops", unit="row"):
                # Skip rows with missing required data
                if not row.get("name"):
                    skipped_rows += 1
                    continue

                # Create or get Crop
                crop_name = row["name"].strip()
                crop, created = Crop.objects.get_or_create(
                    name=crop_name.title(),
                    defaults={
                        "created_by": system_user,
                        "updated_by": system_user,
                    }
                )

                if created:
                    created_crops += 1
                else:
                    # Update existing crops if they don't have created_by/updated_by
                    if not crop.created_by or not crop.updated_by:
                        crop.created_by = system_user
                        crop.updated_by = system_user
                        crop.save()
                        updated_crops += 1
                    existing_crops += 1

        # Summary report
        self.stdout.write(self.style.SUCCESS("\nData import complete!"))
        self.stdout.write(f"Crops: {created_crops} created, {existing_crops} already existed, {updated_crops} updated")
        if skipped_rows > 0:
            self.stdout.write(self.style.WARNING(f"Skipped rows: {skipped_rows}"))

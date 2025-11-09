import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from crops.models import CropVariety, CropGrowthStage
from tqdm import tqdm

User = get_user_model()


class Command(BaseCommand):
    help = "Load crop growth stages from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        # Get or create system superuser for created_by/updated_by fields
        system_user = User.objects.filter(
            is_superuser=True
        ).first()

        created_stages = 0
        existing_stages = 0
        updated_stages = 0
        skipped_rows = 0
        missing_varieties = []

        # Count rows for tqdm
        with open(csv_file, newline="", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in tqdm(reader, total=total_rows, desc="Importing crop growth stages", unit="row"):
                # Skip rows with missing required data
                if not row.get("crop_variety") or not row.get("growth_stage"):
                    skipped_rows += 1
                    continue

                # Get CropVariety
                variety_name = row["crop_variety"].strip()
                try:
                    crop_variety = CropVariety.objects.get(name=variety_name)
                except CropVariety.DoesNotExist:
                    if variety_name not in missing_varieties:
                        missing_varieties.append(variety_name)
                    skipped_rows += 1
                    continue

                # Helper function to safely convert to int
                def safe_int(value, default=0):
                    try:
                        return int(float(value)) if value and value.strip() else default
                    except (ValueError, AttributeError):
                        return default

                # Get values
                growth_stage = row.get("growth_stage", "").strip().lower()
                severity = row.get("severity", "").strip().lower()
                minimum_days = safe_int(row.get("minimum_days", 0))
                maximum_days = safe_int(row.get("maximum_days", 0))

                # Create or get CropGrowthStage
                stage, created = CropGrowthStage.objects.get_or_create(
                    crop_variety=crop_variety,
                    growth_stage=growth_stage,
                    defaults={
                        "severity": severity,
                        "minimum_days": minimum_days,
                        "maximum_days": maximum_days,
                        "created_by": system_user,
                        "updated_by": system_user,
                    },
                )

                if created:
                    created_stages += 1
                else:
                    # Update existing stages if they don't have created_by/updated_by
                    if not stage.created_by or not stage.updated_by:
                        stage.created_by = system_user
                        stage.updated_by = system_user
                        stage.save()
                        updated_stages += 1
                    existing_stages += 1

        # Summary report
        self.stdout.write(self.style.SUCCESS("\nData import complete!"))
        self.stdout.write(f"Crop Growth Stages: {created_stages} created, {existing_stages} already existed, {updated_stages} updated")
        if skipped_rows > 0:
            self.stdout.write(self.style.WARNING(f"Skipped rows: {skipped_rows}"))
        if missing_varieties:
            self.stdout.write(self.style.WARNING(f"\nMissing crop varieties ({len(missing_varieties)}):"))
            for variety in missing_varieties[:10]:  # Show first 10
                self.stdout.write(f"  - {variety}")
            if len(missing_varieties) > 10:
                self.stdout.write(f"  ... and {len(missing_varieties) - 10} more")

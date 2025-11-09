import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from crops.models import Crop, CropVariety
from tqdm import tqdm

User = get_user_model()


class Command(BaseCommand):
    help = "Load crop varieties from CSV"

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
        created_varieties = 0
        existing_varieties = 0
        updated_crops = 0
        updated_varieties = 0
        skipped_rows = 0

        # Count rows for tqdm
        with open(csv_file, newline="", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in tqdm(reader, total=total_rows, desc="Importing crop varieties", unit="row"):
                # Skip rows with missing required data
                if not row.get("crop_variety") or not row.get("crop_type"):
                    skipped_rows += 1
                    continue

                # Create or get Crop
                crop_name = row["crop_type"].strip()
                crop, c_created = Crop.objects.get_or_create(
                    name=crop_name.title(),
                    defaults={
                        "created_by": system_user,
                        "updated_by": system_user,
                    }
                )
                if c_created:
                    created_crops += 1
                else:
                    # Update existing crops if they don't have created_by/updated_by
                    if not crop.created_by or not crop.updated_by:
                        crop.created_by = system_user
                        crop.updated_by = system_user
                        crop.save()
                        updated_crops += 1
                    existing_crops += 1

                # Helper function to safely convert to float
                def safe_float(value, default=0.0):
                    try:
                        return float(value) if value and value.strip() else default
                    except (ValueError, AttributeError):
                        return default

                # Helper function to safely convert to int
                def safe_int(value, default=0):
                    try:
                        return int(float(value)) if value and value.strip() else default
                    except (ValueError, AttributeError):
                        return default

                # Create or get CropVariety
                variety_name = row["crop_variety"].strip()
                variety, v_created = CropVariety.objects.get_or_create(
                    name=variety_name,
                    crop=crop,
                    defaults={
                        "min_maturity_days": safe_int(row.get("min_maturity_in_days", 0)),
                        "max_maturity_days": safe_int(row.get("max_maturity_in_days", 0)),
                        "min_yield": safe_float(row.get("min_estimated_yield", 0)),
                        "max_yield": safe_float(row.get("max_estimated_yield", 0)),
                        "climate": row.get("suitable_climatic_conditions", "").strip(),
                        "min_rainfall_mm": safe_float(row.get("min_annual_rainfall_mm", 0)),
                        "max_rainfall_mm": safe_float(row.get("max_annual_rainfall_mm", 0)),
                        "min_altitude_masl": safe_float(row.get("min_altitude_meters_above_sea_level", 0)),
                        "max_altitude_masl": safe_float(row.get("max_altitude_meters_above_sea_level", 0)),
                        "row_spacing_cm": safe_int(row.get("row_spacing_cm", 0)),
                        "plant_spacing_hill": safe_int(row.get("plant_spacing_1_plant_per_hill", 0)),
                        "fertilizer_dap_kg": safe_int(row.get("fertilizer_requirements_planting_DAP_kgs", 0)),
                        "fertilizer_can_kg": safe_int(row.get("fertilizer_requirements_topdressing_CAN_kgs", 0)),
                        "fertilizer_17_17_17_kg": safe_int(row.get("fertilizer_requirements_topdressing_17_17_kgs", 0)),
                        "disease_tolerance": row.get("diseases_tolerance", "").strip(),
                        "pest_tolerance": row.get("pest_tolerance", "").strip(),
                        "pest_susceptibility": row.get("pest_susceptibility", "").strip(),
                        "disease_susceptibility": row.get("disease_susceptibility", "").strip(),
                        "seed_source": row.get("seed_source", "").strip(),
                        "seed_rate_g_per_acre": safe_int(row.get("Seed_rate_per_acre_grams", 0)),
                        "created_by": system_user,
                        "updated_by": system_user,
                    },
                )
                if v_created:
                    created_varieties += 1
                else:
                    # Update existing varieties if they don't have created_by/updated_by
                    if not variety.created_by or not variety.updated_by:
                        variety.created_by = system_user
                        variety.updated_by = system_user
                        variety.save()
                        updated_varieties += 1
                    existing_varieties += 1

        # Summary report
        self.stdout.write(self.style.SUCCESS("\nData import complete!"))
        self.stdout.write(f"Crops: {created_crops} created, {existing_crops} already existed, {updated_crops} updated")
        self.stdout.write(f"Crop Varieties: {created_varieties} created, {existing_varieties} already existed, {updated_varieties} updated")
        if skipped_rows > 0:
            self.stdout.write(self.style.WARNING(f"Skipped rows: {skipped_rows}"))

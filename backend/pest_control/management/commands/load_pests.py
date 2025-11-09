import csv

from django.core.management.base import BaseCommand
from pest_control.models import Pest
from tqdm import tqdm


class Command(BaseCommand):
    help = "Load pest control data from CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file"
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        created_pests = 0
        existing_pests = 0
        skipped_rows = 0

        # Count rows for tqdm
        with open(csv_file, newline="", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            with tqdm(
                total=total_rows,
                desc="Importing pests",
                unit="row"
            ) as pbar:
                for row in reader:
                    try:
                        # Helper function to safely get and clean values
                        def safe_get(key, default=""):
                            value = row.get(key, default)
                            if not value:
                                return default
                            # Strip whitespace
                            value = value.strip()
                            # Return empty for nan values only
                            if value.lower() == 'nan':
                                return default
                            # Keep 'none' as a valid value
                            return value

                        # Skip rows with missing critical data
                        if not safe_get("pest type") or not safe_get(
                            "scientific name"
                        ):
                            skipped_rows += 1
                            pbar.update(1)
                            continue

                        # Map CSV columns to model fields
                        pest_data = {
                            "name": safe_get("pest type"),
                            "scientific_name": safe_get("scientific name"),
                            "stage": safe_get("stage pest").lower(),
                            "action_threshold": safe_get("action threshold"),
                            "action_threshold_risk": safe_get(
                                "action threshold risk"
                            ).lower(),
                            "crop_growth_stage": safe_get(
                                "stage crop growth"
                            ).lower(),
                            "cultural": safe_get("cultural"),
                            "cultural_description": safe_get(
                                "cultural description"
                            ),
                            "biological": safe_get("biological"),
                            "biological_description": safe_get(
                                "biological description"
                            ),
                            "presence_period": float(
                                row["pest presence period"]
                            ) if row.get(
                                "pest presence period"
                            ) and row[
                                "pest presence period"
                            ].strip() else 0.0,
                            "no_of_plants_affected": float(
                                row["no of plants affected"]
                            ) if row.get(
                                "no of plants affected"
                            ) and row[
                                "no of plants affected"
                            ].strip() else 0.0,
                        }

                        # Create or get Pest
                        # Include descriptions to allow multiple interventions
                        _, created = Pest.objects.get_or_create(
                            name=pest_data["name"],
                            scientific_name=pest_data["scientific_name"],
                            stage=pest_data["stage"],
                            action_threshold=pest_data["action_threshold"],
                            action_threshold_risk=pest_data[
                                "action_threshold_risk"
                            ],
                            crop_growth_stage=pest_data["crop_growth_stage"],
                            cultural=pest_data["cultural"],
                            cultural_description=pest_data[
                                "cultural_description"
                            ],
                            biological=pest_data["biological"],
                            biological_description=pest_data[
                                "biological_description"
                            ],
                            defaults={
                                "presence_period": pest_data[
                                    "presence_period"
                                ],
                                "no_of_plants_affected": pest_data[
                                    "no_of_plants_affected"
                                ],
                            }
                        )

                        if created:
                            created_pests += 1
                        else:
                            existing_pests += 1

                        pbar.update(1)

                    except Exception as e:
                        skipped_rows += 1
                        pbar.update(1)
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipped row: {str(e)}\n"
                                f"Row data: {row}"
                            )
                        )

        # Summary report
        self.stdout.write(
            self.style.SUCCESS("\nData import complete!")
        )
        self.stdout.write(
            f"Pests: {created_pests} created, "
            f"{existing_pests} already existed"
        )
        if skipped_rows > 0:
            self.stdout.write(
                self.style.WARNING(f"Skipped rows: {skipped_rows}")
            )

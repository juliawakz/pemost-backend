import csv
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from app.models.farm import Farm
from app.models.plantation import Plantation
from crops.models import CropVariety
from tqdm import tqdm

User = get_user_model()


class Command(BaseCommand):
    help = "Load plantations from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip duplicate plantations instead of failing'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing plantations instead of skipping'
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]
        skip_duplicates = kwargs.get("skip_duplicates", False)
        update_existing = kwargs.get("update_existing", False)

        created_plantations = 0
        updated_plantations = 0
        skipped_plantations = 0
        error_rows = []

        # Count rows for tqdm
        with open(csv_file, newline="", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(tqdm(reader, total=total_rows, desc="Importing plantations", unit="row"), start=2):
                try:
                    # Parse farm field (format: "calc_size-farmer_full_name")
                    farm_str = row.get("farm", "").strip()
                    if not farm_str:
                        error_rows.append({
                            'row': row_num,
                            'error': 'Missing farm field',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Split farm string to get calc_size and farmer name
                    try:
                        calc_size_str, farmer_full_name = farm_str.split('-', 1)
                        calc_size = float(calc_size_str)
                    except ValueError:
                        error_rows.append({
                            'row': row_num,
                            'error': f'Invalid farm format: {farm_str}. Expected "calc_size-farmer_full_name"',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Find farm by calc_size and farmer full name
                    # Parse farmer full name to get first and last name
                    name_parts = farmer_full_name.strip().split(' ', 1)
                    if len(name_parts) == 2:
                        first_name, last_name = name_parts
                    else:
                        first_name = farmer_full_name.strip()
                        last_name = ""

                    # Find farm matching calc_size and farmer name
                    farm = Farm.objects.filter(
                        Q(calc_size__gte=calc_size - 0.01) & Q(calc_size__lte=calc_size + 0.01),
                        Q(farmer__first_name__iexact=first_name.strip()) &
                        Q(farmer__last_name__iexact=last_name.strip())
                    ).first()

                    if not farm:
                        error_rows.append({
                            'row': row_num,
                            'error': f'Farm not found for calc_size={calc_size} and farmer={farmer_full_name}',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Parse crop variety field (format: "Crop-Variety")
                    crop_variety_str = row.get("crop variety", "").strip()
                    if not crop_variety_str:
                        error_rows.append({
                            'row': row_num,
                            'error': 'Missing crop variety field',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Split crop variety string
                    try:
                        crop_name, variety_name = crop_variety_str.split('-', 1)
                    except ValueError:
                        error_rows.append({
                            'row': row_num,
                            'error': f'Invalid crop variety format: {crop_variety_str}. Expected "Crop-Variety"',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Find crop variety
                    crop_variety = CropVariety.objects.filter(
                        name__iexact=variety_name.strip(),
                        crop__name__iexact=crop_name.strip()
                    ).first()

                    if not crop_variety:
                        error_rows.append({
                            'row': row_num,
                            'error': f'Crop variety not found: {crop_variety_str}',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Parse transplanting date
                    transplanting_date_str = row.get("transplanting date", "").strip()
                    if not transplanting_date_str:
                        error_rows.append({
                            'row': row_num,
                            'error': 'Missing transplanting date',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Try multiple date formats
                    transplanting_date = None
                    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]
                    for date_format in date_formats:
                        try:
                            transplanting_date = datetime.strptime(
                                transplanting_date_str, date_format
                            ).date()
                            break
                        except ValueError:
                            continue

                    if not transplanting_date:
                        error_rows.append({
                            'row': row_num,
                            'error': f'Invalid transplanting date format: {transplanting_date_str}',
                            'data': row
                        })
                        skipped_plantations += 1
                        continue

                    # Check if plantation already exists
                    existing_plantation = Plantation.objects.filter(
                        farm=farm,
                        crop_variety=crop_variety,
                        transplanting_date=transplanting_date
                    ).first()

                    if existing_plantation:
                        if update_existing:
                            # Update the existing plantation (if needed)
                            existing_plantation.save()
                            updated_plantations += 1
                        else:
                            skipped_plantations += 1
                            if not skip_duplicates:
                                error_rows.append({
                                    'row': row_num,
                                    'error': f'Plantation already exists (use --skip-duplicates or --update-existing)',
                                    'data': row
                                })
                    else:
                        # Create new plantation
                        # Note: notification_end_date will be auto-calculated in the save method
                        plantation = Plantation(
                            farm=farm,
                            crop_variety=crop_variety,
                            transplanting_date=transplanting_date
                        )

                        try:
                            # Try to save with validation
                            plantation.save()
                            created_plantations += 1
                        except Exception as validation_error:
                            # If validation fails (e.g., active plantation exists),
                            # log the error and skip
                            error_rows.append({
                                'row': row_num,
                                'error': f'Validation error: {str(validation_error)}',
                                'data': row
                            })
                            skipped_plantations += 1

                except Exception as e:
                    error_rows.append({
                        'row': row_num,
                        'error': f'Unexpected error: {str(e)}',
                        'data': row
                    })
                    skipped_plantations += 1

        # Summary report
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("Plantation Import Summary"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(f"Total rows processed: {total_rows}")
        self.stdout.write(self.style.SUCCESS(f"Plantations created: {created_plantations}"))

        if updated_plantations > 0:
            self.stdout.write(self.style.SUCCESS(f"Plantations updated: {updated_plantations}"))

        if skipped_plantations > 0:
            self.stdout.write(self.style.WARNING(f"Plantations skipped: {skipped_plantations}"))

        if error_rows:
            self.stdout.write(self.style.ERROR(f"\nErrors encountered: {len(error_rows)}"))
            self.stdout.write(self.style.ERROR("\nDetailed errors:"))
            for error in error_rows[:10]:  # Show first 10 errors
                self.stdout.write(
                    self.style.ERROR(
                        f"  Row {error['row']}: {error['error']}"
                    )
                )
            if len(error_rows) > 10:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ... and {len(error_rows) - 10} more errors"
                    )
                )

        self.stdout.write(self.style.SUCCESS("="*50))

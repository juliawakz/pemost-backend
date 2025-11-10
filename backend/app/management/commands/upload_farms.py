import os
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from app.utils.farm_import import FarmImportUtil


class Command(BaseCommand):
    help = 'Upload farm shapefiles from a zip file'

    def add_arguments(self, parser):
        parser.add_argument(
            'shapefile_path',
            type=str,
            help='Path to the shapefile zip file (e.g., farms.zip)'
        )
        parser.add_argument(
            '--mode',
            type=str,
            choices=['skip', 'update', 'create'],
            default='skip',
            help=(
                'How to handle existing farms: '
                'skip (skip duplicates, default), '
                'update (update existing farms), '
                'create (fail on duplicates)'
            )
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing farms before importing'
        )

    def handle(self, *args, **options):
        from app.models.farm import Farm

        shapefile_path = options['shapefile_path']
        mode = options['mode']
        clear = options['clear']

        # Check if file exists
        if not os.path.exists(shapefile_path):
            self.stdout.write(
                self.style.ERROR(f"File not found: {shapefile_path}")
            )
            return

        # Check if it's a zip file
        if not shapefile_path.endswith('.zip'):
            self.stdout.write(
                self.style.ERROR("File must be a .zip file containing shapefile data")
            )
            return

        # Clear existing farms if requested
        if clear:
            existing_count = Farm.objects.count()
            if existing_count > 0:
                confirm = input(
                    f"This will delete {existing_count} existing farms. "
                    "Are you sure? [y/N]: "
                )
                if confirm.lower() == 'y':
                    Farm.objects.all().delete()
                    self.stdout.write(
                        self.style.WARNING(f"Deleted {existing_count} existing farms")
                    )
                else:
                    self.stdout.write("Operation cancelled")
                    return

        self.stdout.write(f"Reading shapefile: {shapefile_path}")
        self.stdout.write(f"Import mode: {mode}")

        try:
            # Read the file and create an UploadedFile-like object
            with open(shapefile_path, 'rb') as f:
                file_content = f.read()
                file_name = os.path.basename(shapefile_path)

                # Create a SimpleUploadedFile to mimic the API behavior
                uploaded_file = SimpleUploadedFile(
                    file_name,
                    file_content,
                    content_type='application/zip'
                )

            # Use the existing FarmImportUtil
            farm_import_util = FarmImportUtil()
            self.stdout.write("Processing shapefile...")

            result = farm_import_util.import_farms(uploaded_file, mode=mode)

            if isinstance(result, str):
                # Error message returned
                self.stdout.write(
                    self.style.ERROR(f"Error: {result}")
                )
            elif isinstance(result, dict):
                # New format with detailed stats
                self.stdout.write(
                    self.style.SUCCESS("\nImport completed successfully!")
                )
                self.stdout.write(f"Total farms in file: {result['total']}")
                self.stdout.write(f"Created: {result['created']}")
                self.stdout.write(f"Updated: {result['updated']}")
                self.stdout.write(f"Skipped: {result['skipped']}")
            else:
                # Old format (backward compatibility)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nSuccessfully uploaded {result} farms"
                    )
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File not found: {shapefile_path}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error: {str(e)}")
            )
            import traceback
            traceback.print_exc()

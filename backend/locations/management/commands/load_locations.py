import csv
from django.core.management.base import BaseCommand
from locations.models import County, SubCounty, Ward
from tqdm import tqdm  # install with: pip install tqdm


class Command(BaseCommand):
    help = "Load counties, subcounties, and wards from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        created_counties = 0
        existing_counties = 0
        created_subcounties = 0
        existing_subcounties = 0
        created_wards = 0
        existing_wards = 0

        # Count rows for tqdm
        with open(csv_file, newline="", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in tqdm(reader, total=total_rows, desc="Importing locations", unit="row"):
                # Create or get County
                county, c_created = County.objects.get_or_create(
                    county_id=int(row["COUNTY_ID"]),
                    defaults={"name": row["COUNTY_NAME"].strip().title()},
                )
                if c_created:
                    created_counties += 1
                else:
                    existing_counties = max(existing_counties, county.county_id)

                # Create or get SubCounty
                subcounty, s_created = SubCounty.objects.get_or_create(
                    subcounty_id=int(float(row["SUBCOUNTY_ID"])),
                    county=county,
                    defaults={"name": row["SUBCOUNTY_NAME"].strip().title()},
                )
                if s_created:
                    created_subcounties += 1
                else:
                    existing_subcounties = max(existing_subcounties, subcounty.subcounty_id)

                # Create or get Ward
                ward, w_created = Ward.objects.get_or_create(
                    ward_id=int(row["WARD_ID"]),
                    subcounty=subcounty,
                    defaults={"name": row["WARD_NAME"].strip().title()},
                )
                if w_created:
                    created_wards += 1
                else:
                    existing_wards = max(existing_wards, ward.ward_id)

        # Summary report
        self.stdout.write(self.style.SUCCESS("\n✅ Data import complete!"))
        self.stdout.write(f"📌 Counties: {created_counties} created, {existing_counties} already existed")
        self.stdout.write(f"📌 Subcounties: {created_subcounties} created, {existing_subcounties} already existed")
        self.stdout.write(f"📌 Wards: {created_wards} created, {existing_wards} already existed")

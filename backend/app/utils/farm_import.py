import os
import os.path
import shutil
import tempfile
import traceback
import zipfile

from django.contrib.auth import get_user_model
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.core.exceptions import ValidationError
from osgeo import ogr

from app.models.farm import Farm
from locations.models import Ward, County, SubCounty
from users.choices import RoleChoices

User = get_user_model()


class FarmImportUtil:
    # Function for shapefiles imports through rest api.
    def import_farms(self, shapefile, mode='skip'):
        # This  function read the contents of the uploaded object
        # and store it into a temporary file on the disk so that we
        # can work with it.
        fd, fname = tempfile.mkstemp(suffix=".zip")
        os.close(fd)
        f = open(fname, "wb")
        for chunk in shapefile.chunks():
            f.write(chunk)
        f.close()

        # This checks whether it is indeed a ZIP archive containing the
        # files that make up a shapefile.
        if not zipfile.is_zipfile(fname):
            # delete the temporary files b4 returning error
            os.remove(fname)
            return "Not a valid zip archive."

        zip = zipfile.ZipFile(fname)

        required_suffixes = [".shp", ".shx", ".dbf", ".prj"]
        has_suffix = {}
        for suffix in required_suffixes:
            has_suffix[suffix] = False

        for info in zip.infolist():
            suffix = os.path.splitext(info.filename)[1].lower()
            if suffix in required_suffixes:
                has_suffix[suffix] = True

        for suffix in required_suffixes:
            if not has_suffix[suffix]:
                # delete the temporary files b4 returning error
                zip.close()
                os.remove(fname)
                return "Archive missing required " + suffix + " file."

        # Extract files and store into a temporary directory
        shapefile_name = None
        dir_name = tempfile.mkdtemp()
        for info in zip.infolist():
            if info.filename.endswith(".shp"):
                shapefile_name = info.filename
            dst_file = os.path.join(dir_name, info.filename)
            f = open(dst_file, "wb")
            f.write(zip.read(info.filename))
            f.close()
        zip.close()

        # Using OGR library to open the shapefile.
        try:
            datasource = ogr.Open(os.path.join(dir_name, shapefile_name))
            layer = datasource.GetLayer(0)
            shapefile_ok = True
        except Exception:
            traceback.print_exc()
            shapefile_ok = False

        if not shapefile_ok:
            # delete the temporary files b4 returning error
            os.remove(fname)
            shutil.rmtree(dir_name)
            raise ValidationError({"shapefile": "Not a valid shapefile."})

        # iterate through the shapefile's features, creating a GeoDjango
        # GEOSGeometry object for each feature
        # features = list()
        total_farms = layer.GetFeatureCount()
        fields = {}
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for i in range(layer.GetFeatureCount()):
            src_feature = layer.GetFeature(i)
            src_geometry = src_feature.GetGeometryRef()
            geometry = GEOSGeometry(src_geometry.ExportToWkt())

            first_name = src_feature.GetFieldAsString("First_Name")
            last_name = src_feature.GetFieldAsString("SecondName")
            mobile_num = src_feature.GetFieldAsString("Telephone")
            id_number = src_feature.GetFieldAsString("ID_No")

            fields["boundary"] = geometry
            fields["name"] = f"{first_name}-{last_name}-{geometry.wkt[-8:-4]}"

            county, created = County.objects.get_or_create(
                name="Machakos", county_id=16)

            subcounty, created = SubCounty.objects.update_or_create(
                name="Kathiani",
                county=county,
                defaults={"county": county}
            )

            ward, created = Ward.objects.update_or_create(
                name="Mitaboni",
                subcounty=subcounty,
                defaults={"subcounty": subcounty}
            )

            fields["ward"] = ward

            if first_name and mobile_num != 0:
                phone = "254" + mobile_num

                payload = {
                    "first_name": first_name.capitalize(),
                    "last_name": last_name.capitalize(),
                    "phone_number": phone,
                    "metadata": {"id_number": id_number},
                    "email": f"{first_name.lower()}.{last_name.lower()}.temp@gmail.com"
                }

                user_pass = "test1234"
                user, created = User.objects.get_or_create(
                    phone_number=payload["phone_number"],
                    role=RoleChoices.FARMER,
                    defaults={
                        'phone_number': phone,
                        'first_name': first_name.capitalize(),
                        'last_name': last_name.capitalize()
                    }
                )
                if created:
                    user.set_password(user_pass)

                fields["farmer"] = user

                # Handle different import modes
                if mode == 'update':
                    # Update or create farm
                    farm, created = Farm.objects.update_or_create(
                        name=fields["name"],
                        defaults=fields
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                elif mode == 'skip':
                    # Skip if farm already exists
                    if Farm.objects.filter(name=fields["name"]).exists():
                        skipped_count += 1
                        continue
                    else:
                        feature = Farm(**fields)
                        feature.save()
                        created_count += 1
                else:
                    # Default: create (will fail on duplicates)
                    feature = Farm(**fields)
                    feature.save()
                    created_count += 1

        # delete the temporary files since data has been uploaded successfully
        os.remove(fname)
        shutil.rmtree(dir_name)

        return {
            'total': total_farms,
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count
        }

    # https://gis.stackexchange.com/questions/421771/ogr-coordinatetransformation-appears-to-be-inverting-xy-coordinates
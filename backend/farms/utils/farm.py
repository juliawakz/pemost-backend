import os
import shutil
import tempfile
import traceback
import zipfile

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from farms.models.farm import Farm
from locations.models import County, SubCounty, Ward
from osgeo import ogr
from rest_framework.serializers import ValidationError
from users.choices import RoleChoices
from users.utils.otp import OtpUtils
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()
otp_utils = OtpUtils()


class FarmUtils:
    # Method to import data from shapefile
    def import_data(self, shapefile):
        fd, fname = tempfile.mkstemp(suffix=".zip")
        os.close(fd)
        with open(fname, "wb") as f:
            for chunk in shapefile.chunks():
                f.write(chunk)

        if not zipfile.is_zipfile(fname):
            os.remove(fname)
            raise ValidationError("Not a valid zip archive.")

        zipf = zipfile.ZipFile(fname)
        required_suffixes = [".shp", ".shx", ".dbf", ".prj"]
        has_suffix = {s: False for s in required_suffixes}

        for info in zipf.infolist():
            suffix = os.path.splitext(info.filename)[1].lower()
            if suffix in required_suffixes:
                has_suffix[suffix] = True

        for suffix in required_suffixes:
            if not has_suffix[suffix]:
                zipf.close()
                os.remove(fname)
                raise ValidationError(f"Archive missing required {suffix} file.")

        shapefile_name = None
        dir_name = tempfile.mkdtemp()
        try:
            # Extract shapefile
            for info in zipf.infolist():
                if info.filename.endswith(".shp"):
                    shapefile_name = info.filename
                dst_file = os.path.join(dir_name, info.filename)
                with open(dst_file, "wb") as f:
                    f.write(zipf.read(info.filename))
            zipf.close()

            # Open shapefile
            try:
                datasource = ogr.Open(os.path.join(dir_name, shapefile_name))
                layer = datasource.GetLayer(0)
            except Exception:
                traceback.print_exc()
                raise ValidationError("Not a valid shapefile.")

            # ✅ Required fields
            required_fields = ["First_Name", "Last_Name", "Phone_Number", "Email", "Id_No"]
            ldef = layer.GetLayerDefn()
            existing_fields = [ldef.GetFieldDefn(i).GetName() for i in range(ldef.GetFieldCount())]

            missing_fields = [f for f in required_fields if f not in existing_fields]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

            total_farms = layer.GetFeatureCount()

            for i in range(total_farms):
                src_feature = layer.GetFeature(i)
                src_geometry = src_feature.GetGeometryRef()
                geometry = GEOSGeometry(src_geometry.ExportToWkt())

                first_name = src_feature.GetFieldAsString("First_Name")
                last_name = src_feature.GetFieldAsString("Last_Name")
                mobile_num = src_feature.GetFieldAsString("Phone_Number")
                email = src_feature.GetFieldAsString("Email")
                id_number = src_feature.GetFieldAsString("Id_No")

                # Normalize phone
                phone = None
                if mobile_num:
                    mobile_num = str(mobile_num).lstrip("+")
                    if not mobile_num.startswith("254"):
                        phone = "254" + mobile_num.lstrip("0")
                    else:
                        phone = mobile_num

                # Farm fields
                fields = {
                    "boundary": geometry,
                    "name": f"{first_name}-{last_name}-{geometry.wkt[-8:-4]}"
                }

                county, _ = County.objects.get_or_create(
                    name="Machakos", county_num=16
                )
                subcounty, _ = SubCounty.objects.update_or_create(
                    name="Kathiani", county=county, defaults={"county": county}
                )
                ward, _ = Ward.objects.update_or_create(
                    name="Mitaboni", subcounty=subcounty,
                    defaults={"subcounty": subcounty}
                )
                fields["ward"] = ward

                if first_name and email:
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            "phone_number": phone,
                            "email": email,
                            "id_number": id_number,
                            "first_name": first_name.capitalize(),
                            "last_name": last_name.capitalize(),
                            "role": RoleChoices.FARMER,
                        },
                    )
                    if created:
                        user_pass = otp_utils.generate_random_password()
                        user.set_password(user_pass)
                        user.save()
                        user_utils.send_login_credentials_email(
                            first_name=first_name, email=email,
                            password=user_pass
                        )
                    user.wards.set([ward])

                    fields["owner"] = user

                farm = Farm(**fields)
                farm.save()

            return total_farms

        finally:
            # ✅ Always cleanup
            try:
                datasource = None
            except Exception:
                pass
            if os.path.exists(fname):
                os.remove(fname)
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

    # https://gis.stackexchange.com/questions/421771/ogr-coordinatetransformation-appears-to-be-inverting-xy-coordinates

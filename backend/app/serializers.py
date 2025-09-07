import datetime
import logging

import pandas as pd
from accounts.serializers import UserDetailSerializer
from app import shapefileIO
from app.choices import ACTION_THRESHOLD_RISK, PEST_STAGE, SERVERE, GrowthStage
from app.models import (
    Any_Occurrence,
    County,
    Crop_Type,
    Crop_Variety,
    Farm,
    Growth_Stage,
    Pest_Control,
    Pest_Control_Modified,
    Planting_Information,
    SubCounty,
    Ward,
)
from app.tasks import get_occurence_and_classification
from django.contrib.auth import get_user_model
from fcm_django.api.rest_framework import FCMDeviceSerializer
from fcm_django.models import FCMDevice
from pnotifications.signals import send_notification
from rest_framework import serializers, status
from rest_framework_gis.serializers import GeoFeatureModelSerializer

logger = logging.getLogger(__name__)

User = get_user_model()

status400 = status.HTTP_400_BAD_REQUEST
status200 = status.HTTP_202_ACCEPTED


class FcmDeviceSerializer(FCMDeviceSerializer):
    device_id = serializers.CharField(max_length=100, required=True)

    class Meta:
        model = FCMDevice
        fields = "__all__"


class CountySerailizer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    county_num = serializers.IntegerField(min_value=1, max_value=47, required=True)

    class Meta:
        model = County
        fields = ["id", "name", "county_num"]

    def validate(self, attrs):
        name = attrs.get("name")
        county_num = attrs.get("county_num")

        if not self.instance:
            try:
                County.objects.get(county_num=county_num)
            except County.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError(
                    "County with this name already exists"
                )

            try:
                County.objects.get(name=name.title())
            except County.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError(
                    "County with this name already exists"
                )

        return attrs


class CountyMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = ["name", "county_num"]


class SubCountySerailizer(serializers.ModelSerializer):
    county_detail = CountyMinSerializer(source="county", read_only=True)

    class Meta:
        model = SubCounty
        fields = ["id", "name", "county", "county_detail"]

    def validate(self, attrs):
        name = attrs.get("name")

        if not self.instance:
            try:
                SubCounty.objects.get(name=name.title())
            except SubCounty.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError(
                    "SubCounty with this name already exists"
                )

        return attrs


class SubCountyMinSerializer(serializers.ModelSerializer):
    county_detail = CountyMinSerializer(source="county", read_only=True)

    class Meta:
        model = SubCounty
        fields = ["name", "county_detail"]


class WardSerailizer(serializers.ModelSerializer):
    subcounty_detail = SubCountyMinSerializer(source="subcounty", read_only=True)

    class Meta:
        model = Ward
        fields = ["id", "name", "subcounty", "subcounty_detail"]

    def validate(self, attrs):
        name = attrs.get("name")

        if not self.instance:
            try:
                Ward.objects.get(name=name.title())
            except Ward.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError("Ward with this name already exists")
        return attrs


class WardDetailSerailizer(serializers.ModelSerializer):
    subcounty_detail = SubCountyMinSerializer(source="subcounty", read_only=True)

    class Meta:
        model = Ward
        fields = ["name", "subcounty", "subcounty_detail"]


class FarmDetailSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Farm
        geo_field = "farm_boundary"
        bbox_geo_field = "farm_boundary"
        fields = [
            "id",
            "farm_area_acres",
            "farm_boundary"
        ]


class OccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Any_Occurrence
        fields = [
            "yellow_buffer",
            "red_buffer",
            "green_buffer",
        ]

    def validate(self, attrs):
        return attrs


class PlantingInfoSerializer(serializers.ModelSerializer):
    transplanting_date = serializers.DateField(required=True)
    notification_end_date = serializers.DateField(read_only=True)

    class Meta:
        model = Planting_Information
        fields = "__all__"

    def validate(self, attrs):
        crop_variety = attrs.get("crop_variety", None)
        transplanting_date = attrs.get("transplanting_date", None)

        if transplanting_date > datetime.date.today():
            raise serializers.ValidationError("Transplanting date cannot be greater than today.")

        if crop_variety and transplanting_date:
            max_maturity_in_days = crop_variety.max_maturity_in_days
            attrs["notification_end_date"] = transplanting_date + datetime.timedelta(days=max_maturity_in_days)

        return attrs


class CropTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop_Type
        fields = "__all__"


class CropVarietySerializer(serializers.ModelSerializer):
    owner_detail = UserDetailSerializer(source="owner", read_only=True)

    class Meta:
        model = Crop_Variety
        fields = [
            "id",
            "crop_type",
            "crop_variety",
            "min_maturity_in_days",
            "max_maturity_in_days",
            "min_estimated_yield",
            "max_estimated_yield",
            "suitable_climatic_conditions",
            "min_altitude_meters_above_sea_level",
            "max_altitude_meters_above_sea_level",
            "min_annual_rainfall_mm",
            "max_annual_rainfall_mm",
            "row_spacing_cm",
            "plant_spacing_1_plant_per_hill",
            "fertilizer_requirements_planting_DAP_kgs",
            "fertilizer_requirements_topdressing_CAN_kgs",
            "fertilizer_requirements_topdressing_17_17_kgs",
            "diseases_tolerance",
            "pest_tolerance",
            "pest_susceptibility",
            "disease_susceptibility",
            "seed_source",
            "Seed_rate_per_acre_grams",
            "owner",
            "owner_detail"
        ]
        read_only_fields = ["owner_detail"]
        extra_kwargs = {"owner": {"write_only": True}}

    def validate(self, attrs):
        crop_type = attrs.get("crop_type")
        crop_variety = attrs.get("crop_variety")

        if not self.instance:
            try:
                Crop_Variety.objects.get(crop_variety=crop_variety.title())
            except Crop_Variety.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError(
                    "Crop with this crop_variety already exists."
                )

            try:
                Crop_Variety.objects.get(
                    crop_variety=crop_variety.title()
                )
            except Crop_Variety.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError(
                    "The fields crop_type, crop_variety must make a unique set."
                )
        return attrs


class CropMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop_Variety
        fields = [
            "crop_type",
            "crop_variety",
        ]


class GrowthStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Growth_Stage
        fields = "__all__"


class FarmSerializer(serializers.ModelSerializer):
    owner_detail = UserDetailSerializer(source="owner", read_only=True)
    ward_detail = WardDetailSerailizer(source="ward", read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "ward",
            "farm_boundary",
            "farm_area_acres",
            "owner",
            "owner_detail",
            "ward_detail",
            "metadata",
        ]
        read_only_fields = ["owner_detail"]
        extra_kwargs = {"owner": {"write_only": True}}


class UploadCropVarietyCsvSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        file = validated_data.pop("file")

        reader = pd.read_csv(file)
        created_crop_types = {}  # Dictionary to store created Crop_Type objects

        for i, row in reader.iterrows():
            crop_type_csv = row["crop_type"]

            user = User.objects.get(is_superuser=True)

            if Crop_Type.objects.filter(name=crop_type_csv.title(), owner=user).exists():
                crop_type_obj = Crop_Type.objects.get(name=crop_type_csv.title())
            else:
                crop_type_obj = Crop_Type.objects.create(name=crop_type_csv.title(), owner=user)

            try:
                if crop_type_obj:
                    crop = Crop_Variety.objects.create(
                        crop_type=crop_type_obj,
                        crop_variety=row["crop_variety"],
                        min_maturity_in_days=row["min_ maturity_ period(days)"],
                        max_maturity_in_days=row["max maturity period(days)"],
                        min_estimated_yield=row["estimated_ min_yield_tons/acre"],
                        max_estimated_yield=row["estimated_max_yield_tons/acre"],

                        suitable_climatic_conditions=row["suitable_climatic_conditions"],
                        min_altitude_meters_above_sea_level=row[
                            "altitude_meters_above_sea_level_min"
                        ],
                        max_altitude_meters_above_sea_level=row[
                            "altitude_meters_above_sea_level_max"
                        ],
                        min_annual_rainfall_mm=row["annual_rainfall_millimeters_min"],
                        max_annual_rainfall_mm=row["annual_rainfall_millimeters_max"],
                        row_spacing_cm=row["row_spacing_cm"],
                        plant_spacing_1_plant_per_hill=row[
                            "plant_spacing_1_plant_per_hill"
                        ],
                        fertilizer_requirements_planting_DAP_kgs=row[
                            "fertilizer_requiments_planting_DAP_kgs"
                        ],
                        fertilizer_requirements_topdressing_CAN_kgs=row[
                            "fertilizer_requiments_topdressing_CAN_kgs"
                        ],
                        fertilizer_requirements_topdressing_17_17_kgs=row[
                            "fertilizer_requiments_topdressing_17:17:17_kgs"
                        ],
                        diseases_tolerance=row[
                            "diseases_tolerance"
                        ],
                        pest_tolerance=row[
                            "pest_tolerance"
                        ],
                        pest_susceptibility=row[
                            "pest_susceptibility"
                        ],
                        disease_susceptibility=row[
                            "disease_susceptibility"
                        ],
                        seed_source=row[
                            "seed source"
                        ],
                        Seed_rate_per_acre_grams=row[
                            "Seed rate_ per acre_grams"
                        ],
                        owner=user

                    )
            except Exception as ex:
                logging.error("error:", ex.args)
                # pass
        return validated_data


class UploadGrowthStageCsvSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        file = validated_data.pop("file")

        reader = pd.read_csv(file)
        count = 0

        for i, row in reader.iterrows():
            count += 1
            user = User.objects.get(is_superuser=True)

            crop = row["crop"].title()
            crop_varietyy = row["variety"].title()
            crop_typee = Crop_Type.objects.get(name=crop)
            crop_variety_obj, created = Crop_Variety.objects.get_or_create(
                crop_type=crop_typee, crop_variety=crop_varietyy, owner=user,
            )

            try:
                stage = None
                severe = None
                if crop_variety_obj:
                    if row["stage of growth"].strip() == "vegetative":
                        stage = GrowthStage.VEGETATIVE
                    if row["stage of growth"].strip() == "flowering":
                        stage = GrowthStage.FLOWERING
                    if row["stage of growth"].strip() == "fruiting":
                        stage = GrowthStage.FRUITING
                    if row["stage of growth"].strip() == "harvesting":
                        stage = GrowthStage.HARVESTING

                    if row["severity"].strip().title() == "Critical":
                        severe = SERVERE.CRITICAL
                    elif row["severity"].strip().title() == "Not Critical":
                        severe = SERVERE.NOT_CRITICAL
                    else:
                        severe = None

                    growth_stage = Growth_Stage.objects.create(
                        crop_variety=crop_variety_obj,
                        growth_stage=stage,
                        severity=severe,
                        minimum_days=row["minimum_days"],
                        maximum_days=row["maximum_days"],
                        owner=user,
                    )
            except Exception as ex:
                logging.error("errrrrrrrrrrror:", ex)
                pass
        if count is None:
            count = 0
            return count
        return count


class FarmsImportSerializer(serializers.Serializer):
    import_file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        shapefile = validated_data.pop("import_file", None)
        info = shapefileIO.import_farms(shapefile)
        return info


class AvailableFarmsSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    radius = serializers.IntegerField(required=True)


class UploadCountySerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        file = validated_data.pop("file")

        reader = pd.read_csv(file)
        total_saved = 0
        messages = []
        for i, row in reader.iterrows():
            try:
                County.objects.create(
                    name=row["name"],
                    county_num=row["county_number"]
                )

                total_saved += 1
            except Exception as ex:
                message = f"Error:{ex}"
                messages.append(message)
                pass
        return validated_data, total_saved, messages


class UploadSubcountyCountySerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        file = validated_data.pop("file")

        reader = pd.read_csv(file)
        total_saved = 0
        messages = []
        for i, row in reader.iterrows():
            try:
                # ensure names have no spaces to the right or in between
                subcounty_strip = row["name"].rstrip()
                subcounty_name = " ".join(subcounty_strip.split())

                county_strip = row["county_name"].rstrip()
                county_name = " ".join(county_strip.split())

                county_instance = County.objects.get(name=county_name)

                SubCounty.objects.create(
                    name=subcounty_name,
                    county=county_instance
                )

                total_saved += 1
            except Exception as ex:
                message = f"Error:{ex}"
                messages.append(message)
                pass
        return validated_data, total_saved, messages


class UploadWardsSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        file = validated_data.pop("file")

        reader = pd.read_csv(file)
        total_saved = 0
        messages = []
        for i, row in reader.iterrows():
            try:
                # ensure names have no spaces to the right or in between
                ward_strip = row["name"].rstrip()
                ward_name = " ".join(ward_strip.split())

                subcounty_strip = row["subcounty_name"].rstrip()
                subcounty_name = " ".join(subcounty_strip.split())

                subcounty_instance = SubCounty.objects.get(name=subcounty_name)

                Ward.objects.create(
                    name=ward_name,
                    subcounty=subcounty_instance
                )

                total_saved += 1
            except Exception as ex:
                message = f"Error:{ex}"
                messages.append(message)
                pass
        return validated_data, total_saved, messages


class UploadPestControlCsvSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        file = validated_data.pop("file")

        reader = pd.read_csv(file)
        count = 0
        stage = None
        stage_crop_growth = None

        for i, row in reader.iterrows():
            count += 1

            try:
                if row["stage_pest"].lower().strip() == "eggs":
                    stage = PEST_STAGE.EGGS
                elif row["stage_pest"].lower().strip() == "larvae":
                    stage = PEST_STAGE.LARVAE
                elif row["stage_pest"].lower().strip() == "adult":
                    stage = PEST_STAGE.ADULT
                elif row["stage_pest"].lower().strip() == "nymph":
                    stage = PEST_STAGE.NYMPH
                elif row["stage_pest"].lower().strip() == "pupae":
                    stage = PEST_STAGE.PUPAE

                if row["stage_crop growth"].lower().strip() == "vegetative":
                    stage_crop_growth = GrowthStage.VEGETATIVE
                elif row["stage_crop growth"].lower().strip() == "flowering":
                    stage_crop_growth = GrowthStage.FLOWERING
                elif row["stage_crop growth"].lower().strip() == "fruiting":
                    stage_crop_growth = GrowthStage.FRUITING
                elif row["stage_crop growth"].lower().strip() == "harvesting":
                    stage_crop_growth = GrowthStage.HARVESTING

                Pest_Control.objects.create(
                    pest_type=row["type of pest"].strip(),
                    scientific_name=row["Scientific_name"],
                    stage_pest=stage,
                    action_threshold=row["action_threshold"],
                    action_threshold_risk=row["action_threshold_risk"],
                    stage_crop_growth=stage_crop_growth,
                    cultural=row["cultural"],
                    cultural_description=row["cultural_description"],
                    biological=row["biological"],
                    biological_description=row["biological_description"],

                )
            except Exception as ex:
                logger.error(f"upload error: {ex}")
                pass

        if count is None:
            count = 0
            return count
        return count


class UploadPestControlModifiedCsvSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        file = validated_data.pop("file")

        reader = pd.read_csv(file)
        count = 0
        stage = None
        stage_crop_growth = None
        action_threshold_risk = None
        no_of_plants_affected = None
        pest_presence_period = None

        for i, row in reader.iterrows():
            count += 1

            try:
                if row["stage_pest"].lower().strip() == "eggs":
                    stage = PEST_STAGE.EGGS
                elif row["stage_pest"].lower().strip() == "larvae":
                    stage = PEST_STAGE.LARVAE
                elif row["stage_pest"].lower().strip() == "adult":
                    stage = PEST_STAGE.ADULT
                elif row["stage_pest"].lower().strip() == "nymph":
                    stage = PEST_STAGE.NYMPH
                elif row["stage_pest"].lower().strip() == "pupae":
                    stage = PEST_STAGE.PUPAE

                if row["stage_crop growth"].lower().strip() == "vegetative":
                    stage_crop_growth = GrowthStage.VEGETATIVE
                elif row["stage_crop growth"].lower().strip() == "flowering":
                    stage_crop_growth = GrowthStage.FLOWERING
                elif row["stage_crop growth"].lower().strip() == "fruiting":
                    stage_crop_growth = GrowthStage.FRUITING
                elif row["stage_crop growth"].lower().strip() == "harvesting":
                    stage_crop_growth = GrowthStage.HARVESTING

                if row["action_threshold_risk"].lower().strip() == "none":
                    action_threshold_risk = ACTION_THRESHOLD_RISK.NONE
                elif row["action_threshold_risk"].lower().strip() == "moderate":
                    action_threshold_risk = ACTION_THRESHOLD_RISK.MODERATE
                elif row["action_threshold_risk"].lower().strip() == "high":
                    action_threshold_risk = ACTION_THRESHOLD_RISK.HIGH
                elif row["action_threshold_risk"].lower().strip() == "low":
                    action_threshold_risk = ACTION_THRESHOLD_RISK.LOW

                Pest_Control_Modified.objects.create(
                    pest_type=row["type of pest"].strip(),
                    scientific_name=row["Scientific_name"],
                    stage_pest=stage,
                    action_threshold=row["action_threshold"],
                    action_threshold_risk=action_threshold_risk,
                    stage_crop_growth=stage_crop_growth,
                    cultural=row["cultural"],
                    cultural_description=row["cultural_description"],
                    biological=row["biological"],
                    biological_description=row["biological_description"],
                    no_of_plants_affected=row["Period of pest presence"],
                    pest_presence_period=row["Period of pest presence"],
                )
            except Exception as ex:
                logger.error(f"upload error: {ex}")
                pass

        if count is None:
            count = 0
            return count
        return count


def send_growth_stage_notification():
    # Get current date
    today = datetime.date.today()

    # Get all planting information records
    planting_infos = Planting_Information.objects.all()

    for planting_info in planting_infos:
        crop_variety = planting_info.crop_variety
        notification_date_end = planting_info.notification_end_date

        # Calculate date ranges for the current crop's growth stages
        growth_stages = Growth_Stage.objects.filter(crop_variety=crop_variety)
        for stage in growth_stages:
            start_date = planting_info.transplanting_date + datetime.timedelta(days=stage.minimum_days)
            end_date = planting_info.transplanting_date + datetime.timedelta(days=stage.maximum_days)

            # Check if current date is within the date range for the growth stage
            if start_date <= today <= end_date:
                # Send a notification about the current stage of growth
                send_notification(planting_info.owner, f"Your {crop_variety} is in {stage.growth_stage} stage.")

            if today > end_date:
                # Send a notification about the current stage of growth
                send_notification(planting_info.owner, f"Your {crop_variety} is past the Harvesting stage.")


all_clipped_yellow_buffers = []
all_clipped_green_buffers = []
farms_with_occurrences = []
yellow_buffer_distance = 300  # buffer distance in meters
green_buffer_distance = 500  # buffer distance in meters


class ProcessOccurrenceSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.DictField())

    def validate(self, attrs):

        get_occurence_and_classification(data=attrs.get("data"))

        return attrs

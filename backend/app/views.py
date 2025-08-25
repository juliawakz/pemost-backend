from accounts.permissions import IsTokenValid
from app.filtersets import (
    CountyFilter,
    CropFilter,
    CropTypeFilter,
    FarmFilter,
    FCMDeviceFilter,
    SubCountyFilter,
    WardFilter,
)
from app.models import (
    Any_Occurrence,
    County,
    Crop_Type,
    Crop_Variety,
    Farm,
    Growth_Stage,
    Planting_Information,
    SubCounty,
    Ward,
)
from app.paginator import custom_paginate
from app.serializers import (
    AvailableFarmsSerializer,
    CountySerailizer,
    CropTypeSerializer,
    CropVarietySerializer,
    FarmDetailSerializer,
    FarmSerializer,
    FarmsImportSerializer,
    FcmDeviceSerializer,
    GrowthStageSerializer,
    OccurrenceSerializer,
    PlantingInfoSerializer,
    ProcessOccurrenceSerializer,
    SubCountySerailizer,
    UploadCountySerializer,
    UploadCropVarietyCsvSerializer,
    UploadGrowthStageCsvSerializer,
    UploadPestControlCsvSerializer,
    UploadPestControlModifiedCsvSerializer,
    UploadSubcountyCountySerializer,
    UploadWardsSerializer,
    WardSerailizer,
)
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q
from fcm_django.models import FCMDevice
from rest_framework import generics, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class FCMDeviceViewset(viewsets.ModelViewSet):
    queryset = FCMDevice.objects.all()
    serializer_class = FcmDeviceSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)
    filterset_class = FCMDeviceFilter


class CountyViewset(viewsets.ModelViewSet):
    queryset = County.objects.all()
    serializer_class = CountySerailizer
    permission_classes = (IsAuthenticated, IsTokenValid)
    filterset_class = CountyFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsTokenValid(), IsAdminUser()]
        return [permission() for permission in self.permission_classes]


class SubCountyViewset(viewsets.ModelViewSet):
    """These are  constituencies"""
    queryset = SubCounty.objects.all()
    serializer_class = SubCountySerailizer
    permission_classes = (IsAuthenticated, IsTokenValid)
    filterset_class = SubCountyFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsTokenValid(), IsAdminUser()]
        return [permission() for permission in self.permission_classes]


class WardViewset(viewsets.ModelViewSet):
    queryset = Ward.objects.all()
    serializer_class = WardSerailizer
    permission_classes = (IsAuthenticated, IsTokenValid)
    filterset_class = WardFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsTokenValid(), IsAdminUser()]
        return super().get_permissions()


class GrowthStageViewset(viewsets.ModelViewSet):
    queryset = Growth_Stage.objects.all()
    serializer_class = GrowthStageSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsTokenValid(), IsAdminUser()]
        return [permission() for permission in self.permission_classes]


class CropTypeViewset(viewsets.ModelViewSet):
    queryset = Crop_Type.objects.all()
    serializer_class = CropTypeSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)
    filterset_class = CropTypeFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsTokenValid(), IsAdminUser()]
        return [permission() for permission in self.permission_classes]


class CropVarietyViewset(viewsets.ModelViewSet):
    queryset = Crop_Variety.objects.all()
    serializer_class = CropVarietySerializer
    permission_classes = (IsAuthenticated, IsTokenValid)
    filterset_class = CropFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsTokenValid(), IsAdminUser()]
        return [permission() for permission in self.permission_classes]


class UploadCropVarietyCsvView(generics.GenericAPIView):
    serializer_class = UploadCropVarietyCsvSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Crop Variety uploaded",
                "status": status.HTTP_200_OK,
            }
        )


class UploadGrowthStageView(generics.GenericAPIView):
    serializer_class = UploadGrowthStageCsvSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        count = serializer.save()
        return Response(
            {
                "message": f"{count} Growth Stages uploaded",
                "status": status.HTTP_200_OK,
            }
        )


class FarmsImportViewset(generics.GenericAPIView):
    queryset = None
    serializer_class = FarmsImportSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        total_farms = serializer.save()
        return Response(
            {
                "message": f"{total_farms} farms uploaded",
                "status": status.HTTP_200_OK,
            }
        )


class FarmViewset(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)
    filterset_class = FarmFilter

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.filter(is_archived=False)
        return self.queryset.filter(Q(owner=user)).filter(is_archived=False)

    def create(self, request, *args, **kwargs):
        data = request.data
        data["owner"] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid()
        if serializer.is_valid():
            self.perform_create(serializer)
            data = serializer.data
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=self.get_success_headers(data),
            )
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class OccurrenceViewset(viewsets.ModelViewSet):
    queryset = Any_Occurrence.objects.all().order_by('-created_at')[:1]
    serializer_class = OccurrenceSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)


class AvailableFarms(generics.ListAPIView):
    serializer_class = FarmSerializer
    queryset = Farm.objects.all()
    permission_classes = (IsAuthenticated, IsTokenValid)

    def get(self, request, *args, **kwargs):
        serializer = AvailableFarmsSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        current_location = Point(
            serializer.data.get("latitude"), serializer.data.get("longitude"), srid=4326
        )

        nearby_farms = Farm.objects.filter(
            farm_boundary__distance_lte=(
                current_location,
                D(m=serializer.data.get("radius")),
            ),
        )
        serializer = custom_paginate(
            serializer=FarmSerializer, queryset=nearby_farms, request=request
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlantingInfoViewset(viewsets.ModelViewSet):
    queryset = Planting_Information.objects.all()
    serializer_class = PlantingInfoSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def create(self, request, *args, **kwargs):
        data = request.data
        data["owner"] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadCountyView(generics.GenericAPIView):
    serializer_class = UploadCountySerializer
    permission_classes = (IsAuthenticated, IsTokenValid, IsAdminUser)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        created_data = serializer.save()
        return Response(
            {
                "message": f"{created_data[1]} Counties uploaded",
                "status": status.HTTP_200_OK,
                "easy_notice": created_data[2]
            }
        )


class UploadSubCountyView(generics.GenericAPIView):
    serializer_class = UploadSubcountyCountySerializer
    permission_classes = (IsAuthenticated, IsTokenValid, IsAdminUser)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        created_data = serializer.save()
        return Response(
            {
                "message": f"{created_data[1]} Sub Counties uploaded",
                "status": status.HTTP_200_OK,
                "easy_notice": created_data[2]
            }
        )


class UploadWardView(generics.GenericAPIView):
    serializer_class = UploadWardsSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, IsAdminUser)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        created_data = serializer.save()
        return Response(
            {
                "message": f"{created_data[1]} Wards uploaded",
                "status": status.HTTP_200_OK,
                "easy_notice": created_data[2]
            }
        )


class UploadPestControlCsvView(generics.GenericAPIView):
    serializer_class = UploadPestControlCsvSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        total_upload = serializer.save()
        return Response(
            {
                "message": f"{total_upload} Pests uploaded",
                "status": status.HTTP_200_OK,
            }
        )


class UploadPestControlModifiedCsvView(generics.GenericAPIView):
    serializer_class = UploadPestControlModifiedCsvSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        total_upload = serializer.save()
        return Response(
            {
                "message": f"{total_upload} Pests uploaded",
                "status": status.HTTP_200_OK,
            }
        )


class NoPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        return None


class FarmDetailViewset(generics.ListAPIView):
    pagination_class = NoPagination
    authentication_classes = [TokenAuthentication, ]
    queryset = Farm.objects.all()
    serializer_class = FarmDetailSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)


class ProcessOccurenceView(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = (IsAuthenticated, IsTokenValid)

    def post(self, request, *args, **kwargs):
        if len(request.data) > 0:
            request_data = {
                "data": request.data
            }
            serializer = ProcessOccurrenceSerializer(data=request_data, context={"request": request_data})
            if serializer.is_valid():
                message = {"detail":"Data Accepted"}
                return Response(message, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"detail":"No data passed"}, status=status.HTTP_400_BAD_REQUEST)

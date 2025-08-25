import datetime
import os
import shutil

import geojson
import rtree
from app.choices import GrowthStage
from app.models import Any_Occurrence, Farm, Pest_Control_Modified, Planting_Information
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import Union
from django.contrib.gis.geos import GEOSGeometry
from osgeo import ogr, osr
from pnotifications.models import BroadCast_Notification
from pnotifications.signals import send_notification
from shapely import wkt
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import cascaded_union, unary_union
from shapely.wkt import loads as wkt_loads

User = get_user_model()


def create_file_shapefile(geometry, filename):
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # Create a new shapefile for the yellow buffer
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(filename)
    layer = data_source.CreateLayer("layer", srs, ogr.wkbPolygon)
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetGeometry(ogr.CreateGeometryFromWkb(geometry.wkb))
    feature.CreateFeature(feature)

    feature = None
    data_source = None


def create_shapefile(geometry, filename):
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # Create shapefile datasource
    driver = ogr.GetDriverByName("ESRI Shapefile")
    datasource = driver.CreateDataSource(filename)

    # Create layer
    layer = datasource.CreateLayer("buffer", srs, geom_type=ogr.wkbPolygon)

    # Add field
    layer.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))

    # Create feature
    featureDefn = layer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetField("id", 1)

    # Create geometry
    ogr_geometry = ogr.CreateGeometryFromWkt(geometry.wkt)
    feature.SetGeometry(ogr_geometry)

    # Add feature to layer
    layer.CreateFeature(feature)

    # Cleanup
    feature = None
    datasource = None


def union_yellow_buffers(clipped_yellow_buffers):
    # Filter out invalid geometries
    valid_clipped_yellow_buffers = [geom for geom in clipped_yellow_buffers if geom and geom.IsValid()]

    # Check if there are valid geometries left
    if not valid_clipped_yellow_buffers:
        return None

    # Create a new geometry collection to store the clipped geometries
    geom_collection = ogr.Geometry(ogr.wkbGeometryCollection)

    # Add all clipped geometries to the collection
    for clipped_yellow_buffer in valid_clipped_yellow_buffers:
        geom_collection.AddGeometry(clipped_yellow_buffer)

    # Perform the union using cascaded union (UnionCascaded)
    try:
        unioned_yellow_buffer_geom = geom_collection.UnionCascaded()
    except Exception as e:
        return None

    # Check if the resulting unioned geometry is valid
    if not unioned_yellow_buffer_geom or not unioned_yellow_buffer_geom.IsValid():
        unioned_yellow_buffer_geom = unioned_yellow_buffer_geom.Buffer(0)

        if not unioned_yellow_buffer_geom or not unioned_yellow_buffer_geom.IsValid():
            return None

    return unioned_yellow_buffer_geom


def union_green_buffers(clipped_green_buffers):
    # Filter out invalid geometries
    valid_clipped_green_buffers = [geom for geom in clipped_green_buffers if geom and geom.IsValid()]

    # Check if there are valid geometries left
    if not valid_clipped_green_buffers:
        return None

    # Create a new geometry collection to store the clipped geometries
    geom_collection = ogr.Geometry(ogr.wkbGeometryCollection)

    # Add all clipped geometries to the collection
    for clipped_green_buffer in valid_clipped_green_buffers:
        geom_collection.AddGeometry(clipped_green_buffer)

    # Perform the union using cascaded union (UnionCascaded)
    try:
        unioned_green_buffer_geom = geom_collection.UnionCascaded()
    except Exception as e:
        return None

    # Check if the resulting unioned geometry is valid
    if not unioned_green_buffer_geom or not unioned_green_buffer_geom.IsValid():
        unioned_green_buffer_geom = unioned_green_buffer_geom.Buffer(0)

        if not unioned_green_buffer_geom or not unioned_green_buffer_geom.IsValid():
            return None

    return unioned_green_buffer_geom


def read_wkt_polygons(file_path):
    with open(file_path, "r") as file:
        return file.read().split('\n')


def create_geometries_from_wkt(wkt_list):
    geometries = []
    for wkt in wkt_list:
        shapely_geometry = wkt_loads(wkt)
        geometries.append(shapely_geometry)
    return geometries


# Modify the create_spatial_index function to calculate bounding boxes using Shapely
def create_spatial_index(geometries):
    index = rtree.index.Index()
    for i, geometry in enumerate(geometries):
        shapely_geometry = wkt_loads(geometry.ExportToWkt())
        envelope = shapely_geometry.bounds
        index.insert(i, envelope, obj=geometry)
    return index


def perform_union(geometries):
    # Convert OGR geometries to Shapely geometries
    geometries = [shape(geom) if hasattr(geom, "ExportToWkt") else geom for geom in geometries]

    index = rtree.index.Index()
    for i, geometry in enumerate(geometries):
        envelope = geometry.bounds
        index.insert(i, envelope, obj=geometry)

    union_results = []
    visited = set()

    for i, geometry in enumerate(geometries):
        if i in visited:
            continue
        union_geometry = geometry
        for intersecting_geometry_id in index.intersection(geometry.bounds):
            if intersecting_geometry_id != i and intersecting_geometry_id not in visited:
                intersecting_geometry = geometries[intersecting_geometry_id]
                if union_geometry.intersects(intersecting_geometry):
                    union_geometry = union_geometry.union(intersecting_geometry)
                    visited.add(intersecting_geometry_id)

        # Append union_geometry directly as a Shapely geometry object
        if isinstance(union_geometry, Polygon):
            union_results.append(union_geometry)
        elif isinstance(union_geometry, MultiPolygon):
            for polygon in union_geometry:
                union_results.append(polygon)

    return union_results


def dissolve_touching_polygons(polygons):
    dissolved_geoms = []
    processed = set()

    for polygon in polygons:
        if polygon in processed:
            continue

        touching_polygons = [polygon]
        for other in polygons:
            if other != polygon and polygon.touches(other):
                touching_polygons.append(other)
                processed.add(other)

        dissolved_geom = cascaded_union(touching_polygons)
        dissolved_geoms.append(dissolved_geom)

    return dissolved_geoms

def all_green_interventions(farm_object):
    pest_info_dict = {"interventions": [f"{farm_object.owner.first_name} {farm_object.owner.last_name}'s farm is currently in the green zone. No interventions needed"]}
    farm_object.metadata['pest_and_interventions'] = pest_info_dict
    farm_object.save()


def all_interventions(farm_object):
    date_today = datetime.date.today()

    # Get the latest Planting_Information object for the farm
    plant_info = get_latest_plant_info(farm_object)
    if not plant_info:
        update_metadata(farm_object, f"{farm_object.owner.first_name} {farm_object.owner.last_name}'s farm has no planting information at the moment.")
        return

    transplanting_date = plant_info.transplanting_date

    if not transplanting_date:
        update_metadata(farm_object, "No transplanting date available for this planting information.")
        return

    total_days_after_transplant = (date_today - transplanting_date).days

    # Get growth stages and process pest information
    growth_stages = plant_info.crop_variety.growth_stage_crop.all()
    if not growth_stages.exists():
        update_metadata(farm_object, "No growth stages found for the current crop variety.")
        return

    process_growth_stages(farm_object, growth_stages, total_days_after_transplant, transplanting_date)


def get_latest_plant_info(farm_object):
    try:
        return Planting_Information.objects.filter(farm=farm_object).latest('transplanting_date')
    except Planting_Information.DoesNotExist:
        return None


def process_growth_stages(farm_object, growth_stages, total_days_after_transplant, transplanting_date):
    found_stage = False  # Flag to check if any growth stage matches the condition

    for growth_stage in growth_stages:
        # Check if total_days_after_transplant is within the current growth stage's range
        if growth_stage.minimum_days <= total_days_after_transplant <= growth_stage.maximum_days:
            found_stage = True  # Set the flag to True as we found a matching stage
            pest_info_list = get_pest_info(growth_stage)

            # Update metadata with pest info if found, or a message if no pests are present
            farm_object.metadata['pest_and_interventions'] = {
                "interventions": pest_info_list or ["No pests found for the current growth stage."]
            }
            break  # Since we found a matching stage, we can stop iterating further

    # If no growth stage matched the condition, update metadata with harvesting stage info
    if not found_stage:
        update_metadata(
            farm_object,
            f"{farm_object.owner.first_name} {farm_object.owner.last_name}'s farm is currently in or past the harvesting stage. "
            f"It is {total_days_after_transplant} days since the transplanting date: {transplanting_date}"
        )

    farm_object.save()


def get_pest_info(growth_stage):
    pests = Pest_Control_Modified.objects.filter(stage_crop_growth=growth_stage.growth_stage)

    pest_info_list = []
    for pest in pests:
        pest_info = {
            'stage_pest': pest.stage_pest,
            'pest_name': pest.pest_type,
            'scientific_name': pest.scientific_name,
            'period_of_pest_presence': pest.pest_presence_period,
            'no_of_plants_affected': pest.no_of_plants_affected,
            'action_threshold': pest.action_threshold,
            'action_threshold_risk': pest.action_threshold_risk,
            'stage_crop_growth': pest.stage_crop_growth,
            'cultural': pest.cultural,
            'cultural_description': pest.cultural_description,
            'biological': pest.biological,
            'biological_description': pest.biological_description,
        }
        pest_info_list.append(pest_info)

    return pest_info_list


def update_metadata(farm_object, message):
    farm_object.metadata['pest_and_interventions'] = {"interventions": [message]}
    farm_object.save()


def get_occurence_and_classification(data):
    counts = 0

    all_clipped_yellow_buffers = []
    all_clipped_green_buffers = []
    farms_with_occurrences = []

    for occurence in data:
        farm_object = Farm.objects.get(id=occurence['id'])
        counts += 1

        farm_geometry = farm_object.farm_boundary

        # Create a Feature with the polygon geometry
        farm_polygon = geojson.loads(farm_geometry.geojson)

        farm_wkt = str(farm_geometry).replace("SRID=4326;", "")
        shapely_area_geometry = wkt.loads(farm_wkt)
        area_geometry = shapely_area_geometry.bounds

        if occurence["Occurence"]:

            yellow_buffer_distance = 300  # buffer distance in meters
            green_buffer_distance = 500  # buffer distance in meters

            # Create OGR geometry from the farm's boundary
            farm_boundary_ogr = ogr.CreateGeometryFromWkt(farm_object.farm_boundary.wkt)
            farm_boundary_wkt = farm_object.farm_boundary.wkt
            farm_boundary_shapely = wkt_loads(farm_boundary_wkt)
            farms_with_occurrences.append(farm_boundary_shapely)

            # Set the spatial reference system (SRS) to WGS 84
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            farm_boundary_ogr.AssignSpatialReference(srs)

            # Convert the buffer distances from meters to degrees
            degree_per_meter = 1 / (2 * 3.14159 * 6371007.2 / 360)  # Approximation for converting meters to degrees
            yellow_buffer_degrees = yellow_buffer_distance * degree_per_meter
            green_buffer_degrees = green_buffer_distance * degree_per_meter

            # Perform the buffer operation in degrees
            yellow_buffer_ogr = farm_boundary_ogr.Buffer(yellow_buffer_degrees)

            # Convert buffer polygons back to WKT
            whole_yellow_buffer = yellow_buffer_ogr.ExportToWkt()

            # Clip yellow_buffer with the farm boundary
            yellow_buffer_geom = ogr.CreateGeometryFromWkt(whole_yellow_buffer)

            # Create a geometry representing the farm boundary
            farm_boundary_geom = ogr.CreateGeometryFromWkt(farm_boundary_ogr.ExportToWkt())

            # Remove the farm boundary area from the clipped yellow buffer
            clipped_yellow_buffer_geom = yellow_buffer_geom.Difference(farm_boundary_geom)

            # Convert the clipped yellow buffer to WKT
            clipped_yellow_buffer_wkt = clipped_yellow_buffer_geom.ExportToWkt()
            # Apply a 500m buffer on the farm boundary to create the clipped green buffer
            clipped_green_buffer_geom = farm_boundary_geom.Buffer(green_buffer_degrees)

            # Get the difference between the clipped green buffer and the clipped yellow buffer
            clipped_green_buffer_geom = clipped_green_buffer_geom.Difference(clipped_yellow_buffer_geom)

            # Remove the farm boundary from the clipped green buffer
            clipped_green_buffer_geom = clipped_green_buffer_geom.Difference(farm_boundary_geom)

            # Convert the clipped green buffer to WKT
            clipped_green_buffer_wkt = clipped_green_buffer_geom.ExportToWkt()

            # Store the clipped_yellow_buffer geometry in the list
            all_clipped_yellow_buffers.append(clipped_yellow_buffer_wkt)

            # Store the clipped_yellow_buffer geometry in the list
            all_clipped_green_buffers.append(clipped_green_buffer_wkt)

    # Create OGR geometries from the WKT representations
    yellow_geometries = create_geometries_from_wkt(all_clipped_yellow_buffers)
    green_geometries = create_geometries_from_wkt(all_clipped_green_buffers)

    # Convert each individual Shapely geometry to a MultiPolygon
    yellow_buffer_multipolygon = MultiPolygon(yellow_geometries)
    green_buffer_multipolygon = MultiPolygon(green_geometries)

    # Assuming yellow_buffer_multipolygon is a MultiPolygon object
    yellow_dissolved_buffer = unary_union(yellow_buffer_multipolygon)
    green_dissolved_buffer = unary_union(green_buffer_multipolygon)

    # Perform union using Shapely's cascaded_union
    unioned_geometry = unary_union(farms_with_occurrences)

    # Perform dissolve on the unioned geometry
    dissolved_geometry = unioned_geometry.buffer(0)

    # Create a MultiPolygon from the dissolved geometry
    if dissolved_geometry.geom_type == 'Polygon':
        dissolved_multipolygon = MultiPolygon([dissolved_geometry])
    else:
        dissolved_multipolygon = dissolved_geometry

    # Convert the MultiPolygon to WKT
    red_dissolved_multipolygon_wkt = dissolved_multipolygon.wkt

    # Convert the WKT representations to Shapely geometries
    yellow_dissolved_buffer_geom = wkt_loads(yellow_dissolved_buffer.wkt)
    green_dissolved_buffer_geom = wkt_loads(green_dissolved_buffer.wkt)

    # Check if the yellow dissolved buffer intersects with the red dissolved buffer
    if yellow_dissolved_buffer.intersects(dissolved_multipolygon):
        # Clip the green dissolved buffer by the yellow dissolved buffer
        clipped_yellow_buffer_geom = yellow_dissolved_buffer_geom.difference(dissolved_multipolygon)

        # If there are multiple polygons in the clipped result, create a MultiPolygon
        if clipped_yellow_buffer_geom.geom_type == 'Polygon':
            yellow_dissolved_buffer = MultiPolygon([clipped_yellow_buffer_geom])
        else:
            yellow_dissolved_buffer = clipped_yellow_buffer_geom
    else:
        # If there is no intersection, use the original green dissolved buffer
        yellow_dissolved_buffer = yellow_dissolved_buffer
        dissolved_yellow_buffer_wkt = yellow_dissolved_buffer.wkt

    # Check if the green dissolved buffer intersects with the yellow dissolved buffer
    if green_dissolved_buffer_geom.intersects(yellow_dissolved_buffer_geom):
        # Clip the green dissolved buffer by the yellow dissolved buffer
        clipped_green_buffer_geom = green_dissolved_buffer_geom.difference(yellow_dissolved_buffer_geom)

        # If there are multiple polygons in the clipped result, create a MultiPolygon
        if clipped_green_buffer_geom.geom_type == 'Polygon':
            green_dissolved_buffer = MultiPolygon([clipped_green_buffer_geom])
        else:
            green_dissolved_buffer = clipped_green_buffer_geom
    else:
        # If there is no intersection, use the original green dissolved buffer
        green_dissolved_buffer = green_dissolved_buffer
        dissolved_green_buffer_wkt = green_dissolved_buffer.wkt

    # Inside the lst_classification function
    yellow_dissolved_buffer_wkt = yellow_dissolved_buffer.wkt
    green_dissolved_buffer_wkt = green_dissolved_buffer.wkt

    # Convert the yellow buffer to a GEOSGeometry object
    yellow_buffer_geometry = GEOSGeometry(yellow_dissolved_buffer_wkt, srid=4326)
    red_buffer_geometry = GEOSGeometry(red_dissolved_multipolygon_wkt, srid=4326)
    green_buffer_geometry = GEOSGeometry(green_dissolved_buffer_wkt, srid=4326)

    # # Create separate shapefiles for each buffer
    # create_shapefile(yellow_buffer_geometry, 'yellow_buffer.shp')
    # create_shapefile(red_buffer_geometry, 'red_buffer.shp')
    # create_shapefile(green_buffer_geometry, 'green_buffer.shp')

    # Query farms that fall within the yellow buffer
    farms_within_yellow_buffer = Farm.objects.filter(farm_boundary__within=yellow_buffer_geometry)
    farms_within_red_buffer = Farm.objects.filter(farm_boundary__within=red_buffer_geometry)
    farms_within_green_buffer = Farm.objects.filter(farm_boundary__within=green_buffer_geometry)

    # Get the farm IDs of farms that fall within the green buffer
    farm_ids_within_green_buffer = farms_within_green_buffer.values_list('id', flat=True)
    farm_owners_within_green_buffer = farms_within_green_buffer.values_list('owner', flat=True)
    unique_farm_owners_within_green_buffer = list(set(farm_owners_within_green_buffer))

    # Get the farm IDs of farms that fall within the yellow buffer
    farm_ids_within_yellow_buffer = farms_within_yellow_buffer.values_list('id', flat=True)
    farm_owners_within_yellow_buffer = farms_within_yellow_buffer.values_list('owner', flat=True)
    unique_farm_owners_within_yellow_buffer = list(set(farm_owners_within_yellow_buffer))

    if farms_within_red_buffer:
        # Get the farm IDs of farms that fall within the red buffer
        farm_ids_within_red_buffer = farms_within_red_buffer.values_list('id', flat=True)
        farm_owners_within_red_buffer = farms_within_red_buffer.values_list('owner', flat=True)
        unique_farm_owners_within_red_buffer = list(set(farm_owners_within_red_buffer))

        # Convert the farm IDs to a list of strings (UUIDs to strings)
        yellow_farm_ids_list = [str(farm_id) for farm_id in farm_ids_within_yellow_buffer]
        red_farm_ids_list = [str(farm_id) for farm_id in farm_ids_within_red_buffer]
        green_farm_ids_list = [str(farm_id) for farm_id in farm_ids_within_green_buffer]

        Any_Occurrence.objects.create(
            yellow_buffer=yellow_dissolved_buffer_wkt,
            red_buffer=red_dissolved_multipolygon_wkt,
            green_buffer=green_dissolved_buffer_wkt,
            metadata={
                'total_farmers_in_yellow_zone': len(unique_farm_owners_within_yellow_buffer),
                'farm_color': 'red',
                'yellow_length': len(farm_ids_within_yellow_buffer),
                'red_length': len(farm_ids_within_red_buffer),
                'farms_within_yellow': yellow_farm_ids_list,
                'farms_within_red': red_farm_ids_list,
                'occurence': True,
                'task_status': 'DONE'
            }
        )
        notifications_to_create = []

        farmer_ids = Planting_Information.objects.values_list('owner__id', flat=True).distinct()
        farmers_with_planting_info = list(farmer_ids)

        # Process green zone
        for farm_owner_uuid in unique_farm_owners_within_green_buffer:
            if farm_owner_uuid in farmers_with_planting_info:
                notification_message = 'You are in the green zone. This is a safe zone'
                notification = BroadCast_Notification(
                    channel=f"pemost_notification_{farm_owner_uuid.hex}",
                    message=notification_message,
                    model='notify',
                    label='zone notification',
                    message_to=User(id=farm_owner_uuid),
                    is_read=False,
                )
                notifications_to_create.append(notification)

        for farm_owner_uuid in unique_farm_owners_within_yellow_buffer:
            if farm_owner_uuid in farmers_with_planting_info:
                notification_message = 'You are in the yellow zone'
                notification = BroadCast_Notification(
                    channel=f"pemost_notification_{farm_owner_uuid.hex}",
                    message=notification_message,
                    model='notify',
                    label='zone notification',
                    message_to=User(id=farm_owner_uuid),
                    is_read=False,
                )
                notifications_to_create.append(notification)

        for farm_owner_uuid in unique_farm_owners_within_red_buffer:
            if farm_owner_uuid in farmers_with_planting_info:
                notification_message = 'You are in the red zone'
                notification = BroadCast_Notification(
                    channel=f"pemost_notification_{farm_owner_uuid.hex}",
                    message=notification_message,
                    model='notify',
                    label='zone notification',
                    message_to=User(id=farm_owner_uuid),
                    is_read=False,
                )

                notifications_to_create.append(notification)


        # Use bulk_create to create all the notifications at once
        BroadCast_Notification.objects.bulk_create(notifications_to_create)

        for notification in notifications_to_create:
            send_notification(BroadCast_Notification, notification, created=True)

        for farm_objectt in Farm.objects.all():
            all_interventions(farm_objectt)

    else:
        farms = Farm.objects.all()
        unioned_farm = farms.aggregate(Union('farm_boundary'))['farm_boundary__union']

        # Get the farm IDs of farms that fall within the red buffer
        farm_ids_within_red_buffer = farms_within_red_buffer.values_list('id', flat=True)
        farm_owners_within_red_buffer = farms_within_red_buffer.values_list('owner', flat=True)
        unique_farm_owners_within_red_buffer = list(set(farm_owners_within_red_buffer))

        # Convert the farm IDs to a list of strings (UUIDs to strings)
        yellow_farm_ids_list = [str(farm_id) for farm_id in farm_ids_within_yellow_buffer]
        red_farm_ids_list = [str(farm_id) for farm_id in farm_ids_within_red_buffer]

        Any_Occurrence.objects.create(
            yellow_buffer=yellow_dissolved_buffer_wkt,
            red_buffer=red_dissolved_multipolygon_wkt,
            green_buffer=unioned_farm,
            metadata={
                'total_farmers_in_yellow_zone': len(unique_farm_owners_within_yellow_buffer),
                'farm_color': 'green',
                'yellow_length': len(farm_ids_within_yellow_buffer),
                'red_length': len(farm_ids_within_red_buffer),
                'farms_within_yellow': yellow_farm_ids_list,
                'farms_within_red': red_farm_ids_list,
                'occurence': True,
                'task_status': 'DONE'
            }
        )

        notifications_to_create = []

        for farm in Farm.objects.all():
            farm_owner_uuid = farm.owner
            notification_message = 'You are in the green zone. This is a safe zone'

            notification = BroadCast_Notification(
                channel=f"pemost_notification_{farm_owner_uuid.id.hex}",
                message=notification_message,
                model='notify',
                label='zone notification',
                message_to=User(id=farm_owner_uuid.id),
                is_read=False,
            )

            notifications_to_create.append(notification)

        # Use bulk_create to create all the notifications at once
        BroadCast_Notification.objects.bulk_create(notifications_to_create)

        for notification in notifications_to_create:
            send_notification(BroadCast_Notification, notification, created=True)

        for farm_objectt in Farm.objects.all():
            all_green_interventions(farm_objectt)

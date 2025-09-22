import math

from django.conf import settings


class FarmUtils:
    def get_sqm_by_wgs84_polygon(self, geom):
        """
        Converts wgs 84 coordinates(lat/lon) to projected coordinates(meters) and get the acreage of a farm
        :param geom:
        :return: area
        """

        def get_utm_by_wgs_84(cent_lon, cent_lat):
            utm_zone_num = int(math.floor((cent_lon + 180) / 6) + 1)
            utm_zone_hemi = 6 if cent_lat >= 0 else 7
            utm_epsg = 32000 + utm_zone_hemi * 100 + utm_zone_num
            return utm_epsg

        lon = geom.centroid.x
        lat = geom.centroid.y
        epsg_code = get_utm_by_wgs_84(lon, lat)

        transformed_geom = geom.transform(epsg_code, clone=True)
        area = transformed_geom.area * settings.ACERAGE_CONVERT
        return area

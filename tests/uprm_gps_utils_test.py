from os import system
system("pip install .")

import unittest
import utm

from uprm_gps_utils import *


class TestLocationWrapper(unittest.TestCase):
    def test_utm_to_gps(self):
        lat, lon = 18, -66
        easting, northing, zone_number, zone_letter = utm.from_latlon(lat, lon)
        location = Location.from_utm(easting, northing, zone_number, zone_letter)
        self.assertAlmostEqual(lat, location.lat, places=5)
        self.assertAlmostEqual(lon, location.lon, places=5)

    def test_gps_to_utm(self):
        easting, northing, zone_number, zone_letter = 817705.2427086288, 1992756.9842168803, 19, "Q"
        lat, lon = utm.to_latlon(easting, northing, zone_number, zone_letter)
        location = Location.from_gps(lat, lon)
        self.assertAlmostEqual(easting, location.easting, places=1)
        self.assertAlmostEqual(northing, location.northing, places=1)
        self.assertEqual(zone_number, location.zone_number)
        self.assertEqual(zone_letter, location.zone_letter)

    def test_translate(self):
        location = Location.from_utm(100000, 100000, 19, "Q")
        self.assertEqual(round(distance_between_locations(location, location.translate(5, 0)), 1), 5)
        self.assertEqual(round(distance_between_locations(location, location.translate(0, 5)), 1), 5)
        self.assertEqual(round(distance_between_locations(location, location.translate(100, 0)), 0), 100)
        self.assertEqual(round(distance_between_locations(location, location.translate(0, 100)), 0), 100)


    def test_rotate_45_deg(self):
        location = Location.from_utm(100000, 200000, 19, "Q")
        origin = Location.from_utm(100000, 100000, 19, "Q")
        rotated_location = location.rotate(pivot=origin, angle_cw_deg=45)
        expected = Location.from_utm(170710.67811865476, 170710.67811865476, 19, "Q")
        self.assertAlmostEqual(rotated_location.easting, expected.easting, places=5)
        self.assertAlmostEqual(rotated_location.northing, expected.northing, places=5)

    def test_rotate_90_deg(self):
        location = Location.from_utm(100000, 200000, 19, "Q")
        origin = Location.from_utm(100000, 100000, 19, "Q")
        rotated_location = location.rotate(pivot=origin, angle_cw_deg=90)
        expected = Location.from_utm(200000, 100000, 19, "Q")
        self.assertEqual(rotated_location.easting, expected.easting)
        self.assertEqual(rotated_location.northing, expected.northing)

    def test_rotate_minus_90_deg(self):
        location = Location.from_utm(500000, 600000, 19, "Q")
        origin = Location.from_utm(500000, 500000, 19, "Q")
        rotated_location = location.rotate(pivot=origin, angle_cw_deg=-90)
        expected = Location.from_utm(400000, 500000, 19, "Q")
        self.assertEqual(rotated_location.easting, expected.easting)
        self.assertEqual(rotated_location.northing, expected.northing)

    def test_rotate_0_deg(self):
        location = Location.from_utm(500000, 600000, 19, "Q")
        origin = Location.from_utm(500000, 500000, 19, "Q")
        rotated_location = location.rotate(pivot=origin, angle_cw_deg=0)
        expected = Location.from_utm(500000, 600000, 19, "Q")
        self.assertEqual(rotated_location.easting, expected.easting)
        self.assertEqual(rotated_location.northing, expected.northing)


class TestNormalizeAngle(unittest.TestCase):
    def test_angles_from_0_to_360(self):
        self.assertEqual(normalize_angle(0), 0)
        self.assertEqual(normalize_angle(90), 90)
        self.assertEqual(normalize_angle(180), 180)
        self.assertEqual(normalize_angle(270), 270)
        self.assertEqual(normalize_angle(360), 0)

    def test_angles_over_360(self):
        self.assertEqual(normalize_angle(540), 180)
        self.assertEqual(normalize_angle(720), 0)
        
    def test_negative_angles(self):
        self.assertEqual(normalize_angle(-90), 270)
        self.assertEqual(normalize_angle(-180), 180)
        self.assertEqual(normalize_angle(-270), 90)
        self.assertEqual(normalize_angle(-360), 0)


class TestRelativeToCardinalAngle(unittest.TestCase):
    def test_facing_north(self):
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=90, yaw=0), 90)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=180, yaw=0,), 180)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=270, yaw=0), 270)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=360, yaw=0), 0)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=0, yaw=0), 0)

    def test_facing_west(self):
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=90, yaw=90), 180)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=180, yaw=90), 270)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=270, yaw=90), 0)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=360, yaw=90), 90)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=0, yaw=90), 90)

    def test_facing_south(self):
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=90, yaw=180), 270)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=180, yaw=180), 0)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=270, yaw=180), 90)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=360, yaw=180), 180)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=0, yaw=180), 180)
        
    def test_facing_east(self):
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=90, yaw=270), 0)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=180, yaw=270), 90)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=270, yaw=270), 180)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=360, yaw=270), 270)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=0, yaw=270), 270)

    def test_facing_26_deg_west_of_north(self):
        # these were manually computed
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=122, yaw=26), 148)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=64, yaw=26), 90)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=90, yaw=26), 116)

    def test_negative_inputs_facing_north(self):
        # negative angle inputs; no yaw
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=-90, yaw=0), 270)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=-180, yaw=0), 180)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=-270, yaw=0), 90)
        self.assertEqual(relative_angle_to_cardinal_angle(angle_relative_to_vehicle=-360, yaw=0), 0)


class TestRelativeRadialToGlobalCoordinates(unittest.TestCase):
    """
    Test cases were validated with: https://www.geoplaner.com
    P.S. this is the most powerful UTM/GPS calculator overall
    """
    LAT = -35.363262
    LON = 149.165337
    DISTANCE = 100

    def _call_with_angle(self, angle: float):
        """
        Call radial_to_gps() with the given angle.
        """
        return relative_radial_to_global_coordinates(Location.from_gps(self.LAT, self.LON), distance_of_object_meters=self.DISTANCE, cardinal_angle_of_object_degrees=angle)
    
    def _check_over_under_360(self, angle: float, expected: Location):
        """
        Call _call_with_angle with the given angle, as well as the ±360º.
        """
        for a in [angle-360, angle, angle+360]:
            obtained = self._call_with_angle(a)
            self.assertEqual(obtained.lat, expected.lat)
            self.assertEqual(obtained.lon, expected.lon)

    def test_0_degrees(self):
        self._check_over_under_360(angle=0, expected=Location.from_gps(-35.36236095328778, 149.16531293015828))

    def test_45_degrees(self):
        self._check_over_under_360(angle=45, expected=Location.from_gps(-35.36261091840879, 149.16609776925307))

    def test_90_degrees(self):
        self._check_over_under_360(angle=90, expected=Location.from_gps(-35.36324227492797, 149.16643696887624))

    def test_135_degrees(self):
        self._check_over_under_360(angle=135, expected=Location.from_gps(-35.36388518670459, 149.16613182261483))

    def test_180_degrees(self):
        self._check_over_under_360(angle=180, expected=Location.from_gps(-35.36416304171753, 149.16536107162474))

    def test_225_degrees(self):
        self._check_over_under_360(angle=225, expected=Location.from_gps(-35.363913072322944, 149.16457621925733))

    def test_270_degrees(self):
        self._check_over_under_360(angle=270, expected=Location.from_gps(-35.36328171022405, 149.1642370307703))

    def test_315_degrees(self):
        self._check_over_under_360(angle=315, expected=Location.from_gps(-35.362638802721015, 149.16454219030433))


class TestDistanceBetweenLocations(unittest.TestCase):
    """
    Test cases validated with: https://www.omnicalculator.com/other/latitude-longitude-distance
    """
    def test_no_distance(self):
        self.assertEqual(round(distance_between_locations(Location.from_gps(0, 0), Location.from_gps(0, 0))), 0)
        self.assertEqual(round(distance_between_locations(Location.from_gps(80, 80), Location.from_gps(80, 80))), 0)

    def test_one_decimal_degree(self):
        self.assertEqual(round(distance_between_locations(Location.from_gps(1, 0), Location.from_gps(0, 0))), 111195)
        self.assertEqual(round(distance_between_locations(Location.from_gps(0, 1), Location.from_gps(0, 0))), 111195)
        self.assertEqual(round(distance_between_locations(Location.from_gps(0, 0), Location.from_gps(1, 0))), 111195)
        self.assertEqual(round(distance_between_locations(Location.from_gps(0, 0), Location.from_gps(0, 1))), 111195)

    def test_one_negative_decimal_degree(self):
        self.assertEqual(round(distance_between_locations(Location.from_gps(-1, 0), Location.from_gps(0, 0))), 111195)
        self.assertEqual(round(distance_between_locations(Location.from_gps(0, -1), Location.from_gps(0, 0))), 111195)
        self.assertEqual(round(distance_between_locations(Location.from_gps(0, 0), Location.from_gps(-1, 0))), 111195)
        self.assertEqual(round(distance_between_locations(Location.from_gps(0, 0), Location.from_gps(0, -1))), 111195)

    def test_short_distances(self):
        self.assertEqual(round(distance_between_locations(Location.from_gps(2, 2), Location.from_gps(2.00001, 2)), 2), 1.11)
        self.assertEqual(round(distance_between_locations(Location.from_gps(2, 2), Location.from_gps(2.0000456, 2)), 2), 5.07)

    def test_large_distances(self):
        self.assertEqual(round(distance_between_locations(Location.from_gps(24.27609, 54.98268), Location.from_gps(78.20945, 63.23442))), 6012302)
        self.assertEqual(round(distance_between_locations(Location.from_gps(-79.09289, 12.121234), Location.from_gps(83.293834, -61.273658))), 18422078)
        self.assertEqual(round(distance_between_locations(Location.from_gps(-30.72834, -18.263819), Location.from_gps(-43.325612, -24.198304))), 1495501)


if __name__ == "__main__":
    unittest.main()
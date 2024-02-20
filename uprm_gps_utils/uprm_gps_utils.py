from math import asin, atan2, cos, degrees, radians, sin, sqrt
import utm


class Location:
    """
    Attributes:
        lat (float): latitude in decimal degrees
        lon (float): longitude in decimal degrees
        easting (float): easting in meters
        northing (float): northing in meters
        zone_number (int): the utm zone number
        zone_letter (str): the utm zone letter
    """
    def __init__(self):
        """
        WARNING: Do not use the constructor externally. Use the factory class methods `from_gps` and `from_utm`.
        """
        self.lat = None
        self.lon = None
        self.easting = None
        self.northing = None
        self.zone_number = None
        self.zone_letter = None

    def translate(self, dx_meters: float, dy_meters: float):
        """
        Simple linear translation of the coordinate.

        Parameters:
            dx_meters (float): The west to east delta.
            dy_meters (float): The south to north delta.

        Return a `Location` with the given deltas given this location.
        """
        return Location.from_utm(easting=self.easting+dx_meters,
                                 northing=self.northing+dy_meters,
                                 zone_number=self.zone_number,
                                 zone_letter=self.zone_letter)
    
    def rotate(self, pivot, angle_cw_deg: float):
        """
        Perrms a rotation in UTM space about the given pivot.

        This function is based on: https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python/34374437#34374437

        Parameters:
            pivot (Location): The point to rotate about.
            angle_cw_deg (float): The angle in degrees to rotate clockwise. Use a negative number for counter-clockwise rotation.

        Return a `Location` rotated around the given pivot.
        """
        angle_rad = radians(-angle_cw_deg) # Flips the angle to make rotatrion clockwise by default.

        sin_angle = sin(angle_rad)
        cos_angle = cos(angle_rad)

        delta_easting = self.easting - pivot.easting
        delta_norhting = self.northing - pivot.northing

        result_easting = pivot.easting + cos_angle * delta_easting - sin_angle * delta_norhting
        result_northing = pivot.northing + sin_angle * delta_easting + cos_angle * delta_norhting

        return Location.from_utm(easting=result_easting,
                                 northing=result_northing,
                                 zone_number=self.zone_number,
                                 zone_letter=self.zone_letter)
    
    @classmethod
    def from_gps(cls, lat: float, lon: float):
        """
        Returned a `Location` from the given GPS coordinates.
        """
        loc = cls()
        loc.lat, loc.lon = lat, lon
        loc.easting, loc.northing, loc.zone_number, loc.zone_letter = utm.from_latlon(lat, lon)
        return loc 

    @classmethod
    def from_utm(cls, easting: float, northing: float, zone_number: int, zone_letter: str):
        """
        Returned a `Location` from the given UTM coordinates.
        """
        loc = cls()
        loc.easting, loc.northing, loc.zone_number, loc.zone_letter = easting, northing, zone_number, zone_letter
        loc.lat, loc.lon = utm.to_latlon(easting, northing, zone_number, zone_letter)
        return loc
    
    def __str__(self) -> str:
        string = f"GPS(lat: {self.lat}, lon: {self.lon}) | "
        string += f"UTM(east: {self.easting}, north: {self.northing}, zone_num: {self.zone_number}, zone_let: {self.zone_letter})"
        return string
    

class Attitude:
    def __init__(self):
        """
        WARNING: Do not use the constructor externally. Use the factory class methods `from_deg` and `from_rad`.
        """
        self.yaw_deg = None
        self.roll_deg = None
        self.pitch_deg = None
        self.yaw_rad = None
        self.roll_rad = None
        self.pitch_rad = None

    @classmethod
    def from_deg(cls, yaw: float=0, roll: float=0, pitch: float=0):
        att = cls()
        att.yaw_deg = yaw
        att.roll_deg = roll
        att.pitch_deg = pitch
        att.yaw_rad = radians(yaw)
        att.roll_rad = radians(roll)
        att.pitch_rad = radians(pitch)
        return att

    @classmethod
    def from_rad(cls, yaw: float=0, roll: float=0, pitch: float=0):
        att = cls()
        att.yaw_deg = degrees(yaw)
        att.roll_deg = degrees(roll)
        att.pitch_deg = degrees(pitch)
        att.yaw_rad = yaw
        att.roll_rad = roll
        att.pitch_rad = pitch
        return att
    
    def __str__(self) -> str:
        return f"YAW({self.yaw_deg}º) | ROLL({self.roll_deg}º) | PITCH({self.pitch_deg}º)"
   

def normalize_angle(angle) -> float:
    """
    Will normalize any angle given to be within the [0º,360º) range.
    Here are some examples:
        365º -> 5º
        270º -> 270º
        -45º -> 315º
    """
    return angle % 360


def relative_angle_to_cardinal_angle(angle_relative_to_vehicle: float, yaw: float, rel_north=0) -> float:
    """
    Given the yaw of the vehicle and the angle of an object,
    calculates the object's angle to the vehicle with respect to cardinal directions.
    Assumes that global NWSE are at 0º, 90º, 180º, and 270º respectively.

    If the vehicle's relative north is 90º, that means it's right side is at 0º and its left side is at 180º.
    If an object is at 100º with respect to the aforementioned vehicle, then it is 10º left of the boat.

    The formula used for calculating is: global = ((angle_relative_to_vehicle - rel_north) + yaw - 360) % 360

    All angles are in degrees.

    Parameters:
        angle_relative_to_boat (float): The relative angle of the object with respect to the vehicle.
        yaw (float): The angle of the vehicle's north with respect to global north.
        rel_north (float): The relative angle that corresponds to the vehicle's front.
    
    Returns (float): The converted angle, in the range [0, 360)
    """
    return normalize_angle((angle_relative_to_vehicle - rel_north) + yaw)


def relative_radial_to_global_coordinates(location: Location, distance_of_object_meters: float, cardinal_angle_of_object_degrees: float) -> Location:
    """
    Given an object's distance to the vehicle and angle with respect to cardinal directions,
    computes the object's GPS coordinates.

    WARNING:
        This function is untested for cases where there is a UTM zone transition.
        However, for our purposes that is extremely unlikely.

    WARNING:
        This function likely fails in areas where the assumption that longitude
        decreases from east to west is broken, like the international dateline on
        the pacific ocean or when the assumption that latitude decreases from north to south
        is broken, like at the south pole.
        However, these scenarios are extremely unlikely.

    UTM zones can be found here: https://www.dmap.co.uk/utmworld.htm
        THe UTM zone for for most of Florida, USA is: 17R
        The UTM zone for Puerto Rico center/west is: 19Q
        The UTM zone for Puerto Rico far east is: 20Q

    In cardinal coordinates, North is 0º and angles sweep clockwise.

    Parameters: 
        location (Location): The location of the vehicle.
        disdistance_of_object_meters (float): Distance between the object and vehicle in meters.
        cardinal_angle_of_object_degrees (float): Object's angle with respect to cardinal coordinates.

    Returns (Location): The location coordinates of the object.
    """

    # vertical and horizontal displacement in meters
    delta_easting = distance_of_object_meters * sin(radians(cardinal_angle_of_object_degrees))
    delta_northing = distance_of_object_meters * cos(radians(cardinal_angle_of_object_degrees))

    # calculate easting and northing (UTM coords) of object
    object_easting = location.easting + delta_easting
    object_northing = location.northing + delta_northing

    return Location.from_utm(object_easting, object_northing, location.zone_number, location.zone_letter) 


def distance_between_locations(locationA: Location, locationB: Location) -> float:
    """
    Compute the distance between two GPS coordinates.
    This function is accurate to the centimeter.

    Source: https://www.geeksforgeeks.org/program-distance-two-points-earth/
    """
    lon1 = radians(locationA.lon)
    lon2 = radians(locationB.lon)
    lat1 = radians(locationA.lat)
    lat2 = radians(locationB.lat)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
      
    # calculate the result
    return (c * r) * 1000 # multiplied by 1000 to obtain meters
# UPRM GPS Utils

[![](https://github.com/Roboboat-Mayaguez/uprm_gps_utils/actions/workflows/python-package-3.10.yml/badge.svg)](https://github.com/Roboboat-Mayaguez/uprm_gps_utils/actions/workflows/python-package-3.10.yml)

## Installation
To install this package, run the following command within your desired virtual environment:
```shellssss
pip install git+https://github.com/Roboboat-Mayaguez/uprm_gps_utils.git@main
```
Confirm that the package has installed:
```shell
pip list | grep uprm
```

Now you're ready to import!
```python
from uprm_gps_utils import *
```

## Guide

#### The `Location` Class:
```python
from uprm_gps_utils import Location

# Make a location with GPS coordinates
location = Location.from_gps(lat=18.211042912960064, lon=-67.14093251407316)

# Make a location with UTM coordinates
location = Location.from_utm(easting=696598.2637150488,
                             northing=2014531.789185768,
                             zone_number=19,
                             zone_letter="Q")
```

#### Translations and Rotations
```python
from uprm_gps_utils import Location

location = Location.from_gps(lat=18.211042912960064, lon=-67.14093251407316)
vehicle_yaw = 75

# Translate a location 10 meters east and 5 meters north
translated_location = location.translate(10, 5)

# Translate a location 10 meters right and 5 meters forward
translated_location = location.translate(10, 5).rotate(pivot=location, angle_cw_deg=vehicle_yaw)

# Rotate a point about another point
rotated_location = location.rotate(translated_location, 60)
```

#### Getting the Location of Other Objects and Generating Waypoint
```python
from uprm_gps_utils import Location, relative_angle_to_cardinal_angle, relative_radial_to_global_coordinates

vehicle_location = Location.from_gps(lat=18.211042912960064, lon=-67.14093251407316)
vehicle_yaw = 75
object_distance_meters = 5
object_relative_angle = 25

# Transform the relative angle to a cardinal angle
object_cardinal_angle = relative_angle_to_cardinal_angle(object_relative_angle, vehicle_yaw)

# Get the location of the object.
object_location = relative_radial_to_global_coordinates(vehicle_location, object_distance_meters, object_cardinal_angle)

# Finally, we can generate waypoints around an object
waypoint_5m_right = object_location.translate(0, 5).rotate(object_location, vehicle_yaw)
waypoint_5m_back = object_location.translate(5, 0).rotate(object_location, vehicle_yaw)
waypoint_5m_left = object_location.translate(0, -5).rotate(object_location, vehicle_yaw)
waypoint_5m_front = object_location.translate(-5, 0).rotate(object_location, vehicle_yaw)
```
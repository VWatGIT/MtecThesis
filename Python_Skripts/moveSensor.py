import numpy as np
from pypylon import pylon
import cv2


def getSensorPos(marker_rvecs, marker_tvecs):

    sensor_rotation = marker_rvecs # + Rotation Matrix
    sensor_position = marker_tvecs # + Translation Matrix 

    return sensor_rotation, sensor_position

def getProbePos(marker_rvecs, marker_tvecs):

    probe_rotation = marker_rvecs # + Rotation Matrix
    probe_position = marker_tvecs # + Translation Matrix 

    return probe_rotation, probe_position

def determineMovement(sensor_rvecs, sensor_tvecs,probe_rvecs, probe_tvecs):
    # move in x, then y, then z direction




    return 0

# move Hexapod function
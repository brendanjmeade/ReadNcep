"""
Based on: http://schubert.atmos.colostate.edu/~cslocum/netcdf_example.html
"""
import glob
import pickle
import numpy as np
from netCDF4 import Dataset, num2date
import matplotlib.pyplot as plt


def get_nc_file_contents(local_file_name, local_field_name):
    """Read and return content from a single .nc file
       for local_field_name == 'pres' the units are Pascals
       For local_field_name == 'pr_wtr' the units are ???
    """
    nc_fid = Dataset(local_file_name, "r")
    lats = nc_fid.variables["lat"][:]
    lons = nc_fid.variables["lon"][:]
    time = nc_fid.variables["time"]  # Hours since 1800...seriously???
    time = num2date(time[:], time.units)
    local_field = nc_fid.variables[local_field_name][:]
    return lons, lats, time, local_field


def plot_field(local_frame, lons, lats):
    """Basic field visualization"""
    plt.figure()
    plt.imshow(
        local_frame,
        interpolation=None,
        extent=[min(lons), max(lons), min(lats), max(lats)],
    )
    plt.show(block=False)


def convert_and_save(ncep_data):
    """Convert all lements of ncep_data to numpy arrays and save as .pkl"""
    for key in ncep_data:
        ncep_data[key] = np.asarray(ncep_data[key])

    pickle_file = open("ncep_data.pkl", "wb")
    pickle.dump(ncep_data, pickle_file)
    pickle_file.close()
    return


def calc_corner_coordinates(ncep_data):
    """Calculate the four cornders of each grid cell"""
    offset = 2.5
    ncep_data["corner_lon_lower_left"] = ncep_data["lon_mat"]
    ncep_data["corner_lon_lower_right"] = ncep_data["lon_mat"] + offset
    ncep_data["corner_lon_upper_right"] = ncep_data["lon_mat"] + offset
    ncep_data["corner_lon_upper_left"] = ncep_data["lon_mat"]
    ncep_data["corner_lat_lower_left"] = ncep_data["lat_mat"]
    ncep_data["corner_lat_lower_right"] = ncep_data["lat_mat"]
    ncep_data["corner_lat_upper_right"] = ncep_data["lat_mat"] + offset
    ncep_data["corner_lat_upper_left"] = ncep_data["lat_mat"] + offset
    return ncep_data


def main():
    """Main function for reading and processing .nc files"""
    nc_file_types = ["pres.sfc.*.nc", "pr_wtr.eatm.*.nc", "hgt.sfc.nc", "land.nc"]
    field_names = ["pres", "pr_wtr", "hgt", "land"]
    field_labels = ["pressure", "precipitation", "elevation", "land"]

    ncep_data = dict()
    ncep_data["date_time"] = list()
    for field_label in field_labels:
        ncep_data[field_label] = list()

    for file_type, name, label in zip(nc_file_types, field_names, field_labels):
        for file in sorted(glob.glob(file_type)):
            print("Working on: " + file)
            lons, lats, date_time, field = get_nc_file_contents(file, name)
            for i in range(field.shape[0]):
                ncep_data[label].append(field[i, :, :])
                # An awkward way to not double count time
                if file_type == nc_file_types[0]:
                    ncep_data["date_time"].append(date_time[i])

    ncep_data["lon_mat"], ncep_data["lat_mat"] = np.meshgrid(lons, lats)
    ncep_data = calc_corner_coordinates(ncep_data)
    convert_and_save(ncep_data)


if __name__ == "__main__":
    main()

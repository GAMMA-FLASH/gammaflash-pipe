import h5py
import tables


# Method to read a file in hdf5, it prints their first level keys and values
# There are other many examples where are illustrated specific key or value get methods
def read(filepath):
    with h5py.File(filepath, "r") as f:

        # Print all root level object names (aka keys)
        # these can be group or dataset names
        print("Keys: %s" % f.keys())

        # get first object name/key; may or may NOT be a group
        a_group_key = list(f.keys())[0]

        # get the object type for a_group_key: usually group or dataset
        print(type(f[a_group_key]))

        # If a_group_key is a group name,
        # this gets the object names in the group and returns as a list
        data = list(f[a_group_key])

        # If a_group_key is a dataset name,
        # this gets the dataset values and returns as a list
        data = list(f[a_group_key])
        # preferred methods to get dataset values:
        ds_obj = f[a_group_key]  # returns as a h5py dataset object
        ds_arr = f[a_group_key][()]  # returns as a numpy array

        # Print all values associated to top level keys
        for key in f.keys():
            print("Key: ", key)
            for elem in f[key]:
                print("Associated element: ", elem)
        print(f[key])


# Method to create a new h5py file
# The key is named "dataset_name" and the data is generated randomly
def write(filename):
    # Create random data
    import numpy as np
    data_matrix = np.random.uniform(-1, 1, size=(10, 3))

    # Write data to HDF5
    with h5py.File(filename, "w") as data_file:
        data_file.create_dataset("dataset_name", data=data_matrix)


# Examples
"""write("filehdf5test.hdf5")
read("filehdf5test.hdf5")"""

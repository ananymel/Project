
# This code has been partially created by ChatGPT
import os
import h5py
import numpy as np

def copy_8_channels_compound(in_path, out_path):
    """
    Reads the original HDF5, which presumably has
    dtype=[('emg_right', '<f4', (16,)), ('time', '<f8'), ('emg_left', '<f4', (16,))],
    and writes a new HDF5 at with only 8 channels  (which are taken as first 8 channels both for left and right)
    each for
    emg_right and emg_left, preserving the field order:
      ('emg_right', '<f4', (8,)), ('time', '<f8'), ('emg_left', '<f4', (8,))
    """
    with h5py.File(in_path, "r") as fin, h5py.File(out_path, "w") as fout:
        # Access the original compound dataset
        old_group = fin["emg2qwerty"]
        old_dset = old_group["timeseries"]
        num_samples = len(old_dset)  # e.g. T

        # Create a new compound dtype with the same field order as the original,
        # but only 8 channels for 'emg_right' and 'emg_left'
        new_dtype = np.dtype([
            ("emg_right", np.float32, (8,)),
            ("time",      np.float64),
            ("emg_left",  np.float32, (8,))
        ])

        # Create an empty NumPy array of that dtype to hold all rows
        new_data = np.empty(num_samples, dtype=new_dtype)

        # Loop over each row in the old dataset
        for i in range(num_samples):
            old_row = old_dset[i]

            # Copy only the first 8 channels from each
            new_data[i]["emg_right"] = old_row["emg_right"][:8]
            new_data[i]["time"]      = old_row["time"]
            new_data[i]["emg_left"]  = old_row["emg_left"][:8]

        # Create the new group and dataset
        new_group = fout.create_group("emg2qwerty")
        new_dset = new_group.create_dataset("timeseries", data=new_data)

        # Copy attributes (e.g. keystrokes, prompts, etc.)
        for k, v in old_group.attrs.items():
            new_group.attrs[k] = v

        print(f"Created new 8-ch dataset at {out_path}")

def process_directory(input_dir, output_dir):
    """
    Loops through all .hdf5 files in `input_dir`, and for each,
    creates a new .hdf5 with 8 channels in `output_dir`.
    Preserves field ordering: (emg_right, time, emg_left).
    """
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        if fname.endswith(".hdf5"):
            in_path = os.path.join(input_dir, fname)
            out_path = os.path.join(output_dir, fname)
            copy_8_channels_compound(in_path, out_path)

if __name__ == "__main__":
    input_dir  = r"C:\Users\melis\Downloads\raw_data\raw_data"
    output_dir = r"C:\Users\melis\Downloads\raw_data\8_channels_data"

    process_directory(input_dir, output_dir)

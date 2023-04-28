import os
import glob
import gzip
import yaml
import shutil
import argparse
import numpy as np

from tqdm import tqdm
from astropy.io import fits


def process_download_data(source_dir, target_dir):
    """
    Extracts all gzip files and copies all fits files from source_dir to target_dir.
    """

    # Define a pattern to match gzip files
    gz_pattern = "*.gz"

    # Define a pattern to match fits files
    fits_pattern = "*.fits"

    # Create the target directory if it doesn't exist yet
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Loop through the source directory and extract each gzip file to the target directory
    for file_path in tqdm(glob.glob(os.path.join(source_dir, gz_pattern)),
                          desc="Extracting .gz files"):

        # Open the gzip file and extract its contents
        with gzip.open(file_path, "rb") as f_in:

            # Define the output file name by removing the ".gz" extension and adding the
            # target directory
            output_file_path = os.path.join(target_dir,
                                            os.path.splitext(os.path.basename(file_path))[0])

            # Open the output file and write the extracted contents
            if output_file_path.endswith(".fits"):
                with open(output_file_path, "wb") as f_out:
                    f_out.write(f_in.read())

    # Copy all the fits files to the target directory
    for file_path in tqdm(glob.glob(os.path.join(source_dir, fits_pattern)),
                          desc="Copying .fits files"):

        # Define the output file path by adding the target directory
        output_file_path = os.path.join(target_dir, os.path.basename(file_path))

        # Copy the file to the target directory
        shutil.copy(file_path, output_file_path)

    # Print a message indicating the extraction and copy is complete
    print("Extraction and copy complete!")


def save_fits_files_as_np(fits_files_dir, output_dir):
    """
    Reads all .fits files in a directory and saves them as .npy files in another directory. Records
    which files could not be read and which ones were successfully processed, and saves the lists
    to separate text files.

    :param fits_files_dir: Path to the directory containing .fits files
    :param output_dir: Path to the directory where output files will be saved
    """
    # Create dir/file paths
    save_directory = os.path.join(output_dir, "npy_files")
    good_filepath = os.path.join(output_dir, "good_files.txt")
    error_filepath = os.path.join(output_dir, "error_files.txt")

    # Create the save directory if it doesn't already exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Initialize lists to store the filenames of good and error files
    good_files = []
    error_files = []

    # Loop over all files in the directory
    for filename in tqdm(os.listdir(fits_files_dir), desc="Converting .fits to .npy"):
        if filename.endswith(".fits"):
            try:
                # Read the .fits file as a numpy array
                filepath = os.path.join(fits_files_dir, filename)
                data = fits.getdata(filepath)

                # Save the numpy array as a .npy file
                save_filename = os.path.splitext(filename)[0] + ".npy"
                save_filepath = os.path.join(save_directory, save_filename)
                np.save(save_filepath, data)

                # Append the filename to the good_files list
                good_files.append(filename)

            except:
                # If an error occurs, append the filename to the error_files list
                error_files.append(filename)
                continue

    # Save the list of good filenames to a text file
    if good_files:
        with open(good_filepath, "w") as f:
            f.write("\n".join(good_files))
        print(f"List of good files saved to {good_filepath}")
    else:
        print("No files were processed successfully")

    # Save the list of error filenames to a text file
    if error_files:
        with open(error_filepath, "w") as f:
            f.write("\n".join(error_files))
        print(f"List of error files saved to {error_filepath}")
    else:
        print("No errors occurred")

    # Print a message indicating the file converting is complete
    print("Numpy saving completes!")



if __name__ == "__main__":

    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', required=True, type=str, help="xxx.yaml")
    args = parser.parse_args()

    # Load config
    with open(args.config_file) as file:
        config = yaml.safe_load(file)

    config["tmp_dir"] = os.path.join(config["output_dir"], "tmp")

    # Execute the processer
    process_download_data(config["source_dir"], config["tmp_dir"])
    save_fits_files_as_np(config["tmp_dir"], config["output_dir"])

    # Remove the tmp folder
    shutil.rmtree(config["tmp_dir"])

    print("Done")

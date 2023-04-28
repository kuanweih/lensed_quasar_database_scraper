import os
import glob
import gzip
import yaml
import shutil
import argparse

from tqdm import tqdm


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




if __name__ == "__main__":

    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', required=True, type=str, help="xxx.yaml")
    args = parser.parse_args()

    # Load config
    with open(args.config_file) as file:
        config = yaml.safe_load(file)

    # Execute the processer
    process_download_data(config["source_dir"], config["target_dir"])

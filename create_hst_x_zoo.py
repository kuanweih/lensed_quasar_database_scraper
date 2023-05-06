import argparse
import os
import shutil
import yaml
import numpy as np

from tqdm import tqdm
from PIL import Image


def process_hst_images(config):
    """ Process HST cutout.npy images.

    Args:
        config (dict): config dict
    """
    dir_out = os.path.join(config["dir_output"], "hst")
    os.makedirs(dir_out)

    files = os.listdir(config["dir_hst"])
    for file in tqdm(files, desc="HST"):

        if not file.endswith("cutout.npy"):
            continue

        img = np.load(os.path.join(config["dir_hst"], file))
        img = normalize_pixels(img)
        img = np.repeat(img[:, :, np.newaxis], 3, axis=2)  # grayscale -> RGB
        img = Image.fromarray((img * 255).astype(np.uint8))
        img = img.resize((config["image_size"], config["image_size"]))
        img = normalize_pixels(np.array(img))

        np.save(os.path.join(dir_out, file), img)


def process_zoo_images(config):
    """ Process Galaxy Zoo .jpg images.

    Args:
        config (dict): config dict
    """
    dir_out = os.path.join(config["dir_output"], "zoo")
    os.makedirs(dir_out)

    files = os.listdir(config["dir_zoo"])
    for file in tqdm(files, desc="ZOO"):
        img = Image.open(os.path.join(config["dir_zoo"], file))
        img = img.resize((config["image_size"], config["image_size"]))
        img = np.array(img)
        img = normalize_pixels(img)

        np.save(os.path.join(dir_out, file.replace(".jpg", ".npy")), img)


def normalize_pixels(img):
    """ Normalize pixel values to be within [0, 1].
    Args:
        img (np.array): a image np.array
    """
    return (img - img.min()) / (img.max() - img.min())




if __name__ == "__main__":

    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', required=True, type=str, help="xxx.yaml")
    args = parser.parse_args()

    # Load config
    with open(args.config_file) as file:
        config = yaml.safe_load(file)

    # Create the output directory
    os.makedirs(config["dir_output"])

    # Process the images
    process_hst_images(config)
    process_zoo_images(config)

    # Copy the yaml file
    shutil.copy2(args.config_file, config["dir_output"])

    print(f"Done :) Output dataset at {config['dir_output']}")

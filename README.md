# lensed_quasar_database_scraper

To scrape and download the images, run
```
python  download.py  -c configs/download.yaml
```

To process the images, run
```
python  process.py  -c configs/process.yaml
```

To create a lensing classification dataset using HST and Galaxy Zoo (downloaded from [this link](https://www.kaggle.com/competitions/galaxy-zoo-the-galaxy-challenge/overview)), run
```
python create_hst_x_zoo.py -c configs/create_hst_x_zoo.yaml
```
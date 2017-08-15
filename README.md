# stock-display

A stock display platform showing both **real-time prices** and historical **candlestick and volume** charts of user-selected stocks 

 * Implemented a scalable streaming data processing platform using Apache Kafka, Apache Spark and Redis
 * Built front webpage and web server using Bootstrap and nodejs
 * Real-time data from [google finance API](https://pypi.python.org/pypi/googlefinance), historical data from [pandas-datareader](https://pandas-datareader.readthedocs.io/en/latest/)
 * Chart drawing using [d3.js](https://d3js.org/) and [highcharts](https://www.hhighcharts.com)
 
# Local setup guide

For easy distribution, this program runs on a docker machine. To set up the environment, first you need to install docker. Install guide can be found [here](https://docs.docker.com/docker-for-mac/install/)

After installing docker, setting up a docker machine (e.g. naming "stockdisplay")

```sh
docker-machine create --driver virtualbox --virtualbox-cpu-count 2 --virtualbox-memory 2048 stockdisplay
```

Then run setup script

```sh
./local-setup.sh stockdisplay
```


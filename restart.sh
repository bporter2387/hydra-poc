#!/bin/bash

docker-compose down
sudo rm -rf docker_data
docker-compose up -d
docker logs -f hydrapoc_hydra_1

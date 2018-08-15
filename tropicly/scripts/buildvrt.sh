#!/bin/bash

IFS='.'

templates=("/home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/cover_americas.tif"
           "/home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/cover_africa.tif"
           "/home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/cover_asia.tif")

for file in /home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/*.txt
    do

    read -a arr <<< "$file"

    if [[ ${arr[0]} =~ .*americas ]]
    then
        template=${templates[0]}

    elif [[ ${arr[0]} =~ .*africa ]]
    then

        template=${templates[1]}

    else
        template=${templates[2]}
    fi

    res=$(gdalinfo -json "$template" | jq -r '. | .geoTransform[1]')
    lower=$(gdalinfo -json "$template" | jq -r '. | .cornerCoordinates.lowerLeft')
    upper=$(gdalinfo -json "$template" | jq -r '. | .cornerCoordinates.upperRight')

    gdalbuildvrt -input_file_list "$file" -tr "$res" "$res" "${arr[0]}.vrt"

done
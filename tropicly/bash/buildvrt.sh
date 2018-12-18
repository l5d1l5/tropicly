#!/bin/bash
# requires gdal and jq

IFS='.'

templates=("/home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/glob/cover_americas.tif"
           "/home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/glob/cover_africa.tif"
           "/home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/glob/cover_asia.tif")

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

    # jq is a command line json parser
    res=$(gdalinfo -json "$template" | jq -r '. | .geoTransform[1]')
    xmin=$(gdalinfo -json "$template" | jq -r '. | .cornerCoordinates.lowerLeft[0]')
    ymin=$(gdalinfo -json "$template" | jq -r '. | .cornerCoordinates.lowerLeft[1]')
    xmax=$(gdalinfo -json "$template" | jq -r '. | .cornerCoordinates.upperRight[0]')
    ymax=$(gdalinfo -json "$template" | jq -r '. | .cornerCoordinates.upperRight[1]')

    gdalbuildvrt -input_file_list "$file" -tr "$res" "$res" -te "$xmin" "$ymin" "$xmax" "$ymax" "${arr[0]}.vrt"

done
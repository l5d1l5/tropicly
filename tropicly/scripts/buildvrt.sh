#!/bin/bash

IFS='.'

# resolutions americas, africa, asia
resolutions=(0.000274052 0.000270417 0.000282743)

for file in /home/tobi/Documents/Master/code/python/Master/data/proc/agg/tif/*.txt
    do

    read -a arr <<< "$file"

    if [[ ${arr[0]} =~ .*americas ]]
    then
        res=${resolutions[0]}

    elif [[ ${arr[0]} =~ .*africa ]]
    then

        res=${resolutions[1]}

    else
        res=${resolutions[2]}
    fi

    gdalbuildvrt -input_file_list "$file" -tr "$res" "$res" "${arr[0]}.vrt"

done
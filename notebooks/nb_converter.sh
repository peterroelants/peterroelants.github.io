#!/bin/bash

# Convert ipython notebooks into stripped down html with the
#  Jekyll front matter.
# Example command:
#  sh nb_converter.sh neuralnets/Simple_neural_network_part01.ipynb "Simple Neural Network Part 1" "2015-05-18"

# Check if the file is passed as argument
if [ "$1" == "" ]; then
    echo "notebook file expected as input"
    exit 2
fi

# Check if a title for the front matter is passed as an argument
if [ "$2" == "" ]; then
    echo "You should provide a title as second argument"
    exit 2
fi

# Check if a date for the filename is passed as an argument
if [ "$3" == "" ]; then
    echo "You should provide a data in YYYY-MM-DD format as third argument"
    exit 2
fi

# Convert to stripped down html
ipython nbconvert --to html --template basic $1

# Get the html filename
result_html_file_name="${1/.ipynb/.html}"
filename="${result_html_file_name##*/}"

# Add the front matter before the html
#echo "---\nlayout: default\ntitle: $2\n---\n\n$(cat $filename)" > $filename
#sed '1 i\ test' "$filename"
sed "1s/^/--- \\
layout: post\\
title: $2\\
---\\
/" "$filename" > temp
mv temp $filename

# Move file to the _post directory
mv $filename "../_posts/$3-$filename"
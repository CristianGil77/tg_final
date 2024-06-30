#!/bin/bash

while getopts b: flag
do
    case "${flag}" in
        b) blue_id=${OPTARG};;
    esac
done


echo -e "--start \n" | pulseaudio  

sleep 5

echo -e "trust $blue_id\n" | bluetoothctl

sleep 3
echo -e "connect $blue_id\n" | bluetoothctl

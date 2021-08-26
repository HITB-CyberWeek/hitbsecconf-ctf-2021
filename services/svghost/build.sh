#!/bin/bash

docker run --rm -v "$(pwd):/app" -w /app mcr.microsoft.com/dotnet/sdk:5.0 dotnet publish src/ -c release -o ./out
tar -zcf svghost.tar.gz --exclude="./src/bin" --exclude="./src/obj" --exclude="./src/data" --exclude="./src/settings" --exclude="./src/Properties" --exclude="./src/vs" --exclude="./src/idea" --exclude="*.user" --exclude="*.suo" ./src/

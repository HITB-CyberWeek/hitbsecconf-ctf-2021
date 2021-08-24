#!/bin/bash

docker run --rm -v $(pwd):/app -w /app mcr.microsoft.com/dotnet/sdk:5.0 dotnet publish src/ -c release -o ./out

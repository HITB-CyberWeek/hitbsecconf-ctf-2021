#!/bin/sh

chown svghost: /app/data /app/settings
chmod -R 755 /app /app/wwwroot
chmod 700 /app/data /app/settings

su svghost -s /bin/sh -c 'dotnet svghost.dll'

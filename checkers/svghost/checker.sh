#/bin/bash

cd `dirname $0`/src/bin/Release/net5.0/publish >/dev/null 2>&1
exec dotnet svghostchecker.dll "$@"

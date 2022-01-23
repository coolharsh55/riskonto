#!/usr/bin/env bash
#author: Harshvardhan J. Pandit
#title: convenience script for widoco

# path to widoco executable jar
WIDOCO=~/apps/widoco/widoco.jar

while getopts ":R" opt; do
    case "${opt}" in
        R)
            REWRITE_ALL=1
            ;;
        *)
            ;;
    esac
done


if [[ ! -f 'riskonto/index-en.html' ]] || [[ "$REWRITE_ALL" == 1 ]]; then
    echo "OPT: Rewrite All"
    java -jar "$WIDOCO" -ontFile ./riskonto.ttl -outFolder ./riskonto -getOntologyMetadata -uniteSections -webVowl -rewriteAll
else
    echo "OPT: CrossRef Only"
    java -jar "$WIDOCO" -ontFile ./riskonto.ttl -outFolder ./riskonto -getOntologyMetadata -uniteSections -webVowl -crossRef
fi;

cp ./riskonto/index-en.html ./riskonto/index.html

rm readme.md
rm ./riskonto/readme.md


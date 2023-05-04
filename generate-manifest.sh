#!/bin/sh

touch manifest.toml && echo "" > manifest.toml

for file in */fred.toml; do
    metadata=$(tomlq -t '.metadata' "$file")
    echo "[[metadata]]\n$metadata\n" >> manifest.toml
done

sed -i '' -e '1{/^$/d;}' manifest.toml
sed -i '' -e '${/^$/d;}' manifest.toml

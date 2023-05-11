#!/bin/sh

pip install tomlq

touch manifest.toml && echo "" > manifest.toml

echo "loop start"
for file in */fred.toml; do
    echo $file
    filename=${file%/fred.toml}
    metadata=$(tomlq -t '.metadata' "$file")
    echo "[[metadata]]\n$metadata\nslug = \"$filename\"\n" >> manifest.toml
done
echo "loop end"

sed -i '' -e '1{/^$/d;}' manifest.toml
sed -i '' -e '${/^$/d;}' manifest.toml

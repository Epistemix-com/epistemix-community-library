# epistemix-community-library

Repository for storing and sharing shared models from the Platform

## Manifest

The `generate-manifest.sh` file is executed when a commit is pushed to the `main` branch. This generates a file called `manifest.toml`, which is then stored in the `model-library-assets` S3 bucket and is used by the API. It is not stored in GitHub.

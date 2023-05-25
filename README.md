# epistemix-community-library

Repository for storing and sharing shared models from the Platform.

## Dockerfile

We include a Dockerfile to help with administrative tasks like dependency
management. To start the dev environment run

```shell
scripts/dev
```

## Updating dependencies

Abstract Python dependencies are specified in the file `requirements.in`. These
are the names of packages used in the Community Library tutorials without pinned
(`==`) version numbers. We use [pip-tools](https://github.com/jazzband/pip-tools)
to generate concrete dependencies (including specific versions of the
dependencies of our named dependencies) in `requirements.txt` from the abstract
`requirements.in` file. The process for adding a dependency is:

1. Add the name of the new dependency to `requirements.in`
2. From within the `dev` container run `scripts/update-requirements`
3. Commit changes to both `requirements.in` and `requirements.txt` to version
   control.

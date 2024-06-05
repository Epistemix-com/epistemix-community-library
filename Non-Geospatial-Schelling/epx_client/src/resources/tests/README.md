# FRED output sample data

Generated FRED run sample output for testing and associated scripts.

As sample output is on the order of 100 kb/ FRED version we propose to simply
check sample output into version control. Scripts should only need to be re-run
when adding FRED versions or changing included model outputs.

Generate output with e.g.

```shell
scripts/generate ~/Projects/FRED-data ~/Projects/FRED-library
```

substituting paths to FRED data and FRED library as appropriate on the host.

# backend


# Build
Since [Flatbuffers](https://google.github.io/flatbuffers/) are used in this project, `flatc` is required (currently v2.0.0).

Flatbuffers are built by issuing:

```
flatc --python -I ./flats -o ./spaceroombas/network/flats ./flats/*
```

This will generate the necessary python classes which ***ARE NOT*** committed to source control.
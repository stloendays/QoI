# Development execution compatibility smoke

Status: **PASS**

This is a provenance/engineering gate. It does not create or tune a scientific result.

| Material | Codec | Linf match | Bader match | Bytes exact | Scientific gate |
|---|---|---:|---:|---:|---:|
| mp-1009084 | ZFP | True | True | True | True |
| mp-1009084 | SZ3 | True | True | True | True |
| mp-1009084 | SPERR | True | True | True | True |
| nomad--O7C25L6mxPu | ZFP | True | True | True | True |
| nomad--O7C25L6mxPu | SZ3 | True | True | True | True |
| nomad--O7C25L6mxPu | SPERR | True | True | True | True |

Compressed-byte equality is retained as a deterministic-codec diagnostic but is not required for the scientific compatibility gate. Source identity, grid/atom invariants, realized Linf, the Bader fixed-domain self-check, and re-derived Bader response are required.

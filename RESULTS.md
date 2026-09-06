# RhoCodec Stage 0 results

Run date: 2026-09-01.  Interpreter
`D:\Research\CatalystForge\.venv\Scripts\python.exe`.  No new DFT calculation
was run and no paid API was used.

## Corpus

32 Materials Project charge densities, fetched anonymously from the public
`materialsproject-parsed` S3 bucket (CC BY 4.0) and stratified across the seven
crystal systems so that low-symmetry material is not under-represented, plus one
local CeO2 CHGCAR from the Rh-CeO2 archive.  Provenance, including source URL,
byte count and SHA-256 for every object, is in `data/mp/provenance.jsonl`.

The served data is lossless `float64` on VASP's native FFT grid with no MP-side
quantization, so it is a legitimate compression target.  Grid sizes run from
504,000 to 4.0 million points; total 398 MB as `float64`.

Command:

```bash
python scripts/fetch_mp_corpus.py --per-system 5 --out data/mp
```

## Result 1: the redundancy exists, and it is not a grouping artefact

Space-group symmetry folding on the local CeO2 CHGCAR (Fm-3m, 72^3 grid):

| Quantity | Value |
|---|---|
| symmetry operations, all commensurate with the grid | 192 |
| grid points | 373,248 |
| distinct orbits | 2,470 |
| fold factor | **151.1x** |
| within-orbit maximum spread | 1e-10 absolute, **7.0e-14 relative** |
| null control, random groups of the same count | **0.98 relative** |

The density obeys its space group to the precision at which the file is printed.
The null control separates from the true folding by ten orders of magnitude, so
the redundancy is real rather than an artefact of grouping a smooth field.
Across the 32-material corpus the median within-orbit spread is 9.05e-12 against
a control median of 9.86e-01, a median separation of 5.3e+10.

## Result 2: the obvious baseline is far too weak, and the honest one is strong

On the same CeO2 file:

| Codec | Bytes | Ratio | Lossless |
|---|---:|---:|---|
| original CHGCAR text | 13,643,340 | 1.0x | - |
| gzip -9 on the text | 1,744,185 | 7.8x | yes |
| xz on the text | 306,760 | 44.5x | yes |
| **zstd-19 on the raw float64 array** | **46,901** | **290.9x** | yes |
| symmetry-folded + zstd-19 | 18,640 | 732.0x | yes |

Gzip on the CHGCAR text - what practitioners actually do - reaches 7.8x, but
zstd on the float array reaches 291x on its own, because symmetry-equivalent
grid points hold bit-identical doubles and a long-range match finder recovers
them with no crystallography at all.  **Reporting a domain method against gzip
would have inflated the claim by roughly forty-fold.**  Against the honest
lossless baseline, folding is worth 2.52x, not 151x.

## Result 3: the domain prior loses to the generic predictor when used alone

Corpus-wide, at matched absolute tolerance expressed as a fraction of each
field's peak-to-peak range, against uniform quantization plus zstd-19:

| Error budget | Symmetry folding | First-order Lorenzo |
|---|---:|---:|
| 1e-5 | 1.96x (byte-weighted) | **4.38x** |
| 1e-4 | 2.03x | **9.33x** |
| 1e-3 | 2.32x | **40.84x** |

The Lorenzo predictor is the family SZ3 is built on.  Used as an alternative to
it, symmetry folding is beaten by a factor of 2 to 17.  Taken alone this reads
as a dead prior, and it is the point at which the previous project would have
kept tuning.

## Result 4: the two priors compose, and that is the contribution

Symmetry folding and Lorenzo prediction are not alternatives.  Sweep the grid in
storage order; if another point of the same orbit has already been decoded, copy
it at zero cost, otherwise encode a causal Lorenzo residual predicted from
already-decoded neighbours.  Because the orbit label is the smallest linear
index in the orbit, the encoded set is exactly the orbit representatives, so the
scheme needs no side information beyond the structure header.  Copies are exact,
so a prediction made from a copied neighbour is as good as one from an original.

Over the 32-material corpus:

| Error budget | float64 -> Lorenzo | float64 -> folded+Lorenzo | Symmetry gain **on top of** Lorenzo | Materials helped >= 1.3x | Compose efficiency |
|---|---:|---:|---:|---:|---:|
| 1e-5 | 39.6x | **92.4x** | **2.22x** | 84 % | 0.88 |
| 1e-4 | 160x | **460x** | **2.67x** | 88 % | 0.77 |
| 1e-3 | 1,248x | **3,711x** | **2.97x** | 91 % | 0.78 |

All figures byte-weighted.  Compose efficiency is the achieved gain divided by
the fold factor; it stays near 1 for small folds and falls to about 0.4 for the
largest, because sparse representatives are harder to predict from their
neighbours.

The control line matters as much as the result: **folding without Lorenzo scores
0.51x, 0.30x and 0.11x against Lorenzo alone.**  Anyone implementing the
symmetry prior on its own would have produced a method that loses to a
general-purpose compressor.  The contribution is the composition, not either
prior.

## Result 5: risk R1 measured

The pre-registered worry was that the symmetry payoff is anti-correlated with
the files that dominate storage, since slabs and relaxed low-symmetry structures
are near-P1 while high-symmetry crystals have small grids.

Measured correlation between `log(file size)` and `log(symmetry gain)` over the
corpus: **-0.19, -0.14, -0.14** at the three budgets.  The anti-correlation is
real but weak, and the byte-weighted and unweighted medians differ by under 5 %.
The stage is not disqualified by R1 on crystalline material.  It remains
untested on slabs and adsorbate series, which is where the effect should be
strongest and where the frozen external test will use the Rh-CeO2 archive.

Five of the 32 materials are genuinely P1 after validation and gain nothing.
Because folding degenerates to the identity there, the method is never worse
than the baseline, which is a structural guarantee rather than an empirical one.

## Result 6: adverse signal on the promolecule prior

Fitting per-element radial profiles by least squares on the CeO2 file (80
parameters, 960 bytes of side information) reduces the value range 12.0x, but
the residual does not encode better than a plain Lorenzo residual:

| Relative tolerance | Baseline | Lorenzo | Promolecule | Promolecule + Lorenzo |
|---|---:|---:|---:|---:|
| 1e-5 | 25,807 | **21,388** | 21,514 | 40,878 |
| 1e-4 | 19,707 | **8,417** | 15,375 | 30,839 |
| 1e-3 | 12,331 | **2,053** | 6,858 | 13,341 |

Subtracting a smooth atom-centred model removes dynamic range but destroys local
smoothness, which is what the Lorenzo predictor lives on, so the two anti-compose
rather than compose.  Under gate G0.c this prior is a candidate for removal; the
corpus-wide measurement has not yet been run.

## Two bugs found and fixed, both of which had understated the method

Recorded because they are the kind of error that silently produces a negative
result.

1. **Translation commensurability was tested far too strictly.**  A symmetry
   operation permutes the grid only when `D t` is integral, but `t` inherits the
   structure's numerical noise and multiplying by `N` amplifies it: an operation
   with `t = 0.9999989` on a 252-point axis misses an integer by 2.8e-4 and was
   discarded by a 1e-6 tolerance.  On one trigonal material this threw away 10
   of 12 operations.
2. **A fixed `symprec` cannot be chosen in advance.**  At `symprec = 1e-5`,
   mp-1112138 was reported as P1 with a fold factor of 1.0.  At 1e-3 it is
   Fm-3m, 48 operations, fold factor 44.6x, with a within-orbit spread of
   6.1e-6 - so the density genuinely obeys those operations.  The symmetry gain
   for that material went from 1.00x to 12.17x once this was fixed.

Both are now handled by generating candidate operations permissively and then
**validating each one against the density field itself** under the error budget
the compressor has to honour anyway.  The fold factor is consequently a function
of the tolerance and is reported as one.  This removes `symprec` from the
method's parameters entirely and is a small algorithmic contribution in its own
right.

## Result 7: gate G0.a, compression ratio against Bader charge deviation

The kill gate, and the number the survey could not find anywhere in the
literature.  Basins are derived once from the original field and both fields are
integrated over the same basins; that reproduces baderkit's own charges to
1.6e-10 e on the original, and avoids re-running a partitioning algorithm that
is unstable on quantized fields (see the script docstring).

Median over the 32 materials, at each nominal pointwise tolerance:

| Scheme | rel tol | ratio | median max dQ (e) | materials under 0.01 e |
|---|---:|---:|---:|---:|
| quantize+zstd | 1e-5 | 11.0x | 0.00001 | 100 % |
| quantize+zstd | 1e-4 | 20.1x | 0.00016 | 100 % |
| quantize+zstd | 1e-3 | 57.1x | 0.00685 | 62 % |
| quantize+zstd | 1e-2 | 220.2x | 0.54464 | 3 % |
| ZFP | 1e-3 | 26.6x | 0.00008 | 100 % |
| **ZFP** | **1e-2** | **54.1x** | **0.00089** | **100 %** |
| folded+quantize+zstd | 1e-3 | 121.6x | 0.00524 | 66 % |
| folded+quantize+zstd | 1e-2 | 549.0x | 0.48881 | 3 % |

**Verdict: PASS, but narrowly.**  Generic compression at 50x or better is
already chemically harmless on 25 of 32 materials; it breaks the 0.01 e
threshold on the other 7.  There is room for a domain method, and the room is
limited.  The gate is recorded as passed rather than as a triumph.

Highest compression ratio that keeps the maximum per-atom Bader deviation under
0.01 e, which is the only rate that matters chemically:

| | generic quantize+zstd | ZFP | symmetry-folded |
|---|---:|---:|---:|
| median over the corpus | 41.4x | **54.1x** | **109.4x** |

Symmetry folding buys **2.05x more compression at equal chemical fidelity**
(median over 32 materials), and about 2.0x against ZFP.

### The finding that reframes the project

**A pointwise error bound does not control the chemical error, and the two are
not even monotonically related across codecs.**  At a nominal tolerance of
1e-3 of the value range, quantize+zstd leaves a median maximum Bader deviation
of 0.00685 e and is chemically safe on only 62 % of materials.  ZFP at 1e-2 - a
tolerance **ten times looser** - leaves 0.00089 e and is safe on 100 %, at a
higher compression ratio.  A smooth decorrelating transform distributes its
error in a way that largely cancels under integration over a basin, while
uniform quantization does not.

So the quantity the entire error-bounded compression field controls is the wrong
one for this data, which is precisely the gap `LITERATURE.md` identified: QoI
preservation has never been pointed at chemistry.  This is the motivating figure
and the argument of the paper.

Note also that ZFP, ignored as a weak baseline on pure rate grounds, is the
**strongest** generic baseline once fidelity is measured chemically.  That is
the third time in this Stage 0 that a baseline turned out stronger than assumed.

### Limitation of this metric

Holding the basins fixed measures how much charge moves within a fixed domain.
Real compression perturbs both the integrand and the domain of integration, so
these deviations are a lower bound.  Quantifying the basin-boundary contribution
needs a partitioning implementation that survives degraded fields; `bader-rs`
should be tried before any publication.

## Stage 1: against the real SZ3

Everything above used an open-loop Lorenzo proxy for the generic baseline.  That
proxy is now retired.  `pysz` ships a `cp312-win_amd64` wheel, so **the actual
SZ3 compressor runs here** with no compiler and no Linux environment; SZ3 is
header-only C++ compiled into the extension.  SPERR is reachable the same way
through `hdf5plugin` 7.0.0.  MGARD has no prebuilt path on Windows at all, which
means its QoI support is out of reach without a toolchain.

Real SZ3 is much stronger than the proxy was, exactly as feared: on one grid the
proxy reached 37.3x where SZ3 reached 88.0x at equal chemical fidelity.  Its
default predictor is multi-level cubic-spline interpolation with auto-tuning,
not the first-order Lorenzo the proxy used.

### The predictor had to be upgraded before the question could be asked

With a Lorenzo-based codec, symmetry folding beat SZ3 where symmetry was strong
and **lost** where it was weak - on mp-2242118 at a 1e-3 tolerance, 25,068 bytes
against SZ3's 20,832.  That comparison confounds two things: a symmetry prior
and a weaker predictor.  So `src/rhocodec/interp.py` reimplements the multi-level
interpolation scheme and fuses orbit copying into its traversal, which needs a
different notion of representative: the orbit member the traversal reaches
*first*, since the hierarchical order is not monotone in linear index.

The control that makes the comparison fair is the same codec with folding
switched off.  Over 186 materials it lands at **1.00x of SZ3** at a 0.01 e Bader
threshold, so the predictor is in SZ3's class and any gain from folding is
attributable to symmetry rather than to a predictor difference.

### Corpus

186 Materials Project charge densities, 1.84 GB as `float64`, deliberately
balanced across crystal systems: 24 cubic, and 27 each of hexagonal,
monoclinic, orthorhombic, tetragonal, triclinic and trigonal.  Balance matters
here, because grid size correlates with low symmetry and an interim sample
processed smallest-first was visibly optimistic.

### Compression ratio at fixed chemical fidelity

Highest ratio each scheme reaches with maximum per-atom Bader deviation under
the threshold.  This is the certification the encoder can actually perform: it
holds the original field, so it can check the decoded field and keep the loosest
tolerance that passes.  Byte-weighted over the corpus.

| Scheme | dQ < 0.001 e | dQ < 0.01 e | dQ < 0.05 e |
|---|---:|---:|---:|
| ZFP | 44.7x | 51.6x | 51.6x |
| **SZ3** | **45.2x** | **144.1x** | **343.5x** |
| interp (folding off, fairness control) | 60.7x | 141.9x | 254.1x |
| SZ3 on orbit representatives, 1D | 76.5x | 152.8x | 261.1x |
| Lorenzo + folding (superseded) | 127.9x | 200.4x | 272.7x |
| **interp + folding (the method)** | **189.7x** | **631.2x** | **1,165.4x** |
| vs SZ3 | **4.22x** | **4.47x** | **3.65x** |

Selecting per material between SZ3 and the folded codec - which the encoder can
do, since it certifies both - beats SZ3 on **92 %** of materials at the 0.01 e
threshold and is never worse.

Across all 186 materials, 7 tolerances and 6 schemes there were **zero
error-bound violations** once the reserve for symmetry mismatch became the
measured within-orbit spread rather than a fixed fraction of the budget.

A correction worth recording: an earlier version selected between the two on
*bytes* rather than on certified fidelity, and that made the combination up to
**2.2x worse** than SZ3 on some materials, because a smaller stream can carry a
larger chemical error.  Selection has to be on the contract, not on the rate.

### Where the symmetry gain lives

Gain of the folded codec over SZ3 at the 0.01 e threshold, by crystal system:

| System | n | median gain | max | win rate |
|---|---:|---:|---:|---:|
| cubic | 24 | 18.20x | 37.0x | 100 % |
| hexagonal | 27 | 9.13x | 45.7x | 96 % |
| tetragonal | 27 | 7.01x | 15.6x | 96 % |
| trigonal | 27 | 4.52x | 16.1x | 100 % |
| orthorhombic | 27 | 4.49x | 7.0x | 100 % |
| monoclinic | 27 | 2.76x | 6.7x | 85 % |
| **triclinic** | 27 | **1.10x** | 3.8x | **67 %** |
| all | 186 | 4.37x | 45.7x | 92 % |

Risk R1 is confirmed in its precise form: the payoff spans a factor of 17
between cubic and triclinic, and triclinic material gains almost nothing.  It
does not disqualify the method - the median over a balanced corpus is still
4.37x and the win rate 92 % - but any claim has to be stated per symmetry class,
and a corpus of slabs and adsorbate structures would sit at the triclinic end.

### The balanced corpus flatters the database claim

The corpus is balanced across crystal systems, which is right for measuring a
method and wrong for claiming a saving on a real archive.  Materials Project is
dominated by low-symmetry structures, and those are also the largest files -
exactly the ones symmetry folding helps least.  Population shares are taken from
the build manifest, so they are measured rather than assumed.

| System | share of MP | corpus n | median gain | median size |
|---|---:|---:|---:|---:|
| monoclinic | 23.5 % | 27 | 2.76x | 11.8 MB |
| orthorhombic | 21.0 % | 27 | 4.49x | 10.1 MB |
| triclinic | 15.7 % | 27 | 1.10x | 8.8 MB |
| cubic | 13.3 % | 24 | 18.20x | 4.1 MB |
| tetragonal | 11.2 % | 27 | 7.01x | 7.1 MB |
| trigonal | 8.4 % | 27 | 4.52x | 11.1 MB |
| hexagonal | 6.9 % | 27 | 9.13x | 7.4 MB |

Three aggregations of the same measurements:

| Aggregation | Gain over SZ3 |
|---|---:|
| balanced corpus, median over materials | 4.41x |
| weighted by Materials Project material counts | 5.66x |
| **storage bill: total SZ3 bytes / total folded bytes** | **2.55x** |

The third is the only one that answers "how much smaller does the archive get",
because a compression ratio is a rate and systems have to be combined through
the bytes they contribute rather than by averaging their ratios.  **The honest
headline for a database claim is 2.55x, not 4.41x.**

Absolute projection, size-weighted: the public bucket holds 7.7 TB of charge
densities stored essentially uncompressed (MP's gzipped JSON costs about
7.2 bytes per value against 8 for raw `float64`).  At a maximum per-atom Bader
deviation of 0.01 e that is **56 GB with SZ3 and 22 GB folded**.

### The central claim, now measured against real SZ3

Median over the corpus at each *nominal* pointwise tolerance:

| Scheme | rel tol | ratio | median max dQ (e) | chemically safe |
|---|---:|---:|---:|---:|
| SZ3 | 1e-3 | 185.2x | 0.01064 | 48 % |
| SZ3 | 1e-2 | 717.8x | 0.13765 | 1 % |
| **ZFP** | **1e-2** | **50.7x** | **0.00070** | **100 %** |
| interp+folded | 1e-3 | 1,046.9x | 0.00828 | 55 % |

At the same nominal tolerance of 1e-2, ZFP's median chemical error is **200x
smaller** than SZ3's, while SZ3 compresses 14x harder.  The pointwise error
bound that the entire error-bounded compression literature controls does not
order these codecs the way chemical fidelity does, and it does not predict
whether a given operating point is usable.  A user who picks a tolerance is not
choosing what they think they are choosing.

That is the argument of the paper, and it now rests on the real compressors
rather than on proxies.

### A decoder exists, and it reproduces the encoder bit for bit

Everything above was checked as "the encoder's reconstruction stays inside the
error bound", which is not the same as "a decoder can rebuild it".  A decoder is
now implemented: it replays the traversal from the symbol stream alone - grid
shape, quantizer step, symbols, escaped values, and the orbit map regenerated
from the structure header plus the transmitted operation bitmask, never from the
original field.  Its output is compared with the encoder's reconstruction by
`np.array_equal`.

**Zero mismatches.**  Without this the byte counts would describe a stream
nobody can decode.

### Throughput, and the cost the rate table hides

Single CPU thread, relative tolerance 1e-4, after JIT warm-up, with the
traversal build inside the timer for both directions:

| Codec | encode | decode |
|---|---:|---:|
| ZFP | 257-283 MB/s | - |
| SZ3 | 76-104 MB/s | - |
| **this codec** | **27-29 MB/s** | **27-29 MB/s** |

Plus a one-off symmetry analysis at **1.4-11 MB/s**, slowest where the operation
count is highest - which is exactly where the compression gain is largest.

So the method is **3-4x slower to encode than SZ3 and about 10x slower than
ZFP**, and the symmetry pass can cost more time than the compression itself.
For a write-once archive, where analysis is paid at ingest and the saving is
paid back on every read, that is an acceptable trade.  For anything on a hot
path it is not, and the rate tables above should not be read without this one.

Two caveats on these numbers, in opposite directions.  The traversal is rebuilt
from scratch on every call as plain NumPy over the whole grid and dominates the
codec time; caching it per grid shape is straightforward engineering that has
not been done.  Against that, SZ3 and ZFP are optimised C++ and this is numba,
so a like-for-like implementation gap remains.

A timing correction worth recording: the first measurement excluded the
traversal build from the encoder but included it in the decoder, which made
encode look ten times faster than decode purely through accounting.

### Gate G0.c closed: the promolecule prior is cut

Re-tested against the interpolation codec that the project actually uses, over
12 materials at two tolerances:

| Relative tolerance | median gain | materials where the prior wins |
|---|---:|---:|
| 1e-4 | **0.47x** | **0 %** |
| 1e-3 | **0.62x** | **0 %** |

The prior does not merely fail to help - it roughly **doubles** the stream, on
every material tested, and the fitted radial profiles cost under a kilobyte so
the loss is not side information.  **Gate G0.c: CUT.**

The instructive part is *why*, because the surface reading was encouraging:
fitting per-element radial profiles cut the value range by 22x, 41x, even 142x
on some materials, and range reduction is the figure of merit people reach for
first.  It is the wrong one.  A predictive codec spends bits on what it cannot
predict, not on amplitude.  Subtracting a smooth atom-centred model lowers the
dynamic range while *roughening* the field locally, and local smoothness is
exactly what the interpolation predictor lives on.  The two priors anti-compose.
The materials with the largest range reduction were not the ones where the prior
did least badly.

This closes the last of the three transform stages proposed at the start.
Symmetry folding survived and composes; the promolecule predictor is cut on
measured rate; cross-configuration delta coding remains untested for want of
data, and is the stage `LITERATURE.md` records as partly owned by BQB anyway.

### Correctness accounting

- The first full run reserved a *fixed* 10 % of the error budget for symmetry
  mismatch while validating operations on a 300,000-point subsample that can
  miss a violating point.  That produced **3 error-bound violations** in 186
  materials (`results/stage1/sz3.jsonl`).  Reserving the **measured** maximum
  within-orbit spread instead makes the bound hold by construction, and the
  re-run under that rule (`results/stage1/sz3_adaptive.jsonl`, the numbers
  quoted above) has **zero violations** and is slightly *better*, because the
  measured reserve is usually well under 10 %.
- Folded streams are charged for the side information they genuinely need: the
  decoder can regenerate candidate operations from the structure header with
  spglib but cannot repeat the validation, which compares against the original
  field.  One byte names the symprec rung and a bitmask says which candidates
  survived, so 1 + ceil(n/8) bytes, at most 25.  Small, but omitting it would
  have made the folded counts fictional.


## Stage 2: the slab test, and the change of claim it forced

### Slabs: the symmetry method is a wash

68 real slab and adsorbate densities pulled from NOMAD - clean and
adsorbate-covered Co(0001), Cr(110), V, Ti+Cl, Ru, RuO2+OCHO (a CO2RR system)
and GaN+H - 2.08 GB, median vacuum fraction 42 %.  Provenance with SHA-256 for
every file is in `data/slabs/provenance.jsonl`.  No new DFT was run.

At a maximum per-atom Bader deviation of 0.01 e:

| | median | byte-weighted |
|---|---:|---:|
| best generic (SZ3 / SPERR / ZFP) | 132.6x | 138.9x |
| symmetry-folded in-house codec | 145.8x | 151.9x |
| ratio | **1.04x** | 1.09x |

**Median gain 1.04x, winning on 51 % of systems.**  On bulk crystals the same
codec was worth several-fold; on slabs it is a coin flip.  The reason is visible
in the breakdown: **54 % of these systems are effectively P1**, and those score
0.74x.  Only the 19 systems retaining a fold factor above 4x show a gain, 1.32x.

This is the regime the project was originally pitched at, so the honest reading
is that **symmetry folding is a bulk-crystal and materials-database technique,
not a surface-science one**.

### What that leaves

The primary claim never depended on symmetry.  It is that a pointwise error
bound does not control the chemical error - and the mechanism behind it turned
out to be the more useful finding.

## Stage 3: error structure, not error magnitude

### The mechanism

At an identical pointwise tolerance SZ3 leaves about 200x more Bader charge
error than ZFP while honouring the same bound, so magnitude cannot be the
explanation.  Measuring the *signed* error summed over each atom's region
against the *absolute* error summed over the same region:

| Codec | fraction of error that survives as net bias |
|---|---:|
| ZFP | **0.01 - 0.04** |
| SZ3 | 0.04 - 0.34 |
| in-house interpolation codec | 0.06 - 0.43 |

A Bader charge is an integral, so oscillating error cancels under it and
locally one-signed error does not.  Closed-loop prediction produces exactly the
latter: in a smooth region every residual quantizes to zero, the reconstruction
simply follows the predictor, and it drifts one way.  A transform codec has no
such loop.  **The rate-optimal codecs have the chemically worst error structure,
and the chemically benign one compresses poorly.**

### The attack, and why it is a wrapper rather than a codec

Remove the part of the error that survives integration.  Partition space into
Voronoi cells around the atoms - a partition that follows from the structure
header alone, so encoder and decoder derive it identically, unlike Bader basins
which are defined by the field the decoder does not have.  Send one number per
cell, the mean signed error inside it; the decoder subtracts it.

Cost: `n_atoms` floats, a few hundred bytes.  Decoder complexity: one subtraction.

The pointwise bound is kept by construction rather than by assumption: the codec
runs at `eb_q < eb` and the applied shift is clamped to `eb - eb_q`, so
`|err - shift| <= eb_q + (eb - eb_q) = eb`.

How much budget to reserve is a real trade - a bigger reserve costs rate but
lets the correction remove more bias.  A fixed heuristic for it proved fragile:
changing the reserve flipped individual materials between a 4x gain and a 2x
loss.  So it is not fixed.  It is swept, and the encoder selects per file by
certifying against the chemical threshold, which it can do because it holds the
original field.  That is the same certification the whole method rests on,
applied to one more axis.

**The correction applies to SZ3 as readily as to the in-house codec**, so the
contribution is a technique for predictive compressors in general rather than a
competing codec.

Corpus-wide numbers are being measured; see `PROJECT_STATE.md` for status.


## CORRECTION (2026-09-03): the chemical metric used above is wrong by an order of magnitude

Every "at equal chemical fidelity" number earlier in this file was computed with
Bader basins derived **once from the original field and held fixed**.  That
metric is blind to basin-boundary movement, and boundary movement is the
dominant error mode.  Re-deriving the basins from each decompressed field - what
a user actually does, since they run Bader on the file they have - gives:

| rel tol | codec | ratio | dQ, fixed basins | dQ, **re-derived basins** |
|---|---:|---:|---:|---:|
| 1e-4 | ZFP | 15.4x | 0.00001 | **0.00107** |
| 1e-4 | SZ3 | 52.2x | 0.00064 | **0.01154** |
| 1e-4 | SPERR | 25.9x | 0.00007 | **0.00804** |
| 1e-3 | ZFP | 27.8x | 0.00006 | **0.00521** |
| 1e-3 | SZ3 | 158.4x | 0.01741 | **0.07120** |
| 1e-3 | SPERR | 58.8x | 0.00072 | **0.08539** |
| 1e-2 | ZFP | 49.7x | 0.00040 | **0.03674** |
| 1e-2 | SZ3 | 531.5x | 0.23408 | **0.41919** |
| 1e-2 | SPERR | 167.7x | 0.01058 | **0.70545** |

Ten materials, five bulk and five slab.

### What this invalidates

- **Every compression ratio quoted at a chemical threshold is inflated by
  roughly 10-20x.**  At an honest 0.01 e threshold the usable ratios are about
  25-30x, not the 130-600x reported above.
- **The flawed metric did not merely rescale errors, it re-ordered codecs.**
  SPERR looked chemically excellent under fixed basins (0.011 e at 1e-2) and is
  in fact the *worst* of the three once basins are re-derived (0.705 e).  Its
  error must sit preferentially near the zero-flux surfaces.  Any conclusion in
  this file that rests on SPERR is void.
- The symmetry result (3.35x on bulk, 1.04x on slabs) and the bias-correction
  result (2.08x on slabs) were both measured at "matched fidelity" under the
  flawed metric and have to be redone.

### What survives

**The primary claim survives, with a smaller magnitude.**  SZ3's chemical error
divided by ZFP's, at a matched nominal tolerance:

| rel tol | fixed basins | re-derived basins |
|---|---:|---:|
| 1e-4 | 109.8x | **8.9x** |
| 1e-3 | 220.8x | **17.6x** |
| 1e-2 | 262.7x | **22.0x** |

So the headline "200x" becomes **9-22x**.  The direction, the ordering between
ZFP and SZ3, and the conclusion are unchanged: at an identical pointwise
tolerance SZ3 compresses about 10x harder than ZFP and leaves about 10-20x more
chemical error, so the tolerance a user sets does not tell them what they are
getting.  If anything the SPERR reversal strengthens the argument, since it shows
that even a careful chemical metric can mislead if it is the wrong one.

### The fix

Re-derived basins are computable: `baderkit` survived on all 10 materials and
all 3 codecs at the tolerances that matter, contradicting the earlier assumption
that it crashes on degraded fields.  The cost is one extra Bader run per
operating point.  All rate-fidelity tables must be regenerated this way before
anything here is quoted.



## Stage 4 (2026-09-03): the honest metric, and what it kills

### Lossless baseline, full corpora - the value proposition holds

| corpus | f64+zstd | f64+xz | float32+zstd |
|---|---:|---:|---:|
| bulk, 186 materials | 2.1x | 3.0x | 4.6x |
| slabs, 68 systems | 1.1x | 1.2x | 2.2x |

Against roughly 25-30x for honestly-measured chemically-safe lossy compression,
lossy is worth about 6-13x over the best exact alternative, in **both** regimes.
BQB's 35:1 is quoted against cube text and converts to about 7.8x on this
denominator, so it is not the threat an earlier note in this file suggested.

An intermediate claim is retracted: a probe on eight files per corpus gave 16.6x
lossless and 26.2x for float32 on bulk, which suggested lossy compression was
pointless there.  That probe took the smallest files, which are the
highest-symmetry ones, and the full corpus is four to five times lower.

### The metric's noise floor is a slab phenomenon

Probing with float32 truncation - a uniform 4e-8 relative field error, which
should be chemically nothing - and re-deriving basins:

| corpus | median dQ | max dQ | above 1e-3 | above 1e-2 |
|---|---:|---:|---:|---:|
| bulk | 6.4e-09 | 3.1e-04 | 0 % | 0 % |
| **slabs** | **1.6e-04** | **1.1e-02** | **20 %** | **10 %** |

Bulk crystals are stable: the watershed does not move under an essentially exact
perturbation.  **Slabs are not.**  In vacuum the density and its gradient are
both near zero, so the zero-flux surface is barely defined there, and for 10-20 %
of slab systems the Bader charge is not a well-defined function of the
compression error at the 0.01 e level at all.

That tension is now the central scientific problem of the project: **lossy
compression is only really needed for slabs, and slabs are where the chemical
metric is least trustworthy.**

### Boundary-protecting allocation: cut

The hypothesis was that since essentially all chemical error is basin-boundary
movement, and flipped voxels lie within one voxel of the original surface,
tightening a thin shell and loosening the rest would buy compression for free.
Implemented with a per-block bound map (block 4, mask entropy-coded, ~0.3-3 kB),
scored on re-derived basins, over 12 slabs:

| | result |
|---|---:|
| boundary / uniform, median | **0.99x** |
| systems helped | **17 %** (2 of 12) |
| systems hurt | 25 % |

Ten of twelve are flat to within 1 %.  **The prior is cut.**

The reason is instructive and was the stated risk: the flips *appear* at the
boundary but are *caused* by error anywhere along a steepest-ascent path, which
is not local.  Protecting the shell does not protect the paths.  Proximity to
the surface is the wrong variable.

### Where that leaves the algorithmic contributions

| prior | status |
|---|---|
| promolecule predictor | cut, 0.47x median, 0/12 |
| symmetry folding | bulk only; slabs 1.04x; bulk figure needs redoing under the honest metric |
| bias correction | gains largely evaporate under the honest metric |
| boundary protection | cut, 0.99x median |

**No mechanism survives cleanly.**  On present evidence the defensible paper is
the measurement and methodology one: how to measure the chemical fidelity of a
compressed charge density, why the obvious way is wrong by an order of magnitude
and mis-orders codecs, and for which systems the question is well posed at all.


## Reproduction

```bash
python scripts/fetch_mp_corpus.py --per-system 5 --out data/mp
python scripts/stage0_audit.py <CHGCAR> --out results/stage0
python scripts/stage0_endtoend.py <CHGCAR> --out results/stage0
python scripts/stage0_corpus.py --corpus data/mp
python scripts/stage0_composition.py --corpus data/mp
python scripts/summarize_stage0.py
python scripts/gate_g0a_bader.py --corpus data/mp --limit 12
python scripts/stage1_sz3.py --corpus data/mp
python scripts/summarize_sz3.py
```

## Known limitations

- **SPERR has not been run.**  It is reachable through `hdf5plugin`, but that is
  a filter API rather than an array API, so it needs a chunking-aware harness.
  MGARD has no Windows path at all, so the only shipped QoI-preserving
  compressor cannot be compared against.
- `den2bin` and BQB, the two existing tools that compress this kind of data,
  have still not been run.  BQB in particular is the work a referee will raise.
- The Bader metric holds the basins fixed and is a lower bound on the chemical
  error, since compression perturbs the domain of integration as well as the
  integrand.  `bader-rs` ships a Windows binary and should be used to bound how
  much this understates.
- The corpus is crystalline Materials Project data only.  Nothing has been
  measured on slabs, adsorbate series or NEB chains, which is where the
  chemistry motivation lives and where the triclinic row of the table above
  predicts the symmetry prior will be worth almost nothing.
- The corpus was used for development.  **Nothing here is an external
  validation**, and the frozen external test of `PREREGISTRATION.md` has not
  been run.
- The promolecule prior has still only been measured in full on one file.
- Tolerances are relative to each field's peak-to-peak range, which is dominated
  by nuclear cusps.  The Stage 1 result is that this is a poor contract - which
  is the point - but it also means the tolerance axis is not comparable to
  compression papers that use a different normalization.

## Stage 5 (2026-09-05): the stability probe was wrong, and Protocol A.1

Discovered while extending the benchmark ladder downward
(`scripts/honest_benchmark_tight.py --limit 1`): on `mp-1007755` (HfAu) the
Protocol A floor is 5.9e-10 e with zero voxels reassigned, yet ZFP at relative
1e-7 — a smaller perturbation than the float32 round trip — gives 4.3e-3 e, and
the Bader error does not fall toward zero as the tolerance is tightened. Cause:
float32 rounding is monotone (no rank exchange, only exact ties), and the
on-grid watershed resolves exact ties deterministically. Full account:
`results/stability/PROTOCOL_A1.md`, `paper/PROBE_VALIDATION.md`.

```
python scripts/stability_floor_noise.py          # 319 systems x 5 seeds  -> results/stability/stability_floor_noise_seeds.csv
python scripts/probe_calibration.py              # 18 systems, 5 seeds, 3 amplitudes -> results/stability/probe_calibration.csv
python scripts/build_eligibility_a1.py           # -> eligibility_by_threshold_a1.csv, eligibility_summary_a1.csv
```

| quantity | Protocol A (archived) | Protocol A.1 |
|---|---:|---:|
| floor, noise / f32, median (single seed) | — | 8 711x (p10 1.9, p90 2.9e5) |
| systems with zero reassigned voxels under the probe | 62.1 % | 1.9 % |
| non-evaluable, all 319, τ = 1e-4 | 23.2 % | **79.9 %** |
| τ = 1e-3 | 7.2 % | **41.4 %** |
| τ = 1e-2 | 2.2 % | **9.7 %** |
| P(vacuum floor > bulk floor), dev / ext | 0.672 / 0.419 | 0.564 / 0.382 |
| r(log floor, log points per atom) | +0.20 | +0.08 |

Calibration (18 systems): float32 creates a median 82 exact neighbour ties and
reassigns nothing in 9/18; noise creates none and reassigns nothing in 2/18.
Seed spread of log10(floor) median 0.47 dec, max 2.4 dec; verdict flips with
seed in 3/18 (1e-4), 2/18 (1e-3), 1/18 (1e-2) → five pre-registered seeds,
floor = maximum. Amplitude x0.1→x10 moves the floor by median 0.76 dec (p10
0.00, p90 2.02): about half plateau, half sub-linear → floor is stated at the
float32 L∞ amplitude; sensitivity is Supplement S4. On the full corpus the
5-seed maximum changes the single-seed verdict for 35 / 17 / 2 of 319 systems.

Side finding: `aflow-Al8Cu4U1_ICSD_601801`, A.1 floor 2.15 e, is a basin
permutation between symmetry-equivalent Al atoms (0.88 ↔ 3.03 e), not a charge
error; registered as `basin_relabelling_symmetry_equivalent`.

Master benchmark rows are probe-independent; the run continued throughout.

## Stage 6 (2026-09-06): the master table is complete, and its Protocol A.1 summary

Slab half run on NUS Vanda (job 1351661, one 36-core node, 36 shards, 2 h 50 min
wall, 24 h CPU, exit 0); bulk half on the workstation. 254 materials, 4627 rows,
every row `bound_respected`. 77 entries in the failure registry, 35 of them
`bader_solver_failure` on ZFP at relative 3e-3-1e-1 on slabs (baderkit IndexError
on heavily degraded vacuum regions) - recorded, not counted.

```
python scripts/honest_benchmark.py                     # bulk, workstation
qsub -P <project> hpc/slab_shards.pbs                  # slabs, Vanda, --domain slab --shard k/36 --resume-from master
python scripts/summarize_benchmark_a1.py               # -> summary_a1.csv, pairwise_a1.csv, best_certified_a1.csv
```

Best certified ratio, Protocol A.1 admission, median [95 % paired-bootstrap CI]:

| τ | stratum | admitted / non-eval | SZ3 | ZFP | SPERR | certified % (SZ3 / ZFP / SPERR) |
|---|---|---:|---:|---:|---:|---|
| 1e-2 | bulk | 168 / 18 | **52.0x** [48.0, 61.7] | 30.0x [27.2, 31.7] | 11.6x [10.1, 13.4] | 94 / 99 / 95 |
| 1e-2 | slab | 61 / 7 | **69.6x** [65.9, 72.3] | 40.5x [37.0, 44.9] | 8.1x [7.7, 9.4] | 70 / 97 / 72 |
| 1e-3 | bulk | 103 / 83 | 17.5x [16.4, 19.5] | **13.8x** [13.1, 14.9] | 7.0x [6.6, 9.0] | 35 / 91 / 44 |
| 1e-3 | slab | 40 / 28 | - (0 certified) | **18.4x** [16.3, 20.5] | 7.7x (1) | 0 / 63 / 3 |
| 1e-4 | bulk | 42 / 144 | 55.7x (1) | 9.4x [8.7, 11.5] | 24.1x (2) | 2 / 26 / 5 |

Paired wins at 1e-2: SZ3 beats ZFP on 86 % of bulk [82, 91] and 62 % of slab
[51, 74]; SPERR beats ZFP on 30 % of bulk and 0 % of slab.

Matched nominal tolerance, re-derived Bader error, SZ3 / ZFP per material:
6.4x (1e-4), 9.2x (1e-3), 12.4x (1e-2); SZ3 worse on 98-100 %.

Metric-reversal claim (claim 3) **falsified**: ZFP is the lowest-error codec at
matched tolerance under both the fixed-basin and the re-derived metric in
96-98 % of materials. The fixed-basin metric mis-orders the two worse codecs in
44 % (1e-3) / 16 % (1e-2) of materials, which is retained under claim 2.

The two headline facts are both true and not in tension: at a *given pointwise
tolerance* ZFP is chemically the safest; at a *given certified chemical
fidelity* of 1e-2 e SZ3 delivers ~1.7x more compression because it compresses
far harder per unit tolerance. At 1e-3 e the order flips to ZFP because SZ3's
tightest base rung no longer certifies most materials (tight-ladder run pending).

### Stage 6b: tight rungs (Vanda job 1351857, 3 min wall on 36 cores, exit 0)

`scripts/honest_benchmark_tight.py` on the 143 A.1-eligible development
materials (103 bulk, 40 slab), rungs 1e-7, 3e-7, 1e-6, 3e-6; 1716 rows, no
failures. Merged into `rate_chemical_tight.csv`; `summarize_benchmark_a1.py`
and `supplement_sensitivity.py` re-run with both files.

| τ | stratum | SZ3 | ZFP | SPERR | certified % (SZ3 / ZFP / SPERR) | SZ3 beats ZFP |
|---|---|---:|---:|---:|---|---|
| 1e-3 | bulk (103) | 12.9x [12.0, 14.3] | 13.5x [12.8, 14.5] | 6.2x [6.0, 6.5] | 99 / 99 / 99 | 41 % [31, 51] |
| 1e-3 | slab (40) | 14.1x [10.8, 15.4] | 15.3x [13.0, 18.4] | 5.1x [4.9, 5.4] | 85 / 100 / 88 | — |
| 1e-4 | bulk (42) | 6.3x [5.8, 7.2] | 7.6x [6.9, 8.0] | 4.2x [4.2, 4.6] | 86 / 100 / 90 | 12 % [2, 24] |

So the frontier is coherent across thresholds once admission and ladder are
both right: SZ3 leads at 1e-2 (52x vs 30x, wins 87 %), ties ZFP at 1e-3, and
trails at 1e-4 where ZFP's error structure pays. The "SZ3 certifies only 35 %
at 1e-3" figure from the base ladder alone is superseded: it was censoring of
admitted materials by the ladder's tightest rung, exactly the gap the tight run
was designed to close. Supplement S1-S4 regenerated in `results/supplement/`.

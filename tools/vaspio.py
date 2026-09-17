"""Fast readers for VASP volumetric files (CHGCAR / CHG / ELFCAR / LOCPOT).

The parser is deliberately independent of pymatgen's line-by-line reader so that
a few hundred multi-megabyte grids can be scanned in a Stage 0 audit.  Only the
pieces the audit needs are extracted: the lattice, the atom positions and
species, and the first (total) grid block.  Augmentation occupancies and any
spin blocks that follow the total grid are recorded by byte offset but not
parsed.

Value convention: VASP writes rho * V on the grid for CHGCAR.  Everything in
this module keeps the raw on-disk values.  Any conversion to electrons per
cubic angstrom happens at the call site so that a compression experiment always
operates on exactly the numbers that are stored in the file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_GRID_LINE = re.compile(rb"^\s*(\d+)\s+(\d+)\s+(\d+)\s*$")


@dataclass
class VolumetricFile:
    """A parsed VASP volumetric file."""

    path: Path
    comment: str
    scale: float
    lattice: np.ndarray  # (3, 3), rows are lattice vectors in angstrom
    species: list[str]
    counts: list[int]
    frac_coords: np.ndarray  # (natoms, 3) fractional
    ngrid: tuple[int, int, int]  # (ngx, ngy, ngz), x fastest on disk
    data: np.ndarray  # (ngx, ngy, ngz) float64, Fortran order semantics
    n_header_bytes: int
    has_augmentation: bool

    @property
    def volume(self) -> float:
        return float(abs(np.linalg.det(self.lattice)))

    @property
    def natoms(self) -> int:
        return int(sum(self.counts))

    @property
    def atomic_numbers(self) -> np.ndarray:
        nums = []
        for sym, n in zip(self.species, self.counts):
            nums.extend([_Z[sym]] * n)
        return np.asarray(nums, dtype=np.int32)

    @property
    def npoints(self) -> int:
        return int(np.prod(self.ngrid))

    def electron_count(self) -> float:
        """Integral of the density over the cell.

        For a CHGCAR the stored values are rho * V, so the integral is the mean
        of the grid values.  This is the primary conservation check used by the
        downstream fidelity gates.
        """
        return float(self.data.mean())


def read_volumetric(path: str | Path, max_bytes: int | None = None) -> VolumetricFile:
    """Read a VASP volumetric file into memory.

    Parameters
    ----------
    path:
        File to read.  Plain text only; callers should decompress first.
    max_bytes:
        Optional guard.  Raises if the file is larger than this, so that a
        batch scan cannot accidentally load a multi-gigabyte grid.
    """
    path = Path(path)
    size = path.stat().st_size
    if max_bytes is not None and size > max_bytes:
        raise ValueError(f"{path} is {size} bytes, above the {max_bytes} byte guard")

    raw = path.read_bytes()

    # --- header ---------------------------------------------------------
    lines: list[bytes] = []
    pos = 0
    for _ in range(9):
        nl = raw.find(b"\n", pos)
        if nl < 0:
            raise ValueError(f"{path}: truncated header")
        lines.append(raw[pos:nl])
        pos = nl + 1

    comment = lines[0].decode("utf-8", "replace").strip()
    scale = float(lines[1].split()[0])
    lattice = np.array(
        [[float(x) for x in lines[i].split()[:3]] for i in (2, 3, 4)],
        dtype=np.float64,
    )
    if scale < 0:
        # Negative scale means "target volume"; rescale isotropically.
        target = -scale
        lattice *= (target / abs(np.linalg.det(lattice))) ** (1.0 / 3.0)
    else:
        lattice *= scale

    tok6 = lines[5].split()
    if tok6 and tok6[0].isdigit():
        # Pre-VASP5 file with no species line.
        species = [f"X{i}" for i in range(len(tok6))]
        counts = [int(t) for t in tok6]
        coord_line_idx = 6
    else:
        species = [t.decode() for t in tok6]
        counts = [int(t) for t in lines[6].split()]
        coord_line_idx = 7

    natoms = sum(counts)

    # Re-walk from the coordinate mode line so selective dynamics is handled.
    pos = 0
    for _ in range(coord_line_idx):
        pos = raw.find(b"\n", pos) + 1
    nl = raw.find(b"\n", pos)
    mode = raw[pos:nl].strip().lower()
    pos = nl + 1
    if mode.startswith(b"s"):  # selective dynamics
        nl = raw.find(b"\n", pos)
        mode = raw[pos:nl].strip().lower()
        pos = nl + 1

    coords = np.empty((natoms, 3), dtype=np.float64)
    for i in range(natoms):
        nl = raw.find(b"\n", pos)
        coords[i] = [float(x) for x in raw[pos:nl].split()[:3]]
        pos = nl + 1
    if mode.startswith(b"c") or mode.startswith(b"k"):
        coords = coords @ np.linalg.inv(lattice)
    frac_coords = coords - np.floor(coords)

    # --- grid dimensions -------------------------------------------------
    ngrid = None
    while pos < len(raw):
        nl = raw.find(b"\n", pos)
        if nl < 0:
            raise ValueError(f"{path}: no grid dimension line found")
        line = raw[pos:nl]
        m = _GRID_LINE.match(line)
        pos = nl + 1
        if m:
            ngrid = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            break
    if ngrid is None:
        raise ValueError(f"{path}: no grid dimension line found")

    n_header_bytes = pos
    npoints = ngrid[0] * ngrid[1] * ngrid[2]

    # --- grid values -----------------------------------------------------
    # Stop at exactly npoints values: a CHGCAR continues with an
    # "augmentation occupancies" section whose text would abort a greedy parse.
    text = raw[pos:].decode("ascii", "replace")
    values = np.fromstring(text, dtype=np.float64, count=npoints, sep=" ")
    if values.size < npoints:
        raise ValueError(
            f"{path}: expected {npoints} grid values, parsed only {values.size}"
        )
    data = values.reshape(ngrid, order="F")

    has_augmentation = b"augmentation" in raw[pos:]

    return VolumetricFile(
        path=path,
        comment=comment,
        scale=scale,
        lattice=lattice,
        species=species,
        counts=counts,
        frac_coords=frac_coords,
        ngrid=ngrid,
        data=data,
        n_header_bytes=n_header_bytes,
        has_augmentation=has_augmentation,
    )


# Minimal symbol -> Z table covering the elements that appear in the datasets
# used here.  Extended lazily rather than pulling in a periodic-table
# dependency for what is a two-line lookup.
_Z = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8,
    "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15,
    "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20, "Sc": 21, "Ti": 22,
    "V": 23, "Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29,
    "Zn": 30, "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36,
    "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43,
    "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49, "Sn": 50,
    "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55, "Ba": 56, "La": 57,
    "Ce": 58, "Pr": 59, "Nd": 60, "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64,
    "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71,
    "Hf": 72, "Ta": 73, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78,
    "Au": 79, "Hg": 80, "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85,
    "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90, "Pa": 91, "U": 92,
}

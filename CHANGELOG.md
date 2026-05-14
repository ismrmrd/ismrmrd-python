# Changelog

## v1.15.0 (unreleased)

### Breaking changes

- `Image.from_array()` default changed from `transpose=True` to `transpose=False`.
  The old default silently transposed array data to match a legacy column-major
  convention inconsistent with the C++ library. Passing `transpose=True`
  explicitly now raises a `DeprecationWarning`.
- `Image.matrix_size` now returns the header's `(x, y, z)` tuple. Previously
  returned `(z, y, x)` from the data array shape, inconsistent with the header
  and the C++ API.
- `requires-python` bumped to `>=3.10` (`@dataclass(kw_only=True)` in the
  xsdata-generated schema code requires 3.10+).

### New features

- `ismrmrd.util`: new module with `sign_of_directions`,
  `directions_to_quaternion`, and `quaternion_to_directions` (all three
  available at the top-level package).
- `AcquisitionHeader` and `Acquisition` gained channel-mask methods:
  `isChannelActive`, `setChannelActive`, `setChannelNotActive`,
  `setAllChannelsNotActive` (matches C++ `ISMRMRD_ChannelMask`).
- `ProtocolDeserializer` gained `peek()` and `peek_image_data_type()` for
  non-consuming look-ahead.
- `ProtocolSerializer`/`ProtocolDeserializer` handle `CONFIG_FILE` (ID 1) and
  `CONFIG_TEXT` (ID 2) message types.
- `ismrmrd.__version__` exposed via `importlib.metadata`.

### Bug fixes

- `Waveform.setHead()` called non-existent `active_channels` field; corrected
  to `channels`.

### Infrastructure

- xsdata-generated schema files committed to the repo; no longer regenerated at
  install time. Run `python setup.py generate_schema` to update them.
- CI (both PyPI and conda workflows) now fails fast if committed schema files
  diverge from a fresh regeneration.
- `requirements.txt` removed; dev setup: `pip install -e ".[dev]"`.
- Python version matrix added to CI (3.10, 3.11, 3.12, 3.13).
- `dependabot.yml` added for monthly pip and GitHub Actions updates.

## v1.14.2

- Fix compatibility with xsdata 26.1.
- Enable re-building and publishing Conda package.
- Remove deprecated macos-13 runner.

## v1.14.1 and earlier

See git history.

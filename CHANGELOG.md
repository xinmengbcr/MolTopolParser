# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `MolTopDihedral`: parse combined bending-torsion (CBT, GROMACS func 11) dihedrals — 10-column
  `[ dihedrals ]` lines now map `a0..a4` to `c0..c4` (previously silently dropped), and the model
  validator allows `c3`/`c4` for func 11.

### Fixed
- ...

## [0.0.1a3] - 2024-06-21

### Fixed
- updating docs and README.MD 

## [0.0.1a2] - 2024-06-18

### Fixed
- parser functions into classmethods
- updating docs 

## [0.0.1a1] - 2024-06-12

### Added
- Initial release of `moltopolparser`.
- Basic parsing and processing of molecule simulation files.
- Initial documentation and examples.
- Basic support for **Gromacs** file formats: *.gro*, *top*, *itp* 


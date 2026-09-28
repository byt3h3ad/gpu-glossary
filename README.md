# GPU Glossary

This repository contains the source content for the
[Modal GPU Glossary](https://modal.com/gpu-glossary),
a dictionary of terms related to programming GPUs,
with a focus on the GPUs that run on the [Modal platform](https://modal.com),
NVIDIA GPUs.

## Licenses

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/80x15.png)](gpu-glossary/LICENSE)


All files in the `gpu-glossary` folder of this repository are licensed under the 
[Creative Commons Attribution 4.0 International (CC BY 4.0) License](https://creativecommons.org/licenses/by/4.0/).
See [`gpu-glossary/LICENSE`](gpu-glossary/LICENSE) for details.

The remainder of the files in this repository are licensed under the
[MIT License](https://opensource.org/license/mit).
See [`LICENSE`](LICENSE) for details.

## Translations

- [简体中文](https://github.com/miter6/gpu-glossary-zh)

## PDF

A printable PDF export of the whole glossary is generated automatically and
published as a GitHub Release
(https://github.com/byt3h3ad/gpu-glossary/releases) whenever this fork syncs
new content from modal-labs/gpu-glossary
(https://github.com/modal-labs/gpu-glossary). Grab the latest
`gpu-glossary.pdf` from the Releases page
(https://github.com/byt3h3ad/gpu-glossary/releases/latest).

To build it yourself (install `uv` first, see
https://docs.astral.sh/uv/getting-started/installation/):

    uv run --with-requirements utils/requirements.txt python utils/build_pdf.py

Output goes to `dist/gpu-glossary.pdf`.

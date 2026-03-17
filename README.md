# Limef Docs

Please go to [Limef library documentation](https://elsampsa.github.io/limef-docs/sphinx/_build/html/index.html)

## Structure

This folder is a git submodule pointing to the public `limef-docs` repository, served via GitHub Pages.

```
docs/
  sphinx/      # Sphinx source (.md/.rst, conf.py) + built HTML (_build/)
  doxygen/     # Doxyfile + built HTML (html/) + doxygen-awesome-css theme
  index.html   # Top-level redirect page
```

## Building & publishing

From the repo root:

```bash
./makedocs.bash              # clean + build locally (no push)
./makedocs.bash --clean      # clean only
./makedocs.bash --publish    # push built docs to GitHub Pages
./makedocs.bash --publish "release 1.2.0 docs"
```

## Dependencies

### Doxygen

```bash
sudo apt install doxygen graphviz
```

Doxygen reads C++ sources via relative paths defined in `doxygen/Doxyfile`:
```
INPUT = ../../src/   ../../md/
```
i.e. `docs/doxygen/` → `../../` → repo root → `src/` and `md/`.
Output goes to `doxygen/html/`.

### Sphinx

```bash
sudo apt install python3-pip
pip3 install sphinx furo myst-parser sphinx-copybutton sphinxcontrib-mermaid linkify-it-py
```

Extensions used (`sphinx/conf.py`):

| Extension | Package |
|---|---|
| `sphinx.ext.autodoc` + `autosummary` + `viewcode` + `doctest` + `todo` | `sphinx` (built-in) |
| `myst_parser` | `myst-parser` |
| `sphinx_copybutton` | `sphinx-copybutton` |
| `sphinxcontrib.mermaid` | `sphinxcontrib-mermaid` |
| linkify in MyST | `linkify-it-py` |
| Theme | `furo` |

## Third-party: doxygen-awesome-css

`doxygen/doxygen-awesome-css/` is a copy of
[jothepro/doxygen-awesome-css](https://github.com/jothepro/doxygen-awesome-css)
**v2.3.4** (MIT licence).

Currently stored as plain files (no submodule).  To upgrade, replace the
folder contents with the desired release from upstream.

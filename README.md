# AINCRAD Community Catalog

Themes and block extensions for AINCRAD, the SAO-style macOS launcher.
AINCRAD's **Settings › Browse** tab reads `catalog.json` from here, shows the previews, and
installs with one click. Every download is checked against the SHA-256 listed in the catalog.

## Using it

AINCRAD's Browse tab uses this catalog by default:
`https://raw.githubusercontent.com/djag1337/AINCRAD-catalog/main/catalog.json`.

To try changes before pushing, point Browse's Catalog field at your local copy's `catalog.json`
(macOS may ask once whether AINCRAD can open files in Documents).

## Contents

```
src/themes/<id>.json           theme sources (keys left out use Aincrad Classic)
src/extensions/<folder>/       extension folders (extension.json + any data files)
tools/build_catalog.py         packages, previews, checksums → catalog.json
tools/seed_examples.py         wrote the example extensions (kept for reference)
packages/                      built: themes/*.json and *.aincrad files
previews/                      built: 500×260 preview images
catalog.json                   built: the index AINCRAD reads
```

## Adding something

1. **A theme:** in AINCRAD, Settings › Themes › Export…, then save the file into `src/themes/`
   (its file name becomes the id).
   **An extension:** make it in the Extension Studio, then copy its folder from
   `~/Library/Application Support/AINCRAD/Extensions/<id>` into `src/extensions/`.
2. Run `python3 tools/build_catalog.py` (needs Pillow: `pip3 install pillow`).
3. Commit everything, including `packages/`, `previews/` and `catalog.json`.

Submissions from others arrive as pull requests. Review the extension's `extension.json`
before merging: check the permissions it asks for, and what its `fetch` blocks contact.

## Index format (`catalog.json`)

```json
{ "schemaVersion": 1, "name": "…", "description": "…",
  "items": [ { "id": "gun-gale", "type": "theme", "name": "Gun Gale", "author": "…", "version": "1.0",
               "description": "…", "preview": "previews/gun-gale.png", "package": "packages/themes/gun-gale.json",
               "sha256": "…", "permissions": [], "tags": ["theme"] } ] }
```

`type` is `theme` (package = a theme JSON) or `extension` (package = an `.aincrad` file).
Paths are relative to `catalog.json`. For extensions, `id` must equal the manifest's `id`.
Theme ids become file names in the user's themes folder.

## What's in it

| | |
|---|---|
| Themes | Aincrad Classic, Dark Aincrad, Alfheim, Gun Gale, Underworld, Midnight Blue |
| Extensions | System HP (CPU as an HP gauge) · Steam Mode (Gun Gale theme while Steam runs) · Focus Timer (25-minute focus with menu + gauge) · Welcome Message · Weather (Open-Meteo, needs network) |

Unofficial fan content, not affiliated with the Sword Art Online rights holders.

# Build inputs (library)

Assets consumed by the generators in `../scripts/`. These are build inputs, not
deliverables — deliverables live in `../assets/`.

| File | What it is | Provenance |
|---|---|---|
| `type_data.json` | ROANOKE wordmark pre-outlined to vector paths (Montserrat Bold 700, upright, via Inkscape). No live text ships in any generated SVG. | Vendor font: `fonts/vendor/Montserrat/Montserrat[wght].ttf` @ wght=700 |
| `bsides_core.svg` | Canonical BSides core silhouette (the "Prishtina" geometry: wordmark + infinity + two dots). Path data is embedded verbatim in `scripts/bsides_engine.py`; this file is the visual reference. | `tools/bsides_prishtina_core.svg` |
| `golden_geometry.json` | Golden-ratio tube scales for the Mill Mountain Star: `1 : 0.7794 : 0.5627`. | `tools/golden_geometry.json` |
| `OFL-Montserrat.txt` | SIL Open Font License for the Montserrat typeface used to outline ROANOKE. Must ship alongside any use of the wordmark. | Google Fonts / Montserrat project |

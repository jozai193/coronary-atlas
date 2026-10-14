# Anatomical assets

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.

- Official archive: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- Download: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip
- Mapping: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_element_parts.txt
- Current license (updated 2025-02-27, inspected 2026-10-07): https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html
- License text: https://creativecommons.org/licenses/by/4.0/
- Citation: Mitsuhashi N, Fujieda K, Tamura T, Kawamoto S, Takagi T, Okubo K. BodyParts3D: 3D structure database for anatomical concepts. Nucleic Acids Research. 2009;37:D782–D785. https://doi.org/10.1093/nar/gkn613

`frontend/public/anatomy/manifest.json` records each source OBJ hash, vertex/face counts, bounds, FMA mapping and shared center/scale. `anatomy_provenance.json` records original archive and manifest hashes. Files were extracted unchanged. The application changes material colors/opacity and applies a shared rotation, translation and scale at runtime.

| Display | FMA | Source components |
|---|---|---|
| LAD trunk | FMA74912 | FJ2631 |
| LCX | FMA3895 | FJ2649–FJ2654 |
| RCA trunk | FMA3802 | FJ2723 |
| Ventricular wall | FMA13884 | FJ2428 |
| Right atrial wall | FMA9457 | FJ2439 |
| Left atrial wall | FMA9531 | FJ2438 |
| Ascending aorta | FMA3736 | FJ3413 |
| Left coronary trunk | FMA3855 | FJ2737 |
| Contextual coronary branches | FMA3860, FMA3892, FMA3818, FMA3840, FMA3815, FMA3837, FMA3868 | 41 components; individual IDs and hashes in manifest |
| Coronary sinus | FMA4706 | FJ2655 |
| Pulmonary trunk | FMA8612 | FJ2966 |
| Cardiac veins | FMA4707, FMA4712, FMA4713, FMA4714, FMA76767 | 29 components; individual IDs/hashes in manifest |
| Atrial chamber cavities | FMA9465, FMA11359 | 2 components |
| Ventricular chamber cavities | FMA9291, FMA9466 | 2 components |
| Valve leaflets/cusps | FMA7238, FMA7239, FMA7240, FMA7242, FMA7243, FMA7247, FMA7249, FMA7250, FMA7252, FMA7253, FMA7254 | 11 components |
| Papillary muscles | FMA7260, FMA7261, FMA7262, FMA7264 | 4 components |

This is a generic reference atlas, not an individual's scan. Small branches are incomplete. The LCX mapping includes several source components; each receives the same vessel probability when probability shading is active. Neither atlas geometry nor RWMA input supplies lesion coordinates. Vessel colors use the conventional blood-flow diagram: oxygen-rich aorta/coronary arteries red; oxygen-poor pulmonary trunk, cardiac veins and coronary sinus blue. This is illustrative, not a measurement of oxygenation. Pulmonary veins would be red but are not separately included in the current mesh mapping. Pale red myocardium identifies tissue rather than oxygenation. Probability shading applies only to the three named target arteries. The pulmonary trunk remains visible when optional atlas detail is turned off.

The expanded scene contains 104 unchanged source meshes, 147,474 faces and 10,042,179 bytes of OBJ data. The original 56 mesh files, native coordinates, center/scale and target anchors are preserved. Added veins, chambers, valves and muscles are atlas context and never receive predicted disease labels. **Inside heart** makes walls translucent to reveal internal parts; the source meshes have not been digitally reshaped into a patient's echo. Source geometry has gaps and does not represent every anatomical variant. Qualified anatomical sign-off remains open.

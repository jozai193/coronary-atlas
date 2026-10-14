# Product, prior art and audience research

Reviewed 7 October 2026. This is desk research of public discussions, repository descriptions, primary studies and official product documentation. It is not an exhaustive novelty search, code-similarity audit, representative survey, clinical endorsement or user test of Coronary Atlas. No people were contacted, posts made, competitor code copied, or proprietary assets imported.

**9 October update:** [HEARTio](https://heartio.ai/) publicly describes investigational ECG-derived CAD/vessel estimates, a colored coronary tree and a clinical evidence program; its own site says it is not FDA cleared or approved. [CathSim](https://cathsim.com/) publicly offers catheterization training. These strengthen the case against claiming novelty or a near-term clinical triage advantage from prediction-plus-3D alone. The [judge-direction audit](winning_direction_audit.md) instead tests whether a held-out model-error lesson and transparent transport evidence offer a distinct learner task; no user adoption is established yet.

## Conclusion and intended audience

Heart-disease prediction plus SHAP is common; interactive coronary anatomy also exists. Do not pitch either as an invention. The defensible contribution is an independently implemented, locally reproducible Track A workflow connecting four separately evaluated labels, named coronary structures, actual per-model attribution and visible uncertainty. This combination is a positioning hypothesis, not proven uniqueness.

The strongest initial audience hypothesis is medical learners, nursing/cath-lab educators and educators teaching interpretable medical ML. They need to connect unfamiliar vessel names, model outputs and input measurements. A potential secondary audience is researchers reviewing the pipeline. A self-service diagnosis tool or replacement for clinical risk calculators is unsupported by the 303-record dataset and current validation.

## Prior art checked

| Source | Observed overlap | Lesson / boundary |
|---|---|---|
| [global-ad-snap/heart-disease-risk-analysis](https://github.com/global-ad-snap/heart-disease-risk-analysis) | Clinical-feature prediction, model comparison, SHAP, Streamlit, model card | This broad feature set is established. Repository claims were read, not independently reproduced; its different dataset/metrics are not comparable to ours. |
| [Emart29/Heart-Disease-Prediction](https://github.com/Emart29/heart-disease-prediction) | FastAPI, Streamlit, SHAP, Docker and ML engineering | API + explanation + packaging is not a novelty claim. No source code imported. |
| [t1modeler dataset script](https://github.com/t1modeler/data_script/blob/master/uci_049_extention_of_z_alizadeh_sani.py) | Same UCI dataset and explicit removal of vessel labels for Cath classification | Label exclusion is necessary practice, not our innovation. |
| [Human Atlas](https://github.com/ashemag/human-atlas) and [AAS](https://github.com/Kehn-Marv/AAS) | Open-source anatomy exploration, selection and guided heart learning | Generic 3D anatomy and lessons are established. Human Atlas also uses BodyParts3D, so its mapping is a useful implementation cross-check but not independent clinical validation. Our distinct task must be the held-out model-error lesson linked to reference anatomy and transport evidence. |
| [BioDigital platform](https://www.biodigital.com/product/the-biodigital-human) and [Anatomy Tree documentation](https://support.biodigital.com/hc/en-us/articles/360005542733-What-is-the-Anatomy-Tree) | Browser anatomy, guided experiences, search, isolate/fade/focus | Mature commercial anatomy tools already solve detailed exploration. Adopt familiar interaction conventions; do not copy their assets, branding or claim equal anatomical scope. |
| [CathSim author and public feedback](https://www.reddit.com/r/CathLabLounge/comments/1wxekk0/cath_lab_nurse_here_built_a_small_app_for/) | Interactive coronary anatomy and educational cases, phone access | Adjacent training product with specific angiographic objectives. Our tabular predictions do not support its lesion-location or projection-grading tasks. |

Searches included GitHub heart-disease/SHAP apps, Z-Alizadeh/LAD/LCX repositories, coronary 3D prediction, Reddit anatomy apps, coronary training and risk-score confusion. Search can miss private, unindexed or differently named work. No claim of patent clearance or guaranteed originality is made.

The focused [9 October GitHub opportunity audit](github_repo_opportunities.md) also reviewed InterpretML, Evidently, ImageCAS-X, Fairlearn, MAPIE and repeated-dataset classifier examples. Their licenses, possible use and task mismatches are recorded there; no repository score is promoted as evidence for this app.

## Public feedback and research signals

| Evidence | What it supports | Design decision |
|---|---|---|
| [Medical-school anatomy discussion](https://www.reddit.com/r/medicalschool/comments/1vqewr0/best_interactive_anatomy_app/) | Posters wanted to locate structures quickly and inspect spatial relationships; commenters liked hiding/isolating structures but described excessive detail as overwhelming. Anecdotal and self-selected. | Named vessel controls, plain-language vessel descriptions and optional detail. |
| [CathSim discussion](https://www.reddit.com/r/CathLabLounge/comments/1wxekk0/cath_lab_nurse_here_built_a_small_app_for/) | Self-described nurses/educators welcomed training use; comments requested additional branches/venous anatomy and challenged segment accuracy. Roles are not independently verified. | Add only source-mapped branches; distinguish contextual anatomy from predicted targets. Do not fabricate lesion locations. |
| [LearnCHD feedback](https://www.reddit.com/r/medicalschool/comments/1j47lyj/cardiac_anatomycongenital_heart_disease/) | Reports of broken search, awkward scrolling and sign-up failures show how interaction friction can undermine anatomy tools. | Keep local access without signup, use restrained zoom, verify search and mobile flows in a browser. |
| [Patient discussion of coronary-risk numbers](https://www.reddit.com/r/Cholesterol/comments/1m3mm84/help_understanding_these_numbers/) and [unit confusion](https://www.reddit.com/r/Cholesterol/comments/1emjopz/the_young_cad_guy_improved_cholestrol_with/) | Individuals confused test values, risk percentages, time horizons and units. These are accounts of confusion, not medical evidence or advice. | Explain what each estimate means beside results; preserve units and show that it is neither blockage percentage nor a future-event forecast. |
| [Mangal et al., 2024, primary study](https://scholars.mssm.edu/en/publications/it-attracts-your-eyes-and-brain-refining-visualizations-for-share/) | 32 interviews with 9 heart-failure participants favored labeled reference images and qualitative explanations alongside numbers. This studied medication-trial results, not our classifier. | Use labeled anatomy and a short explanation before detailed attribution charts. Transfer is a design inference. |
| [Barda et al., 2020, primary study PDF](https://d-nb.info/1222021196/34) | Healthcare-provider feedback favored high-level explanations with detail on demand, understandable terminology and raw feature values. Context was pediatric intensive-care mortality. | Show a plain-language summary, keep actual measurements and offer the full SHAP table on demand. Avoid adding unsupported time trends or intervention effects. |

## Implemented direction

1. Deep navy / teal interface, warm anatomical materials, larger readable text and clearly separated sections. Color is always paired with text/numbers. This visual direction is our design choice, not an experimentally proven preference.
2. Real additional BodyParts3D coronary branches, pulmonary trunk and coronary sinus, all from the already licensed archive. The three prediction target meshes retain their verified mappings. Extra branches are neutral contextual structures, not separately predicted.
3. Front/back/side views, tissue modes, target isolation and contextual-detail controls. Manual interaction does not imply a patient-specific scan or measured flow.
4. Prominent synthetic examples, a three-step guide, searchable observations, group completion counts, missing-field filtering and an explicit explanation when prediction is disabled. Clinical input requirements remain unchanged.
5. Plain-language summaries of actual SHAP factors, basic vessel descriptions and visible interpretation limits. No generated diagnosis, treatment advice, causal what-if claims or invented confidence interval.

## Still unvalidated

We do not know willingness to pay, frequency of use, learning improvement or whether educators would replace existing materials. Public enthusiasm for other apps does not establish demand for ours. Clinical usefulness and anatomical accuracy need direct expert review.

A small next study should observe 3-5 learners/educators completing: load a case; identify LAD/LCX/RCA; isolate LCX and return; explain the largest contributing measurement; explain why a 70% model probability is not 70% narrowing; locate weak model sensitivity. Record completion, errors, time and interpretations. Ask what they use today, where it fails, how often the task occurs and whether this changes that workflow. Do not count praise as adoption evidence. No such study has yet been run.

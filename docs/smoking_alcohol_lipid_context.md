# Smoking, alcohol, lipid profile and lifestyle review

14 October 2026. The user relayed further doctor feedback requesting smoking history, alcohol, lipid values and lifestyle changes.

## Trained inputs already available

Current smoking, former smoking, LDL, HDL and triglycerides are existing model inputs. A prominent review section now shows their entered values and links directly to editing the corresponding modeled observations. Model edits retain the existing result-clearing and completeness checks.

## Additional review context

Added reported pack-years, smoking history details, alcohol use history and type/amount/frequency, total cholesterol (mg/dL), physical activity, diet and reported lifestyle changes. The source training dataset does not contain these additional observations. They remain unknown unless entered; no alcohol status, smoking exposure, total cholesterol or lifestyle history is fabricated or derived from other fields.

These fields are excluded from prediction. They do not affect probabilities, SHAP, eligibility counts or the 55-feature input schema. Their provenance is separate and unverified. They cannot establish an accuracy improvement or an effect of changing lifestyle. Reviewers should check consistency between reported smoking history and the current/former smoking model flags; notes do not automatically rewrite those flags.

Context is shown in the case summary, printable worksheet and explicit JSON result export (`clinical_context_used_by_model: false`). It is held only in browser memory. Switching profiles, clearing the case, replacing inputs through CSV or applying a report in new-case mode clears it. A same-case report merge preserves it deliberately. Reloading clears all entered state. Report-photo autofill continues to target its supported model observations; these additional context fields are entered manually.

## Verification

Focused tests verify the existing lipid values, unknown defaults, context edits without rewriting model features, escaped worksheet exports and reset behavior. An authenticated live-browser test entered clearly labeled synthetic review notes and illustrative numbers, checked summary/JSON/worksheet exports, and repeated inference: both request bodies remained identical and contained exactly `features` and `model_variant`, with 55 model inputs. No context was sent to the prediction API. Model-field navigation, profile switching, CSV replacement, Clear and 390px layout checks passed.

The test annotations are not observations from the public R1 source record. R1 still has only its 55 recorded model inputs; additional clinical context starts unknown. No live model weights, training data, original accuracy metrics or API completeness rules were changed by this addition.

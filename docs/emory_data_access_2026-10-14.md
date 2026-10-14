# Emory dataset access inquiry — 14 October 2026

## Verified route

The author is Carlos Ordonez, University of Houston. His [current contact page](https://www2.cs.uh.edu/~ordonez/co_contact.html) lists carlos@uh.edu and directs outside inquiries through the CS department office or a current PhD student. The [official staff directory](https://www.uh.edu/nsm/computer-science/people/staff/) lists Daphne Brown (Faculty Affairs, Assistant to the Chair), debrown3@uh.edu. The inquiry uses that office relay route. The office is not asserted to own or approve access to the Emory records.

The [author-hosted 2006 paper](https://www2.cs.uh.edu/~ordonez/pdfwww/w-2006-HIKM-ardtmed.pdf) confirms 655 profiles and measured LM/LAD/LCX/RCA percentages. Its 25 listed fields include nine perfusion measures and four outcomes; they are not 25 matching app predictors. Most laboratory/echo inputs in the current app are absent from that table. This remains a promising reduced-input vessel study, not established full-input validation.

The author's software listings and paper did not expose a patient-level data download during this check. Current custody, availability and permission remain unconfirmed. The inquiry asks for the approved route, without signing an agreement or claiming institutional/ethics approval. A Gmail search found no existing message matching this cohort or the author's listed email before this inquiry.

## Request

To: debrown3@uh.edu

Subject: For Prof. Carlos Ordonez: access route for the 655-patient Emory Heart dataset

Dear Daphne Brown,

Could you please relay this inquiry to Professor Carlos Ordonez? His contact page suggests that outside inquiries can be passed through the department office.

I am developing Coronary Atlas, an educational research prototype for a hackathon. It currently uses the public 303-patient Z-Alizadeh Sani cohort. Professor Ordonez's 2006 paper, "Comparing Association Rules and Decision Trees for Disease Prediction" (https://doi.org/10.1145/1183568.1183573), describes 655 patients, clinical risk factors, and LM/LAD/LCX/RCA narrowing measurements.

Could he advise whether a de-identified patient-level release is available, or who at Emory is authorized to handle access? To assess compatibility, I would need:

- Available clinical predictors recorded before angiography and the artery narrowing outcomes, preferably as original percentages.
- A data dictionary covering codes, missing values, units and measurement timing, plus collection period, participant selection and prior-treatment exclusions.
- Reuse terms for local model training and evaluation, and any separate permission needed for aggregate results in a hackathon report or public demo.

The prototype is not clinically validated. I would follow the approved access process; please let me know whether institutional sponsorship, ethics approval or a data-use agreement is required.

Thank you for your time.

Regards,
Aditya Jevoor

## Status

Sent through the connected Gmail account on 14 October 2026 at 15:13 IST. Gmail accepted the message with the SENT label; a subsequent full read verified the To/From/Subject headers and exact intended body. The private mail receipt is excluded from Git. This confirms sending, not delivery, a reply or approved data access. No data-use agreement was signed and no institutional approval was asserted.

## Checks when access is offered

- Establish the custodian's authority, release terms, allowed training/evaluation use and separate aggregate-demo permissions before acquiring restricted records.
- Check one participant per row, duplicate/repeated visits, center and collection period, study selection and pre-existing interventions; the anonymous public source cannot prove identity independence by itself.
- Review actual field definitions and timing. Age and sex look closest; HTA/DIAB/HYPLD/FHCAD/SMOKE need documented definitions before mapping to HTN/DM/DLP/FH/Current Smoker.
- Keep total cholesterol distinct from LDL, prior angina distinct from typical chest pain, perfusion measures distinct from echo wall-motion findings and claudication distinct from a pulse examination.
- Confirm raw or binned narrowing values, inclusivity of the 50% boundary, missing codes, vessel coverage and aggregation. Do not assume CAD is the same label merely by combining vessel measures.
- Freeze an evaluation protocol before viewing new aggregate performance. With only a shared subset, train a separate source-only predictor and retain the acquired cohort for a transport evaluation before any augmentation study. The current 55-input candidate cannot claim full-input external validation from a reduced-input table.


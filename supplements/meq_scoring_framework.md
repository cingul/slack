# Supplemental Methods: Midodrine Equivalents (MEQ) Scoring Framework

## Purpose

Midodrine Equivalents (MEQ; also called ME in some STANDUP source documents) quantify orthostatic hypotension (OH) medication burden across common vasoactive medications. MEQ is designed for research reporting and medication-burden analysis. It is not a prescribing recommendation and should not be used to imply direct pharmacologic interchangeability.

## Framework version

**Version:** 1.0-STANDUP draft  
**Anchor:** Each medication's usual maximum daily dose for OH is assigned 100 MEQ.  
**Primary use:** Pre/post comparison of OH medication burden after supracardiac venous angioplasty and/or stenting.

## Core definition

For each OH-directed medication:

> medication-specific MEQ = actual total daily dose / usual maximum daily dose x 100

Total MEQ is the sum of all medication-specific MEQ values.

## Conversion table

| Medication | Unit | Usual maximum daily dose | Conversion factor | Formula |
| --- | --- | ---: | ---: | --- |
| Midodrine | mg/day | 30 | 3.3333 MEQ/mg | total daily mg x 3.3333 |
| Droxidopa | mg/day | 1800 | 0.055556 MEQ/mg | total daily mg x 0.055556 |
| Fludrocortisone | mg/day | 0.3 | 333.3333 MEQ/mg | total daily mg x 333.3333 |
| Pyridostigmine | mg/day | 180 | 0.55556 MEQ/mg | total daily mg x 0.55556 |

## Calculation steps

1. List all OH-directed medications at the study visit.
2. Calculate total daily dose:
   - scheduled medication: dose per administration x administrations per day;
   - as-needed medication: average actual daily use during the measurement window;
   - intermittent medication: average daily dose across the measurement window.
3. Convert each medication to MEQ using the prespecified factor.
4. Sum medication-specific MEQ values.
5. Record non-pharmacologic supports separately.
6. Record medications that may worsen OH separately.

## Examples

### Example 1: multidrug regimen

A patient takes:

- midodrine 15 mg/day;
- fludrocortisone 0.2 mg/day;
- droxidopa 600 mg/day.

MEQ calculation:

- midodrine: 15 x 3.3333 = 50 MEQ;
- fludrocortisone: 0.2 x 333.3333 = 66.7 MEQ;
- droxidopa: 600 x 0.055556 = 33.3 MEQ.

Total MEQ = 150.

If the post-intervention regimen is fludrocortisone 0.1 mg/day only, post-intervention MEQ = 33.3. The absolute MEQ reduction is 116.7 and the percent reduction is 77.8%.

### Example 2: medication independence

A patient has baseline MEQ = 124.2 and follow-up MEQ = 0.

- Absolute MEQ reduction = -124.2.
- Percent MEQ reduction = -100%.
- Medication independence endpoint = achieved.

## Measurement window

Use a consistent window for each study:

- **Baseline MEQ:** highest stable OH medication regimen before intervention, or average actual use during the 7 days before baseline if as-needed dosing is common.
- **Follow-up MEQ:** prescribed daily regimen or average actual use during the 7 days before the follow-up visit.
- **Primary endpoint MEQ:** prespecify the follow-up window, such as 3 months, 6 months, or the latest available stable follow-up.

## Preferred STANDUP de-escalation order

The source medication de-escalation framework recommends the following clinician-directed sequence after intervention:

1. droxidopa;
2. pyridostigmine;
3. fludrocortisone;
4. midodrine.

Rationale:

- Droxidopa is prioritized because of high cost and variable response.
- Pyridostigmine is often adjunctive with modest BP effect.
- Fludrocortisone carries risks related to edema, hypokalemia, heart failure, and delayed offset.
- Midodrine is retained longest because it has rapid onset and can be used as a titratable or rescue agent.

This order is pragmatic and clinician-directed. It should be stopped or slowed if orthostatic symptoms, standing BP, syncope, falls, or patient safety worsen.

## Recommended endpoints

| Endpoint | Definition |
| --- | --- |
| Absolute MEQ change | follow-up MEQ - baseline MEQ |
| Percent MEQ change | (follow-up MEQ - baseline MEQ) / baseline MEQ x 100 |
| At least 50% MEQ reduction | percent MEQ change <= -50% |
| Medication independence | follow-up MEQ = 0 |
| Failed taper | attempted MEQ reduction followed by dose restoration because of symptoms, BP worsening, syncope, falls, or clinician concern |

## Safety checks

MEQ reduction should be interpreted as favorable only if there is no clinically important worsening in:

- syncope;
- near-syncope;
- falls;
- OHQ composite score or CGI-I;
- standing duration;
- orthostatic SBP drop;
- rescue medication use;
- supine hypertension or other medication toxicity.

## Suggested case report language

"At baseline, the patient required midodrine 15 mg/day, fludrocortisone 0.2 mg/day, and droxidopa 600 mg/day, corresponding to 150 MEQ. After supracardiac venous stenting, the regimen was reduced to fludrocortisone 0.1 mg/day only, corresponding to 33 MEQ. This represented a 117 MEQ absolute reduction and a 78% reduction in medication burden, accompanied by stable or improved orthostatic symptoms and no increase in syncope or falls."

## Limitations

MEQ assumes dose proportionality and equal maximum-dose weighting across medications. These assumptions improve usability but may not reflect true biologic potency, pharmacokinetics, adverse-effect burden, or patient-specific response. Future studies should validate MEQ against OHQ, standing time, falls, syncope, supine hypertension, quality of life, and medication adverse effects.

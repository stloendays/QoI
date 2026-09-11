from pathlib import Path
import re

MANUSCRIPT = Path('paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md')
PATCH = Path('paper/SUBMISSION_STORYLINE_PATCH_20260912.md')

text = MANUSCRIPT.read_text(encoding='utf-8')
patch = PATCH.read_text(encoding='utf-8')


def extract(heading, next_heading):
    pattern = rf'(?ms)^## {re.escape(heading)}\n\n(.*?)(?=^## {re.escape(next_heading)}\n)'
    match = re.search(pattern, patch)
    if not match:
        raise RuntimeError(f'Cannot find patch section: {heading}')
    return match.group(1).strip()

abstract = extract('Revised abstract', 'Revised end of Introduction')
intro_end = extract('Revised end of Introduction', 'Figure 3 lead-in paragraph')
fig3_lead = extract('Figure 3 lead-in paragraph', 'Figure 3 result paragraph')
fig3_result = extract('Figure 3 result paragraph', 'P3A interpretation paragraph')
discussion_open = extract('Revised opening of Discussion', 'Revised closing of Discussion')

# 1. Abstract: make the validated measurement-contract contribution explicit.
text, n = re.subn(
    r'(?s)(## Abstract\n\n).*?(\n\n\*\*Keywords:\*\*)',
    lambda m: m.group(1) + abstract + m.group(2),
    text,
    count=1,
)
if n != 1:
    raise RuntimeError(f'Abstract replacement count={n}')

# 2. Introduction: end with the four-stage evidence hierarchy rather than a methods inventory.
text, n = re.subn(
    r'(?s)Here we analyse 6,343 frozen reconstructions of 254 development densities.*?not relabelled as untouched validation of these later research extensions\.',
    intro_end,
    text,
    count=1,
)
if n != 1:
    raise RuntimeError(f'Introduction replacement count={n}')

# 3. Figure 3 Results: demote the ladder-dependent historical reclassification and lead with P1/P2.
fig3_historical_note = (
    'The earlier full-record binary-to-three-state audit is retained as a sensitivity and provenance analysis rather than the headline result. '
    'Its 97.2% and 95.5% strict-threshold reclassification fractions depend on the original eligibility-targeted tight-ladder design; '
    'they therefore cannot be interpreted as design-independent causal misattribution rates. The historical counts remain reported in the Supplementary Information and frozen audit record.'
)
fig3_replacement = fig3_lead + '\n\n' + fig3_result + '\n\n' + fig3_historical_note
text, n = re.subn(
    r'(?s)Figure 3 and Supplementary Table S4/Fig\. S7 retain the historical full-record analysis:.*?although this result alone does not validate unseen reference perturbations or assign causality to individual codec discrepancies\.',
    fig3_replacement,
    text,
    count=1,
)
if n != 1:
    raise RuntimeError(f'Figure 3 Results replacement count={n}')

# 4. Prospective subsection: make clear this is the detailed uncertainty/secondary-threshold readout of Figure 3.
text = text.replace(
    '### The frozen QSQ gate prospectively stratifies unseen perturbation risk\n\nWe prospectively challenged the deployed five-seed QSQ gate',
    '### Prospective validation quantifies the separation across thresholds\n\nThe prospective component of Fig. 3 challenged the deployed five-seed QSQ gate',
    1,
)

# 5. Methods: the old binary reclassification is no longer Figure 3; keep it explicitly as historical sensitivity evidence.
text = text.replace(
    '### Binary-to-three-state reclassification\n\nThe Figure 3 audit uses one material–codec decision at a fixed Bader threshold as the analysis unit.',
    '### Historical binary-to-three-state sensitivity audit\n\nThe historical reclassification audit uses one material–codec decision at a fixed Bader threshold as the analysis unit.',
    1,
)

# 6. Discussion: sharpen the novelty boundary while preserving the controlled/prospective interpretation.
current_discussion_first = re.search(r'(?s)(## Discussion\n\n)(.*?)(?=\n\nThis result extends, rather than repeats, established QoI-aware compression work\.)', text)
if not current_discussion_first:
    raise RuntimeError('Cannot locate Discussion opening paragraph')
combined_discussion = (
    discussion_open
    + ' The equal-search control provides the complementary benchmark-design test: at the same primary threshold, '
      'failure to find a numerical pass is 3.3% for eligible versus 66.4% for screen-rejected material–codec pairs (20.34-fold).'
)
text = text[:current_discussion_first.start(2)] + combined_discussion + text[current_discussion_first.end(2):]

# 7. Mark the narrative patch integrated without deleting its audit trail.
patch = patch.replace('Status: **READY FOR MANUSCRIPT INTEGRATION**', 'Status: **INTEGRATED ON SUBMISSION STORYLINE BRANCH**', 1)

# Guardrails: central evidence and forbidden headline interpretation must be present/absent as intended.
required = [
    '20.34-fold',
    '50.83-fold',
    '14,986/14,986',
    '24/24 systems',
    '60/60 compressed charge-transfer directions',
    'not a worst-case stability guarantee',
]
for token in required:
    if token not in text:
        raise RuntimeError(f'Missing required submission token: {token}')

for forbidden in [
    'more than 95% of apparent binary failures cannot be scientifically attributed to the compressor',
    '95% of codec failures are invalid',
]:
    if forbidden in text:
        raise RuntimeError(f'Stale headline language remains: {forbidden}')

MANUSCRIPT.write_text(text, encoding='utf-8')
PATCH.write_text(patch, encoding='utf-8')
print('Submission storyline integrated into active manuscript.')

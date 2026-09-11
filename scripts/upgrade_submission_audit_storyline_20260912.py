from pathlib import Path

path = Path('scripts/audit_submission_upgrade_consistency.py')
text = path.read_text(encoding='utf-8')

# Synchronize legacy exact-string checks with the current reader-facing wording.
legacy_replacements = {
    'must(manuscript, "3.3% of eligible versus 66.4% of QSQ screen-rejected", "P1 manuscript risks")':
        'must(manuscript, "3.3% for QSQ-eligible versus 66.4% for screen-rejected", "P1 manuscript risks")',
    'must(manuscript, "14,986/14,986 successful trials", "P2 manuscript accounting")':
        'must(manuscript, "14,986/14,986 valid", "P2 manuscript accounting")',
    'must(manuscript, "a 50.83-fold risk ratio", "P2 manuscript RR")':
        'must(manuscript, "50.83-fold", "P2 manuscript RR")',
    'must(fig3_caption, "Primary result: equal-search separation plus prospective risk stratification", "Figure 3 caption hierarchy")':
        'must(fig3_caption, "The primary Figure 3 claim is prospective risk stratification after a separate equal-search control.", "Figure 3 caption hierarchy")',
}
for old, new in legacy_replacements.items():
    if old in text:
        text = text.replace(old, new, 1)

# Add the Figure 3 caption to the audit inputs if not already present.
fig3_read = '    fig3 = (ROOT / "figures/R/figure3_certification_landscape.R").read_text(encoding="utf-8")\n'
caption_read = '    fig3_caption = (PAPER / "FIGURE3_CAPTION_FINAL_20260911.md").read_text(encoding="utf-8")\n'
if caption_read not in text:
    if fig3_read not in text:
        raise RuntimeError('Cannot locate Figure 3 source read')
    text = text.replace(fig3_read, fig3_read + caption_read, 1)

# Add caption checks if not already present.
p2_anchor = '    must(fig3, "14,986/14,986 fresh trials", "P2 Figure 3 accounting")\n'
hierarchy_check = '    must(fig3_caption, "The primary Figure 3 claim is prospective risk stratification after a separate equal-search control.", "Figure 3 caption hierarchy")\n'
rr_check = '    must(fig3_caption, "50.83-fold", "Figure 3 caption prospective RR")\n'
if hierarchy_check not in text:
    if p2_anchor not in text:
        raise RuntimeError('Cannot locate P2 Figure 3 audit line')
    text = text.replace(p2_anchor, p2_anchor + hierarchy_check, 1)
if rr_check not in text:
    if hierarchy_check not in text:
        raise RuntimeError('Cannot locate Figure 3 hierarchy check')
    text = text.replace(hierarchy_check, hierarchy_check + rr_check, 1)

old_scope = '        "Scope: machine-readable P1-P4 results versus the active manuscript, Figure 3 source, Supplementary Information, Claim–Evidence Matrix, authoritative status and research plan. Historical provenance files are intentionally not required to adopt current status wording.",'
new_scope = '        "Scope: machine-readable P1-P4 results versus the active manuscript, Figure 3 source and caption, Supplementary Information, Claim–Evidence Matrix, authoritative status and research plan. Historical provenance files are intentionally not required to adopt current status wording.",'
if old_scope in text:
    text = text.replace(old_scope, new_scope, 1)

required_final = [
    '3.3% for QSQ-eligible versus 66.4% for screen-rejected',
    '14,986/14,986 valid',
    '50.83-fold',
    'The primary Figure 3 claim is prospective risk stratification after a separate equal-search control.',
]
for token in required_final:
    if token not in text:
        raise RuntimeError(f'Audit synchronization incomplete: {token}')

path.write_text(text, encoding='utf-8')
print('Submission audit synchronized with current Figure 3 storyline.')

from pathlib import Path

path = Path('scripts/audit_submission_upgrade_consistency.py')
text = path.read_text(encoding='utf-8')

replacements = {
    'must(manuscript, "3.3% of eligible versus 66.4% of QSQ screen-rejected", "P1 manuscript risks")':
        'must(manuscript, "3.3% for QSQ-eligible versus 66.4% for screen-rejected", "P1 manuscript risks")',
    'must(manuscript, "14,986/14,986 successful trials", "P2 manuscript accounting")':
        'must(manuscript, "14,986/14,986 valid", "P2 manuscript accounting")',
    'must(manuscript, "a 50.83-fold risk ratio", "P2 manuscript RR")':
        'must(manuscript, "50.83-fold", "P2 manuscript RR")',
}
for old, new in replacements.items():
    if old not in text:
        raise RuntimeError(f'Missing audit line to update: {old}')
    text = text.replace(old, new, 1)

old_read = '    fig3 = (ROOT / "figures/R/figure3_certification_landscape.R").read_text(encoding="utf-8")\n'
new_read = old_read + '    fig3_caption = (PAPER / "FIGURE3_CAPTION_FINAL_20260911.md").read_text(encoding="utf-8")\n'
if old_read not in text:
    raise RuntimeError('Cannot locate Figure 3 source read')
text = text.replace(old_read, new_read, 1)

old_p2 = '    must(fig3, "14,986/14,986 fresh trials", "P2 Figure 3 accounting")\n'
new_p2 = old_p2 + '    must(fig3_caption, "Primary result: equal-search separation plus prospective risk stratification", "Figure 3 caption hierarchy")\n    must(fig3_caption, "50.83-fold", "Figure 3 caption prospective RR")\n'
if old_p2 not in text:
    raise RuntimeError('Cannot locate P2 Figure 3 audit line')
text = text.replace(old_p2, new_p2, 1)

old_scope = '        "Scope: machine-readable P1-P4 results versus the active manuscript, Figure 3 source, Supplementary Information, Claim–Evidence Matrix, authoritative status and research plan.",'
if old_scope in text:
    text = text.replace(old_scope, '        "Scope: machine-readable P1-P4 results versus the active manuscript, Figure 3 source and caption, Supplementary Information, Claim–Evidence Matrix, authoritative status and research plan.",', 1)

path.write_text(text, encoding='utf-8')
print('Submission audit updated for current Figure 3 storyline.')

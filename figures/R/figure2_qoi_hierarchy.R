# Figure 2 — QoI operator hierarchy
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(scales); library(patchwork)
})

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

rowsf <- file.path(root, "analysis", "hartree_potential_expansion", "rows.csv")
smoothf <- file.path(root, "analysis", "hartree_potential_expansion", "material_smoothness.csv")
dispf <- file.path(root, "analysis", "hartree_potential_expansion", "matched_error_dispersion.csv")
decf <- file.path(root, "analysis", "electron_count_qoi", "electron_bader_decoupling.csv")
stopifnot(file.exists(rowsf), file.exists(smoothf), file.exists(dispf), file.exists(decf))

rows <- read.csv(rowsf, check.names=FALSE, stringsAsFactors=FALSE)
sm <- read.csv(smoothf, check.names=FALSE, stringsAsFactors=FALSE)
disp <- read.csv(dispf, check.names=FALSE, stringsAsFactors=FALSE)
dec <- read.csv(decf, check.names=FALSE, stringsAsFactors=FALSE)

# Frozen full-expansion statistics use only gate-passing rows.
if ("reproduction_gate_pass" %in% names(rows)) {
  gp <- rows[rows$reproduction_gate_pass %in% c(TRUE, "True", "TRUE", 1), ]
} else if ("gate_pass" %in% names(rows)) {
  gp <- rows[rows$gate_pass %in% c(TRUE, "True", "TRUE", 1), ]
} else {
  stop("rows.csv has no reproduction gate column")
}

codec_cols <- c(ZFP="#D55E00", SZ3="#0072B2", SPERR="#009E73")
bg <- "#FAFAF8"; ink <- "#1A1A1A"; grid <- "#DDD9D2"; muted <- "#6A6A6A"
theme_qoi <- theme_minimal(base_size=10.2) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(), panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink), axis.text=element_text(colour=ink),
  strip.text=element_text(face="bold", colour=ink),
  plot.title=element_text(face="bold", size=11.2, margin=margin(b=5)),
  plot.subtitle=element_text(size=9.0, colour="#4F4F4F", margin=margin(b=6)),
  legend.position="top", legend.title=element_blank(), plot.margin=margin(8,10,8,8)
)

# A — negative control: globally conserved electron count does not certify local Bader fidelity.
# Use frozen row-level master values available in the expansion table.
a <- gp %>%
  filter(is.finite(electron_count_abs_dev), is.finite(Bader_error_resolved_e),
         electron_count_abs_dev > 0, Bader_error_resolved_e > 0)

pA <- ggplot(a, aes(electron_count_abs_dev, Bader_error_resolved_e)) +
  geom_vline(xintercept=1e-4, linetype=2, colour="#777777", linewidth=.55) +
  geom_hline(yintercept=1e-3, linetype=2, colour="#777777", linewidth=.55) +
  geom_point(aes(colour=codec), alpha=.18, size=.8) +
  annotate("label", x=2e-7, y=3e-2, label="electron count preserved\nBader criterion failed", hjust=0,
           size=3.0, label.size=.18, fill=alpha(bg,.92), colour=ink) +
  scale_colour_manual(values=codec_cols) +
  scale_x_log10(labels=label_scientific()) + scale_y_log10(labels=label_scientific()) +
  labs(title="A | Global conservation is not a chemical certificate",
       subtitle="Same reconstructions; dashed lines: |Delta N| = 1e-4 e and Bader error = 1e-3 e",
       x="Absolute electron-count deviation (e)", y="Resolved Bader error (e)") + theme_qoi

# B — Hartree potential behaves as a smooth, near-first-order response to realized Linf.
b <- gp %>% filter(is.finite(realized_Linf), is.finite(potential_rel_RMSE), realized_Linf>0, potential_rel_RMSE>0)
# Downsample only for display; fits are shown per codec from all gate-passing rows.
set.seed(20260909)
b_show <- b %>% group_by(codec) %>% slice_sample(n=min(n(), 1200)) %>% ungroup()

pB <- ggplot(b_show, aes(realized_Linf, potential_rel_RMSE, colour=codec)) +
  geom_point(alpha=.18, size=.75) +
  geom_smooth(data=b, method="lm", formula=y~x, se=FALSE, linewidth=.9) +
  scale_colour_manual(values=codec_cols) +
  scale_x_log10(labels=label_scientific()) + scale_y_log10(labels=label_scientific()) +
  labs(title="B | A smooth nonlocal QoI tracks realized perturbation",
       subtitle="Hartree relative RMSE; pooled exponent alpha = 1.02, per-material R2 median 0.994-0.997",
       x="Realized L-inf density error", y="Relative Hartree-potential RMSE") + theme_qoi

# C — material-level response structure: paired R2 and monotonicity.
sm_long <- bind_rows(
  sm %>% transmute(codec, system_type, operator="Hartree", R2=hartree_R2, monotone=hartree_monotone),
  sm %>% transmute(codec, system_type, operator="Bader", R2=bader_R2, monotone=bader_monotone)
)
sm_long$operator <- factor(sm_long$operator, levels=c("Hartree","Bader"))
mono_sum <- sm_long %>% group_by(codec, operator) %>% summarise(frac=mean(monotone %in% c(TRUE,"True","TRUE",1), na.rm=TRUE), .groups="drop")

pC <- ggplot(sm_long, aes(operator, R2, fill=operator)) +
  geom_boxplot(width=.56, outlier.shape=NA, linewidth=.45) +
  stat_summary(fun=median, geom="point", shape=23, size=2.0, fill="white") +
  facet_wrap(~codec, nrow=1) +
  coord_cartesian(ylim=c(0,1.02)) +
  scale_fill_manual(values=c(Hartree="#B8D5E5", Bader="#D9B8B0"), guide="none") +
  labs(title="C | Operator structure changes error regularity",
       subtitle="Material-level log-log R2; Hartree is monotone in 88.6% of pairs vs 32.4% for Bader",
       x=NULL, y="Material-level log-log R2") + theme_qoi

# D — matched-Hartree fidelity still permits broad Bader error dispersion.
# Column names are generated by frozen summarizer; tolerate descriptive variants.
ratio_col <- intersect(c("p90_p10_ratio","P90_over_P10","bader_p90_p10","ratio_p90_p10"), names(disp))
if (length(ratio_col)==0) stop("Cannot identify P90/P10 ratio column in matched_error_dispersion.csv")
ratio_col <- ratio_col[1]
disp$ratio <- as.numeric(disp[[ratio_col]])
if (!"codec" %in% names(disp) || !"system_type" %in% names(disp)) stop("matched_error_dispersion.csv missing codec/system_type")

d <- disp %>% filter(is.finite(ratio), ratio>0)
pD <- ggplot(d, aes(interaction(codec, system_type, sep="\n"), ratio, fill=codec)) +
  geom_hline(yintercept=10, linetype=2, colour="#777777", linewidth=.55) +
  geom_boxplot(width=.62, outlier.alpha=.25, linewidth=.45) +
  scale_fill_manual(values=codec_cols, guide="none") +
  scale_y_log10(labels=label_number(accuracy=.1, suffix="x")) +
  labs(title="D | Similar smooth-field fidelity does not fix Bader fidelity",
       subtitle="P90/P10 Bader-error spread within 0.5-decade matched-Hartree-error bins; dashed line = 10x",
       x=NULL, y="Bader error dispersion (P90 / P10)") + theme_qoi

fig <- ((pA | pB) / (pC | pD)) + plot_layout(guides="collect") +
  plot_annotation(
    title="Figure 2 | Scientific fidelity is QoI-dependent",
    subtitle="The same density reconstructions preserve a global linear integral, propagate smoothly through the nonlocal Hartree operator, yet produce irregular errors after topology-dependent Bader partitioning.",
    caption="Hartree statistics use only reproduction-gate-passing rows. The 73 SZ3 stream-size mismatches are excluded by the frozen gate. Strict monotonicity is weaker for slabs; the main contrast there is supported by R2, local elasticity, and jump magnitude rather than monotonicity alone.",
    theme=theme(plot.background=element_rect(fill=bg, colour=NA),
                plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
                plot.subtitle=element_text(size=10, colour="#4F4F4F", margin=margin(b=8)),
                plot.caption=element_text(size=8.2, colour=muted, hjust=0, margin=margin(t=7)))
  )

ggsave(file.path(outdir,"figure2_qoi_hierarchy_R.png"), fig, width=11.8, height=8.3, dpi=360, bg=bg)
ggsave(file.path(outdir,"figure2_qoi_hierarchy_R.pdf"), fig, width=11.8, height=8.3, bg=bg)

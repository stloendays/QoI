# Figure 2 - QoI operator hierarchy
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(scales)
  library(patchwork)
})

if (!requireNamespace("svglite", quietly=TRUE)) {
  stop("Package 'svglite' is required for the vector SVG export.")
}

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

rowsf <- file.path(root, "analysis", "hartree_potential_expansion", "rows.csv")
smoothf <- file.path(root, "analysis", "hartree_potential_expansion", "material_smoothness.csv")
dispf <- file.path(root, "analysis", "hartree_potential_expansion", "matched_error_dispersion.csv")
decf <- file.path(root, "analysis", "electron_count_qoi", "electron_bader_decoupling.csv")
benchf <- file.path(root, "benchmark", "master_benchmark_full.csv")
stopifnot(file.exists(rowsf), file.exists(smoothf), file.exists(dispf), file.exists(decf), file.exists(benchf))

rows <- read.csv(rowsf, check.names=FALSE, stringsAsFactors=FALSE)
sm <- read.csv(smoothf, check.names=FALSE, stringsAsFactors=FALSE)
disp <- read.csv(dispf, check.names=FALSE, stringsAsFactors=FALSE)
dec <- read.csv(decf, check.names=FALSE, stringsAsFactors=FALSE)
bench <- read.csv(benchf, check.names=FALSE, stringsAsFactors=FALSE)

# Frozen full-expansion statistics use only gate-passing rows.
if ("reproduction_gate_pass" %in% names(rows)) {
  gp <- rows[rows$reproduction_gate_pass %in% c(TRUE, "True", "TRUE", 1), ]
} else if ("gate_pass" %in% names(rows)) {
  gp <- rows[rows$gate_pass %in% c(TRUE, "True", "TRUE", 1), ]
} else {
  stop("rows.csv has no reproduction gate column")
}

# Palette adapted from the manuscript visual system.
pal <- c(
  light_green = "#B8DBB3",
  green       = "#72B063",
  blue        = "#719AAC",
  orange      = "#E29135",
  teal        = "#94C6CD",
  navy        = "#4A5F7E"
)
codec_cols <- c(ZFP=pal[["blue"]], SZ3=pal[["orange"]], SPERR=pal[["teal"]])
operator_cols <- c(Hartree=pal[["green"]], Bader=pal[["navy"]])
bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E7E8EA"; muted <- "#646A73"

theme_qoi <- theme_minimal(base_size=10.2) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink),
  axis.text=element_text(colour=ink),
  strip.text=element_text(face="bold", colour=ink),
  plot.title=element_text(face="bold", size=11.2, margin=margin(b=5)),
  plot.subtitle=element_text(size=8.8, colour="#4F545C", lineheight=1.05, margin=margin(b=6)),
  legend.position="none",
  legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

# A - global linear conservation does not certify local Bader fidelity.
a <- bench %>%
  filter(is.finite(electron_count_abs_dev), is.finite(Bader_error_resolved_e),
         electron_count_abs_dev > 0, Bader_error_resolved_e > 0)
preserved <- a$electron_count_abs_dev <= 1e-4
if (!any(preserved)) stop("No electron-count-preserved rows for Figure 2A")
adec <- 100 * mean(a$Bader_error_resolved_e[preserved] >= 1e-3)

pA <- ggplot(a, aes(electron_count_abs_dev, Bader_error_resolved_e)) +
  annotate("rect", xmin=min(a$electron_count_abs_dev), xmax=1e-4,
           ymin=1e-3, ymax=max(a$Bader_error_resolved_e),
           fill=pal[["light_green"]], alpha=.24) +
  geom_vline(xintercept=1e-4, linetype=2, colour="#55585D", linewidth=.55) +
  geom_hline(yintercept=1e-3, linetype=2, colour="#55585D", linewidth=.55) +
  geom_point(colour="#747B83", alpha=.24, size=.78) +
  annotate("label", x=min(a$electron_count_abs_dev)*2.2,
           y=max(a$Bader_error_resolved_e)/2.5,
           label=sprintf("%.2f%% of electron-count-preserved rows\nfail the 10^-3 e Bader criterion", adec),
           hjust=0, vjust=1, size=2.85, label.size=.18,
           fill=alpha("white", .90), colour=ink) +
  scale_x_log10(labels=label_log()) +
  scale_y_log10(labels=label_log()) +
  labs(title="A | Global conservation does not guarantee local fidelity",
       subtitle="Same reconstructions; dashed thresholds mark\n|Delta N| = 10^-4 e and Bader error = 10^-3 e",
       x="Electron-count absolute deviation |Delta N| (e)",
       y="Bader resolved error (e)") + theme_qoi

# B - smooth nonlocal Hartree response. Fit in log-log space, then transform back.
b <- gp %>%
  filter(is.finite(realized_Linf_over_ptp), is.finite(potential_rel_RMSE),
         realized_Linf_over_ptp > 0, potential_rel_RMSE > 0)
set.seed(20260909)
b_show <- b %>%
  group_by(codec) %>%
  group_modify(~slice_sample(.x, n=min(nrow(.x), 1200))) %>%
  ungroup()

fit_lines <- b %>% group_by(codec) %>% group_modify(~{
  m <- lm(log10(potential_rel_RMSE) ~ log10(realized_Linf_over_ptp), data=.x)
  xs <- 10^seq(min(log10(.x$realized_Linf_over_ptp)),
               max(log10(.x$realized_Linf_over_ptp)), length.out=120)
  data.frame(realized_Linf_over_ptp=xs,
             potential_rel_RMSE=10^predict(m, newdata=data.frame(realized_Linf_over_ptp=xs)))
}) %>% ungroup()

pm <- lm(log10(potential_rel_RMSE) ~ log10(realized_Linf_over_ptp), data=b)
px <- 10^seq(min(log10(b$realized_Linf_over_ptp)), max(log10(b$realized_Linf_over_ptp)), length.out=160)
pooled <- data.frame(realized_Linf_over_ptp=px,
                     potential_rel_RMSE=10^predict(pm, newdata=data.frame(realized_Linf_over_ptp=px)))

pB <- ggplot(b_show, aes(realized_Linf_over_ptp, potential_rel_RMSE,
                         colour=codec, shape=system_type)) +
  geom_point(alpha=.30, size=.85) +
  geom_line(data=fit_lines,
            aes(realized_Linf_over_ptp, potential_rel_RMSE, colour=codec, group=codec),
            inherit.aes=FALSE, linewidth=.95) +
  geom_line(data=pooled,
            aes(realized_Linf_over_ptp, potential_rel_RMSE),
            inherit.aes=FALSE, linewidth=.72, linetype=2, colour="#30343A") +
  scale_colour_manual(values=codec_cols) +
  scale_shape_manual(values=c(bulk=16, slab=17)) +
  scale_x_log10(labels=label_log()) +
  scale_y_log10(labels=label_log()) +
  annotate("label", x=quantile(b$realized_Linf_over_ptp, .60),
           y=quantile(b$potential_rel_RMSE, .03),
           label="pooled slope = 1.02\nPearson = 0.89",
           hjust=0, size=3.0, label.size=.18, fill=alpha("white", .92), colour=ink) +
  labs(title="B | Hartree potential follows a smooth near-linear response",
       subtitle="All codecs and bulk/slab systems;\ndashed line: pooled log-log fit",
       x="Realized L-inf / density ptp",
       y="Hartree-potential relative RMSE") + theme_qoi +
  theme(legend.position="bottom", legend.box="horizontal",
        legend.margin=margin(t=1, b=0), legend.key.height=unit(8, "pt")) +
  guides(colour=guide_legend(order=1), shape=guide_legend(order=2))

# C - material-level regularity: distribution rather than bars.
sm_long <- bind_rows(
  sm %>% transmute(codec, system_type, operator="Hartree", R2=hartree_R2),
  sm %>% transmute(codec, system_type, operator="Bader", R2=bader_R2)
) %>% filter(is.finite(R2))
sm_long$operator <- factor(sm_long$operator, levels=c("Hartree","Bader"))

pC <- ggplot(sm_long, aes(operator, R2, fill=operator, colour=operator)) +
  geom_violin(width=.88, alpha=.40, linewidth=.45, trim=TRUE) +
  geom_boxplot(width=.22, outlier.shape=NA, linewidth=.45, fill="white", alpha=.86) +
  geom_jitter(width=.11, height=0, alpha=.18, size=.55, show.legend=FALSE) +
  stat_summary(fun=median, geom="point", shape=23, size=2.2, fill="white", colour=ink) +
  facet_wrap(~codec, nrow=1) +
  coord_cartesian(ylim=c(0,1.02)) +
  scale_fill_manual(values=operator_cols, guide="none") +
  scale_colour_manual(values=operator_cols, guide="none") +
  labs(title="C | Operator structure changes error regularity",
       subtitle="Material-level log-log R2; Hartree median 0.994-0.997,\nBader median 0.89-0.95",
       x=NULL, y="Material-level log-log R2") + theme_qoi

# D - Bader dispersion after conditioning on matched Hartree fidelity.
ratio_col <- intersect(c("bader_p90_over_p10","p90_p10_ratio","P90_over_P10",
                         "bader_p90_p10","ratio_p90_p10"), names(disp))
if (length(ratio_col)==0) stop("Cannot identify P90/P10 ratio column in matched_error_dispersion.csv")
ratio_col <- ratio_col[1]
disp$ratio <- as.numeric(disp[[ratio_col]])
if (!"codec" %in% names(disp) || !"system_type" %in% names(disp)) {
  stop("matched_error_dispersion.csv missing codec/system_type")
}
d <- disp %>% filter(is.finite(ratio), ratio>0)

pD <- ggplot(d, aes(interaction(codec, system_type, sep="\n"), ratio, fill=codec)) +
  geom_hline(yintercept=10, linetype=2, colour="#55585D", linewidth=.55) +
  geom_violin(width=.86, alpha=.32, colour=NA, trim=FALSE) +
  geom_boxplot(width=.24, outlier.alpha=.22, linewidth=.45, fill="white") +
  geom_jitter(aes(colour=codec), width=.10, alpha=.34, size=.7, show.legend=FALSE) +
  scale_fill_manual(values=codec_cols, guide="none") +
  scale_colour_manual(values=codec_cols, guide="none") +
  scale_y_log10(labels=label_number(accuracy=.1, suffix="x", big.mark=",")) +
  labs(title="D | Similar Hartree fidelity does not imply similar Bader fidelity",
       subtitle="P90/P10 spread within 0.5-decade Hartree-error bins;\n55.4% of rows lie in bins with at least 10x spread",
       x=NULL, y="Bader error dispersion (P90 / P10)") + theme_qoi

fig <- ((pA | pB) / (pC | pD)) + plot_layout(guides="keep") +
  plot_annotation(
    title="Figure 2 | QoI hierarchy reveals operator-dependent error propagation",
    subtitle="global linear: electron count  ->  smooth nonlocal: Hartree potential  ->  topology-dependent: Bader charge",
    caption=paste0(
      "Hartree statistics use reproduction-gate-passing rows; 73 SZ3 stream-size mismatches remain excluded by the frozen gate.\n",
      "Slab conclusions rely on R2, local elasticity and jump magnitude rather than universal rung-wise monotonicity."
    ),
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=10, colour="#4F545C", margin=margin(b=8)),
      plot.caption=element_text(size=8.0, colour=muted, hjust=0, lineheight=1.05, margin=margin(t=7))
    )
  )

png_path <- file.path(outdir,"figure2_qoi_hierarchy_R.png")
pdf_path <- file.path(outdir,"figure2_qoi_hierarchy_R.pdf")
svg_path <- file.path(outdir,"figure2_qoi_hierarchy_R.svg")

ggsave(png_path, fig, width=11.8, height=8.3, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=11.8, height=8.3, bg=bg)
ggsave(svg_path, fig, width=11.8, height=8.3, bg=bg, device=svglite::svglite)

message("Rendered Figure 2:")
message("  ", png_path)
message("  ", pdf_path)
message("  ", svg_path)

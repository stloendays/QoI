# Figure 7 — Fourier-spectrum mechanism audit at matched realized L-infinity
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(scales)
  library(patchwork)
  library(jsonlite)
})

if (!requireNamespace("svglite", quietly=TRUE)) stop("Package 'svglite' is required for SVG export.")

root <- getwd()
indir <- file.path(root, "analysis", "hartree_spectral_mechanism", "results")
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

radial_path <- file.path(indir, "radial_spectrum_summary.csv")
ratio_path <- file.path(indir, "mechanism_ratio_summary.csv")
pair_path <- file.path(indir, "matched_pair_mechanism.csv")
summary_path <- file.path(indir, "SUMMARY.json")
stopifnot(file.exists(radial_path), file.exists(ratio_path), file.exists(pair_path), file.exists(summary_path))

R <- read.csv(radial_path, stringsAsFactors=FALSE, check.names=FALSE)
M <- read.csv(ratio_path, stringsAsFactors=FALSE, check.names=FALSE)
P <- read.csv(pair_path, stringsAsFactors=FALSE, check.names=FALSE)
S <- jsonlite::fromJSON(summary_path)

stopifnot(nrow(P) == 457)
stopifnot(length(unique(P$material_id)) == 214)
stopifnot(S$status == "FREQUENCY_STRUCTURE_DOMINANT")
stopifnot(S$checks$safe_parseval_identity)
stopifnot(S$checks$safe_hartree_equals_weighted_spectrum_identity)

bg <- "#FAFAF8"
ink <- "#1A1A1A"
muted <- "#5E636A"
grid <- "#DDD9D2"
blue <- "#0072B2"
orange <- "#D55E00"
teal <- "#009E73"
purple <- "#7B61A8"
codec_cols <- c(ZFP=blue, SZ3=orange)

R <- R %>%
  mutate(
    q_mid = (q_low + q_high) / 2,
    codec = factor(codec, levels=c("ZFP","SZ3"))
  )

theme_qoi <- theme_minimal(base_size=10.5) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink),
  axis.text=element_text(colour=ink),
  plot.title=element_text(face="bold", size=11.2, colour=ink, margin=margin(b=4)),
  plot.subtitle=element_text(size=8.9, colour=muted, margin=margin(b=6)),
  legend.position="top",
  legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

# A — actual radial reconstruction-error spectrum.
pA <- ggplot(R, aes(q_mid, median_error_energy_fraction, colour=codec, fill=codec)) +
  annotate("rect", xmin=0, xmax=.25, ymin=-Inf, ymax=Inf, fill="#F6DFDB", alpha=.42) +
  geom_ribbon(aes(ymin=p25_error_energy_fraction, ymax=p75_error_energy_fraction), alpha=.15, colour=NA) +
  geom_line(linewidth=1.0) +
  geom_vline(xintercept=.25, linetype=2, colour="#888888", linewidth=.45) +
  scale_colour_manual(values=codec_cols) +
  scale_fill_manual(values=codec_cols) +
  scale_y_log10(
    breaks=c(1e-5,1e-4,1e-3,1e-2,1e-1),
    labels=label_scientific(digits=1)
  ) +
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,.25), expand=expansion(mult=c(.01,.01))) +
  annotate("text", x=.125, y=.16, label="low G", colour="#8C2E23", fontface="bold", size=3.0) +
  labs(
    title="A | ZFP shifts reconstruction error away from low G",
    subtitle="Median radial error-energy fraction; ribbons show pairwise IQR across 457 matched pairs",
    x=expression(q==abs(G)/G[max]),
    y="Error-energy fraction per radial bin"
  ) + theme_qoi

# B — the downstream Hartree operator concentrates sensitivity at low G.
pB <- ggplot(R, aes(q_mid, median_hartree_weighted_fraction, colour=codec, fill=codec)) +
  annotate("rect", xmin=0, xmax=.25, ymin=-Inf, ymax=Inf, fill="#F6DFDB", alpha=.42) +
  geom_ribbon(aes(ymin=p25_hartree_weighted_fraction, ymax=p75_hartree_weighted_fraction), alpha=.15, colour=NA) +
  geom_line(linewidth=1.0) +
  geom_vline(xintercept=.25, linetype=2, colour="#888888", linewidth=.45) +
  scale_colour_manual(values=codec_cols) +
  scale_fill_manual(values=codec_cols) +
  scale_y_log10(
    breaks=c(1e-10,1e-8,1e-6,1e-4,1e-2,1),
    labels=label_scientific(digits=1)
  ) +
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,.25), expand=expansion(mult=c(.01,.01))) +
  labs(
    title=expression("B | " * abs(G)^{-4} * " weighting makes low-G error decisive"),
    subtitle="Median fraction of Hartree-weighted spectral energy in each radial bin",
    x=expression(q==abs(G)/G[max]),
    y="Hartree-weighted fraction per radial bin"
  ) + theme_qoi

# C — material-level centers and bootstrap intervals for the exact decomposition factors.
wanted <- c(
  "sqrt_total_safe_error_energy_ratio",
  "sqrt_spectral_hartree_susceptibility_ratio",
  "nyquist_safe_hartree_ratio"
)
C <- M %>%
  filter(metric %in% wanted) %>%
  mutate(
    label = recode(
      metric,
      sqrt_total_safe_error_energy_ratio="Total spectral-energy factor",
      sqrt_spectral_hartree_susceptibility_ratio="Spectral susceptibility factor",
      nyquist_safe_hartree_ratio="Hartree error ratio"
    ),
    label=factor(label, levels=rev(c(
      "Total spectral-energy factor",
      "Spectral susceptibility factor",
      "Hartree error ratio"
    )))
  )

stopifnot(nrow(C)==3)

pC <- ggplot(C, aes(material_level_center, label)) +
  geom_vline(xintercept=1, linetype=2, colour="#777777", linewidth=.5) +
  geom_errorbarh(aes(xmin=ci_low, xmax=ci_high), height=.14, linewidth=.7, colour="#555555") +
  geom_point(aes(colour=metric), size=3.4) +
  geom_text(
    aes(label=sprintf("%.3f", material_level_center)),
    nudge_y=.22, hjust=.5, size=3.1, colour=ink
  ) +
  scale_colour_manual(
    values=c(
      sqrt_total_safe_error_energy_ratio=blue,
      sqrt_spectral_hartree_susceptibility_ratio=orange,
      nyquist_safe_hartree_ratio=teal
    ),
    guide="none"
  ) +
  scale_x_log10(
    limits=c(.05,1.15),
    breaks=c(.05,.1,.2,.4,.8,1),
    labels=label_number(accuracy=.01)
  ) +
  labs(
    title="C | Decomposition of the Hartree codec effect",
    subtitle="Material-level centers with 95% bootstrap intervals; exact closure is pairwise",
    x="ZFP / SZ3 factor",
    y=NULL
  ) + theme_qoi

# D — distribution of the material-level contribution from spectral structure.
D <- P %>%
  group_by(material_id) %>%
  summarise(structure_share=median(spectral_structure_abs_log_share, na.rm=TRUE), .groups="drop") %>%
  filter(is.finite(structure_share))

median_share <- median(D$structure_share)
stopifnot(abs(median_share - S$mechanism_diagnostics$median_material_spectral_structure_abs_log_share) < 1e-12)

anno <- sprintf(
  "median = %.1f%%\n99.5%%: susceptibility lower\n98.1%%: centroid higher\n99.1%%: low-G fraction lower",
  100*median_share
)

pD <- ggplot(D, aes(structure_share)) +
  geom_histogram(binwidth=.05, boundary=0, closed="left", fill="#9BB7CE", colour="white", linewidth=.35) +
  geom_vline(xintercept=.5, linetype=2, colour="#777777", linewidth=.55) +
  geom_vline(xintercept=median_share, colour=purple, linewidth=1.0) +
  annotate(
    "label", x=.96, y=Inf, label=anno, hjust=1, vjust=1.12,
    size=2.85, label.size=.18, fill=alpha("white",.94), colour=ink
  ) +
  scale_x_continuous(
    limits=c(0,1), breaks=seq(0,1,.2),
    labels=label_percent(accuracy=1)
  ) +
  labs(
    title="D | Frequency structure dominates",
    subtitle="Material-level share of the absolute-log effect from spectral susceptibility",
    x="Spectral-structure share of |log effect|",
    y="Materials"
  ) + theme_qoi + theme(legend.position="none")

fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(guides="collect") +
  plot_annotation(
    title=expression("Figure 7 | Frequency allocation of reconstruction error controls Hartree fidelity at matched " * L[infinity]),
    subtitle="Exact ZFP/SZ3 common-support audit: 457 matched pairs across 214 materials. The Nyquist-safe operator reproduces the historical codec effect while restoring exact Fourier/real-space parity.",
    caption=paste0(
      "Historical Hartree ratio = 0.0776221; Nyquist-safe ratio = 0.0776219; maximum Parseval relative error = 1.30 x 10^-15.\n",
      "Exact pairwise identity: R_H = sqrt(E_ZFP/E_SZ3) x sqrt(S_H,ZFP/S_H,SZ3). Panel C reports separately aggregated material-level centers."
    ),
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=9.5, colour=muted, lineheight=1.05, margin=margin(b=8)),
      plot.caption=element_text(size=8.0, colour=muted, hjust=0, margin=margin(t=7))
    )
  ) & theme(legend.position="top")

png_path <- file.path(outdir, "figure7_fourier_spectrum_mechanism_R.png")
pdf_path <- file.path(outdir, "figure7_fourier_spectrum_mechanism_R.pdf")
svg_path <- file.path(outdir, "figure7_fourier_spectrum_mechanism_R.svg")

ggsave(png_path, fig, width=11.8, height=8.3, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=11.8, height=8.3, device=cairo_pdf, bg=bg)
ggsave(svg_path, fig, width=11.8, height=8.3, device=svglite::svglite, bg=bg)

stopifnot(file.exists(png_path), file.exists(pdf_path), file.exists(svg_path))
message("Rendered Figure 7 Fourier-spectrum mechanism: PNG + PDF + SVG")

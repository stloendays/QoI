# Figure 8 — QOAC-H diagnosis-to-design and certified compression gain
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(scales)
  library(patchwork)
  library(jsonlite)
})

if (!requireNamespace("svglite", quietly=TRUE)) stop("Package 'svglite' is required for SVG export.")

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

mechanism_path <- file.path(root, "analysis", "operator_aware_codec_hartree", "results", "mechanism_material.csv")
mechanism_summary_path <- file.path(root, "analysis", "operator_aware_codec_hartree", "results", "SUMMARY.json")
confirm_path <- file.path(root, "analysis", "operator_aware_codec_hartree_v02_confirmatory", "results", "confirmatory_material.csv")
confirm_summary_path <- file.path(root, "analysis", "operator_aware_codec_hartree_v02_confirmatory", "results", "SUMMARY.json")
census_path <- file.path(root, "analysis", "operator_aware_codec_hartree_v02_census", "results", "census_tau_summary.csv")
census_summary_path <- file.path(root, "analysis", "operator_aware_codec_hartree_v02_census", "results", "SUMMARY.json")

stopifnot(all(file.exists(c(
  mechanism_path, mechanism_summary_path, confirm_path, confirm_summary_path,
  census_path, census_summary_path
))))

M <- read.csv(mechanism_path, stringsAsFactors=FALSE, check.names=FALSE)
MS <- jsonlite::fromJSON(mechanism_summary_path)
C <- read.csv(confirm_path, stringsAsFactors=FALSE, check.names=FALSE)
CS <- jsonlite::fromJSON(confirm_summary_path)
T <- read.csv(census_path, stringsAsFactors=FALSE, check.names=FALSE)
TS <- jsonlite::fromJSON(census_summary_path)

# Frozen evidence assertions.
stopifnot(nrow(M) == 12, all(tolower(M$evaluable) == "true"), all(tolower(M$beta2_better) == "true"))
stopifnot(abs(median(M$median_hartree_ratio_beta2_over_beta0) -
              MS$mechanism_gate$median_material_hartree_ratio_beta2_over_beta0) < 1e-12)
stopifnot(nrow(C) == 48, all(tolower(C$qoac_certified) == "true"), all(tolower(C$baseline_certified) == "true"), all(tolower(C$safe_guardrail) == "true"))
stopifnot(sum(C$ratio_qoac_over_baseline > 1) == 48)
stopifnot(abs(median(C$ratio_qoac_over_baseline) - CS$median_ratio_qoac_over_best_baseline) < 1e-12)
stopifnot(nrow(T) == 6, all(T$win_fraction == 1))
primary <- T[abs(T$tau - 1e-6) < 1e-15, ]
stopifnot(nrow(primary) == 1, primary$wins == 253, primary$comparable == 253)
stopifnot(abs(primary$median_ratio - 12.462638210336847) < 1e-12)
stopifnot(TS$settings == 6350, TS$failures == 0)

bg <- "#FAFAF8"
ink <- "#1A1A1A"
muted <- "#5E636A"
grid <- "#DDD9D2"
blue <- "#0072B2"
orange <- "#D55E00"
teal <- "#009E73"
purple <- "#7B61A8"

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

# A — exact Hartree operator weighting translated into the frozen quantization law.
q <- 10^seq(log10(0.05), 0, length.out=240)
A <- bind_rows(
  data.frame(q=q, value=q^-4, curve="Hartree sensitivity  |G|^-4"),
  data.frame(q=q, value=q^2, curve="Allowed step  Delta_G ~ |G|^2")
)
A$curve <- factor(A$curve, levels=c(
  "Hartree sensitivity  |G|^-4",
  "Allowed step  Delta_G ~ |G|^2"
))

pA <- ggplot(A, aes(q, value, colour=curve)) +
  geom_line(linewidth=1.15) +
  scale_colour_manual(values=c(
    "Hartree sensitivity  |G|^-4"=purple,
    "Allowed step  Delta_G ~ |G|^2"=teal
  )) +
  scale_x_log10(
    limits=c(.05,1),
    breaks=c(.05,.1,.2,.5,1),
    labels=label_number(accuracy=.01)
  ) +
  scale_y_log10(
    limits=c(1e-3,2e5),
    breaks=10^seq(-2,5,1),
    labels=label_math()
  ) +
  annotate("text", x=.066, y=6e4, label="protect low G", colour=purple,
           fontface="bold", hjust=0, size=3.0) +
  annotate("text", x=.31, y=.055, label="coarsen high G", colour=teal,
           fontface="bold", hjust=0, size=3.0) +
  labs(
    title="A | The Hartree operator defines the distortion geometry",
    subtitle="Normalized at q = 1; the quantizer is derived from the physical Fourier weighting",
    x=expression(q==abs(G)/G[max]),
    y="Relative weight / quantization step"
  ) + theme_qoi +
  theme(legend.position="top", legend.text=element_text(size=8.2))

# B — pre-specified operator-blind ablation.
M <- M %>%
  arrange(median_hartree_ratio_beta2_over_beta0) %>%
  mutate(order=row_number())
med_mech <- median(M$median_hartree_ratio_beta2_over_beta0)

pB <- ggplot(M, aes(x=1, y=median_hartree_ratio_beta2_over_beta0)) +
  geom_hline(yintercept=1, linetype=2, colour="#777777", linewidth=.55) +
  geom_jitter(width=.095, height=0, size=2.5, alpha=.86, colour=purple) +
  annotate("segment", x=.76, xend=1.24, y=med_mech, yend=med_mech,
           linewidth=1.15, colour=ink) +
  annotate("label", x=1.32, y=med_mech,
           label=sprintf("median = %.3f", med_mech),
           hjust=0, size=2.9, label.size=.18, fill=alpha("white",.94)) +
  scale_y_log10(
    limits=c(.035,1.3),
    breaks=c(.05,.1,.2,.5,1),
    labels=label_number(accuracy=.01)
  ) +
  scale_x_continuous(limits=c(.62,1.72), breaks=NULL) +
  labs(
    title="B | Operator-derived beta=2 beats operator-blind beta=0",
    subtitle="12/12 engineering materials; matched serialized storage",
    x=NULL,
    y=expression(D[H](beta==2) / D[H](beta==0))
  ) + theme_qoi + theme(legend.position="none")

# C — disjoint confirmatory cohort.
C <- C %>%
  mutate(system_type=factor(system_type, levels=c("bulk","slab")))
confirm_cols <- c(bulk=blue, slab=orange)
medC <- C %>% group_by(system_type) %>%
  summarise(med=median(ratio_qoac_over_baseline), .groups="drop")

pC <- ggplot(C, aes(system_type, ratio_qoac_over_baseline, colour=system_type, fill=system_type)) +
  geom_hline(yintercept=1, linetype=2, colour="#777777", linewidth=.55) +
  geom_violin(width=.78, alpha=.10, colour=NA, trim=FALSE) +
  geom_boxplot(width=.28, outlier.shape=NA, alpha=.12, linewidth=.55) +
  geom_jitter(width=.13, height=0, size=1.8, alpha=.72) +
  geom_text(
    data=medC, aes(system_type, med, label=sprintf("%.1fx", med)),
    inherit.aes=FALSE, nudge_x=.28, hjust=0, vjust=.5, size=3.0, colour=ink
  ) +
  scale_colour_manual(values=confirm_cols, guide="none") +
  scale_fill_manual(values=confirm_cols, guide="none") +
  scale_y_log10(
    limits=c(.8,230),
    breaks=c(1,2,5,10,20,50,100,200),
    labels=function(x) paste0(x,"x")
  ) +
  labs(
    title="C | The frozen codec wins on unseen materials",
    subtitle="48/48 disjoint confirmatory materials at Hartree relative RMSE < 10^-6",
    x=NULL,
    y="QOAC-H / best certified baseline CR"
  ) + theme_qoi + theme(legend.position="none")

# D — full 254-material census across the frozen Hartree tolerance ladder.
T <- T %>%
  mutate(
    tau_label=factor(
      sprintf("10^%d", round(log10(tau))),
      levels=sprintf("10^%d", -8:-3)
    ),
    denom=sprintf("n=%d", comparable)
  )

pD <- ggplot(T, aes(tau_label, median_ratio)) +
  geom_hline(yintercept=1, linetype=2, colour="#777777", linewidth=.55) +
  geom_linerange(aes(ymin=p05_ratio, ymax=p95_ratio), linewidth=.75, colour="#94B8A9") +
  geom_linerange(aes(ymin=p25_ratio, ymax=p75_ratio), linewidth=3.1, colour=teal, alpha=.50) +
  geom_point(size=3.0, shape=21, stroke=.7, fill=bg, colour=teal) +
  geom_text(aes(label=sprintf("%.1fx", median_ratio)), nudge_y=.11,
            vjust=0, size=2.9, colour=ink) +
  geom_text(aes(y=.78, label=denom), size=2.55, colour=muted) +
  scale_y_log10(
    limits=c(.7,70),
    breaks=c(1,2,5,10,20,50),
    labels=function(x) paste0(x,"x")
  ) +
  labs(
    title="D | The gain persists across the full Hartree contract ladder",
    subtitle="254-material census; thick bars IQR, thin bars P05-P95; denominators are comparable systems",
    x=expression("Hartree relative-RMSE tolerance " * tau[H]),
    y="QOAC-H / best certified baseline CR"
  ) + theme_qoi + theme(legend.position="none")

fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(guides="collect") +
  plot_annotation(
    title="Figure 8 | The downstream operator converts compression diagnosis into design",
    subtitle="QOAC-H allocates reciprocal-space error from the Hartree operator, verifies the allocation against an operator-blind ablation, and preserves the gain on a disjoint cohort and the full development population.",
    caption=paste0(
      "Primary Hartree contract: relative RMSE < 10^-6. Confirmatory cohort: 48/48 wins, median CR ratio 15.016x ",
      "(bootstrap 95% CI 11.204-21.461), with 48/48 Nyquist-safe guardrails passed. ",
      "Full census at 10^-6: 253/253 comparable wins, median 12.463x, P05 4.459x, minimum 2.444x. ",
      "Eligibility and baseline availability define the denominator at each tolerance."
    ),
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=9.5, colour=muted, lineheight=1.05, margin=margin(b=8)),
      plot.caption=element_text(size=8.0, colour=muted, hjust=0, margin=margin(t=7))
    )
  ) & theme(legend.position="top")

png_path <- file.path(outdir, "figure8_qoac_h_R.png")
pdf_path <- file.path(outdir, "figure8_qoac_h_R.pdf")
svg_path <- file.path(outdir, "figure8_qoac_h_R.svg")

ggsave(png_path, fig, width=11.8, height=8.3, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=11.8, height=8.3, device=cairo_pdf, bg=bg)
ggsave(svg_path, fig, width=11.8, height=8.3, device=svglite::svglite, bg=bg)

stopifnot(file.exists(png_path), file.exists(pdf_path), file.exists(svg_path))
message("Rendered Figure 8 QOAC-H: PNG + PDF + SVG")

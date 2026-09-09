# Figure 7 — external confirmation and practical decision frontier
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(scales)
  library(patchwork)
  library(jsonlite)
})

if (!requireNamespace("svglite", quietly=TRUE)) {
  stop("Package 'svglite' is required for the vector SVG export.")
}

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

extdir <- file.path(
  root, "validation", "final_external_confirmatory63_20260908", "confirmatory63"
)
summary_path <- file.path(extdir, "external_summary_a1.csv")
pair_path <- file.path(extdir, "pairwise_external.csv")
best_path <- file.path(extdir, "best_certified_external.csv")
audit_path <- file.path(extdir, "summary.json")
stopifnot(file.exists(summary_path), file.exists(pair_path),
          file.exists(best_path), file.exists(audit_path))

S <- read.csv(summary_path, stringsAsFactors=FALSE, check.names=FALSE)
P <- read.csv(pair_path, stringsAsFactors=FALSE, check.names=FALSE)
B <- read.csv(best_path, stringsAsFactors=FALSE, check.names=FALSE)
A <- jsonlite::fromJSON(audit_path)

pal <- c(
  light_green = "#B8DBB3",
  green       = "#72B063",
  blue        = "#719AAC",
  orange      = "#E29135",
  teal        = "#94C6CD",
  navy        = "#4A5F7E"
)
codec_cols <- c(ZFP=pal[["blue"]], SZ3=pal[["orange"]], SPERR=pal[["teal"]])
bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E7E8EA"; muted <- "#646A73"

codec_label <- function(x) {
  out <- toupper(as.character(x))
  out[out == "SPERR"] <- "SPERR"
  out
}

tau_levels <- c(1e-4, 1e-3, 1e-2)
tau_labels <- c("10^-4", "10^-3", "10^-2")

th <- theme_minimal(base_size=10.2) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink),
  axis.text=element_text(colour=ink),
  plot.title=element_text(face="bold", size=11.0, margin=margin(b=4)),
  plot.subtitle=element_text(size=8.8, colour="#4F545C", margin=margin(b=6)),
  legend.position="top",
  legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

# A — external best-certified rate-fidelity frontier.
a <- S %>%
  filter(stratum == "overall", threshold_e %in% tau_levels) %>%
  mutate(
    codec = factor(codec_label(codec), levels=c("ZFP","SZ3","SPERR")),
    tau = factor(threshold_e, levels=tau_levels, labels=tau_labels)
  )

pA <- ggplot(a, aes(tau, ratio_median, colour=codec, group=codec)) +
  geom_errorbar(aes(ymin=ratio_median_ci_lo, ymax=ratio_median_ci_hi),
                width=.13, linewidth=.7, alpha=.78) +
  geom_line(linewidth=1.05) +
  geom_point(size=2.8) +
  scale_colour_manual(values=codec_cols) +
  scale_y_log10(
    breaks=c(5,10,20,40,80,160),
    labels=label_number(accuracy=.1, suffix="x")
  ) +
  labs(
    title="A | The external cohort reproduces the rate-fidelity transition",
    subtitle="Median best-certified compression ratio; error bars are frozen bootstrap intervals",
    x="Bader contract tau (e)", y="Best-certified compression ratio"
  ) + th

# B — direct ZFP/SZ3 transition with frozen pairwise interval.
b <- P %>%
  filter(stratum == "overall", codec_a == "sz3", codec_b == "zfp",
         threshold_e %in% tau_levels) %>%
  mutate(tau=factor(threshold_e, levels=tau_levels, labels=tau_labels))

pB <- ggplot(b, aes(tau, frac_a_wins)) +
  geom_hline(yintercept=.5, linetype=2, colour="#6B7076", linewidth=.55) +
  geom_errorbar(aes(ymin=a_wins_ci_lo, ymax=a_wins_ci_hi),
                width=.13, linewidth=.75, colour=pal[["orange"]]) +
  geom_line(aes(group=1), linewidth=1.1, colour=pal[["orange"]]) +
  geom_point(size=3.0, colour=pal[["orange"]]) +
  geom_text(aes(label=percent(frac_a_wins, accuracy=1)),
            vjust=-.75, size=3.0, colour=ink) +
  scale_y_continuous(limits=c(0,1), breaks=seq(0,1,.25), labels=label_percent()) +
  labs(
    title="B | The ZFP-SZ3 ordering changes with the scientific tolerance",
    subtitle="Fraction of eligible external materials where SZ3 achieves the higher certified ratio",
    x="Bader contract tau (e)", y="SZ3 win fraction"
  ) + th + theme(legend.position="none")

# C — external replication of nominal-budget non-equivalence.
as_flag <- function(x) x %in% c(TRUE, 1, "1", "TRUE", "True", "true")
c <- B %>%
  filter(as_flag(has_certified_point),
         is.finite(realized_Linf_over_nominal_at_CCR),
         realized_Linf_over_nominal_at_CCR > 0) %>%
  mutate(codec=factor(codec_label(codec), levels=c("ZFP","SZ3","SPERR")))

c_med <- c %>% group_by(codec) %>% summarise(
  med=median(realized_Linf_over_nominal_at_CCR, na.rm=TRUE), .groups="drop"
)

pC <- ggplot(c, aes(codec, realized_Linf_over_nominal_at_CCR, fill=codec, colour=codec)) +
  geom_violin(width=.84, alpha=.28, linewidth=.45, trim=TRUE) +
  geom_boxplot(width=.22, outlier.shape=NA, linewidth=.48, fill="white", alpha=.88) +
  geom_jitter(width=.09, alpha=.22, size=.55, show.legend=FALSE) +
  geom_text(data=c_med, aes(y=med, label=sprintf("median %.2f", med)),
            inherit.aes=FALSE, x=as.numeric(c_med$codec),
            vjust=-1.05, size=2.9, colour=ink) +
  geom_hline(yintercept=1, linetype=2, linewidth=.55, colour="#6B7076") +
  scale_fill_manual(values=codec_cols, guide="none") +
  scale_colour_manual(values=codec_cols, guide="none") +
  scale_y_log10(
    limits=c(.05,1.7),
    breaks=c(.05,.1,.2,.5,1),
    labels=label_number(accuracy=.01)
  ) +
  labs(
    title="C | Nominal tolerance remains a codec-dependent distortion control",
    subtitle="Certified external points; dashed line indicates full use of the nominal L-infinity budget",
    x=NULL, y="Realized L-inf / nominal budget"
  ) + th

# D — eligibility ceiling plus confirmatory audit.
d <- S %>%
  filter(stratum == "overall", codec == "zfp", threshold_e %in% tau_levels) %>%
  mutate(
    tau=factor(threshold_e, levels=tau_levels, labels=tau_labels),
    eligible=n_admitted,
    frac=eligible / A$n_materials_complete
  )

audit_text <- sprintf(
  "%d/%d complete  |  %d material failures  |  %d codec-bound violations\n%d retained scientific rows",
  A$n_materials_complete, A$n_materials_observed,
  A$n_material_pipeline_failures, A$n_bound_violations, A$n_rows
)

pD <- ggplot(d, aes(tau, eligible, group=1)) +
  geom_segment(aes(x=tau, xend=tau, y=0, yend=eligible),
               linewidth=4.4, colour=alpha(pal[["light_green"]], .72)) +
  geom_line(linewidth=1.0, colour=pal[["navy"]]) +
  geom_point(size=3.0, colour=pal[["navy"]]) +
  geom_text(aes(label=sprintf("%d / %d\n(%s)", eligible, A$n_materials_complete,
                              percent(frac, accuracy=1))),
            vjust=-.72, size=3.0, colour=ink) +
  annotate("label", x=1.02, y=61.5, label=audit_text,
           hjust=0, vjust=1, size=2.85, label.size=.18,
           fill=alpha("white", .94), colour=ink) +
  scale_y_continuous(limits=c(0,63), breaks=c(0,20,40,60)) +
  labs(
    title="D | Stability qualification defines the measurable scientific cohort",
    subtitle="Protocol A.1 eligibility rises with the requested Bader tolerance without retuning",
    x="Bader contract tau (e)", y="Eligible external materials"
  ) + th + theme(legend.position="none")

fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(guides="collect") +
  plot_annotation(
    title="Figure 7 | Untouched external systems reproduce the stability-qualified decision frontier",
    subtitle="A pre-frozen 63-system cohort preserves the codec-ordering transition, realized-distortion asymmetry, and Protocol A.1 eligibility logic without retuning.",
    caption="External confirmatory cohort: 63/63 observed systems completed, 1,689 retained scientific rows, zero material-level pipeline failures and zero codec-bound violations. Pairwise intervals and compression-ratio intervals are the frozen external bootstrap summaries.",
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=9.8, colour="#4F545C", margin=margin(b=8)),
      plot.caption=element_text(size=8.1, colour=muted, hjust=0, margin=margin(t=7))
    )
  )

png_path <- file.path(outdir, "figure7_external_confirmation_R.png")
pdf_path <- file.path(outdir, "figure7_external_confirmation_R.pdf")
svg_path <- file.path(outdir, "figure7_external_confirmation_R.svg")

ggsave(png_path, fig, width=11.8, height=8.3, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=11.8, height=8.3, bg=bg)
ggsave(svg_path, fig, width=11.8, height=8.3, bg=bg, device=svglite::svglite)

message("Rendered: ", svg_path)

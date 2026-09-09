# Figure 6 — compression–chemistry tradeoff from the frozen benchmark
#
# Main-text role:
#   nominal control -> realized density perturbation -> QoI response -> chemical certification
#
# This script is intentionally data-driven. It does not hard-code a "winning" codec.
# Panel D defines a certification frontier as the fraction of A.1-eligible materials
# for which at least one certified reconstruction achieves compression ratio >= x.
#
# Inputs:
#   benchmark/master_benchmark_full.csv
# Outputs:
#   figures/R/rendered/figure6_compression_chemistry_tradeoff_R.{png,pdf,svg}

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(scales)
  library(patchwork)
  library(svglite)
})

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

benchf <- file.path(root, "benchmark", "master_benchmark_full.csv")
stopifnot(file.exists(benchf))
d <- read.csv(benchf, check.names=FALSE, stringsAsFactors=FALSE)

required <- c(
  "material_id", "codec", "nominal_tolerance_relative",
  "realized_Linf", "realized_Linf_over_nominal", "value_ptp",
  "compression_ratio", "Bader_error_resolved_e"
)
missing_required <- setdiff(required, names(d))
if (length(missing_required) > 0) {
  stop("Missing required columns: ", paste(missing_required, collapse=", "))
}

as_bool <- function(x) {
  if (is.logical(x)) return(x)
  z <- tolower(trimws(as.character(x)))
  z %in% c("true", "t", "1", "yes", "y")
}

# Publication palette fixed across the manuscript figures.
pal <- c(
  light_green = "#B8DBB3",
  green       = "#72B063",
  blue        = "#719AAC",
  orange      = "#E29135",
  teal        = "#94C6CD",
  navy        = "#4A5F7E"
)
codec_cols <- c(ZFP=pal[["blue"]], SZ3=pal[["orange"]], SPERR=pal[["teal"]])
bg <- "#FAFAF8"
ink <- "#202124"
grid <- "#DEDCD7"
muted <- "#646A73"

codec_levels <- c("ZFP", "SZ3", "SPERR")
d$codec <- factor(d$codec, levels=codec_levels)

# Derived quantities used for fair, realized-error comparisons.
d <- d %>% mutate(
  nominal_rel = suppressWarnings(as.numeric(nominal_tolerance_relative)),
  budget_use = suppressWarnings(as.numeric(realized_Linf_over_nominal)),
  realized_rel = suppressWarnings(as.numeric(realized_Linf)) /
    suppressWarnings(as.numeric(value_ptp)),
  cr = suppressWarnings(as.numeric(compression_ratio)),
  bader_err = suppressWarnings(as.numeric(Bader_error_resolved_e))
)

theme_qoi <- theme_minimal(base_size=10.4) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink),
  axis.text=element_text(colour=ink),
  strip.background=element_rect(fill="#F0F1F0", colour="#C7CBCF", linewidth=.4),
  strip.text=element_text(face="bold", colour=ink),
  plot.title=element_text(face="bold", size=11.1, colour=ink, margin=margin(b=4)),
  plot.subtitle=element_text(size=8.9, colour="#535860", margin=margin(b=6)),
  legend.position="top",
  legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

# -----------------------------------------------------------------------------
# A — nominal error control is not equal realized error-budget usage.
# -----------------------------------------------------------------------------
a <- d %>% filter(
  codec %in% codec_levels,
  is.finite(nominal_rel), nominal_rel > 0,
  is.finite(budget_use), budget_use > 0
)

set.seed(20260909)
a_show <- a %>% group_by(codec) %>% slice_sample(n=min(n(), 1600)) %>% ungroup() %>%
  mutate(nominal_rel_jitter = nominal_rel * 10^runif(n(), -.025, .025))

a_med <- a %>% group_by(codec, nominal_rel) %>%
  summarise(median_budget=median(budget_use, na.rm=TRUE), n=n(), .groups="drop")
overall_budget <- a %>% group_by(codec) %>%
  summarise(med=median(budget_use, na.rm=TRUE), .groups="drop")

budget_label <- paste(
  sprintf("%s %.3g", as.character(overall_budget$codec), overall_budget$med),
  collapse="\n"
)

pA <- ggplot(a_show, aes(nominal_rel_jitter, budget_use, colour=codec)) +
  geom_hline(yintercept=1, linetype=2, colour="#60646A", linewidth=.55) +
  geom_point(alpha=.20, size=.78) +
  geom_line(data=a_med, aes(nominal_rel, median_budget, group=codec),
            inherit.aes=FALSE, colour="#FFFFFF", linewidth=2.5, alpha=.9) +
  geom_line(data=a_med, aes(nominal_rel, median_budget, colour=codec, group=codec),
            inherit.aes=FALSE, linewidth=1.15) +
  geom_point(data=a_med, aes(nominal_rel, median_budget, colour=codec),
             inherit.aes=FALSE, shape=21, fill="white", stroke=.85, size=2.5) +
  scale_colour_manual(values=codec_cols) +
  scale_x_log10(labels=label_math()) +
  scale_y_log10(labels=label_math()) +
  annotate("label",
           x=quantile(a$nominal_rel, .56, na.rm=TRUE),
           y=quantile(a$budget_use, .035, na.rm=TRUE),
           label=paste0("median realized / nominal\n", budget_label),
           hjust=0, vjust=0, size=2.8, label.size=.18,
           fill=alpha("white", .92), colour=ink) +
  labs(
    title="A | Realized error-budget usage differs by codec",
    subtitle="Equal requested tolerance does not imply equal realized perturbation",
    x=expression(Nominal~relative~L[infinity]~tolerance),
    y=expression(Realized/nominal~L[infinity])
  ) + theme_qoi

# -----------------------------------------------------------------------------
# B — fair codec comparison uses realized perturbation, not requested tolerance.
# -----------------------------------------------------------------------------
b <- d %>% filter(
  codec %in% codec_levels,
  is.finite(realized_rel), realized_rel > 0,
  is.finite(cr), cr > 0
)
set.seed(20260909)
b_show <- b %>% group_by(codec) %>% slice_sample(n=min(n(), 1800)) %>% ungroup()

pB <- ggplot(b_show, aes(realized_rel, cr, colour=codec)) +
  geom_point(alpha=.24, size=.78) +
  geom_smooth(method="lm", formula=y~x, se=TRUE, linewidth=1.0, alpha=.10) +
  scale_colour_manual(values=codec_cols) +
  scale_x_log10(labels=label_math()) +
  scale_y_log10(labels=label_math()) +
  labs(
    title="B | Compression ratio should be compared against realized perturbation",
    subtitle="The realized density error removes a major nominal-tolerance confounder",
    x=expression(Realized~L[infinity] / density~ptp),
    y="Compression ratio"
  ) + theme_qoi

# -----------------------------------------------------------------------------
# C — matched realized perturbation still allows broad chemical response.
# -----------------------------------------------------------------------------
c <- d %>% filter(
  codec %in% codec_levels,
  is.finite(realized_rel), realized_rel > 0,
  is.finite(bader_err), bader_err > 0
)
set.seed(20260909)
c_show <- c %>% group_by(codec) %>% slice_sample(n=min(n(), 1800)) %>% ungroup()

# Use a data-driven one-decade matched-perturbation window centred near the
# median log10 realized perturbation; this is visual context, not an inference cut.
mid_log <- median(log10(c$realized_rel), na.rm=TRUE)
window_lo <- 10^(floor(mid_log - .5))
window_hi <- window_lo * 10
cw <- c %>% filter(realized_rel >= window_lo, realized_rel < window_hi)
spread_ratio <- if (nrow(cw) >= 20) {
  q <- quantile(cw$bader_err, c(.10,.90), na.rm=TRUE, names=FALSE)
  if (is.finite(q[1]) && q[1] > 0) q[2]/q[1] else NA_real_
} else NA_real_
spread_text <- if (is.finite(spread_ratio)) {
  sprintf("within highlighted decade:\nBader P90/P10 = %.1fx", spread_ratio)
} else {
  "highlighted decade:\nmatched realized perturbation"
}

pC <- ggplot(c_show, aes(realized_rel, bader_err, colour=codec)) +
  annotate("rect", xmin=window_lo, xmax=window_hi, ymin=-Inf, ymax=Inf,
           fill=pal[["light_green"]], alpha=.22) +
  geom_point(alpha=.26, size=.78) +
  scale_colour_manual(values=codec_cols) +
  scale_x_log10(labels=label_math()) +
  scale_y_log10(labels=label_math()) +
  annotate("label", x=sqrt(window_lo*window_hi),
           y=quantile(c$bader_err, .95, na.rm=TRUE),
           label=spread_text, size=2.8, label.size=.18,
           fill=alpha("white", .92), colour=ink) +
  labs(
    title="C | Similar realized perturbation still yields dispersed Bader response",
    subtitle="Density-error magnitude does not uniquely determine topology-sensitive chemical error",
    x=expression(Realized~L[infinity] / density~ptp),
    y="Bader resolved error (e)"
  ) + theme_qoi

# -----------------------------------------------------------------------------
# D — stability-aware certification frontier versus compression ratio.
# -----------------------------------------------------------------------------
taus <- c("0.0001", "0.001", "0.01")
tau_labels <- c(
  "0.0001" = "tau = 1e-4 e",
  "0.001"  = "tau = 1e-3 e",
  "0.01"   = "tau = 1e-2 e"
)

frontier_parts <- list()
part_i <- 1
for (tau in taus) {
  elig_col <- paste0("eligible_A1_at_", tau)
  cert_col <- paste0("certified_at_", tau)
  if (!all(c(elig_col, cert_col) %in% names(d))) {
    stop("Missing certification columns for tau=", tau)
  }

  z <- d %>%
    filter(codec %in% codec_levels, is.finite(cr), cr > 0) %>%
    mutate(
      eligible_tmp = as_bool(.data[[elig_col]]),
      certified_tmp = as_bool(.data[[cert_col]])
    ) %>%
    group_by(material_id, codec) %>%
    summarise(
      eligible = any(eligible_tmp, na.rm=TRUE),
      max_cert_cr = if (any(certified_tmp, na.rm=TRUE))
        max(cr[certified_tmp], na.rm=TRUE) else 0,
      .groups="drop"
    ) %>%
    filter(eligible)

  positive_max <- z$max_cert_cr[z$max_cert_cr > 0 & is.finite(z$max_cert_cr)]
  if (length(positive_max) < 5) next
  lo <- max(1, as.numeric(quantile(positive_max, .01, na.rm=TRUE)))
  hi <- as.numeric(quantile(positive_max, .99, na.rm=TRUE))
  if (!is.finite(hi) || hi <= lo) hi <- max(positive_max, na.rm=TRUE)
  grid_cr <- 10^seq(log10(lo), log10(hi), length.out=55)

  for (cc in codec_levels) {
    zz <- z %>% filter(as.character(codec) == cc)
    if (nrow(zz) == 0) next
    frontier_parts[[part_i]] <- data.frame(
      tau=tau,
      tau_label=tau_labels[[tau]],
      codec=cc,
      compression_threshold=grid_cr,
      achievable_fraction=vapply(grid_cr, function(g) mean(zz$max_cert_cr >= g), numeric(1)),
      n_eligible=nrow(zz)
    )
    part_i <- part_i + 1
  }
}
frontier <- bind_rows(frontier_parts)
if (nrow(frontier) == 0) stop("Could not construct certification frontiers")
frontier$codec <- factor(frontier$codec, levels=codec_levels)
frontier$tau_label <- factor(frontier$tau_label, levels=unname(tau_labels[taus]))

pD <- ggplot(frontier,
             aes(compression_threshold, achievable_fraction, colour=codec, group=codec)) +
  geom_line(linewidth=1.05) +
  geom_point(data=frontier %>% group_by(tau_label, codec) %>% slice(seq(1,n(),length.out=8)),
             size=1.6) +
  facet_wrap(~tau_label, nrow=1, scales="free_x") +
  scale_colour_manual(values=codec_cols) +
  scale_x_log10(labels=label_math()) +
  scale_y_continuous(limits=c(0,1), labels=label_percent(accuracy=1)) +
  labs(
    title="D | Chemical tolerance reshapes the achievable certification frontier",
    subtitle="Fraction of A.1-eligible materials with a certified row at or above the stated compression ratio",
    x="Required compression ratio",
    y="Certified-achievable material fraction"
  ) + theme_qoi +
  theme(legend.position="bottom")

# -----------------------------------------------------------------------------
# Assemble and export.
# -----------------------------------------------------------------------------
fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(guides="collect", widths=c(1,1.12)) +
  plot_annotation(
    title="Figure 6 | Compression–chemistry tradeoffs depend on realized perturbation, not nominal tolerance alone",
    subtitle="nominal control  ->  realized density perturbation  ->  QoI response  ->  chemical certification",
    caption=paste0(
      "All panels use the frozen development benchmark. Panel D is stability-aware: the denominator contains only Protocol A.1-eligible materials at each chemical tolerance. ",
      "The frontier is an empirical decision curve, not a fitted performance model."
    ),
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=10, colour="#4F545C", margin=margin(b=8)),
      plot.caption=element_text(size=8.1, colour=muted, hjust=0, margin=margin(t=7))
    )
  )

png_path <- file.path(outdir, "figure6_compression_chemistry_tradeoff_R.png")
pdf_path <- file.path(outdir, "figure6_compression_chemistry_tradeoff_R.pdf")
svg_path <- file.path(outdir, "figure6_compression_chemistry_tradeoff_R.svg")

ggsave(png_path, fig, width=12.4, height=8.4, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=12.4, height=8.4, bg=bg)
ggsave(svg_path, fig, width=12.4, height=8.4, bg=bg, device=svglite::svglite)

message("Rendered Figure 6:")
message("  ", png_path)
message("  ", pdf_path)
message("  ", svg_path)

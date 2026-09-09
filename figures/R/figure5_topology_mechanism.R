# Figure 5 — topology-induced amplification in re-solved Bader response
#
# This script replaces the earlier illustrative mock with a data-driven version.
# It preserves the manuscript palette used by Figures 2, 3, 4, and 6.
#
# Inputs:
#   benchmark/master_benchmark_full.csv
#   mechanism/basin_error_decomposition_summary.csv
#   mechanism/basin_error_decomposition_per_atom.csv
# Outputs:
#   figures/R/rendered/figure5_topology_mechanism_R.{png,pdf,svg}

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
sumf <- file.path(root, "mechanism", "basin_error_decomposition_summary.csv")
atomf <- file.path(root, "mechanism", "basin_error_decomposition_per_atom.csv")
stopifnot(file.exists(benchf), file.exists(sumf), file.exists(atomf))

bench <- read.csv(benchf, check.names=FALSE, stringsAsFactors=FALSE)
ms <- read.csv(sumf, check.names=FALSE, stringsAsFactors=FALSE)
ma <- read.csv(atomf, check.names=FALSE, stringsAsFactors=FALSE)

needed_bench <- c(
  "material_id", "codec", "realized_Linf", "value_ptp",
  "Bader_error_fixed_e", "Bader_error_resolved_e", "frac_voxels_reassigned"
)
miss <- setdiff(needed_bench, names(bench))
if (length(miss) > 0) stop("Benchmark missing columns: ", paste(miss, collapse=", "))

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

normalize_codec <- function(x) toupper(as.character(x))
bench$codec <- factor(normalize_codec(bench$codec), levels=c("ZFP","SZ3","SPERR"))
ms$codec <- factor(normalize_codec(ms$codec), levels=c("ZFP","SZ3","SPERR"))
ma$codec <- factor(normalize_codec(ma$codec), levels=c("ZFP","SZ3","SPERR"))

bench <- bench %>% mutate(
  realized_rel = suppressWarnings(as.numeric(realized_Linf)) /
    suppressWarnings(as.numeric(value_ptp)),
  fixed_err = suppressWarnings(as.numeric(Bader_error_fixed_e)),
  resolved_err = suppressWarnings(as.numeric(Bader_error_resolved_e)),
  reassign_frac = suppressWarnings(as.numeric(frac_voxels_reassigned))
)

base_theme <- theme_minimal(base_size=10.3) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink), axis.text=element_text(colour=ink),
  strip.background=element_rect(fill="#F0F1F0", colour="#C7CBCF", linewidth=.4),
  strip.text=element_text(face="bold", colour=ink),
  plot.title=element_text(face="bold", size=11.0, colour=ink, margin=margin(b=4)),
  plot.subtitle=element_text(size=8.8, colour="#535860", margin=margin(b=6)),
  legend.position="top", legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

# -----------------------------------------------------------------------------
# A — fixed-basin/integrand-only error versus re-solved total error.
# Mechanism summary is limited to the frozen representative mechanism corpus.
# -----------------------------------------------------------------------------
a <- ms %>% transmute(
  material_id, codec, domain, relative_tolerance,
  total=abs(as.numeric(dq_total_max_e)),
  integrand=abs(as.numeric(dq_integrand_max_e)),
  domain_term=abs(as.numeric(dq_domain_max_e)),
  reassign=as.numeric(frac_voxels_reassigned)
) %>% filter(
  is.finite(total), total > 0,
  is.finite(integrand), integrand > 0,
  is.finite(reassign), reassign >= 0
)

pA <- ggplot(a, aes(integrand, total, colour=reassign)) +
  geom_abline(slope=1, intercept=0, linetype=2, colour="#595D63", linewidth=.6) +
  geom_point(size=2.0, alpha=.78) +
  scale_x_log10(labels=label_math()) +
  scale_y_log10(labels=label_math()) +
  scale_colour_gradient(low=pal[["light_green"]], high=pal[["green"]],
                        trans="sqrt", name="Reassigned\nvoxel fraction") +
  labs(
    title="A | Re-solving the basins can amplify fixed-basin perturbation",
    subtitle="Representative mechanism corpus; identity line marks equal integrand-only and total error",
    x="Integrand / fixed-basin contribution (e)",
    y="Re-solved total Bader error (e)"
  ) + base_theme

# -----------------------------------------------------------------------------
# B — signed per-atom decomposition into integrand and domain contributions.
# A pseudo-log scale preserves signs while retaining the order-of-magnitude view.
# -----------------------------------------------------------------------------
b <- ma %>% transmute(
  material_id, codec, domain, atom_index, element,
  integrand=as.numeric(dq_integrand_e),
  domain_term=as.numeric(dq_domain_e),
  total=as.numeric(dq_total_e)
) %>% filter(is.finite(integrand), is.finite(domain_term), is.finite(total)) %>%
  mutate(class=ifelse(abs(total) >= 1e-3, "Large deviation", "Typical"))

pB <- ggplot(b, aes(integrand, domain_term, colour=class)) +
  geom_hline(yintercept=0, linetype=2, colour="#6A6E74", linewidth=.45) +
  geom_vline(xintercept=0, linetype=2, colour="#6A6E74", linewidth=.45) +
  geom_point(alpha=.48, size=.80) +
  scale_x_continuous(trans=pseudo_log_trans(base=10, sigma=1e-7), labels=label_scientific()) +
  scale_y_continuous(trans=pseudo_log_trans(base=10, sigma=1e-7), labels=label_scientific()) +
  scale_colour_manual(values=c("Typical"=pal[["navy"]], "Large deviation"=pal[["orange"]])) +
  labs(
    title="B | Large atomic deviations expose the domain-migration term",
    subtitle=expression(Delta*q[total] == Delta*q[integrand] + Delta*q[domain]),
    x="Integrand contribution (e)",
    y="Domain-migration contribution (e)"
  ) + base_theme

# -----------------------------------------------------------------------------
# Build full-ladder local jump diagnostics from the frozen benchmark.
# -----------------------------------------------------------------------------
step_rows <- bench %>% filter(
  codec %in% c("ZFP","SZ3","SPERR"),
  is.finite(realized_rel), realized_rel > 0,
  is.finite(resolved_err), resolved_err > 0,
  is.finite(reassign_frac), reassign_frac >= 0
) %>%
  arrange(material_id, codec, realized_rel) %>%
  group_by(material_id, codec) %>%
  mutate(
    prev_err=lag(resolved_err),
    prev_rel=lag(realized_rel),
    jump_factor=ifelse(
      is.finite(prev_err) & prev_err > 0,
      pmax(resolved_err/prev_err, prev_err/resolved_err),
      NA_real_
    )
  ) %>% ungroup()

pair_summary <- step_rows %>% group_by(material_id, codec) %>%
  summarise(
    n=sum(is.finite(resolved_err)),
    max_jump=max(jump_factor, na.rm=TRUE),
    .groups="drop"
  ) %>% filter(n >= 5, is.finite(max_jump), max_jump >= 1)

if (nrow(pair_summary) < 3) stop("Insufficient full-ladder pairs for representative trajectories")

# Prefer ZFP because the largest frozen jump is in ZFP and it supplies the broadest
# illustrative jump range; fall back to all codecs if necessary.
select_pool <- pair_summary %>% filter(as.character(codec) == "ZFP")
if (nrow(select_pool) < 3) select_pool <- pair_summary
select_pool <- select_pool %>% arrange(max_jump)
idx <- unique(pmax(1, pmin(nrow(select_pool), c(
  1,
  round((nrow(select_pool)+1)/2),
  nrow(select_pool)
))))
while (length(idx) < 3) idx <- unique(c(idx, seq_len(nrow(select_pool))))
idx <- idx[1:3]
chosen <- select_pool[idx, ] %>% arrange(max_jump) %>%
  mutate(case=c("Smooth case", "Intermediate case", "Jump case"))

rep <- bench %>% inner_join(chosen %>% select(material_id, codec, case),
                            by=c("material_id","codec")) %>%
  filter(
    is.finite(realized_rel), realized_rel > 0,
    is.finite(fixed_err), fixed_err > 0,
    is.finite(resolved_err), resolved_err > 0
  ) %>%
  arrange(case, realized_rel) %>%
  select(material_id, codec, case, realized_rel, fixed_err, resolved_err, reassign_frac) %>%
  pivot_longer(c(fixed_err, resolved_err), names_to="evaluation", values_to="error_e") %>%
  mutate(
    evaluation=recode(evaluation,
                      fixed_err="Fixed-basin",
                      resolved_err="Re-solved Bader"),
    case=factor(case, levels=c("Smooth case","Intermediate case","Jump case"))
  )

pC <- ggplot(rep, aes(realized_rel, error_e, colour=evaluation, group=evaluation)) +
  geom_line(linewidth=.82) +
  geom_point(aes(size=pmax(reassign_frac, 0)), alpha=.86) +
  facet_wrap(~case, ncol=1, scales="free_y") +
  scale_x_log10(labels=label_math()) +
  scale_y_log10(labels=label_math()) +
  scale_colour_manual(values=c("Fixed-basin"=pal[["teal"]],
                               "Re-solved Bader"=pal[["orange"]])) +
  scale_size_continuous(range=c(1.2,4.0), trans="sqrt", guide="none") +
  labs(
    title="C | Representative ladders separate smooth integrand change from abrupt re-solving",
    subtitle="Point size encodes the fraction of voxels reassigned by the Bader partition",
    x=expression(Realized~L[infinity] / density~ptp),
    y="Bader error (e)"
  ) + base_theme + theme(legend.position="bottom")

# -----------------------------------------------------------------------------
# D — rung-to-rung jump severity versus basin reassignment.
# Use association language rather than causal language.
# -----------------------------------------------------------------------------
dd <- step_rows %>% filter(
  is.finite(jump_factor), jump_factor >= 1,
  is.finite(reassign_frac), reassign_frac > 0
)
set.seed(20260909)
dd_show <- dd %>% group_by(codec) %>% slice_sample(n=min(n(), 1500)) %>% ungroup()
rho <- suppressWarnings(cor(log10(dd$reassign_frac), log10(dd$jump_factor),
                            method="spearman", use="complete.obs"))

pD <- ggplot(dd_show, aes(reassign_frac, jump_factor, colour=codec)) +
  geom_point(alpha=.25, size=.72) +
  geom_smooth(method="lm", formula=y~x, se=FALSE, linewidth=.9) +
  scale_colour_manual(values=codec_cols) +
  scale_x_log10(labels=label_math()) +
  scale_y_log10(labels=label_math()) +
  annotate("label",
           x=quantile(dd$reassign_frac, .06, na.rm=TRUE),
           y=quantile(dd$jump_factor, .95, na.rm=TRUE),
           label=sprintf("Spearman rho = %.2f", rho),
           hjust=0, size=2.8, label.size=.18,
           fill=alpha("white", .92), colour=ink) +
  labs(
    title="D | Larger basin reassignment accompanies larger rung-to-rung Bader jumps",
    subtitle="Full frozen benchmark; trend is descriptive association, not a causal fit",
    x="Reassigned voxel fraction",
    y="Consecutive Bader-error jump factor"
  ) + base_theme

fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(guides="collect", widths=c(1,1)) +
  plot_annotation(
    title="Figure 5 | Topology-induced amplification explains irregular Bader response",
    subtitle="re-solved Bader error = integrand perturbation + topology-driven domain migration",
    caption=paste0(
      "Panels A–B use the frozen representative mechanism decomposition; Panels C–D use the full frozen benchmark. ",
      "Figure 5 supports a Bader-specific topological mechanism and should not be generalized to all downstream QoIs."
    ),
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=10, colour="#4F545C", margin=margin(b=8)),
      plot.caption=element_text(size=8.1, colour=muted, hjust=0, margin=margin(t=7))
    )
  )

png_path <- file.path(outdir, "figure5_topology_mechanism_R.png")
pdf_path <- file.path(outdir, "figure5_topology_mechanism_R.pdf")
svg_path <- file.path(outdir, "figure5_topology_mechanism_R.svg")

ggsave(png_path, fig, width=12.4, height=8.8, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=12.4, height=8.8, bg=bg)
ggsave(svg_path, fig, width=12.4, height=8.8, bg=bg, device=svglite::svglite)

message("Rendered Figure 5:")
message("  ", png_path)
message("  ", pdf_path)
message("  ", svg_path)

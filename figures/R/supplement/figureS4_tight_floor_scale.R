# Supplementary Figure S4 — strict certified regime relative to the Protocol A.1 floor
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(scales)
  library(patchwork)
})
if (!requireNamespace("svglite", quietly = TRUE)) stop("Package 'svglite' is required for SVG export.")

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

master <- read.csv(file.path(root, "benchmark", "master_benchmark_full.csv"), stringsAsFactors = FALSE)
tight <- read.csv(file.path(root, "benchmark", "master_benchmark_tight_ladder.csv"), stringsAsFactors = FALSE)
sum_floor <- read.csv(file.path(root, "supplement", "S2_floor_relative.csv"), stringsAsFactors = FALSE)

stopifnot(nrow(master) == 6343)
stopifnot(nrow(tight) == 1716)
stopifnot(all(c("material_id", "codec", "compression_ratio", "Bader_error_resolved_e", "stability_floor_A1_e") %in% names(master)))

codec_levels <- c("ZFP", "SZ3", "SPERR")
codec_cols <- c(ZFP = "#4A5F7E", SZ3 = "#D55E00", SPERR = "#2A9D8F")
bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E5E7EB"; muted <- "#5F6368"; red <- "#D94B41"

theme_si <- theme_minimal(base_size = 10.4) + theme(
  plot.background = element_rect(fill = bg, colour = NA),
  panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(),
  panel.grid.major = element_line(colour = grid, linewidth = .3),
  axis.title = element_text(colour = ink), axis.text = element_text(colour = ink),
  plot.title = element_text(face = "bold", size = 11.2, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 9.0, colour = muted, margin = margin(b = 6)),
  legend.title = element_blank(), legend.text = element_text(size = 8.8),
  plot.margin = margin(8, 10, 8, 8)
)

to_logical <- function(x) {
  if (is.logical(x)) return(x)
  tolower(as.character(x)) %in% c("true", "t", "1")
}

# Reconstruct one highest-rate certified operating point per material-codec-threshold.
tau_specs <- data.frame(
  threshold_e = c(1e-4, 1e-3, 1e-2),
  suffix = c("0.0001", "0.001", "0.01"),
  tau_label = c("10^-4 e", "10^-3 e", "10^-2 e"),
  stringsAsFactors = FALSE
)

best_list <- lapply(seq_len(nrow(tau_specs)), function(i) {
  tau <- tau_specs$threshold_e[i]
  suffix <- tau_specs$suffix[i]
  cert_col <- paste0("certified_at_", suffix)
  stopifnot(cert_col %in% names(master))
  flag <- to_logical(master[[cert_col]])
  master %>%
    mutate(.cert = flag) %>%
    filter(.cert, is.finite(compression_ratio), is.finite(Bader_error_resolved_e),
           is.finite(stability_floor_A1_e), stability_floor_A1_e > 0) %>%
    group_by(material_id, codec) %>%
    slice_max(order_by = compression_ratio, n = 1, with_ties = FALSE) %>%
    ungroup() %>%
    mutate(threshold_e = tau, tau_label = tau_specs$tau_label[i], dq_over_floor = Bader_error_resolved_e / stability_floor_A1_e)
})
best <- bind_rows(best_list) %>% mutate(codec = factor(toupper(codec), levels = codec_levels), tau_label = factor(tau_label, levels = tau_specs$tau_label))

# Frozen S2 counts/medians must reproduce from the master table selection.
derived <- best %>% group_by(threshold_e, codec) %>% summarise(
  n = n(),
  median = median(dq_over_floor),
  p10 = quantile(dq_over_floor, .10),
  p90 = quantile(dq_over_floor, .90),
  .groups = "drop"
) %>% arrange(threshold_e, codec)
expected <- sum_floor %>% transmute(
  threshold_e,
  codec = factor(toupper(codec), levels = codec_levels),
  n,
  median = dq_over_floor_median,
  p10 = dq_over_floor_p10,
  p90 = dq_over_floor_p90
) %>% arrange(threshold_e, codec)
stopifnot(identical(as.integer(derived$n), as.integer(expected$n)))
stopifnot(max(abs(derived$median - expected$median)) < 1e-9)

# Panel A: compact frozen S2 summary.
plot_sum <- expected %>%
  mutate(tau_label = factor(threshold_e, levels = tau_specs$threshold_e, labels = tau_specs$tau_label))

pA <- ggplot(plot_sum, aes(tau_label, median, colour = codec, group = codec)) +
  geom_hline(yintercept = 1, linetype = 2, colour = "#9AA0A6", linewidth = .6) +
  geom_linerange(aes(ymin = p10, ymax = p90), position = position_dodge(width = .26), linewidth = .75) +
  geom_point(position = position_dodge(width = .26), size = 2.8) +
  scale_colour_manual(values = codec_cols) +
  scale_y_log10(labels = label_number(accuracy = .1)) +
  labs(
    title = "A | Certified Bader error is floor-scale only at the strictest contract",
    subtitle = "Median with P10-P90; one highest-rate certified point per material-codec pair",
    x = "Bader certification threshold", y = "Re-derived Bader error / Protocol A.1 floor"
  ) + theme_si + theme(legend.position = "top")

# Panel B: raw strict-contract relationship.
strict <- best %>% filter(threshold_e == 1e-4) %>% mutate(
  floor_plot = pmax(stability_floor_A1_e, 1e-12),
  error_plot = pmax(Bader_error_resolved_e, 1e-12)
)
stopifnot(nrow(strict) == 123)

pB <- ggplot(strict, aes(floor_plot, error_plot, colour = codec)) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, linewidth = .65, colour = "#70757A") +
  geom_point(size = 1.8, alpha = .68) +
  scale_colour_manual(values = codec_cols) +
  scale_x_log10(labels = label_scientific(digits = 1)) +
  scale_y_log10(labels = label_scientific(digits = 1)) +
  coord_equal() +
  labs(
    title = "B | Strict certified points lie near the independent floor scale",
    subtitle = "10^-4 e contract; n = 123 material-codec decisions",
    x = "Protocol A.1 stability floor (e)", y = "Best-certified re-derived Bader error (e)"
  ) + theme_si + theme(legend.position = "top")

# Panel C: full tight-ladder diagnostic, deliberately not a plateau estimator.
tight2 <- tight %>%
  filter(is.finite(Bader_error_resolved_e), is.finite(stability_floor_A1_e), stability_floor_A1_e > 0) %>%
  mutate(
    codec = factor(toupper(codec), levels = codec_levels),
    dq_over_floor = pmax(Bader_error_resolved_e / stability_floor_A1_e, 1e-6)
  )
tight_summary <- tight2 %>%
  group_by(codec, nominal_tolerance_relative) %>%
  summarise(
    median = median(dq_over_floor),
    q25 = quantile(dq_over_floor, .25),
    q75 = quantile(dq_over_floor, .75),
    n = n(), .groups = "drop"
  )

pC <- ggplot(tight_summary, aes(nominal_tolerance_relative, median, colour = codec, fill = codec)) +
  geom_hline(yintercept = 1, linetype = 2, colour = "#9AA0A6", linewidth = .6) +
  geom_ribbon(aes(ymin = q25, ymax = q75), alpha = .12, colour = NA) +
  geom_line(linewidth = .9) + geom_point(size = 2.4) +
  scale_colour_manual(values = codec_cols) + scale_fill_manual(values = codec_cols) +
  scale_x_log10(breaks = c(1e-7, 3e-7, 1e-6, 3e-6), labels = label_scientific(digits = 1)) +
  scale_y_log10(labels = label_number()) +
  labs(
    title = "C | Tight-ladder response remains heterogeneous relative to the floor",
    subtitle = "Median and IQR across the frozen tight-ladder materials; descriptive, not a plateau fit",
    x = "Nominal relative codec tolerance", y = "Re-derived Bader error / Protocol A.1 floor"
  ) + theme_si + theme(legend.position = "top")

fig <- ((pA | pB) / pC) +
  plot_layout(heights = c(1.05, .85)) +
  plot_annotation(
    title = "Supplementary Figure S4 | The strictest certified Bader regime is floor-scale, not a universal plateau",
    subtitle = "Independent Protocol A.1 stability floors provide the numerical reference scale; certified compression error increasingly exceeds that scale at looser contracts.",
    caption = "A, frozen error/floor summaries for certified points. B, strict-contract material-level relationship. C, full tight-ladder diagnostic. These data are consistent with an emerging analysis-limited regime at 10^-4 e but do not establish a universal material-level identity between a compression plateau and the A.1 floor.",
    theme = theme(plot.background = element_rect(fill = bg, colour = NA),
                  plot.title = element_text(face = "bold", size = 13.8, colour = ink, margin = margin(b = 4)),
                  plot.subtitle = element_text(size = 9.4, colour = muted, margin = margin(b = 8)),
                  plot.caption = element_text(size = 8.0, colour = muted, hjust = 0, margin = margin(t = 8)))
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS4_tight_floor_scale_R.png"),
  pdf = file.path(outdir, "supplementary_figureS4_tight_floor_scale_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS4_tight_floor_scale_R.svg")
)
ggsave(paths[["png"]], fig, width = 12.8, height = 8.7, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 12.8, height = 8.7, bg = bg)
ggsave(paths[["svg"]], fig, width = 12.8, height = 8.7, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S4: PNG + PDF + SVG")

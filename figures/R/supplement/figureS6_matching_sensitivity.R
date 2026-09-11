# Supplementary Figure S6 — realized-Linf matching sensitivity
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(scales)
  library(patchwork)
})
if (!requireNamespace("svglite", quietly = TRUE)) stop("Package 'svglite' is required for SVG export.")

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

d <- read.csv(file.path(root, "supplement", "S12_matching_sensitivity.csv"), stringsAsFactors = FALSE)
stopifnot(nrow(d) == 12)
stopifnot(all(sort(unique(d$caliper_dex)) == c(0.05, 0.10, 0.20, 0.30)))
stopifnot(all(c("ZFP/SZ3", "ZFP/SPERR", "SZ3/SPERR") %in% d$pair_label))

# Frozen primary assertions.
pri <- d %>% filter(abs(caliper_dex - 0.10) < 1e-12)
stopifnot(nrow(pri) == 3)
stopifnot(abs(pri$resolved_bader_ratio[pri$pair_label == "ZFP/SZ3"] - 0.5574478963397762) < 1e-10)
stopifnot(abs(pri$resolved_bader_ratio[pri$pair_label == "ZFP/SPERR"] - 0.6007474002367663) < 1e-10)
stopifnot(abs(pri$resolved_bader_ratio[pri$pair_label == "SZ3/SPERR"] - 1.0325070260736608) < 1e-10)
stopifnot(pri$n_pairs[pri$pair_label == "ZFP/SZ3"] == 457)
stopifnot(pri$n_materials[pri$pair_label == "ZFP/SZ3"] == 214)

pair_levels <- c("ZFP/SZ3", "ZFP/SPERR", "SZ3/SPERR")
pair_cols <- c("ZFP/SZ3" = "#4A5F7E", "ZFP/SPERR" = "#D55E00", "SZ3/SPERR" = "#2A9D8F")
d <- d %>% mutate(pair_label = factor(pair_label, levels = pair_levels))

bg <- "#FFFFFF"; ink <- "#202124"; muted <- "#5F6368"; grid <- "#E5E7EB"
base_theme <- theme_minimal(base_size = 10.4) + theme(
  plot.background = element_rect(fill = bg, colour = NA),
  panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(),
  panel.grid.major = element_line(colour = grid, linewidth = .3),
  axis.title = element_text(colour = ink),
  axis.text = element_text(colour = ink),
  legend.title = element_blank(),
  legend.text = element_text(size = 8.8),
  plot.title = element_text(face = "bold", size = 10.8, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 8.5, colour = muted, margin = margin(b = 6)),
  plot.margin = margin(8, 10, 8, 8)
)

# A — scientific effect stability across matching calipers.
pA <- ggplot(d, aes(caliper_dex, resolved_bader_ratio, colour = pair_label, group = pair_label)) +
  geom_hline(yintercept = 1, linetype = 2, colour = "#70757A", linewidth = .65) +
  geom_vline(xintercept = 0.10, linetype = 3, colour = "#9AA0A6", linewidth = .55) +
  geom_ribbon(aes(ymin = resolved_ci_low, ymax = resolved_ci_high, fill = pair_label), alpha = .10, colour = NA) +
  geom_line(linewidth = .9) +
  geom_point(size = 2.5) +
  scale_colour_manual(values = pair_cols) +
  scale_fill_manual(values = pair_cols) +
  scale_x_continuous(breaks = c(.05,.10,.20,.30), labels = number_format(accuracy = .01)) +
  labs(
    title = "A | Matched Bader effects are stable across calipers",
    subtitle = "95% material-bootstrap CI; vertical line marks the primary 0.10-dex analysis",
    x = "Matching caliper in log10(realized L-infinity) (dex)",
    y = "Re-derived Bader-error ratio"
  ) + base_theme + theme(legend.position = "top")

# B — common support expands as the caliper is relaxed.
pB <- ggplot(d, aes(caliper_dex, n_materials, colour = pair_label, group = pair_label)) +
  geom_vline(xintercept = 0.10, linetype = 3, colour = "#9AA0A6", linewidth = .55) +
  geom_line(linewidth = .9) +
  geom_point(size = 2.5) +
  scale_colour_manual(values = pair_cols) +
  scale_x_continuous(breaks = c(.05,.10,.20,.30), labels = number_format(accuracy = .01)) +
  scale_y_continuous(breaks = c(100,150,200,250)) +
  labs(
    title = "B | Wider calipers increase common support",
    subtitle = "SZ3/SPERR is matched throughout; ZFP comparisons gain materials as the caliper widens",
    x = "Matching caliper (dex)", y = "Materials represented"
  ) + base_theme + theme(legend.position = "top")

# C — matching quality / actual realized-distortion imbalance.
pC <- ggplot(d, aes(caliper_dex, median_linf_ratio_larger_over_smaller, colour = pair_label, group = pair_label)) +
  geom_hline(yintercept = 1, linetype = 2, colour = "#70757A", linewidth = .65) +
  geom_vline(xintercept = 0.10, linetype = 3, colour = "#9AA0A6", linewidth = .55) +
  geom_ribbon(aes(ymin = median_linf_ratio_larger_over_smaller, ymax = p95_linf_ratio_larger_over_smaller, fill = pair_label), alpha = .10, colour = NA) +
  geom_line(linewidth = .9) +
  geom_point(size = 2.5) +
  scale_colour_manual(values = pair_cols) +
  scale_fill_manual(values = pair_cols) +
  scale_x_continuous(breaks = c(.05,.10,.20,.30), labels = number_format(accuracy = .01)) +
  labs(
    title = "C | The primary match keeps realized perturbations close",
    subtitle = "Line shows the median larger/smaller realized L-infinity; ribbon extends to P95",
    x = "Matching caliper (dex)", y = "Larger / smaller realized L-infinity"
  ) + base_theme + theme(legend.position = "top")

fig <- ((pA | pB) / pC) +
  plot_layout(heights = c(1.0, .82)) +
  plot_annotation(
    title = "Supplementary Figure S6 | Realized-distortion matching conclusions are robust to the caliper choice",
    subtitle = "The primary 0.10-dex analysis balances support and distortion similarity; ZFP retains lower re-derived Bader error than SZ3/SPERR after matching, whereas SZ3 and SPERR remain similar.",
    caption = paste0(
      "A, re-derived Bader-error ratios across all pre-specified calipers; values below one favour the numerator codec. ",
      "B, material common support. C, residual realized-L-infinity imbalance among matched pairs.\n",
      "Matching controls scalar maximum perturbation but not the full geometry of the error field; the residual codec effect is consistent with an error-structure contribution but does not identify a unique spatial invariant."
    ),
    theme = theme(
      plot.background = element_rect(fill = bg, colour = NA),
      plot.title = element_text(face = "bold", size = 13.8, colour = ink, margin = margin(b = 4)),
      plot.subtitle = element_text(size = 9.3, colour = muted, margin = margin(b = 8)),
      plot.caption = element_text(size = 7.8, colour = muted, hjust = 0, lineheight = 1.15, margin = margin(t = 8))
    )
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS6_matching_sensitivity_R.png"),
  pdf = file.path(outdir, "supplementary_figureS6_matching_sensitivity_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS6_matching_sensitivity_R.svg")
)
ggsave(paths[["png"]], fig, width = 12.8, height = 8.6, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 12.8, height = 8.6, bg = bg)
ggsave(paths[["svg"]], fig, width = 12.8, height = 8.6, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S6: PNG + PDF + SVG")
# Supplementary Figure S3 — extended electron-count and Hartree operator controls
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

bench <- read.csv(file.path(root, "benchmark", "master_benchmark_full.csv"), stringsAsFactors = FALSE)
smooth <- read.csv(file.path(root, "analysis", "hartree_potential_expansion", "material_smoothness.csv"), stringsAsFactors = FALSE)
disp <- read.csv(file.path(root, "analysis", "hartree_potential_expansion", "matched_error_dispersion.csv"), stringsAsFactors = FALSE)

stopifnot(nrow(bench) == 6343)
stopifnot(all(c("electron_count_abs_dev", "Bader_error_resolved_e", "codec", "system_type") %in% names(bench)))
stopifnot(all(c("hartree_R2", "bader_R2", "hartree_monotone", "bader_monotone", "codec", "system_type") %in% names(smooth)))
stopifnot(all(c("codec", "system_type", "hartree_log10_bin_left", "n", "bader_p90_over_p10") %in% names(disp)))

codec_levels <- c("ZFP", "SZ3", "SPERR")
codec_cols <- c(ZFP = "#4A5F7E", SZ3 = "#D55E00", SPERR = "#2A9D8F")
bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E5E7EB"; muted <- "#5F6368"; red <- "#D94B41"

theme_si <- theme_minimal(base_size = 10.3) + theme(
  plot.background = element_rect(fill = bg, colour = NA),
  panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(),
  panel.grid.major = element_line(colour = grid, linewidth = .3),
  axis.title = element_text(colour = ink), axis.text = element_text(colour = ink),
  plot.title = element_text(face = "bold", size = 10.8, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 8.8, colour = muted, margin = margin(b = 6)),
  legend.title = element_blank(), legend.text = element_text(size = 8.7),
  strip.text = element_text(face = "bold", colour = ink),
  strip.background = element_rect(fill = "#F8FAFC", colour = NA),
  plot.margin = margin(8, 10, 8, 8)
)

# Panel A: global electron-number conservation does not certify local Bader fidelity.
e <- bench %>%
  filter(is.finite(electron_count_abs_dev), is.finite(Bader_error_resolved_e)) %>%
  mutate(
    electron_plot = pmax(electron_count_abs_dev, 1e-12),
    bader_plot = pmax(Bader_error_resolved_e, 1e-12)
  )
ngood <- sum(e$electron_count_abs_dev < 1e-4)
ndecoupled <- sum(e$electron_count_abs_dev < 1e-4 & e$Bader_error_resolved_e >= 1e-3)
stopifnot(ngood == 3205, ndecoupled == 1383)

pA <- ggplot(e, aes(electron_plot, bader_plot)) +
  geom_bin_2d(bins = 48) +
  geom_vline(xintercept = 1e-4, linetype = 2, linewidth = .65, colour = red) +
  geom_hline(yintercept = 1e-3, linetype = 2, linewidth = .65, colour = red) +
  scale_x_log10(labels = label_scientific(digits = 1)) +
  scale_y_log10(labels = label_scientific(digits = 1)) +
  scale_fill_gradient(low = "#F1F4F7", high = "#4A5F7E", trans = "log10") +
  annotate("label", x = 2e-11, y = max(e$bader_plot, na.rm = TRUE) / 2,
           hjust = 0, vjust = 1, size = 3.0, label.size = .2, fill = alpha("white", .95),
           label = sprintf("|Delta Ne| < 10^-4 e but Bader >= 10^-3 e\n%d / %d = %.2f%%", ndecoupled, ngood, 100 * ndecoupled / ngood)) +
  labs(
    title = "A | Global electron conservation does not certify local Bader fidelity",
    subtitle = "All finite development reconstructions; dashed lines mark the negative-control thresholds",
    x = "Absolute electron-count deviation (e)", y = "Re-derived Bader error (e)", fill = "Rows"
  ) + theme_si + theme(legend.position = "right")

# Normalize logical columns defensively for CSV readers.
to_logical <- function(x) {
  if (is.logical(x)) return(x)
  tolower(as.character(x)) %in% c("true", "t", "1")
}
smooth <- smooth %>%
  mutate(
    codec = factor(toupper(codec), levels = codec_levels),
    system_type = factor(system_type, levels = c("bulk", "slab"), labels = c("Bulk", "Slab")),
    hartree_monotone = to_logical(hartree_monotone),
    bader_monotone = to_logical(bader_monotone)
  )
stopifnot(nrow(smooth) == 678)

# Panel B: paired material-level smoothness.
pB <- ggplot(smooth, aes(bader_R2, hartree_R2, colour = codec)) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, linewidth = .55, colour = "#9AA0A6") +
  geom_point(alpha = .48, size = 1.5) +
  scale_colour_manual(values = codec_cols) +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  labs(
    title = "B | Hartree fits are smoother than Bader fits",
    subtitle = "Paired material-codec ladder fits; n = 678",
    x = expression(Bader~R^2), y = expression(Hartree~R^2)
  ) + theme_si + theme(legend.position = "top")

# Panel C: preserve the slab monotonicity caveat rather than hiding it.
mono <- smooth %>%
  group_by(codec, system_type) %>%
  summarise(Hartree = mean(hartree_monotone), Bader = mean(bader_monotone), n = n(), .groups = "drop") %>%
  pivot_longer(c(Hartree, Bader), names_to = "operator", values_to = "fraction") %>%
  mutate(operator = factor(operator, levels = c("Bader", "Hartree")))

pC <- ggplot(mono, aes(operator, fraction, colour = codec, group = codec)) +
  geom_line(linewidth = .85) + geom_point(size = 2.6) +
  facet_wrap(~ system_type, nrow = 1) +
  scale_colour_manual(values = codec_cols) +
  scale_y_continuous(limits = c(0, 1), labels = label_percent(), breaks = seq(0, 1, .2), expand = c(0, 0)) +
  labs(
    title = "C | Strict monotonicity retains a bulk/slab nuance",
    subtitle = "Hartree remains smoother by R2; slab ladders contain small local Hartree wiggles",
    x = NULL, y = "Strictly monotone material-codec ladders"
  ) + theme_si + theme(legend.position = "top", panel.grid.major.x = element_blank())

# Panel D: matched-Hartree error does not determine Bader error.
disp2 <- disp %>%
  filter(is.finite(bader_p90_over_p10), bader_p90_over_p10 > 0, n >= 10) %>%
  mutate(
    codec = factor(toupper(codec), levels = codec_levels),
    system_type = factor(system_type, levels = c("bulk", "slab"), labels = c("Bulk", "Slab")),
    hartree_log10_center = hartree_log10_bin_left + 0.25
  )
weighted_frac <- with(disp2, sum(n[bader_p90_over_p10 >= 10]) / sum(n))

pD <- ggplot(disp2, aes(hartree_log10_center, bader_p90_over_p10, colour = codec, shape = system_type, size = n)) +
  geom_hline(yintercept = 10, linetype = 2, linewidth = .65, colour = red) +
  geom_point(alpha = .72) +
  scale_colour_manual(values = codec_cols) +
  scale_shape_manual(values = c(Bulk = 16, Slab = 17)) +
  scale_size_continuous(range = c(1.7, 4.4), guide = "none") +
  scale_y_log10(labels = label_number()) +
  annotate("label", x = min(disp2$hartree_log10_center), y = max(disp2$bader_p90_over_p10, na.rm = TRUE),
           hjust = 0, vjust = 1, size = 2.9, label.size = .2, fill = alpha("white", .95),
           label = sprintf("%.1f%% of rows lie in bins with Bader P90/P10 >= 10", 100 * weighted_frac)) +
  labs(
    title = "D | Matched Hartree error leaves large Bader dispersion",
    subtitle = "0.5-decade Hartree-error bins with at least 10 rows",
    x = "log10 relative Hartree RMSE (bin centre)", y = "Bader P90 / P10 within matched-Hartree bin"
  ) + theme_si + theme(legend.position = "top")

fig <- ((pA | pB) / (pC | pD)) +
  plot_annotation(
    title = "Supplementary Figure S3 | Extended controls separate global, smooth nonlocal and topology-sensitive QoIs",
    subtitle = "The same frozen corpus is interrogated with electron count, periodic Hartree potential and re-derived Bader charge.",
    caption = "A, electron-count negative control. B-C, material-level Hartree/Bader smoothness. D, Bader dispersion at matched Hartree-error scale. These are operator controls, not the benchmark-validity novelty claim.",
    theme = theme(plot.background = element_rect(fill = bg, colour = NA),
                  plot.title = element_text(face = "bold", size = 13.7, colour = ink, margin = margin(b = 4)),
                  plot.subtitle = element_text(size = 9.3, colour = muted, margin = margin(b = 8)),
                  plot.caption = element_text(size = 7.9, colour = muted, hjust = 0, margin = margin(t = 8)))
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS3_operator_controls_R.png"),
  pdf = file.path(outdir, "supplementary_figureS3_operator_controls_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS3_operator_controls_R.svg")
)
ggsave(paths[["png"]], fig, width = 13.8, height = 9.2, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 13.8, height = 9.2, bg = bg)
ggsave(paths[["svg"]], fig, width = 13.8, height = 9.2, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S3: PNG + PDF + SVG")
message(sprintf("Electron/Bader decoupling: %d/%d = %.4f; matched-Hartree-bin weighted fraction = %.4f", ndecoupled, ngood, ndecoupled / ngood, weighted_frac))

# Supplementary Figure S2 — Protocol A.1 probe robustness
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

cal <- read.csv(file.path(root, "stability", "probe_calibration.csv"), check.names = FALSE, stringsAsFactors = FALSE)
seed <- read.csv(file.path(root, "stability", "stability_floor_A1_per_seed.csv"), check.names = FALSE, stringsAsFactors = FALSE)
amp <- read.csv(file.path(root, "supplement", "S4_amplitude_sensitivity.csv"), check.names = FALSE, stringsAsFactors = FALSE)

stopifnot(length(unique(cal$material_id)) == 18)
stopifnot(all(c("floor_noise_resolved_e", "seed", "material_id", "corpus") %in% names(seed)))
stopifnot(all(c("floor_x0.1", "floor_x1", "floor_x10", "log10_floor_x10_over_x0.1") %in% names(amp)))

bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E5E7EB"; muted <- "#5F6368"
col_arch <- "#9AA0A6"; col_noise <- "#4A5F7E"; col_orange <- "#E9B13A"; col_vac <- "#8C6BB1"; col_red <- "#D94B41"
theme_si <- theme_minimal(base_size = 10.4) + theme(
  plot.background = element_rect(fill = bg, colour = NA),
  panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(),
  panel.grid.major = element_line(colour = grid, linewidth = .3),
  axis.title = element_text(colour = ink), axis.text = element_text(colour = ink),
  plot.title = element_text(face = "bold", size = 11.1, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 9.0, colour = muted, margin = margin(b = 6)),
  legend.title = element_blank(), legend.text = element_text(size = 8.8),
  plot.margin = margin(8, 10, 8, 8)
)

# Calibration comparison at the same amplitude.
cal_pair <- cal %>%
  mutate(seed_chr = as.character(seed)) %>%
  filter(amplitude_factor == 1, seed_chr %in% c("float32", "20260905")) %>%
  mutate(
    probe = ifelse(seed_chr == "float32", "Archived float32", "A.1 noise"),
    probe = factor(probe, levels = c("Archived float32", "A.1 noise"))
  )
stopifnot(nrow(cal_pair) == 36)

cal_stats <- cal_pair %>% group_by(probe) %>% summarise(
  median_ties = median(n_exact_neighbour_ties_created),
  zero_reassign = sum(n_voxels_reassigned == 0),
  n = n(), .groups = "drop"
)

pA <- ggplot(cal_pair, aes(probe, log10(1 + n_exact_neighbour_ties_created), fill = probe)) +
  geom_boxplot(width = .55, outlier.shape = NA, alpha = .75) +
  geom_jitter(width = .10, size = 1.45, alpha = .60, colour = ink) +
  scale_fill_manual(values = c("Archived float32" = col_arch, "A.1 noise" = col_noise), guide = "none") +
  scale_y_continuous(breaks = 0:4, labels = c("0", "9", "99", "999", "9,999")) +
  annotate("text", x = 1, y = max(log10(1 + cal_pair$n_exact_neighbour_ties_created)) * .95,
           label = sprintf("median = %.0f ties", cal_stats$median_ties[cal_stats$probe == "Archived float32"]),
           size = 3.0, colour = ink) +
  annotate("text", x = 2, y = max(log10(1 + cal_pair$n_exact_neighbour_ties_created)) * .95,
           label = sprintf("median = %.0f ties", cal_stats$median_ties[cal_stats$probe == "A.1 noise"]),
           size = 3.0, colour = ink) +
  labs(title = "A | Order-preserving rounding creates exact ties", subtitle = "18-material pre-freeze calibration; matched perturbation amplitude", x = NULL, y = "Exact neighbour ties created") +
  theme_si

pB <- ggplot(cal_pair, aes(probe, log10(1 + n_voxels_reassigned), fill = probe)) +
  geom_boxplot(width = .55, outlier.shape = NA, alpha = .75) +
  geom_jitter(width = .10, size = 1.45, alpha = .60, colour = ink) +
  scale_fill_manual(values = c("Archived float32" = col_arch, "A.1 noise" = col_noise), guide = "none") +
  scale_y_continuous(breaks = 0:5, labels = c("0", "9", "99", "999", "9,999", "99,999")) +
  annotate("label", x = 1, y = max(log10(1 + cal_pair$n_voxels_reassigned)) * .90,
           label = sprintf("zero reassignment\n%d / %d", cal_stats$zero_reassign[cal_stats$probe == "Archived float32"], cal_stats$n[cal_stats$probe == "Archived float32"]),
           size = 2.9, label.size = .18, fill = alpha("white", .94)) +
  annotate("label", x = 2, y = max(log10(1 + cal_pair$n_voxels_reassigned)) * .90,
           label = sprintf("zero reassignment\n%d / %d", cal_stats$zero_reassign[cal_stats$probe == "A.1 noise"], cal_stats$n[cal_stats$probe == "A.1 noise"]),
           size = 2.9, label.size = .18, fill = alpha("white", .94)) +
  labs(title = "B | Noise excites basin reassignment", subtitle = "A.1 removes the archived probe's order-preserving blind spot", x = NULL, y = "Voxels reassigned") +
  theme_si

# Full 319-system seed sensitivity. This is deliberately distinguished from
# the 18-material pre-freeze calibration statistics documented in PROTOCOL_A1.md.
seed2 <- seed %>%
  filter(is.finite(floor_noise_resolved_e), floor_noise_resolved_e > 0) %>%
  mutate(seed_chr = as.character(seed))
spread <- seed2 %>% group_by(material_id, corpus) %>% summarise(
  log10_span = max(log10(floor_noise_resolved_e)) - min(log10(floor_noise_resolved_e)),
  .groups = "drop"
)
stopifnot(nrow(spread) == 319)
med_span <- median(spread$log10_span)
max_span <- max(spread$log10_span)

primary <- seed2 %>% filter(seed_chr == "20260905") %>% select(material_id, primary_floor = floor_noise_resolved_e)
mx <- seed2 %>% group_by(material_id) %>% summarise(max_floor = max(floor_noise_resolved_e), .groups = "drop")
verdict <- inner_join(primary, mx, by = "material_id")
taus <- c(1e-4, 1e-3, 1e-2)
flips <- vapply(taus, function(t) sum((verdict$primary_floor < t) != (verdict$max_floor < t)), numeric(1))
stopifnot(identical(as.integer(flips), c(35L, 17L, 2L)))

pC <- ggplot(spread, aes(log10_span)) +
  geom_histogram(binwidth = .15, boundary = 0, fill = "#94C6CD", colour = "white", linewidth = .35) +
  geom_vline(xintercept = med_span, colour = col_red, linetype = 2, linewidth = .75) +
  annotate("label", x = max(spread$log10_span) * .98, y = Inf, vjust = 1.15, hjust = 1,
           label = sprintf("Full-corpus median = %.2f decades\nMaximum = %.2f decades\nPrimary seed vs five-seed max eligibility flips:\n10^-4 e: %d/319   10^-3 e: %d/319   10^-2 e: %d/319",
                           med_span, max_span, flips[1], flips[2], flips[3]),
           size = 2.95, lineheight = .98, label.size = .2, fill = alpha("white", .95), colour = ink) +
  labs(title = "C | A single seed is insufficient for conservative qualification", subtitle = "Full 319-system corpus after the A.1 protocol was frozen", x = "Within-material log10 floor span across five seeds (decades)", y = "Number of materials") +
  theme_si

# Amplitude sensitivity in the pre-freeze 18-material panel.
domain_map <- cal %>% distinct(material_id, domain)
amp_long <- amp %>%
  left_join(domain_map, by = "material_id") %>%
  pivot_longer(cols = all_of(c("floor_x0.1", "floor_x1", "floor_x10")), names_to = "amp_name", values_to = "floor_e") %>%
  mutate(amplitude = case_when(amp_name == "floor_x0.1" ~ 0.1, amp_name == "floor_x1" ~ 1, TRUE ~ 10))
stopifnot(all(!is.na(amp_long$domain)))
shift <- amp$log10_floor_x10_over_x0.1
med_shift <- median(shift, na.rm = TRUE); p10_shift <- quantile(shift, .10, na.rm = TRUE); p90_shift <- quantile(shift, .90, na.rm = TRUE)

pD <- ggplot(amp_long, aes(amplitude, floor_e, group = material_id, colour = domain)) +
  geom_line(alpha = .48, linewidth = .65) + geom_point(size = 1.45, alpha = .72) +
  scale_x_log10(breaks = c(.1, 1, 10), labels = c("x0.1", "x1", "x10")) +
  scale_y_log10(labels = label_scientific(digits = 1)) +
  scale_colour_manual(
    values = c(bulk = col_noise, slab = col_orange, vacuum2d = col_vac),
    labels = c(bulk = "Bulk", slab = "Slab", vacuum2d = "External vacuum-2D")
  ) +
  annotate("label", x = .12, y = max(amp_long$floor_e, na.rm = TRUE), hjust = 0, vjust = 1,
           label = sprintf("x0.1 -> x10 floor shift\nmedian %.2f decades\nP10 %.2f, P90 %.2f", med_shift, p10_shift, p90_shift),
           size = 2.9, label.size = .2, fill = alpha("white", .95), colour = ink) +
  labs(title = "D | The floor is protocol-defined, not amplitude-free", subtitle = "Pre-freeze amplitude sweep on the 18 calibration materials", x = "Noise amplitude relative to the A.1 definition", y = "Re-derived Bader floor (e)") +
  theme_si + theme(legend.position = "top")

fig <- ((pA | pB) / (pC | pD)) +
  plot_annotation(
    title = "Supplementary Figure S2 | Protocol A.1 probe validation, seed sensitivity and amplitude sensitivity",
    subtitle = "The calibration justifies a non-order-preserving, multi-seed probe; full-corpus statistics quantify its deployment behavior without retuning.",
    caption = "A-B, 18-material pre-freeze probe calibration. C, five-seed variability in all 319 systems. D, pre-freeze two-decade amplitude sensitivity. The A.1 amplitude and seed set remained frozen.",
    theme = theme(plot.background = element_rect(fill = bg, colour = NA),
                  plot.title = element_text(face = "bold", size = 13.9, colour = ink, margin = margin(b = 4)),
                  plot.subtitle = element_text(size = 9.5, colour = muted, margin = margin(b = 8)),
                  plot.caption = element_text(size = 8.0, colour = muted, hjust = 0, margin = margin(t = 8)))
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS2_probe_seed_amplitude_R.png"),
  pdf = file.path(outdir, "supplementary_figureS2_probe_seed_amplitude_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS2_probe_seed_amplitude_R.svg")
)
ggsave(paths[["png"]], fig, width = 12.8, height = 9.1, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 12.8, height = 9.1, bg = bg)
ggsave(paths[["svg"]], fig, width = 12.8, height = 9.1, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S2: PNG + PDF + SVG")
message(sprintf("Full-corpus seed span median %.3f dec, max %.3f dec; flips %d/%d/%d", med_span, max_span, flips[1], flips[2], flips[3]))

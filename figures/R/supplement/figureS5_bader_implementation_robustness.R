# Supplementary Figure S5 — independent Bader implementation robustness
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

read_bool <- function(x) tolower(as.character(x)) %in% c("true", "t", "1", "yes")

# Frozen independent-implementation assets.
dec <- read.csv(file.path(root, "mechanism", "independent_bader_20260908", "mechanism_domain_decomposition.csv"), stringsAsFactors = FALSE)
stab <- read.csv(file.path(root, "mechanism", "independent_bader_20260908", "stability_comparison.csv"), stringsAsFactors = FALSE)
pairs <- read.csv(file.path(root, "supplement", "S11_cross_implementation_pairs.csv"), stringsAsFactors = FALSE)
impl <- read.csv(file.path(root, "supplement", "S11_independent_implementation_summary.csv"), stringsAsFactors = FALSE)
spatial <- read.csv(file.path(root, "supplement", "S11_spatial_control_summary.csv"), stringsAsFactors = FALSE)

# Frozen assertions from Tables S10-S11.
stopifnot(sum(!read_bool(dec$sentinel) & dec$kind == "codec") == 70)
stopifnot(sum(!read_bool(dec$sentinel) & dec$kind == "noise") == 60)
stopifnot(sum(!read_bool(dec$sentinel) & dec$kind == "spatial_control") == 324)
stopifnot(sum(!read_bool(dec$sentinel) & dec$kind == "float32") == 12)
stopifnot(length(unique(stab$material[!read_bool(stab$sentinel)])) == 12)
stopifnot(nrow(pairs) == 144)
stopifnot(nrow(spatial) == 9)

get_impl <- function(solver, filter) {
  z <- impl %>% filter(metric == "codec_response_ratio", .data$solver == solver, .data$filter == filter)
  stopifnot(nrow(z) == 1)
  z
}
ongrid_stat <- get_impl("henkelman_ongrid", "above_print_resolution")
neargrid_stat <- get_impl("henkelman_neargrid", "above_print_resolution")
# Assert the frozen scientific regime, not a machine-precision serialization detail.
stopifnot(abs(ongrid_stat$median - 1.0) < 0.01)
stopifnot(neargrid_stat$median > 0.70, neargrid_stat$median < 0.85)

bg <- "#FFFFFF"; ink <- "#202124"; muted <- "#5F6368"; grid <- "#E5E7EB"
codec_cols <- c(ZFP = "#4A5F7E", SZ3 = "#D55E00", SPERR = "#2A9D8F")
kind_cols <- c(codec = "#4A5F7E", noise = "#2A9D8F", spatial_control = "#D55E00", float32 = "#9AA0A6")
solver_cols <- c(baderkit_ongrid = "#4A5F7E", henkelman_ongrid = "#2A9D8F", henkelman_neargrid = "#D55E00")

base_theme <- theme_minimal(base_size = 10.1) + theme(
  plot.background = element_rect(fill = bg, colour = NA),
  panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(),
  panel.grid.major = element_line(colour = grid, linewidth = .3),
  axis.title = element_text(colour = ink), axis.text = element_text(colour = ink),
  strip.text = element_text(face = "bold", colour = ink, size = 9.0),
  strip.background = element_rect(fill = "#F5F6F7", colour = NA),
  legend.title = element_blank(), legend.text = element_text(size = 8.4),
  plot.title = element_text(face = "bold", size = 11.0, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 8.8, colour = muted, margin = margin(b = 5)),
  plot.margin = margin(7, 8, 7, 7)
)

# A — exact decomposition: domain term versus integrand term.
dec_plot <- dec %>%
  filter(!read_bool(sentinel)) %>%
  mutate(
    kind = factor(kind, levels = c("codec", "noise", "spatial_control", "float32"),
                  labels = c("Codec", "QSQ noise", "Spatial control", "Float32")),
    integrand_plot = pmax(integrand_max_e, 1e-12),
    domain_plot = pmax(domain_max_e, 1e-12)
  )
kind_cols_lab <- c("Codec" = kind_cols[["codec"]], "QSQ noise" = kind_cols[["noise"]],
                   "Spatial control" = kind_cols[["spatial_control"]], "Float32" = kind_cols[["float32"]])

pA <- ggplot(dec_plot, aes(integrand_plot, domain_plot, colour = kind)) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, linewidth = .65, colour = "#70757A") +
  geom_point(size = 1.65, alpha = .54) +
  scale_colour_manual(values = kind_cols_lab) +
  scale_x_log10(labels = label_scientific(digits = 1)) +
  scale_y_log10(labels = label_scientific(digits = 1)) +
  labs(
    title = "A | Domain migration dominates most non-order-preserving perturbations",
    subtitle = "Exact BaderKit decomposition; sentinel excluded",
    x = "Integrand contribution, max |Delta Q| (e)", y = "Domain-migration contribution, max |Delta Q| (e)"
  ) + base_theme + theme(legend.position = "top")

# B — QSQ floor cross-implementation comparison. Use the material-domain map
# from the paired codec table so this join is independent of stability CSV schema.
stab2 <- stab %>% filter(!read_bool(sentinel))
domain_map <- pairs %>% select(material, domain) %>% distinct()
ref <- stab2 %>% filter(solver == "baderkit_ongrid") %>%
  select(material, baderkit_floor = probe_response_max_e)
comp <- stab2 %>% filter(solver != "baderkit_ongrid") %>%
  select(material, solver, comparison_floor = probe_response_max_e)
stab_pair <- inner_join(comp, ref, by = "material") %>%
  left_join(domain_map, by = "material") %>%
  mutate(
    solver = factor(solver, levels = c("henkelman_ongrid", "henkelman_neargrid"),
                    labels = c("Henkelman on-grid", "Henkelman near-grid")),
    domain = factor(domain, levels = c("bulk", "slab")),
    baderkit_floor = pmax(baderkit_floor, 1e-9),
    comparison_floor = pmax(comparison_floor, 1e-9)
  )
stopifnot(nrow(stab_pair) == 24, all(!is.na(stab_pair$domain)))

pB <- ggplot(stab_pair, aes(baderkit_floor, comparison_floor, shape = domain)) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, linewidth = .65, colour = "#70757A") +
  geom_point(size = 2.3, alpha = .78, colour = "#2A9D8F") +
  facet_wrap(~solver, nrow = 1) +
  scale_x_log10(labels = label_scientific(digits = 1)) +
  scale_y_log10(labels = label_scientific(digits = 1)) +
  scale_shape_manual(values = c(bulk = 16, slab = 17)) +
  labs(
    title = "B | Absolute stability floors depend on the basin implementation",
    subtitle = "Twelve deliberately stratified development systems",
    x = "BaderKit on-grid QSQ floor (e)", y = "Independent implementation QSQ floor (e)"
  ) + base_theme + theme(legend.position = "top")

# C — paired codec responses; one-to-one for on-grid implementation, wider for near-grid.
expected_pair_n <- sum(read_bool(pairs$above_2e.6_print_region))
pair_plot <- pairs %>%
  filter(read_bool(above_2e.6_print_region)) %>%
  mutate(
    codec = factor(codec, levels = c("ZFP", "SZ3", "SPERR")),
    comparison_solver = factor(comparison_solver,
      levels = c("henkelman_ongrid", "henkelman_neargrid"),
      labels = c("Henkelman on-grid", "Henkelman near-grid")),
    x = pmax(baderkit_error_e, 1e-8), y = pmax(comparison_error_e, 1e-8)
  )
stopifnot(expected_pair_n > 0, nrow(pair_plot) == expected_pair_n)
message("Figure S5 paired codec-response points above print region: ", nrow(pair_plot))
ann <- data.frame(
  comparison_solver = factor(c("Henkelman on-grid", "Henkelman near-grid"), levels = levels(pair_plot$comparison_solver)),
  label = c(
    sprintf("median ratio %.3f\nIQR %.3f-%.3f", ongrid_stat$median, ongrid_stat$q25, ongrid_stat$q75),
    sprintf("median ratio %.3f\nIQR %.3f-%.3f", neargrid_stat$median, neargrid_stat$q25, neargrid_stat$q75)
  ),
  x = 5e-6, y = 2e-1
)

pC <- ggplot(pair_plot, aes(x, y, colour = codec)) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, linewidth = .65, colour = "#70757A") +
  geom_point(size = 1.65, alpha = .65) +
  geom_label(data = ann, aes(x = x, y = y, label = label), inherit.aes = FALSE,
             hjust = 0, vjust = 1, size = 2.75, linewidth = .18, fill = alpha("white", .9)) +
  facet_wrap(~comparison_solver, nrow = 1) +
  scale_colour_manual(values = codec_cols) +
  scale_x_log10(labels = label_scientific(digits = 1), limits = c(2e-6, 4e-1)) +
  scale_y_log10(labels = label_scientific(digits = 1), limits = c(2e-6, 4e-1)) +
  labs(
    title = "C | On-grid codec responses reproduce nearly one-for-one",
    subtitle = "Successful pairs above the 2e-6 e Henkelman print-resolution region",
    x = "BaderKit re-derived charge error (e)", y = "Independent implementation charge error (e)"
  ) + base_theme + theme(legend.position = "top")

# D — spatial controls: distributional effect beyond simple periodic alignment.
sp2 <- spatial %>%
  mutate(
    control = factor(control, levels = c("global", "shift", "stratified"),
                     labels = c("Global shuffle", "Periodic shift", "Stratified shuffle")),
    solver = factor(solver, levels = c("baderkit_ongrid", "henkelman_ongrid", "henkelman_neargrid"),
                    labels = c("BaderKit on-grid", "Henkelman on-grid", "Henkelman near-grid"))
  )
solver_cols_lab <- c("BaderKit on-grid" = solver_cols[["baderkit_ongrid"]],
                     "Henkelman on-grid" = solver_cols[["henkelman_ongrid"]],
                     "Henkelman near-grid" = solver_cols[["henkelman_neargrid"]])

pD <- ggplot(sp2, aes(control, median_log2_control_over_codec, colour = solver, group = solver)) +
  geom_hline(yintercept = 0, linetype = 2, linewidth = .6, colour = "#70757A") +
  geom_linerange(aes(ymin = q25, ymax = q75), position = position_dodge(width = .35), linewidth = .8) +
  geom_point(position = position_dodge(width = .35), size = 2.4) +
  scale_colour_manual(values = solver_cols_lab) +
  labs(
    title = "D | Spatial reorganization has a modest implementation-robust effect",
    subtitle = "Median log2(control / original codec response), with IQR; n = 36 pairs per point",
    x = NULL, y = "log2(control error / codec error)"
  ) + base_theme + theme(legend.position = "top", axis.text.x = element_text(angle = 15, hjust = 1))

fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(heights = c(1, 1)) +
  plot_annotation(
    title = "Supplementary Figure S5 | Bader mechanism is robust to an independent implementation",
    subtitle = "Exact decomposition, stability-floor cross-checks and error-reorganization controls on a deliberately stratified 12-system panel.",
    caption = "A, density-dependent basin migration dominates codec, QSQ-noise and spatial-control perturbations; float32 is heterogeneous. B, changing the basin implementation can shift the absolute numerical floor. C, the independent on-grid implementation reproduces codec responses nearly one-for-one, whereas near-grid basins broaden the absolute response scale. D, shuffling error values modestly changes Bader response, while a periodic shift is near-null. This is a mechanism/implementation robustness study, not a prevalence estimate, and it does not alter the frozen QSQ benchmark definition.",
    theme = theme(
      plot.background = element_rect(fill = bg, colour = NA),
      plot.title = element_text(face = "bold", size = 13.8, colour = ink, margin = margin(b = 4)),
      plot.subtitle = element_text(size = 9.3, colour = muted, margin = margin(b = 8)),
      plot.caption = element_text(size = 7.7, colour = muted, hjust = 0, margin = margin(t = 8))
    )
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS5_bader_implementation_robustness_R.png"),
  pdf = file.path(outdir, "supplementary_figureS5_bader_implementation_robustness_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS5_bader_implementation_robustness_R.svg")
)
ggsave(paths[["png"]], fig, width = 13.4, height = 9.2, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 13.4, height = 9.2, bg = bg)
ggsave(paths[["svg"]], fig, width = 13.4, height = 9.2, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S5: PNG + PDF + SVG")
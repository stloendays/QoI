# Supplementary Figure S1 — stability-floor landscape and eligibility
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

a1 <- read.csv(file.path(root, "stability", "stability_floor_A1.csv"), stringsAsFactors = FALSE)
a0 <- read.csv(file.path(root, "stability", "stability_floor_A_archived_float32.csv"), stringsAsFactors = FALSE)
elig <- read.csv(file.path(root, "stability", "eligibility_summary_A1.csv"), stringsAsFactors = FALSE)

stopifnot(all(c("material_id", "stability_floor_A1_e", "corpus") %in% names(a1)))
stopifnot(all(c("material_id", "floor_resolved_e") %in% names(a0)))
stopifnot(all(c("threshold_e", "stratum", "frac_non_evaluable_a1", "frac_non_evaluable_a_archived") %in% names(elig)))

paired <- merge(
  a1[, c("material_id", "corpus", "stability_floor_A1_e")],
  a0[, c("material_id", "floor_resolved_e")],
  by = "material_id"
) %>%
  filter(is.finite(stability_floor_A1_e), is.finite(floor_resolved_e), stability_floor_A1_e > 0, floor_resolved_e > 0) %>%
  mutate(ratio = stability_floor_A1_e / floor_resolved_e)

stopifnot(nrow(paired) >= 250)
median_shift <- median(paired$ratio, na.rm = TRUE)

corpus_labels <- c(
  dev_bulk = "Development bulk",
  dev_slab = "Development slab",
  ext_bulk = "External bulk",
  ext_vacuum = "External vacuum-2D"
)
corpus_cols <- c(
  dev_bulk = "#4A5F7E",
  dev_slab = "#D55E00",
  ext_bulk = "#2A9D8F",
  ext_vacuum = "#8C6BB1"
)

bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E5E7EB"; muted <- "#5F6368"
theme_si <- theme_minimal(base_size = 10.5) + theme(
  plot.background = element_rect(fill = bg, colour = NA),
  panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(),
  panel.grid.major = element_line(colour = grid, linewidth = 0.3),
  axis.title = element_text(colour = ink),
  axis.text = element_text(colour = ink),
  plot.title = element_text(face = "bold", size = 11.6, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 9.2, colour = muted, margin = margin(b = 6)),
  legend.title = element_blank(),
  legend.text = element_text(size = 9.0),
  plot.margin = margin(8, 10, 8, 8)
)

pA <- ggplot(paired, aes(floor_resolved_e, stability_floor_A1_e, colour = corpus)) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, linewidth = .6, colour = "#70757A") +
  geom_point(alpha = .48, size = 1.45) +
  scale_colour_manual(values = corpus_cols, labels = corpus_labels) +
  scale_x_log10(labels = label_scientific(digits = 1)) +
  scale_y_log10(labels = label_scientific(digits = 1)) +
  annotate("label", x = quantile(paired$floor_resolved_e, .04), y = quantile(paired$stability_floor_A1_e, .96),
           hjust = 0, vjust = 1, size = 3.0, label.size = .2, fill = alpha("white", .95),
           label = sprintf("Median A.1 / archived shift = %.2g x", median_shift)) +
  labs(
    title = "A | The archived probe systematically understates Bader instability",
    subtitle = sprintf("Paired material-level floors; n = %d", nrow(paired)),
    x = "Archived Protocol A floor (e)", y = "Protocol A.1 floor (e)"
  ) + theme_si + theme(legend.position = "top")

overall <- elig %>%
  filter(stratum == "overall") %>%
  transmute(
    threshold_e,
    A1 = frac_non_evaluable_a1,
    Archived = frac_non_evaluable_a_archived,
    tau = factor(threshold_e, levels = c(1e-4, 1e-3, 1e-2), labels = c("10^-4 e", "10^-3 e", "10^-2 e"))
  )

pB <- ggplot(overall) +
  geom_segment(aes(x = Archived, xend = A1, y = tau, yend = tau), colour = "#C7CBD1", linewidth = 1.2) +
  geom_point(aes(x = Archived, y = tau, colour = "Archived A"), size = 3.2) +
  geom_point(aes(x = A1, y = tau, colour = "Protocol A.1"), size = 3.2) +
  geom_text(aes(x = A1, y = tau, label = percent(A1, accuracy = .1)), hjust = -0.28, size = 3.05, colour = ink) +
  scale_colour_manual(values = c("Archived A" = "#9AA0A6", "Protocol A.1" = "#E9B13A")) +
  scale_x_continuous(limits = c(0, .91), breaks = seq(0, .8, .2), labels = label_percent(), expand = c(0, 0)) +
  labs(
    title = "B | Eligibility changes materially when the relevant failure channel is probed",
    subtitle = "Overall 319-system non-evaluable fraction",
    x = "Non-evaluable fraction", y = NULL
  ) + theme_si + theme(legend.position = "top", panel.grid.major.y = element_blank())

heat <- elig %>%
  filter(stratum != "overall") %>%
  mutate(
    tau = factor(threshold_e, levels = c(1e-4, 1e-3, 1e-2), labels = c("10^-4 e", "10^-3 e", "10^-2 e")),
    stratum_label = factor(stratum,
      levels = c("dev_bulk", "dev_slab", "ext_bulk", "ext_vacuum"),
      labels = c("Development bulk", "Development slab", "External bulk", "External vacuum-2D"))
  )

pC <- ggplot(heat, aes(tau, stratum_label, fill = frac_non_evaluable_a1)) +
  geom_tile(colour = "white", linewidth = 1) +
  geom_text(aes(label = percent(frac_non_evaluable_a1, accuracy = .1)), fontface = "bold", size = 3.35, colour = ink) +
  scale_fill_gradient(low = "#F4F8F7", high = "#2A9D8F", limits = c(0, 1), labels = label_percent()) +
  labs(
    title = "C | Numerical eligibility is material- and tolerance-dependent",
    subtitle = "Protocol A.1; the structural-class contrast is not universal",
    x = "Bader tolerance", y = NULL, fill = "Non-evaluable"
  ) + theme_si + theme(panel.grid = element_blank(), legend.position = "right")

fig <- ((pA | pB) / pC) +
  plot_layout(heights = c(1.05, .95)) +
  plot_annotation(
    title = "Supplementary Figure S1 | Protocol A.1 redefines the measurable Bader-fidelity landscape",
    subtitle = "The archived order-preserving float32 round trip is retained only as provenance; all current eligibility and certification use Protocol A.1.",
    caption = "A. Paired archived and A.1 stability floors. B. Overall non-evaluable fractions at the three chemical contracts. C. A.1 non-evaluable fractions by analysis stratum. Non-evaluable means the reference Bader QoI is not independently resolvable at the requested tolerance and is neither a codec pass nor a codec failure.",
    theme = theme(
      plot.background = element_rect(fill = bg, colour = NA),
      plot.title = element_text(face = "bold", size = 14.2, colour = ink, margin = margin(b = 4)),
      plot.subtitle = element_text(size = 9.8, colour = muted, margin = margin(b = 8)),
      plot.caption = element_text(size = 8.2, colour = muted, hjust = 0, margin = margin(t = 8))
    )
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS1_stability_floor_landscape_R.png"),
  pdf = file.path(outdir, "supplementary_figureS1_stability_floor_landscape_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS1_stability_floor_landscape_R.svg")
)
ggsave(paths[["png"]], fig, width = 11.8, height = 8.3, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 11.8, height = 8.3, bg = bg)
ggsave(paths[["svg"]], fig, width = 11.8, height = 8.3, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S1: PNG + PDF + SVG")

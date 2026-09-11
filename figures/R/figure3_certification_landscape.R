# Figure 3 — binary benchmark -> stability-qualified three-state certification
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(scales)
  library(patchwork)
})

if (!requireNamespace("svglite", quietly = TRUE)) {
  stop("Package 'svglite' is required for vector SVG export.")
}

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

d <- read.csv(
  file.path(root, "benchmark", "master_benchmark_full.csv"),
  check.names = FALSE,
  stringsAsFactors = FALSE
)

# ---- frozen semantics ---------------------------------------------------------
taus <- c("0.0001", "0.001", "0.01")
codecs <- c("ZFP", "SZ3", "SPERR")
threshold_labels <- c(expression(10^-4~e), expression(10^-3~e), expression(10^-2~e))

as_flag <- function(x) x %in% c(TRUE, 1, "1", "TRUE", "True", "true")

summarise_one_decision <- function(g, cert_col, elig_col, ign_col) {
  g %>%
    group_by(material_id) %>%
    summarise(
      certified = any(as_flag(.data[[cert_col]]), na.rm = TRUE),
      eligible = any(as_flag(.data[[elig_col]]), na.rm = TRUE),
      naive_pass = any(as_flag(.data[[ign_col]]), na.rm = TRUE),
      .groups = "drop"
    )
}

D <- bind_rows(lapply(taus, function(t) {
  bind_rows(lapply(codecs, function(cc) {
    g <- d[toupper(d$codec) == cc, , drop = FALSE]
    cert_col <- paste0("certified_at_", t)
    elig_col <- paste0("eligible_A1_at_", t)
    ign_col <- paste0("certified_at_", t, "_ignoring_eligibility")
    needed <- c(cert_col, elig_col, ign_col)
    if (!all(needed %in% names(g))) {
      stop("Missing Figure 3 certification columns for tau = ", t)
    }

    z <- summarise_one_decision(g, cert_col, elig_col, ign_col)
    z %>%
      mutate(
        codec = cc,
        tau = t,
        naive_fail = !naive_pass,
        eligible_fail = eligible & !certified,
        non_evaluable = !eligible,
        naive_fail_reclassified_non_evaluable = naive_fail & !eligible,
        genuine_eligible_failure = naive_fail & eligible,
        non_evaluable_naive_pass = naive_pass & !eligible
      )
  }))
}))

S <- D %>%
  group_by(tau) %>%
  summarise(
    n_decisions = n(),
    naive_pass = sum(naive_pass),
    naive_fail = sum(naive_fail),
    qualified_pass = sum(certified),
    eligible_fail = sum(eligible_fail),
    non_evaluable = sum(non_evaluable),
    non_evaluable_naive_pass = sum(non_evaluable_naive_pass),
    naive_fail_reclassified_non_evaluable = sum(naive_fail_reclassified_non_evaluable),
    genuine_eligible_failure = sum(genuine_eligible_failure),
    .groups = "drop"
  ) %>%
  mutate(
    x = match(tau, taus),
    fraction_naive_fail_reclassified = naive_fail_reclassified_non_evaluable / naive_fail,
    fraction_naive_pass_non_evaluable = non_evaluable_naive_pass / naive_pass
  )

# Fail loudly if a future data change would silently alter the frozen headline.
expected <- data.frame(
  tau = taus,
  n_decisions = c(762, 762, 762),
  naive_pass = c(229, 452, 654),
  naive_fail = c(533, 310, 108),
  qualified_pass = c(123, 415, 640),
  eligible_fail = c(15, 14, 47),
  non_evaluable = c(624, 333, 75),
  non_evaluable_naive_pass = c(106, 37, 14),
  naive_fail_reclassified_non_evaluable = c(518, 296, 61),
  stringsAsFactors = FALSE
)
check_cols <- setdiff(names(expected), "tau")
for (nm in check_cols) {
  if (!identical(as.integer(S[[nm]]), as.integer(expected[[nm]]))) {
    stop("Frozen Figure 3 assertion failed for column: ", nm)
  }
}

# ---- visual system ------------------------------------------------------------
col_grey <- "#9AA0A6"
col_red <- "#D94B41"
col_teal <- "#2A9D8F"
col_orange <- "#E9B13A"
col_text <- "#1F2937"
col_grid <- "#E5E7EB"
col_box <- "#F8FAFC"

base_theme <- theme_minimal(base_size = 11.2) +
  theme(
    plot.background = element_rect(fill = "white", colour = NA),
    panel.background = element_rect(fill = "white", colour = NA),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_line(colour = col_grid, linewidth = 0.35),
    axis.title = element_text(colour = col_text, size = 11.8),
    axis.text = element_text(colour = col_text, size = 10.6),
    plot.title = element_text(face = "bold", colour = col_text, size = 14.2,
                              margin = margin(b = 4)),
    plot.subtitle = element_text(colour = "#4B5563", size = 10.0,
                                 lineheight = 1.05, margin = margin(b = 8)),
    legend.title = element_blank(),
    legend.text = element_text(size = 9.6, colour = col_text),
    plot.margin = margin(10, 12, 8, 10)
  )

bar_half <- 0.36

# ---- Panel A: naive binary benchmark -----------------------------------------
p_a <- ggplot(S, aes(x = x)) +
  geom_rect(aes(xmin = x - bar_half, xmax = x + bar_half,
                ymin = 0, ymax = naive_pass, fill = "Naive pass"),
            colour = "white", linewidth = 0.55) +
  geom_rect(aes(xmin = x - bar_half, xmax = x + bar_half,
                ymin = naive_pass, ymax = n_decisions, fill = "Naive fail"),
            colour = "white", linewidth = 0.55) +
  geom_text(aes(y = naive_pass / 2, label = naive_pass),
            colour = "white", fontface = "bold", size = 4.4) +
  geom_text(aes(y = naive_pass + naive_fail / 2, label = naive_fail),
            colour = "white", fontface = "bold", size = 4.4) +
  geom_text(aes(y = 794, label = "Total = 762"),
            colour = col_text, size = 3.45) +
  scale_fill_manual(values = c("Naive pass" = col_grey, "Naive fail" = col_red)) +
  scale_x_continuous(breaks = 1:3, labels = threshold_labels,
                     limits = c(0.5, 3.5), expand = c(0, 0)) +
  scale_y_continuous(breaks = seq(0, 800, 100), limits = c(0, 815),
                     expand = c(0, 0)) +
  labs(
    title = "A  Naive binary benchmark",
    subtitle = "762 development material-codec decisions per threshold",
    x = "Bader threshold",
    y = "Number of decisions"
  ) +
  guides(fill = guide_legend(nrow = 1, byrow = TRUE)) +
  base_theme +
  theme(legend.position = "bottom", legend.box.margin = margin(t = -4))

# ---- Panel B: qualified three-state benchmark --------------------------------
p_b <- ggplot(S, aes(x = x)) +
  geom_rect(aes(xmin = x - bar_half, xmax = x + bar_half,
                ymin = 0, ymax = qualified_pass, fill = "Certified"),
            colour = "white", linewidth = 0.55) +
  geom_rect(aes(xmin = x - bar_half, xmax = x + bar_half,
                ymin = qualified_pass, ymax = qualified_pass + eligible_fail,
                fill = "Eligible failure"),
            colour = "white", linewidth = 0.55) +
  geom_rect(aes(xmin = x - bar_half, xmax = x + bar_half,
                ymin = qualified_pass + eligible_fail, ymax = n_decisions,
                fill = "Non-evaluable"),
            colour = "white", linewidth = 0.55) +
  geom_text(aes(y = qualified_pass / 2, label = qualified_pass),
            colour = "white", fontface = "bold", size = 4.4) +
  geom_text(aes(y = qualified_pass + eligible_fail / 2, label = eligible_fail),
            colour = "white", fontface = "bold", size = 3.7) +
  geom_text(aes(y = qualified_pass + eligible_fail + non_evaluable / 2,
                label = non_evaluable),
            colour = "white", fontface = "bold", size = 4.4) +
  geom_text(aes(y = 794, label = "Total = 762"),
            colour = col_text, size = 3.45) +
  scale_fill_manual(values = c(
    "Certified" = col_teal,
    "Eligible failure" = col_red,
    "Non-evaluable" = col_orange
  )) +
  scale_x_continuous(breaks = 1:3, labels = threshold_labels,
                     limits = c(0.5, 3.5), expand = c(0, 0)) +
  scale_y_continuous(breaks = seq(0, 800, 100), limits = c(0, 815),
                     expand = c(0, 0)) +
  labs(
    title = "B  Protocol A.1 three-state certification",
    subtitle = "Eligibility is established before codec success or failure is assigned",
    x = "Bader threshold",
    y = "Number of decisions"
  ) +
  guides(fill = guide_legend(nrow = 1, byrow = TRUE)) +
  base_theme +
  theme(legend.position = "bottom", legend.box.margin = margin(t = -4))

# ---- Panel C: failure reclassification ---------------------------------------
S_c <- S %>%
  mutate(
    callout_y = c(675, 540, 350),
    naive_label_y = naive_fail + c(28, 27, 24)
  )

p_c <- ggplot(S_c, aes(x = x)) +
  geom_rect(aes(xmin = x - bar_half, xmax = x + bar_half,
                ymin = 0, ymax = genuine_eligible_failure,
                fill = "Genuine eligible failure"),
            colour = "white", linewidth = 0.55) +
  geom_rect(aes(xmin = x - bar_half, xmax = x + bar_half,
                ymin = genuine_eligible_failure, ymax = naive_fail,
                fill = "Reclassified non-evaluable"),
            colour = "white", linewidth = 0.55) +
  geom_text(aes(y = genuine_eligible_failure / 2,
                label = genuine_eligible_failure),
            colour = "white", fontface = "bold", size = 3.7) +
  geom_text(aes(y = genuine_eligible_failure +
                  naive_fail_reclassified_non_evaluable / 2,
                label = naive_fail_reclassified_non_evaluable),
            colour = "white", fontface = "bold", size = 4.4) +
  geom_text(aes(y = naive_label_y,
                label = paste0("Naive failures = ", naive_fail)),
            colour = col_text, size = 3.35) +
  geom_label(aes(y = callout_y,
                 label = paste0(percent(fraction_naive_fail_reclassified,
                                        accuracy = 0.1), "\nreclassified")),
             fill = "white", colour = col_red, fontface = "bold",
             label.size = 0.35, size = 4.15, lineheight = 0.92) +
  scale_fill_manual(values = c(
    "Genuine eligible failure" = col_red,
    "Reclassified non-evaluable" = col_orange
  )) +
  scale_x_continuous(breaks = 1:3, labels = threshold_labels,
                     limits = c(0.5, 3.5), expand = c(0, 0)) +
  scale_y_continuous(breaks = seq(0, 700, 100), limits = c(0, 720),
                     expand = c(0, 0)) +
  labs(
    title = "C  Failure reclassification under Protocol A.1",
    subtitle = "Most naive failures at strict thresholds are non-evaluable targets",
    x = "Bader threshold",
    y = "Number of naive failures"
  ) +
  guides(fill = guide_legend(nrow = 2, byrow = TRUE)) +
  base_theme +
  theme(legend.position = "bottom", legend.box.margin = margin(t = -4))

# ---- Bottom takeaway ----------------------------------------------------------
p_key <- ggplot() +
  coord_cartesian(xlim = c(0, 1), ylim = c(0, 1), clip = "off") +
  theme_void() +
  annotate("rect", xmin = 0.005, xmax = 0.995, ymin = 0.08, ymax = 0.92,
           fill = "white", colour = "#94A3B8", linewidth = 0.45) +
  annotate("rect", xmin = 0.005, xmax = 0.16, ymin = 0.08, ymax = 0.92,
           fill = col_box, colour = "#94A3B8", linewidth = 0.45) +
  annotate("text", x = 0.082, y = 0.50,
           label = "Key takeaway", fontface = "bold", size = 5.8,
           colour = col_text) +
  annotate("segment", x = 0.175, xend = 0.175, y = 0.16, yend = 0.84,
           colour = "#94A3B8", linewidth = 0.45) +
  annotate("text", x = 0.195, y = 0.61, hjust = 0,
           label = "At strict Bader contracts, most apparent codec failures are not genuine compressor failures;",
           fontface = "bold", size = 4.35, colour = col_text) +
  annotate("text", x = 0.195, y = 0.37, hjust = 0,
           label = "they occur on material-threshold pairs that are non-evaluable under the independent Protocol A.1 stability qualification.",
           size = 4.05, colour = col_text) +
  annotate("text", x = 0.195, y = 0.19, hjust = 0,
           label = "Eligibility also invalidates apparent passes: 106/229 (46.3%) at 10^-4 e.",
           size = 3.65, colour = "#4B5563")

# ---- assemble -----------------------------------------------------------------
main_row <- p_a | p_b | p_c
fig <- (main_row / p_key) +
  plot_layout(heights = c(8.4, 1.6)) +
  plot_annotation(
    title = "Figure 3 | Binary benchmark vs stability-qualified three-state certification",
    theme = theme(
      plot.background = element_rect(fill = "white", colour = NA),
      plot.title = element_text(face = "bold", size = 18.5, hjust = 0.5,
                                colour = col_text, margin = margin(b = 7))
    )
  )

png_path <- file.path(outdir, "figure3_certification_landscape_R.png")
pdf_path <- file.path(outdir, "figure3_certification_landscape_R.pdf")
svg_path <- file.path(outdir, "figure3_certification_landscape_R.svg")

ggsave(png_path, fig, width = 14.2, height = 9.0, dpi = 360, bg = "white")
ggsave(pdf_path, fig, width = 14.2, height = 9.0, bg = "white")
ggsave(svg_path, fig, width = 14.2, height = 9.0, bg = "white",
       device = svglite::svglite)

message("Rendered: ", png_path)
message("Rendered: ", pdf_path)
message("Rendered: ", svg_path)
message("Headline reclassification: ",
        paste(percent(S$fraction_naive_fail_reclassified, accuracy = 0.1),
              collapse = " / "))
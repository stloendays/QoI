# Supplementary Figure S8 — untouched external confirmation details
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

sumd <- read.csv(file.path(root, "supplement", "S13_rate_fidelity_summary.csv"), stringsAsFactors = FALSE)
pair <- read.csv(file.path(root, "supplement", "S13_pairwise_sz3_zfp.csv"), stringsAsFactors = FALSE)

stopifnot(nrow(sumd) == 54)
stopifnot(nrow(pair) == 18)

thr_levels <- c(1e-4, 1e-3, 1e-2)
thr_labels <- c("10^-4 e", "10^-3 e", "10^-2 e")
codec_levels <- c("ZFP", "SZ3", "SPERR")
codec_cols <- c(ZFP = "#4A5F7E", SZ3 = "#D55E00", SPERR = "#2A9D8F")
cohort_cols <- c("Development" = "#4A5F7E", "External 63" = "#2A9D8F")

# Frozen external assertions.
ext <- sumd %>% filter(cohort == "external_confirmatory63", stratum == "overall")
stopifnot(nrow(ext) == 9)
for (i in seq_along(thr_levels)) {
  z <- ext %>% filter(abs(threshold_e - thr_levels[i]) < 1e-15, codec == "ZFP")
  stopifnot(nrow(z) == 1)
}
stopifnot((ext %>% filter(codec == "ZFP") %>% arrange(threshold_e) %>% pull(n_admitted)) |> sort() |> identical(c(16L,42L,57L)))
stopifnot(abs((ext %>% filter(abs(threshold_e - 1e-2) < 1e-15, codec == "SZ3"))$ratio_median - 65.89190594093266) < 1e-10)

bg <- "#FFFFFF"; ink <- "#202124"; muted <- "#5F6368"; grid <- "#E5E7EB"
base_theme <- theme_minimal(base_size = 10.2) + theme(
  plot.background = element_rect(fill = bg, colour = NA),
  panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(), panel.grid.major = element_line(colour = grid, linewidth = .3),
  axis.title = element_text(colour = ink), axis.text = element_text(colour = ink),
  strip.text = element_text(face = "bold", size = 9.0, colour = ink),
  strip.background = element_rect(fill = "#F5F6F7", colour = NA),
  legend.title = element_blank(), legend.text = element_text(size = 8.6),
  plot.title = element_text(face = "bold", size = 10.9, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 8.6, colour = muted, margin = margin(b = 6)),
  plot.margin = margin(8, 9, 8, 8)
)

prep <- function(df) df %>% mutate(
  threshold = factor(threshold_e, levels = thr_levels, labels = thr_labels),
  codec = factor(codec, levels = codec_levels),
  cohort_label = factor(ifelse(cohort == "development", "Development", "External 63"), levels = c("Development", "External 63"))
)

# A — overall rate-fidelity transition reproduced externally.
a <- prep(sumd %>% filter(stratum == "overall"))
pA <- ggplot(a, aes(threshold, ratio_median, colour = codec, group = codec)) +
  geom_linerange(aes(ymin = ratio_median_ci_lo, ymax = ratio_median_ci_hi), linewidth = .7, position = position_dodge(width = .18)) +
  geom_line(linewidth = .85) + geom_point(size = 2.4) +
  facet_wrap(~cohort_label, nrow = 1) +
  scale_colour_manual(values = codec_cols) +
  scale_y_log10(breaks = c(4, 8, 16, 32, 64, 128), labels = label_number(suffix = "x")) +
  labs(
    title = "A | Rate-fidelity ordering changes with the scientific contract",
    subtitle = "Median best-certified compression ratio with 95% material-bootstrap CI",
    x = "Bader contract", y = "Best-certified compression ratio"
  ) + base_theme + theme(legend.position = "top")

# B — external eligible cohort expands with tolerance.
elig <- ext %>% filter(codec == "ZFP") %>% arrange(threshold_e) %>% mutate(
  threshold = factor(threshold_e, levels = thr_levels, labels = thr_labels),
  eligible_fraction = n_admitted / 63,
  label = paste0(n_admitted, "/63")
)
pB <- ggplot(elig, aes(threshold, eligible_fraction, group = 1)) +
  geom_line(linewidth = .9, colour = "#2A9D8F") +
  geom_point(size = 3.0, colour = "#2A9D8F") +
  geom_text(aes(label = label), vjust = -0.8, size = 3.1, colour = ink) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0,1,.25), labels = percent_format(accuracy = 1), expand = expansion(mult = c(.02,.12))) +
  labs(
    title = "B | The externally measurable cohort expands as tolerance relaxes",
    subtitle = "QSQ eligibility; denominator is the untouched 63-system cohort",
    x = "Bader contract", y = "Eligible external systems"
  ) + base_theme

# C — pairwise SZ3-vs-ZFP transition in development and external confirmation.
c <- pair %>% filter(stratum == "overall") %>% mutate(
  threshold = factor(threshold_e, levels = thr_levels, labels = thr_labels),
  cohort_label = factor(ifelse(cohort == "development", "Development", "External 63"), levels = c("Development", "External 63"))
)
stopifnot(nrow(c) == 6)
pC <- ggplot(c, aes(threshold, sz3_win_fraction, colour = cohort_label, group = cohort_label)) +
  geom_hline(yintercept = .5, linetype = 2, colour = "#9AA0A6", linewidth = .6) +
  geom_linerange(aes(ymin = sz3_win_ci_lo, ymax = sz3_win_ci_hi), position = position_dodge(width = .18), linewidth = .75) +
  geom_line(linewidth = .9) + geom_point(size = 2.6) +
  scale_colour_manual(values = cohort_cols) +
  scale_y_continuous(limits = c(0,1), labels = percent_format(accuracy = 1)) +
  labs(
    title = "C | The SZ3-versus-ZFP crossover reproduces externally",
    subtitle = "Pairwise win fraction among eligible material comparisons; bars show bootstrap interval for SZ3 wins",
    x = "Bader contract", y = "SZ3 win fraction versus ZFP"
  ) + base_theme + theme(legend.position = "top")

# D — certification conditional on external eligibility.
d <- prep(ext)
pD <- ggplot(d, aes(threshold, frac_certified, colour = codec, group = codec)) +
  geom_hline(yintercept = 1, linetype = 2, colour = "#9AA0A6", linewidth = .6) +
  geom_line(linewidth = .9) + geom_point(size = 2.6) +
  scale_colour_manual(values = codec_cols) +
  scale_y_continuous(limits = c(.75,1.01), breaks = c(.75,.80,.85,.90,.95,1), labels = percent_format(accuracy = 1)) +
  labs(
    title = "D | Certification remains high after conditioning on eligibility",
    subtitle = "External certification fraction among QSQ-eligible systems",
    x = "Bader contract", y = "Certified fraction among admitted"
  ) + base_theme + theme(legend.position = "top")

fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(heights = c(1, 1)) +
  plot_annotation(
    title = "Supplementary Figure S8 | Frozen rate-fidelity conclusions reproduce on the untouched external cohort",
    subtitle = "Eligibility expands with tolerance and the codec ordering changes with the scientific contract; no qualification or scoring rule was retuned for external evaluation.",
    caption = paste0(
      "A, pooled development and external rate-fidelity frontiers. B, external QSQ eligibility. ",
      "C, pairwise SZ3-versus-ZFP crossover. D, certification conditional on eligibility.\n",
      "The 63-system confirmatory cohort is distinct from the 65-system external descriptive/stability set; external rate-fidelity claims use only the frozen 63-system confirmatory outputs."
    ),
    theme = theme(
      plot.background = element_rect(fill = bg, colour = NA),
      plot.title = element_text(face = "bold", size = 13.8, colour = ink, margin = margin(b = 4)),
      plot.subtitle = element_text(size = 9.3, colour = muted, margin = margin(b = 8)),
      plot.caption = element_text(size = 7.8, colour = muted, hjust = 0, lineheight = 1.15, margin = margin(t = 8))
    )
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS8_external_confirmation_R.png"),
  pdf = file.path(outdir, "supplementary_figureS8_external_confirmation_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS8_external_confirmation_R.svg")
)
ggsave(paths[["png"]], fig, width = 13.4, height = 9.2, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 13.4, height = 9.2, bg = bg)
ggsave(paths[["svg"]], fig, width = 13.4, height = 9.2, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S8: PNG + PDF + SVG")
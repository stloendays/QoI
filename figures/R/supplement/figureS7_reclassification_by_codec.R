# Supplementary Figure S7 — codec-resolved binary-to-three-state reclassification
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

f <- file.path(root, "analysis", "certifiability_reclassification_by_codec_20260911.csv")
d <- read.csv(f, stringsAsFactors = FALSE)
stopifnot(nrow(d) == 9)
stopifnot(all(c("threshold_e", "codec", "naive_pass", "naive_fail", "eligible_fail", "non_evaluable_naive_pass", "naive_fail_reclassified_non_evaluable", "reclassified_fraction_of_naive_fail") %in% names(d)))

codec_levels <- c("ZFP", "SZ3", "SPERR")
d$codec <- factor(toupper(d$codec), levels = codec_levels)
d$tau <- factor(d$threshold_e, levels = c(1e-4, 1e-3, 1e-2), labels = c("10^-4 e", "10^-3 e", "10^-2 e"))
stopifnot(all(!is.na(d$codec)), all(!is.na(d$tau)))

# Frozen assertions from the audited development benchmark.
expected_fail <- c(135, 86, 21, 205, 114, 45, 193, 110, 42)
check <- d %>% arrange(codec, threshold_e)
stopifnot(identical(as.integer(check$naive_fail), as.integer(expected_fail)))

fail_long <- d %>%
  select(codec, tau, naive_fail, eligible_fail, naive_fail_reclassified_non_evaluable, reclassified_fraction_of_naive_fail) %>%
  pivot_longer(cols = c(eligible_fail, naive_fail_reclassified_non_evaluable), names_to = "state", values_to = "count") %>%
  mutate(state = recode(state,
    eligible_fail = "Genuine eligible failure",
    naive_fail_reclassified_non_evaluable = "Reclassified non-evaluable"))

pass <- d %>% mutate(invalid_pass_fraction = non_evaluable_naive_pass / naive_pass)
pass_strict <- pass %>% filter(threshold_e == 1e-4)

bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E5E7EB"; muted <- "#5F6368"
col_red <- "#D94B41"; col_orange <- "#E9B13A"
codec_cols <- c(ZFP = "#4A5F7E", SZ3 = "#D55E00", SPERR = "#2A9D8F")
theme_si <- theme_minimal(base_size = 10.6) + theme(
  plot.background = element_rect(fill = bg, colour = NA), panel.background = element_rect(fill = bg, colour = NA),
  panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
  panel.grid.major.y = element_line(colour = grid, linewidth = .3),
  axis.title = element_text(colour = ink), axis.text = element_text(colour = ink),
  plot.title = element_text(face = "bold", size = 11.3, colour = ink, margin = margin(b = 4)),
  plot.subtitle = element_text(size = 9.0, colour = muted, margin = margin(b = 6)),
  strip.text = element_text(face = "bold", colour = ink), strip.background = element_rect(fill = "#F8FAFC", colour = NA),
  legend.title = element_blank(), legend.text = element_text(size = 9.0), plot.margin = margin(8, 10, 8, 8)
)

pA <- ggplot(fail_long, aes(tau, count, fill = state)) +
  geom_col(width = .68, colour = "white", linewidth = .5) +
  geom_text(data = d, aes(tau, naive_fail + 10, label = percent(reclassified_fraction_of_naive_fail, accuracy = .1)),
            inherit.aes = FALSE, fontface = "bold", size = 3.35, colour = col_red) +
  geom_text(data = d, aes(tau, naive_fail + 24, label = paste0("n=", naive_fail)),
            inherit.aes = FALSE, size = 2.85, colour = muted) +
  facet_wrap(~ codec, nrow = 1) +
  scale_fill_manual(values = c("Genuine eligible failure" = col_red, "Reclassified non-evaluable" = col_orange)) +
  scale_y_continuous(limits = c(0, 245), breaks = seq(0, 200, 50), expand = c(0, 0)) +
  labs(
    title = "A | Strict-threshold reclassification appears in every codec",
    subtitle = "Percent labels are naive failures reclassified as non-evaluable",
    x = "Bader tolerance", y = "Naive failures"
  ) + theme_si + theme(legend.position = "top")

pB <- ggplot(pass, aes(tau, invalid_pass_fraction, colour = codec, group = codec)) +
  geom_hline(yintercept = 0, colour = "#AEB4BB", linewidth = .4) +
  geom_line(linewidth = .9) + geom_point(size = 2.8) +
  geom_text(data = pass_strict, aes(label = paste0(non_evaluable_naive_pass, "/", naive_pass)),
            vjust = -1.05, size = 2.9, show.legend = FALSE) +
  scale_colour_manual(values = codec_cols) +
  scale_y_continuous(limits = c(0, .70), breaks = seq(0, .6, .1), labels = label_percent(), expand = c(0, 0)) +
  labs(
    title = "B | Qualification also invalidates apparent successes",
    subtitle = "Strict-contract counts are labelled; complete counts are in Supplementary Table S4",
    x = "Bader tolerance", y = "Non-evaluable fraction of naive passes"
  ) + theme_si + theme(legend.position = "top")

pC <- ggplot(d, aes(tau, eligible_fail / n_eligible, colour = codec, group = codec)) +
  geom_line(linewidth = .9) + geom_point(size = 2.8) +
  scale_colour_manual(values = codec_cols) +
  scale_y_continuous(limits = c(0, .12), breaks = seq(0, .10, .02), labels = label_percent(), expand = c(0, 0)) +
  labs(
    title = "C | Genuine failure is defined only among eligible decisions",
    subtitle = "Exact counts are reported in Supplementary Table S4",
    x = "Bader tolerance", y = "Eligible failure fraction"
  ) + theme_si + theme(legend.position = "top")

fig <- (pA / (pB | pC)) +
  plot_layout(heights = c(1.15, .85)) +
  plot_annotation(
    title = "Supplementary Figure S7 | Codec-resolved consequences of stability qualification",
    subtitle = "At 10^-4 and 10^-3 e, more than 93% of naive failures for every codec lie on non-evaluable material-threshold pairs.",
    caption = "Each codec contributes 254 development decisions per threshold. Protocol A.1 removes invalid successes as well as invalid failures; non-evaluable is neither pass nor failure.",
    theme = theme(plot.background = element_rect(fill = bg, colour = NA),
                  plot.title = element_text(face = "bold", size = 14.1, colour = ink, margin = margin(b = 4)),
                  plot.subtitle = element_text(size = 9.6, colour = muted, margin = margin(b = 8)),
                  plot.caption = element_text(size = 8.1, colour = muted, hjust = 0, margin = margin(t = 8)))
  )

paths <- c(
  png = file.path(outdir, "supplementary_figureS7_reclassification_by_codec_R.png"),
  pdf = file.path(outdir, "supplementary_figureS7_reclassification_by_codec_R.pdf"),
  svg = file.path(outdir, "supplementary_figureS7_reclassification_by_codec_R.svg")
)
ggsave(paths[["png"]], fig, width = 12.6, height = 8.5, dpi = 360, bg = bg)
ggsave(paths[["pdf"]], fig, width = 12.6, height = 8.5, bg = bg)
ggsave(paths[["svg"]], fig, width = 12.6, height = 8.5, device = svglite::svglite, bg = bg)
stopifnot(all(file.exists(paths)), all(file.info(paths)$size > 0))
message("Rendered Supplementary Figure S7: PNG + PDF + SVG")

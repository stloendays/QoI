# Figure 3 — QSQ prospective validation after equalizing benchmark opportunity
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

p1_path <- file.path(root, "analysis", "research_upgrade", "p1_common_tight_summary.csv")
p2_path <- file.path(root, "analysis", "research_upgrade", "p2_fresh_probe_cohort_summary.csv")
if (!file.exists(p1_path) || !file.exists(p2_path)) stop("Figure 3 requires completed P1 and P2 machine-readable summaries.")
p1 <- read.csv(p1_path, stringsAsFactors = FALSE, check.names = FALSE)
p2 <- read.csv(p2_path, stringsAsFactors = FALSE, check.names = FALSE)

# Frozen prospective-result assertions. Fail formal rendering if the source evidence drifts silently.
stopifnot(nrow(p1) == 3L, all(p1$design == "completed_common_tight"))
stopifnot(identical(as.integer(p1$n_decisions), c(762L, 762L, 762L)))
stopifnot(all(abs(p1$no_pass_risk_eligible - c(0.10869565217391304, 0.03263403263403263, 0.0)) < 1e-15))
stopifnot(all(abs(p1$no_pass_risk_non_evaluable - c(0.7932692307692307, 0.6636636636636637, 0.68)) < 1e-15))
stopifnot(nrow(p2) == 6L)
stopifnot(all(tapply(p2$planned_trials, p2$tau_e, sum) == 14986L)) # same 14,986 physical trials summarized at each threshold
p2_primary <- p2[p2$tau_e == 1e-3, , drop = FALSE]
stopifnot(nrow(p2_primary) == 2L)
stopifnot(sum(p2_primary$valid_trials) == 14986L, sum(p2_primary$unresolved_trials) == 0L)
stopifnot(p2_primary$n_materials[p2_primary$gate_group == "eligible"] == 143L)
stopifnot(p2_primary$n_materials[p2_primary$gate_group == "screen_rejected"] == 111L)
stopifnot(p2_primary$exceedance_events[p2_primary$gate_group == "eligible"] == 135L)
stopifnot(p2_primary$exceedance_events[p2_primary$gate_group == "screen_rejected"] == 5326L)

threshold_order <- c(1e-4, 1e-3, 1e-2)
threshold_labels <- c(expression(10^-4~e), expression(10^-3~e), expression(10^-2~e))
threshold_text <- c("10^-4 e", "10^-3 e", "10^-2 e")

col_teal <- "#2A9D8F"
col_red <- "#D94B41"
col_orange <- "#E9B13A"
col_navy <- "#355C7D"
col_text <- "#1F2937"
col_mid <- "#64748B"
col_grid <- "#E5E7EB"
col_box <- "#F8FAFC"

base_theme <- theme_minimal(base_size = 11.2) + theme(
  plot.background = element_rect(fill = "white", colour = NA),
  panel.background = element_rect(fill = "white", colour = NA),
  panel.grid.minor = element_blank(),
  panel.grid.major.y = element_blank(),
  panel.grid.major.x = element_line(colour = col_grid, linewidth = 0.35),
  axis.title = element_text(colour = col_text, size = 11.4),
  axis.text = element_text(colour = col_text, size = 10.1),
  plot.title = element_text(face = "bold", colour = col_text, size = 13.4, margin = margin(b = 4)),
  plot.subtitle = element_text(colour = col_mid, size = 9.8, lineheight = 1.06, margin = margin(b = 8)),
  legend.title = element_blank(),
  legend.text = element_text(colour = col_text, size = 9.6),
  plot.margin = margin(8, 10, 8, 8)
)

# Panel A: primary endpoint as an outcome-blind gate -> fresh-test flow.
A <- data.frame(
  group = c("Eligible", "Screen-rejected"),
  materials = c(143, 111),
  trials = c(8437, 6549),
  events = c(135, 5326),
  risk = c(0.016000948204338034, 0.8132539318979997),
  ymin = c(0.53, 0.08), ymax = c(0.92, 0.47),
  colour = c(col_teal, col_red), stringsAsFactors = FALSE
)

p_a <- ggplot() +
  coord_cartesian(xlim = c(0, 1), ylim = c(0, 1), clip = "off") +
  annotate("rect", xmin = 0.02, xmax = 0.29, ymin = 0.35, ymax = 0.67, fill = col_box, colour = "#94A3B8", linewidth = 0.55) +
  annotate("text", x = 0.155, y = 0.57, label = "Frozen QSQ gate", fontface = "bold", size = 4.5, colour = col_text) +
  annotate("text", x = 0.155, y = 0.47, label = "254 development materials", size = 3.75, colour = col_mid) +
  annotate("text", x = 0.155, y = 0.395, label = expression(tau == 10^-3~e), size = 3.8, colour = col_mid) +
  annotate("segment", x = 0.29, xend = 0.42, y = 0.55, yend = 0.73, colour = "#94A3B8", linewidth = 0.65) +
  annotate("segment", x = 0.29, xend = 0.42, y = 0.47, yend = 0.27, colour = "#94A3B8", linewidth = 0.65) +
  annotate("rect", xmin = 0.42, xmax = 0.98, ymin = A$ymin[1], ymax = A$ymax[1], fill = "#F4FBF9", colour = col_teal, linewidth = 0.75) +
  annotate("rect", xmin = 0.42, xmax = 0.98, ymin = A$ymin[2], ymax = A$ymax[2], fill = "#FFF7F5", colour = col_red, linewidth = 0.75) +
  annotate("text", x = 0.455, y = 0.84, hjust = 0, label = "Eligible  |  143 materials", fontface = "bold", size = 4.15, colour = col_teal) +
  annotate("text", x = 0.455, y = 0.73, hjust = 0, label = "135 / 8,437 fresh trials exceed threshold", size = 3.55, colour = col_text) +
  annotate("text", x = 0.455, y = 0.62, hjust = 0, label = "1.60%  [0.78–2.60%]", fontface = "bold", size = 4.35, colour = col_teal) +
  annotate("text", x = 0.455, y = 0.39, hjust = 0, label = "Screen-rejected  |  111 materials", fontface = "bold", size = 4.15, colour = col_red) +
  annotate("text", x = 0.455, y = 0.28, hjust = 0, label = "5,326 / 6,549 fresh trials exceed threshold", size = 3.55, colour = col_text) +
  annotate("text", x = 0.455, y = 0.17, hjust = 0, label = "81.33%  [75.98–86.26%]", fontface = "bold", size = 4.35, colour = col_red) +
  labs(title = "A  Frozen gate predicts fresh perturbation risk",
       subtitle = "Primary endpoint; 59 pre-registered unseen streams per material") +
  theme_void(base_size = 11.2) +
  theme(plot.title = element_text(face = "bold", colour = col_text, size = 13.4, margin = margin(b = 4)),
        plot.subtitle = element_text(colour = col_mid, size = 9.8, margin = margin(b = 6)),
        plot.margin = margin(8, 10, 8, 8))

# Panel B: completed common tight ladder, equal search opportunity across all materials.
p1_plot <- p1 %>%
  mutate(threshold = factor(tau_e, levels = threshold_order, labels = threshold_text)) %>%
  select(threshold, eligible = no_pass_risk_eligible, rejected = no_pass_risk_non_evaluable,
         rr = risk_ratio_non_evaluable_vs_eligible) %>%
  pivot_longer(c(eligible, rejected), names_to = "group", values_to = "risk") %>%
  mutate(group = recode(group, eligible = "Eligible", rejected = "Screen-rejected"))

p1_lines <- p1 %>% mutate(threshold = factor(tau_e, levels = threshold_order, labels = threshold_text),
                          xmin = no_pass_risk_eligible, xmax = no_pass_risk_non_evaluable)
rr_lab <- c("7.30×", "20.34×", "∞")
p1_lines$rr_lab <- rr_lab

p_b <- ggplot() +
  geom_segment(data = p1_lines, aes(x = xmin, xend = xmax, y = threshold, yend = threshold), colour = "#CBD5E1", linewidth = 1.3) +
  geom_point(data = p1_plot, aes(x = risk, y = threshold, fill = group), shape = 21, size = 4.6, colour = "white", stroke = 0.5) +
  geom_text(data = p1_lines, aes(x = pmin(xmax + 0.055, 0.96), y = threshold, label = rr_lab), hjust = 0, fontface = "bold", size = 3.5, colour = col_navy) +
  scale_fill_manual(values = c("Eligible" = col_teal, "Screen-rejected" = col_red)) +
  scale_x_continuous(labels = label_percent(accuracy = 1), limits = c(0, 1.03), breaks = seq(0, 1, 0.2), expand = c(0,0)) +
  labs(title = "B  Risk persists after equalizing codec search opportunity",
       subtitle = "1,332/1,332 additive tight-ladder reconstructions succeeded",
       x = "Material–codec risk of finding no numerical pass", y = "Bader threshold") +
  base_theme + theme(legend.position = "bottom")

# Panel C: prospective fresh perturbation risk with material-cluster uncertainty.
p2_plot <- p2 %>%
  mutate(threshold = factor(tau_e, levels = threshold_order, labels = threshold_text),
         group = recode(gate_group, eligible = "Eligible", screen_rejected = "Screen-rejected"))

rr2 <- data.frame(threshold = factor(threshold_text, levels = threshold_text),
                  label = c("21.65×", "50.83×", "537.69×"), y = c(0.985, 0.985, 0.985))

p_c <- ggplot(p2_plot, aes(x = valid_trial_exceedance_fraction, y = threshold, fill = group)) +
  geom_errorbarh(aes(xmin = material_cluster_ci_low, xmax = material_cluster_ci_high), height = 0.17,
                 position = position_dodge(width = 0.42), linewidth = 0.8, colour = "#64748B") +
  geom_point(shape = 21, size = 4.7, colour = "white", stroke = 0.55, position = position_dodge(width = 0.42)) +
  geom_text(data = rr2, aes(x = y, y = threshold, label = label), inherit.aes = FALSE,
            hjust = 1, fontface = "bold", size = 3.5, colour = col_navy) +
  scale_fill_manual(values = c("Eligible" = col_teal, "Screen-rejected" = col_red)) +
  scale_x_continuous(labels = label_percent(accuracy = 1), limits = c(0, 1.0), breaks = seq(0, 1, 0.2), expand = c(0,0)) +
  labs(title = "C  Prospective discrimination generalizes across thresholds",
       subtitle = "14,986/14,986 fresh trials; intervals resample materials, not trials",
       x = "Fresh-threshold exceedance risk", y = "Bader threshold") +
  base_theme + theme(legend.position = "bottom")

p_key <- ggplot() + coord_cartesian(xlim = c(0,1), ylim = c(0,1), clip = "off") + theme_void() +
  annotate("rect", xmin=.005, xmax=.995, ymin=.08, ymax=.92, fill="white", colour="#94A3B8", linewidth=.45) +
  annotate("rect", xmin=.005, xmax=.17, ymin=.08, ymax=.92, fill=col_box, colour="#94A3B8", linewidth=.45) +
  annotate("text", x=.087, y=.50, label="Primary result", fontface="bold", size=5.5, colour=col_text) +
  annotate("segment", x=.185, xend=.185, y=.16, yend=.84, colour="#94A3B8", linewidth=.45) +
  annotate("text", x=.205, y=.62, hjust=0, label="At 10^-3 e, the frozen five-seed QSQ gate retains 56.3% of materials while separating", fontface="bold", size=4.2, colour=col_text) +
  annotate("text", x=.205, y=.40, hjust=0, label="1.60% fresh exceedance risk in admitted materials from 81.33% in screen-rejected materials (50.83×).", size=4.05, colour=col_text) +
  annotate("text", x=.205, y=.20, hjust=0, label="This is prospective risk stratification under the declared iid-uniform model — not a worst-case stability guarantee.", size=3.7, colour=col_mid)

fig <- ((p_a | p_b | p_c) / p_key) + plot_layout(heights = c(8.5,1.5), widths = c(1.05,1,1)) +
  plot_annotation(title = "Figure 3 | QoI Stability Qualification prospectively stratifies downstream numerical risk",
                  theme = theme(plot.background = element_rect(fill="white", colour=NA),
                                plot.title = element_text(face="bold", size=18.0, hjust=.5, colour=col_text, margin=margin(b=7))))

png_path <- file.path(outdir, "figure3_certification_landscape_R.png")
pdf_path <- file.path(outdir, "figure3_certification_landscape_R.pdf")
svg_path <- file.path(outdir, "figure3_certification_landscape_R.svg")
ggsave(png_path, fig, width=15.4, height=8.9, dpi=360, bg="white")
ggsave(pdf_path, fig, width=15.4, height=8.9, bg="white")
ggsave(svg_path, fig, width=15.4, height=8.9, bg="white", device=svglite::svglite)
message("Rendered: ", png_path)
message("Rendered: ", pdf_path)
message("Rendered: ", svg_path)
message("Primary P2: eligible risk 1.600%; screen-rejected risk 81.325%; RR 50.83x; acceptance 56.3%")

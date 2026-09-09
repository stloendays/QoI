# Figure 4 — Protocol A -> A.1 stability floor
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(scales)
  library(patchwork)
})

if (!requireNamespace("svglite", quietly=TRUE)) {
  stop("Package 'svglite' is required for the vector SVG export.")
}

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

a1 <- read.csv(file.path(root, "stability", "stability_floor_A1.csv"), stringsAsFactors=FALSE)
a0 <- read.csv(file.path(root, "stability", "stability_floor_A_archived_float32.csv"), stringsAsFactors=FALSE)

if (!"floor_resolved_e" %in% names(a0)) {
  stop("Archived Protocol A table is missing floor_resolved_e")
}

# Palette synchronized with Figures 2–3.
pal <- c(
  light_green = "#B8DBB3",
  green       = "#72B063",
  blue        = "#719AAC",
  orange      = "#E29135",
  teal        = "#94C6CD",
  navy        = "#4A5F7E"
)
bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E7E8EA"; muted <- "#646A73"

m <- merge(
  a1[, c("material_id", "domain", "stability_floor_A1_e")],
  a0[, c("material_id", "floor_resolved_e")],
  by="material_id"
) %>%
  rename(archived=floor_resolved_e) %>%
  filter(is.finite(archived), is.finite(stability_floor_A1_e),
         archived > 0, stability_floor_A1_e > 0) %>%
  mutate(ratio=stability_floor_A1_e/archived)

th <- theme_minimal(base_size=10.4) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink),
  axis.text=element_text(colour=ink),
  plot.title=element_text(face="bold", size=11.2, margin=margin(b=5)),
  plot.subtitle=element_text(size=9.0, colour="#4F545C", margin=margin(b=6)),
  legend.position="top",
  legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

# A — paired material-level shift from archived Protocol A to frozen A.1.
L <- m %>%
  mutate(id=row_number()) %>%
  select(id, domain, Archived=archived, `A.1`=stability_floor_A1_e) %>%
  pivot_longer(c(Archived, `A.1`), names_to="protocol", values_to="floor")
L$protocol <- factor(L$protocol, levels=c("Archived", "A.1"))

p1 <- ggplot(L, aes(protocol, floor, group=id)) +
  geom_line(alpha=.13, colour="#969B9F", linewidth=.35) +
  geom_point(data=L %>% filter(protocol=="Archived"),
             colour="#B7BABD", alpha=.42, size=.8) +
  geom_point(data=L %>% filter(protocol=="A.1"),
             colour=pal[["blue"]], alpha=.48, size=.85) +
  scale_y_log10(labels=label_scientific()) +
  labs(
    title="A | Probe definition materially changes the inferred stability floor",
    subtitle=sprintf("Paired comparison across %d materials; each line is one density field", nrow(m)),
    x=NULL, y="Resolved Bader stability floor (e)"
  ) + th

# B — ECDF against chemically meaningful certification thresholds.
thresholds <- data.frame(
  x=c(1e-4, 1e-3, 1e-2),
  label=c("10^-4", "10^-3", "10^-2"),
  col=c(pal[["green"]], pal[["orange"]], pal[["navy"]])
)

p2 <- ggplot(a1 %>% filter(is.finite(stability_floor_A1_e), stability_floor_A1_e>0),
             aes(stability_floor_A1_e)) +
  stat_ecdf(geom="step", linewidth=1.25, colour=pal[["navy"]]) +
  geom_vline(data=thresholds, aes(xintercept=x, colour=label), linetype=2, linewidth=.65) +
  scale_colour_manual(values=setNames(thresholds$col, thresholds$label)) +
  scale_x_log10(labels=label_scientific()) +
  scale_y_continuous(limits=c(0,1), breaks=seq(0,1,.2), labels=label_percent()) +
  labs(
    title="B | Eligibility follows directly from the A.1 floor distribution",
    subtitle="A material is eligible at tau only when its uncompressed stability floor is below tau",
    x="Protocol A.1 stability floor (e)", y="Cumulative material fraction",
    colour="Chemical tolerance tau (e)"
  ) + th

# C — protocol correction factor is heterogeneous rather than a global rescaling.
med_ratio <- median(m$ratio, na.rm=TRUE)
q_ratio <- quantile(m$ratio, c(.10,.90), na.rm=TRUE)

p3 <- ggplot(m, aes(ratio)) +
  geom_histogram(aes(y=after_stat(density)), bins=45,
                 fill=pal[["light_green"]], colour=bg, alpha=.75) +
  geom_density(colour=pal[["orange"]], linewidth=1.05, adjust=1.05) +
  geom_vline(xintercept=1, linetype=2, colour="#676C72", linewidth=.6) +
  geom_vline(xintercept=med_ratio, colour=pal[["navy"]], linewidth=.7) +
  annotate("label",
           x=quantile(m$ratio, .72, na.rm=TRUE),
           y=Inf,
           label=sprintf("median = %.2fx\n10th–90th = %.2fx–%.2fx", med_ratio, q_ratio[[1]], q_ratio[[2]]),
           hjust=0, vjust=1.3, size=3.0, label.size=.18,
           fill=alpha("white", .92), colour=ink) +
  scale_x_log10(labels=label_number(accuracy=.1, suffix="x")) +
  labs(
    title="C | The protocol correction is strongly material dependent",
    subtitle="A single multiplicative correction cannot recover the A.1 identifiability floor",
    x="A.1 / archived stability-floor ratio", y="Density"
  ) + th

fig <- (p1 | p2 | p3) +
  plot_layout(widths=c(1.10,1.08,1.05), guides="collect") +
  plot_annotation(
    title="Figure 4 | Stability is a property of the observable and its measurement protocol",
    subtitle="Protocol A.1 replaces the archived float32 perturbation probe with a frozen five-seed uniform-noise probe at the same float32 L-infinity amplitude.",
    caption="Protocol A remains archived and unchanged. All headline eligibility and certification statistics use the frozen Protocol A.1 definition.",
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=10, colour="#4F545C", margin=margin(b=8)),
      plot.caption=element_text(size=8.2, colour=muted, hjust=0, margin=margin(t=7))
    )
  )

png_path <- file.path(outdir, "figure4_stability_protocol_R.png")
pdf_path <- file.path(outdir, "figure4_stability_protocol_R.pdf")
svg_path <- file.path(outdir, "figure4_stability_protocol_R.svg")

ggsave(png_path, fig, width=12.4, height=4.9, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=12.4, height=4.9, bg=bg)
ggsave(svg_path, fig, width=12.4, height=4.9, bg=bg, device=svglite::svglite)

message("Rendered: ", svg_path)

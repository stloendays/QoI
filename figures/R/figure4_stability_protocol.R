# Figure 4 — QSQ perturbation-probe validation against the archived float32 probe
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
if (!"floor_resolved_e" %in% names(a0)) stop("Archived float32-probe table is missing floor_resolved_e")

pal <- c(light_green="#B8DBB3", green="#72B063", blue="#719AAC",
         orange="#E29135", teal="#94C6CD", navy="#4A5F7E")
bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E7E8EA"; muted <- "#646A73"

m <- merge(a1[, c("material_id", "domain", "stability_floor_A1_e")],
           a0[, c("material_id", "floor_resolved_e")], by="material_id") %>%
  rename(archived=floor_resolved_e) %>%
  filter(is.finite(archived), is.finite(stability_floor_A1_e), archived>0, stability_floor_A1_e>0) %>%
  mutate(ratio=stability_floor_A1_e/archived)

all_a1 <- a1 %>% filter(is.finite(stability_floor_A1_e), stability_floor_A1_e>0)

th <- theme_minimal(base_size=10.4) + theme(
  plot.background=element_rect(fill=bg, colour=NA), panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(), panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink), axis.text=element_text(colour=ink),
  plot.title=element_text(face="bold", size=11.2, margin=margin(b=4)),
  plot.subtitle=element_text(size=9.0, colour="#4F545C", margin=margin(b=6)),
  plot.margin=margin(8,10,8,8), legend.position="none")

# A — paired development-material shift from the archived float32 probe to QSQ.
L <- m %>% mutate(id=row_number()) %>%
  select(id, `Archived probe`=archived, QSQ=stability_floor_A1_e) %>%
  pivot_longer(c(`Archived probe`, QSQ), names_to="procedure", values_to="floor")
L$procedure <- factor(L$procedure, levels=c("Archived probe","QSQ"))

p1 <- ggplot(L, aes(procedure, floor, group=id)) +
  geom_line(alpha=.12, colour="#969B9F", linewidth=.34) +
  geom_point(data=L %>% filter(procedure=="Archived probe"), colour="#B7BABD", alpha=.42, size=.8) +
  geom_point(data=L %>% filter(procedure=="QSQ"), colour=pal[["blue"]], alpha=.48, size=.85) +
  scale_y_log10(labels=label_scientific(digits=1)) +
  labs(title="A | The stability probe materially changes the inferred floor",
       subtitle=sprintf("Paired development comparison across %d density fields", nrow(m)),
       x=NULL, y="Re-derived Bader stability floor (e)") + th

# B — paired scatter makes heterogeneity and direction explicit.
med_ratio <- median(m$ratio, na.rm=TRUE)
p2 <- ggplot(m, aes(archived, stability_floor_A1_e)) +
  geom_abline(slope=1, intercept=0, linetype=2, linewidth=.55, colour="#6B7076") +
  geom_point(alpha=.38, size=1.25, colour=pal[["navy"]]) +
  annotate("label", x=quantile(m$archived,.06), y=quantile(m$stability_floor_A1_e,.94),
           label=sprintf("paired-development median shift\n= %.2g x", med_ratio),
           hjust=0, vjust=1, size=3.0, label.size=.18, fill=alpha("white",.94), colour=ink) +
  scale_x_log10(labels=label_scientific(digits=1)) +
  scale_y_log10(labels=label_scientific(digits=1)) +
  labs(title="B | The correction is heterogeneous, not a global rescaling",
       subtitle="Dashed line is equality; points above it have a larger QSQ floor",
       x="Archived float32-probe floor (e)", y="QSQ stability floor (e)") + th

# C — all QSQ systems define the scientific eligibility ceiling.
thresholds <- data.frame(x=c(1e-4,1e-3,1e-2), lab=c("10^-4","10^-3","10^-2"),
                         col=c(pal[["green"]],pal[["orange"]],pal[["navy"]]))
thresholds$eligible <- vapply(thresholds$x, function(z) mean(all_a1$stability_floor_A1_e < z), numeric(1))

p3 <- ggplot(all_a1, aes(stability_floor_A1_e)) +
  stat_ecdf(geom="step", linewidth=1.25, colour=pal[["navy"]]) +
  geom_vline(data=thresholds, aes(xintercept=x, colour=lab), linetype=2, linewidth=.7, show.legend=FALSE) +
  scale_colour_manual(values=setNames(thresholds$col, thresholds$lab), guide="none") +
  geom_text(data=thresholds,
            aes(x=x, y=.08, label=sprintf("tau %s: %.0f%% eligible", lab, 100*eligible), colour=lab),
            angle=90, hjust=0, vjust=-.35, size=3.0, inherit.aes=FALSE, show.legend=FALSE) +
  scale_x_log10(labels=label_scientific(digits=1)) +
  scale_y_continuous(limits=c(0,1), breaks=seq(0,1,.2), labels=label_percent()) +
  labs(title="C | QSQ defines which chemical contracts are measurable",
       subtitle=sprintf("All %d development + external systems with a finite QSQ floor", nrow(all_a1)),
       x="QSQ stability floor (e)", y="Cumulative material fraction") + th

fig <- ((p1 | p2) / p3) +
  plot_layout(heights=c(1.02,.98)) +
  plot_annotation(
    title="Figure 4 | Stability is a property of the observable and its measurement procedure",
    subtitle="QSQ uses five fixed-seed uniform-noise probes at the material-specific float32 L-infinity amplitude.",
    caption="The archived float32 probe remains frozen for provenance. Panels A-B compare the paired development subset with both predecessor and QSQ outputs.\nPanel C uses all available QSQ systems and defines the eligibility ceiling used for headline certification.",
    theme=theme(plot.background=element_rect(fill=bg, colour=NA),
                plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
                plot.subtitle=element_text(size=9.8, colour="#4F545C", margin=margin(b=8)),
                plot.caption=element_text(size=8.1, colour=muted, hjust=0, margin=margin(t=7))))

png_path <- file.path(outdir,"figure4_stability_protocol_R.png")
pdf_path <- file.path(outdir,"figure4_stability_protocol_R.pdf")
svg_path <- file.path(outdir,"figure4_stability_protocol_R.svg")
ggsave(png_path, fig, width=11.8, height=8.1, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=11.8, height=8.1, bg=bg)
ggsave(svg_path, fig, width=11.8, height=8.1, bg=bg, device=svglite::svglite)
message("Rendered: ", svg_path)
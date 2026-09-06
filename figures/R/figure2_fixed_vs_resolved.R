# Figure 2 — fixed basin vs resolved basin
# R / ggplot2 version with diversified geometries.

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(scales)
  library(patchwork)
  library(ggridges)
})

root <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), "../.."), mustWork = FALSE)
if (!file.exists(file.path(root, "benchmark", "master_benchmark_full.csv"))) root <- getwd()
d <- read.csv(file.path(root, "benchmark", "master_benchmark_full.csv"), check.names = FALSE)

pal <- c(SPERR="#56B4E9", SZ3="#0072B2", ZFP="#D55E00")
bg <- "#FAFAF8"; ink <- "#1A1A1A"; grid <- "#D8D8D2"

theme_qoi <- theme_minimal(base_size = 10) +
  theme(plot.background=element_rect(fill=bg, colour=NA),
        panel.background=element_rect(fill=bg, colour=NA),
        panel.grid.minor=element_blank(),
        panel.grid.major=element_line(colour=grid, linewidth=.3),
        axis.title=element_text(colour=ink), axis.text=element_text(colour=ink),
        plot.title=element_text(face="bold", size=11),
        legend.position="top")

p1 <- ggplot(d, aes(Bader_error_fixed_e, Bader_error_resolved_e, colour=codec)) +
  geom_hex(bins=45, aes(fill=after_stat(count)), colour=NA, alpha=.8, inherit.aes = FALSE,
           data=d, mapping=aes(Bader_error_fixed_e, Bader_error_resolved_e)) +
  geom_point(alpha=.18, size=.65) +
  geom_abline(slope=1, intercept=0, linetype=2, colour="#777777") +
  scale_x_log10(labels=label_scientific()) + scale_y_log10(labels=label_scientific()) +
  scale_colour_manual(values=pal) + scale_fill_gradient(low="#FDDBC7", high="#003366") +
  labs(title="Fixed-domain error misses the dominant contribution",
       x="Fixed-basin Bader error (e)", y="Resolved-basin Bader error (e)", fill="density") +
  theme_qoi

u <- d %>% filter(is.finite(fixed_basin_understatement), fixed_basin_understatement>0)
p2 <- ggplot(u, aes(fixed_basin_understatement, codec, fill=codec)) +
  geom_density_ridges(scale=1.25, alpha=.75, colour="white", linewidth=.3, rel_min_height=.01) +
  geom_vline(xintercept=1, linetype=2, colour="#777777") +
  scale_x_log10(labels=label_number(suffix="×")) + scale_fill_manual(values=pal) +
  labs(title="Understatement spans orders of magnitude", x="Resolved / fixed error", y=NULL) +
  theme_qoi + theme(legend.position="none")

p3 <- ggplot(u, aes(frac_voxels_reassigned, fixed_basin_understatement, colour=codec)) +
  geom_point(alpha=.20, size=.75) +
  geom_smooth(se=FALSE, method="loess", linewidth=.9) +
  scale_y_log10(labels=label_number(suffix="×")) + scale_colour_manual(values=pal) +
  labs(title="Basin migration tracks hidden chemical error",
       x="Fraction of voxels reassigned", y="Resolved / fixed error") +
  theme_qoi

fig <- (p1 | p2 | p3) + plot_annotation(title="Figure 2 | Basin migration is the missing error channel")
out <- file.path(root, "figures", "R")
dir.create(out, recursive=TRUE, showWarnings=FALSE)
ggsave(file.path(out,"figure2_fixed_vs_resolved_R.pdf"), fig, width=11.5, height=4.2)
ggsave(file.path(out,"figure2_fixed_vs_resolved_R.png"), fig, width=11.5, height=4.2, dpi=400)

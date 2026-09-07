# Figure 6 — matched realized-Linf analysis
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(scales); library(patchwork)
})

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

sumf <- file.path(root, "analysis", "matched_realized_linf_v1", "matched_effects_summary.csv")
basef <- file.path(root, "analysis", "matched_realized_linf_v1", "equal_nominal_diagnostics.csv")
stopifnot(file.exists(sumf), file.exists(basef))

eff <- read.csv(sumf, check.names=FALSE, stringsAsFactors=FALSE)
base <- read.csv(basef, check.names=FALSE, stringsAsFactors=FALSE)
eff$caliper_dex <- as.numeric(eff$caliper_dex)

pair_lab <- c(
  zfp_vs_sz3 = "ZFP / SZ3",
  zfp_vs_sperr = "ZFP / SPERR",
  sz3_vs_sperr = "SZ3 / SPERR"
)
pair_cols <- c(
  zfp_vs_sz3 = "#D55E00",
  zfp_vs_sperr = "#56B4E9",
  sz3_vs_sperr = "#0072B2"
)

bg <- "#FAFAF8"; ink <- "#1A1A1A"; grid <- "#DDD9D2"
theme_qoi <- theme_minimal(base_size=10.5) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink), axis.text=element_text(colour=ink),
  plot.title=element_text(face="bold", size=11.2, margin=margin(b=5)),
  plot.subtitle=element_text(size=9.1, colour="#4F4F4F", margin=margin(b=6)),
  legend.position="top", legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

base$pair_label <- factor(pair_lab[base$pair], levels=rev(unname(pair_lab)))

pA <- ggplot(base, aes(y=pair_label, x=median_realized_Linf_ratio_A_over_B)) +
  geom_vline(xintercept=1, linetype=2, colour="#777777", linewidth=.55) +
  geom_segment(aes(x=1, xend=median_realized_Linf_ratio_A_over_B, yend=pair_label),
               linewidth=1.0, colour="#AAA49C") +
  geom_point(aes(colour=pair), size=3.3) +
  geom_text(aes(label=sprintf("%.2fx", median_realized_Linf_ratio_A_over_B)),
            hjust=-.18, size=3.05, colour=ink) +
  scale_colour_manual(values=pair_cols, guide="none") +
  scale_x_log10(limits=c(.13,1.35), breaks=c(.15,.2,.3,.5,1),
                labels=label_number(accuracy=.01, suffix="x")) +
  labs(
    title="A | Equal nominal tolerance is not equal distortion",
    subtitle="Median realized L-inf ratio at the same requested tolerance",
    x="Realized L-inf ratio (A / B)", y=NULL
  ) + theme_qoi

resolved <- eff %>%
  filter(metric == "Bader_error_resolved_e") %>%
  mutate(pair_label=pair_lab[pair])

pB <- ggplot(resolved, aes(caliper_dex, effect, colour=pair, group=pair)) +
  geom_hline(yintercept=1, linetype=2, colour="#777777", linewidth=.55) +
  geom_errorbar(aes(ymin=ci_low, ymax=ci_high), width=.012, linewidth=.55) +
  geom_line(linewidth=.95) + geom_point(size=2.5) +
  scale_colour_manual(values=pair_cols, labels=pair_lab) +
  scale_x_continuous(breaks=c(.05,.10,.20,.30), labels=c("0.05","0.10","0.20","0.30")) +
  scale_y_continuous(limits=c(.45,1.15), breaks=c(.5,.6,.7,.8,.9,1,1.1),
                     labels=label_number(accuracy=.1, suffix="x")) +
  labs(
    title="B | A chemical effect remains after matching realized L-inf",
    subtitle="Resolved Bader error; ratio < 1 means codec A is lower-error",
    x="Matching caliper (dex in log10 realized L-inf)", y="Material-level error ratio (A / B)"
  ) + theme_qoi

comp <- eff %>%
  filter(metric == "compression_ratio") %>%
  mutate(pair_label=pair_lab[pair])

pC <- ggplot(comp, aes(caliper_dex, effect, colour=pair, group=pair)) +
  geom_hline(yintercept=1, linetype=2, colour="#777777", linewidth=.55) +
  geom_errorbar(aes(ymin=ci_low, ymax=ci_high), width=.012, linewidth=.55) +
  geom_line(linewidth=.95) + geom_point(size=2.5) +
  scale_colour_manual(values=pair_cols, labels=pair_lab) +
  scale_x_continuous(breaks=c(.05,.10,.20,.30), labels=c("0.05","0.10","0.20","0.30")) +
  scale_y_log10(limits=c(.24,4.2), breaks=c(.25,.5,1,2,4),
                labels=label_number(accuracy=.01, suffix="x")) +
  labs(
    title="C | Chemical fidelity and rate remain distinct axes",
    subtitle="Compression ratio at matched realized L-inf",
    x="Matching caliper (dex in log10 realized L-inf)", y="Compression-ratio effect (A / B)"
  ) + theme_qoi

cert <- eff %>%
  filter(grepl("^certified_at_0.01 \\| both eligible_A1_at_0.01=TRUE$", metric)) %>%
  mutate(pair_label=pair_lab[pair], effect_pp=100*effect, lo_pp=100*ci_low, hi_pp=100*ci_high)

pD <- ggplot(cert, aes(caliper_dex, effect_pp, colour=pair, group=pair)) +
  geom_hline(yintercept=0, linetype=2, colour="#777777", linewidth=.55) +
  geom_errorbar(aes(ymin=lo_pp, ymax=hi_pp), width=.012, linewidth=.55) +
  geom_line(linewidth=.95) + geom_point(size=2.5) +
  scale_colour_manual(values=pair_cols, labels=pair_lab) +
  scale_x_continuous(breaks=c(.05,.10,.20,.30), labels=c("0.05","0.10","0.20","0.30")) +
  scale_y_continuous(labels=label_number(accuracy=1, suffix=" pp")) +
  labs(
    title="D | The residual geometry effect is decision-relevant",
    subtitle="Certification-rate difference at tau = 0.01 e; jointly A.1-eligible pairs",
    x="Matching caliper (dex in log10 realized L-inf)", y="Certification difference (A - B)"
  ) + theme_qoi

fig <- ((pA | pB) / (pC | pD)) +
  plot_layout(guides="collect") +
  plot_annotation(
    title="Figure 6 | Equal nominal tolerance conflates distortion magnitude with error geometry",
    subtitle="ZFP realizes only about one-sixth of the L-inf perturbation of SZ3/SPERR at equal nominal tolerance. After matching actual L-inf within material, the dramatic gap shrinks but does not vanish.",
    caption="Points are material-level effects; intervals are 95% material-bootstrap CIs. Matching is without replacement within material. Primary analysis uses a 0.10-dex caliper.",
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=10, colour="#4F4F4F", margin=margin(b=8)),
      plot.caption=element_text(size=8.5, colour="#5F5F5F", hjust=0, margin=margin(t=7))
    )
  )

ggsave(file.path(outdir,"figure6_matched_realized_linf_R.png"), fig,
       width=11.8, height=8.3, dpi=360, bg=bg)
ggsave(file.path(outdir,"figure6_matched_realized_linf_R.pdf"), fig,
       width=11.8, height=8.3, bg=bg)

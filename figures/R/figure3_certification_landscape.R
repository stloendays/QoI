# Figure 3 — certification landscape
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

d <- read.csv(
  file.path(root, "benchmark", "master_benchmark_full.csv"),
  check.names=FALSE,
  stringsAsFactors=FALSE
)

# Palette synchronized with Figure 2 and the manuscript visual system.
pal <- c(
  light_green = "#B8DBB3",
  green       = "#72B063",
  blue        = "#719AAC",
  orange      = "#E29135",
  teal        = "#94C6CD",
  navy        = "#4A5F7E"
)
codec_cols <- c(ZFP=pal[["blue"]], SZ3=pal[["orange"]], SPERR=pal[["teal"]])
bg <- "#FFFFFF"; ink <- "#202124"; grid <- "#E7E8EA"; muted <- "#646A73"

taus <- c("0.0001", "0.001", "0.01")
tau_labels <- c("10^-4", "10^-3", "10^-2")

as_flag <- function(x) {
  x %in% c(TRUE, 1, "1", "TRUE", "True", "true")
}

summarize_material <- function(g, cert_col, elig_col, ign_col) {
  g %>%
    group_by(material_id) %>%
    summarise(
      cert = any(as_flag(.data[[cert_col]]), na.rm=TRUE),
      elig = any(as_flag(.data[[elig_col]]), na.rm=TRUE),
      ign  = any(as_flag(.data[[ign_col]]), na.rm=TRUE),
      .groups="drop"
    )
}

S <- bind_rows(lapply(names(codec_cols), function(cc) {
  bind_rows(lapply(taus, function(t) {
    g <- d[d$codec == cc, , drop=FALSE]
    cert_col <- paste0("certified_at_", t)
    elig_col <- paste0("eligible_A1_at_", t)
    ign_col  <- paste0("certified_at_", t, "_ignoring_eligibility")
    needed <- c(cert_col, elig_col, ign_col)
    if (!all(needed %in% names(g))) {
      stop("Missing certification columns: ", paste(setdiff(needed, names(g)), collapse=", "))
    }
    z <- summarize_material(g, cert_col, elig_col, ign_col)
    data.frame(
      codec=cc,
      tau=t,
      n_materials=nrow(z),
      cert=100*mean(z$cert),
      elig=100*mean(z$elig),
      ign=100*mean(z$ign),
      overstatement=100*mean(z$ign)-100*mean(z$cert)
    )
  }))
}))

S$tau <- factor(S$tau, levels=taus, labels=tau_labels)
S$codec <- factor(S$codec, levels=c("ZFP", "SZ3", "SPERR"))

th <- theme_minimal(base_size=10.4) + theme(
  plot.background=element_rect(fill=bg, colour=NA),
  panel.background=element_rect(fill=bg, colour=NA),
  panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour=grid, linewidth=.28),
  axis.title=element_text(colour=ink),
  axis.text=element_text(colour=ink),
  strip.text=element_text(face="bold", colour=ink),
  plot.title=element_text(face="bold", size=11.2, margin=margin(b=5)),
  plot.subtitle=element_text(size=9.0, colour="#4F545C", margin=margin(b=6)),
  legend.position="top",
  legend.title=element_blank(),
  plot.margin=margin(8,10,8,8)
)

# A — protocol-valid certification landscape.
p1 <- ggplot(S, aes(tau, codec, fill=cert)) +
  geom_tile(colour=bg, linewidth=3) +
  geom_text(aes(label=sprintf("%.0f%%", cert)), fontface="bold", size=3.8, colour=ink) +
  scale_fill_gradientn(
    colours=c("#F4F6F5", pal[["light_green"]], pal[["green"]], pal[["navy"]]),
    limits=c(0,100),
    labels=label_percent(scale=1)
  ) +
  labs(
    title="A | Certification is jointly controlled by codec and chemical tolerance",
    subtitle="Fraction of development materials satisfying Protocol A.1 eligibility and resolved Bader error < tau",
    x="Chemical tolerance tau (e)", y=NULL, fill="Certified"
  ) + th +
  theme(panel.grid=element_blank())

# B — identifiability ceiling imposed by the uncompressed stability floor.
p2 <- ggplot(S, aes(tau, elig, group=codec, colour=codec)) +
  geom_line(linewidth=1.15) +
  geom_point(size=2.9) +
  scale_colour_manual(values=codec_cols) +
  scale_y_continuous(limits=c(0,100), breaks=seq(0,100,20), labels=label_percent(scale=1)) +
  labs(
    title="B | The uncompressed stability floor sets the certification ceiling",
    subtitle="Eligibility is defined before codec success is counted",
    x="Chemical tolerance tau (e)", y="Eligible materials"
  ) + th

# C — apparent success if eligibility is ignored versus protocol-valid success.
ord <- expand.grid(
  codec=factor(c("ZFP","SZ3","SPERR"), levels=c("ZFP","SZ3","SPERR")),
  tau=factor(tau_labels, levels=tau_labels)
)
ord$key <- interaction(ord$codec, ord$tau, sep="  |  ", lex.order=TRUE)
S$key <- factor(interaction(S$codec, S$tau, sep="  |  ", lex.order=TRUE), levels=ord$key)

p3 <- ggplot(S, aes(y=key)) +
  geom_segment(aes(x=cert, xend=ign, yend=key), colour="#C7C9CC", linewidth=1.6) +
  geom_point(aes(x=ign), shape=21, fill=bg, colour="#777C82", stroke=.8, size=3.2) +
  geom_point(aes(x=cert, colour=codec), size=3.2) +
  scale_colour_manual(values=codec_cols) +
  scale_x_continuous(limits=c(0,100), breaks=seq(0,100,20), labels=label_percent(scale=1)) +
  labs(
    title="C | Ignoring identifiability systematically overstates scientific success",
    subtitle="Filled point: Protocol A.1 certified; open point: Bader error criterion counted without eligibility",
    x="Material fraction", y="codec  |  tau"
  ) + th

fig <- (p1 | p2 | p3) +
  plot_layout(widths=c(1.02,1.05,1.22), guides="collect") +
  plot_annotation(
    title="Figure 3 | Chemical certification is a stability-aware decision problem",
    subtitle="Compression fidelity is only scientifically interpretable after the downstream observable is identifiable at the requested tolerance.",
    caption="Development corpus; Protocol A.1 uses fixed-seed uniform perturbations at the float32 L-infinity amplitude. Certification requires eligibility and resolved Bader error below the chemical tolerance.",
    theme=theme(
      plot.background=element_rect(fill=bg, colour=NA),
      plot.title=element_text(face="bold", size=14, colour=ink, margin=margin(b=4)),
      plot.subtitle=element_text(size=10, colour="#4F545C", margin=margin(b=8)),
      plot.caption=element_text(size=8.2, colour=muted, hjust=0, margin=margin(t=7))
    )
  )

png_path <- file.path(outdir, "figure3_certification_landscape_R.png")
pdf_path <- file.path(outdir, "figure3_certification_landscape_R.pdf")
svg_path <- file.path(outdir, "figure3_certification_landscape_R.svg")

ggsave(png_path, fig, width=12.4, height=4.9, dpi=360, bg=bg)
ggsave(pdf_path, fig, width=12.4, height=4.9, bg=bg)
ggsave(svg_path, fig, width=12.4, height=4.9, bg=bg, device=svglite::svglite)

message("Rendered: ", svg_path)

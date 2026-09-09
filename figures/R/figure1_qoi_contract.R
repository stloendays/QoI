# Figure 1 — conceptual QoI-aware scientific fidelity contract
suppressPackageStartupMessages({
  library(ggplot2)
  library(grid)
})

if (!requireNamespace("svglite", quietly=TRUE)) {
  stop("Package 'svglite' is required for the vector SVG export.")
}

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

pal <- c(
  light_green="#B8DBB3", green="#72B063", blue="#719AAC",
  orange="#E29135", teal="#94C6CD", navy="#4A5F7E"
)
bg <- "#FFFFFF"; ink <- "#202124"; muted <- "#646A73"; gridc <- "#D8DADD"

# Canvas only; all objects are deliberately positioned for reproducibility.
p <- ggplot() +
  coord_cartesian(xlim=c(0,12), ylim=c(0,7), expand=FALSE, clip="off") +
  theme_void() +
  theme(
    plot.background=element_rect(fill=bg, colour=NA),
    plot.margin=margin(16,20,12,20)
  )

# Title and subtitle.
p <- p +
  annotate("text", x=.15, y=6.88, hjust=0, vjust=1,
           label="Figure 1 | Scientific fidelity is defined by the downstream QoI operator",
           family="sans", fontface="bold", size=5.2, colour=ink) +
  annotate("text", x=.15, y=6.52, hjust=0, vjust=1,
           label="One controlled density perturbation can enter distinct error-propagation regimes after reconstruction.",
           family="sans", size=3.55, colour=muted)

# Shared field-level pipeline boxes.
p <- p +
  annotate("rect", xmin=.25, xmax=2.0, ymin=2.75, ymax=4.65,
           fill="#F7FAFB", colour=pal[["blue"]], linewidth=.8) +
  annotate("rect", xmin=2.35, xmax=3.75, ymin=3.05, ymax=4.35,
           fill="#FFF9F2", colour=pal[["orange"]], linewidth=.8) +
  annotate("rect", xmin=4.10, xmax=5.85, ymin=2.75, ymax=4.65,
           fill="#F7FAFB", colour=pal[["blue"]], linewidth=.8)

# Density glyphs: concentric contours and atom cores.
for (cx in c(1.12, 4.97)) {
  p <- p +
    annotate("point", x=cx, y=3.55, size=19, shape=21, fill=alpha(pal[["teal"]],.14), colour=NA) +
    annotate("point", x=cx, y=3.55, size=14, shape=21, fill=alpha(pal[["blue"]],.16), colour=NA) +
    annotate("point", x=cx, y=3.55, size=8.5, shape=21, fill=alpha(pal[["navy"]],.18), colour=NA) +
    annotate("point", x=cx-.24, y=3.45, size=4.0, shape=21, fill="white", colour=pal[["navy"]], stroke=.65) +
    annotate("point", x=cx+.27, y=3.68, size=3.5, shape=21, fill="white", colour=pal[["navy"]], stroke=.65)
}

p <- p +
  annotate("text", x=1.12, y=4.36, label="Original density ρ", fontface="bold", size=3.7, colour=ink) +
  annotate("text", x=1.12, y=2.98, label="reference field", size=3.0, colour=muted) +
  annotate("text", x=3.05, y=4.02, label="Error-bounded\ncodec", fontface="bold", size=3.7, colour=ink) +
  annotate("text", x=3.05, y=3.52, label="ZFP  ·  SZ3  ·  SPERR", size=3.05, colour=muted) +
  annotate("text", x=3.05, y=3.22, label="requested tolerance ε", size=3.0, colour=pal[["orange"]]) +
  annotate("text", x=4.97, y=4.36, label="Reconstructed density ρ̃", fontface="bold", size=3.7, colour=ink) +
  annotate("text", x=4.97, y=2.98, label="ρ̃ = ρ + Δρ", size=3.15, colour=muted)

# Pipeline arrows.
p <- p +
  annotate("segment", x=2.02, xend=2.32, y=3.70, yend=3.70,
           colour=ink, linewidth=.65, arrow=arrow(length=unit(.10,"inches"), type="closed")) +
  annotate("segment", x=3.77, xend=4.07, y=3.70, yend=3.70,
           colour=ink, linewidth=.65, arrow=arrow(length=unit(.10,"inches"), type="closed")) +
  annotate("text", x=3.92, y=4.00, label="field-level bound", size=2.75, colour=muted, hjust=.5)

# Branch spine.
p <- p +
  annotate("segment", x=5.87, xend=6.24, y=3.70, yend=3.70, colour=ink, linewidth=.65) +
  annotate("segment", x=6.24, xend=6.24, y=1.67, yend=5.47, colour=gridc, linewidth=.75)

# Three QoI lanes.
lane <- function(ymin,ymax,fill,border) {
  annotate("rect", xmin=6.55, xmax=11.72, ymin=ymin, ymax=ymax,
           fill=fill, colour=border, linewidth=.65)
}
p <- p +
  lane(4.80,6.06,"#F6FBF5",pal[["green"]]) +
  lane(3.25,4.48,"#F4FAFB",pal[["teal"]]) +
  lane(1.15,2.92,"#F7F8FB",pal[["navy"]])

# Arrows into each lane.
for (yy in c(5.43,3.86,2.02)) {
  p <- p + annotate("segment", x=6.24, xend=6.51, y=yy, yend=yy,
                    colour=ink, linewidth=.62,
                    arrow=arrow(length=unit(.09,"inches"), type="closed"))
}

# Lane A — electron count.
p <- p +
  annotate("text", x=6.78, y=5.82, hjust=0, label="GLOBAL LINEAR", fontface="bold", size=2.85, colour=pal[["green"]]) +
  annotate("text", x=6.78, y=5.43, hjust=0, label="Electron count", fontface="bold", size=3.6, colour=ink) +
  annotate("text", x=8.30, y=5.43, hjust=0, label="Nₑ = ∫ ρ dV", size=3.45, colour=ink) +
  annotate("text", x=9.72, y=5.43, hjust=0, label="→  global conservation", size=3.25, colour=pal[["green"]]) +
  annotate("text", x=6.78, y=5.05, hjust=0,
           label="Local perturbations can cancel under a global integral.", size=3.0, colour=muted)

# Lane B — Hartree potential.
p <- p +
  annotate("text", x=6.78, y=4.24, hjust=0, label="LINEAR NONLOCAL", fontface="bold", size=2.85, colour=pal[["teal"]]) +
  annotate("text", x=6.78, y=3.87, hjust=0, label="Hartree potential", fontface="bold", size=3.6, colour=ink) +
  annotate("text", x=8.47, y=3.87, hjust=0, label="V_H ∝ ∇⁻²ρ", size=3.45, colour=ink) +
  annotate("text", x=9.72, y=3.87, hjust=0, label="→  smooth propagation", size=3.25, colour=pal[["teal"]]) +
  annotate("text", x=6.78, y=3.49, hjust=0,
           label="The downstream response remains continuous and approximately first-order.", size=3.0, colour=muted)

# Lane C — Bader topology-sensitive operator.
p <- p +
  annotate("text", x=6.78, y=2.68, hjust=0, label="TOPOLOGY-DEPENDENT", fontface="bold", size=2.85, colour=pal[["navy"]]) +
  annotate("text", x=6.78, y=2.36, hjust=0, label="Bader charge", fontface="bold", size=3.6, colour=ink) +
  annotate("text", x=8.00, y=2.36, hjust=0, label="Q_A = ∫Ω_A[ρ] ρ dV", size=3.35, colour=ink) +
  annotate("text", x=10.08, y=2.36, hjust=0, label="re-partition after reconstruction", size=2.85, colour=pal[["orange"]])

# Mini reference/re-solved basin sketches in bottom lane.
p <- p +
  annotate("rect", xmin=6.83, xmax=8.18, ymin=1.40, ymax=2.05, fill="white", colour=gridc, linewidth=.5) +
  annotate("rect", xmin=8.43, xmax=9.78, ymin=1.40, ymax=2.05, fill="white", colour=gridc, linewidth=.5) +
  annotate("text", x=7.50, y=1.93, label="reference basins", size=2.45, colour=muted) +
  annotate("text", x=9.10, y=1.93, label="re-solved basins", size=2.45, colour=muted) +
  annotate("point", x=c(7.15,7.84,8.75,9.47), y=c(1.60,1.65,1.60,1.65),
           size=3.4, shape=21, fill="white", colour=pal[["navy"]], stroke=.6)

# Curved-ish boundaries built as polylines.
refb <- data.frame(x=seq(7.51,7.51,length.out=40), y=seq(1.43,1.86,length.out=40))
refb$x <- refb$x + .045*sin(seq(0,2*pi,length.out=40))
reb <- data.frame(x=seq(9.08,9.17,length.out=40), y=seq(1.43,1.86,length.out=40))
reb$x <- reb$x + .09*sin(seq(0,2*pi,length.out=40))
p <- p +
  geom_path(data=refb, aes(x,y), inherit.aes=FALSE, colour=pal[["green"]], linewidth=.75) +
  geom_path(data=reb, aes(x,y), inherit.aes=FALSE, colour=pal[["orange"]], linewidth=.85) +
  annotate("segment", x=8.22, xend=8.38, y=1.70, yend=1.70, colour=pal[["orange"]], linewidth=.6,
           arrow=arrow(length=unit(.07,"inches"), type="closed")) +
  annotate("text", x=10.05, y=1.79, hjust=0,
           label="ΔQ_total = ΔQ_integrand + ΔQ_domain", size=3.02, colour=ink) +
  annotate("text", x=10.05, y=1.48, hjust=0,
           label="basin migration can amplify a small Δρ", size=2.8, colour=pal[["orange"]])

# Explicit warning and conclusion.
p <- p +
  annotate("text", x=3.05, y=2.62, label="controls Δρ — not Q[ρ]", fontface="bold", size=3.0, colour=pal[["orange"]]) +
  annotate("rect", xmin=.55, xmax=11.45, ymin=.18, ymax=.86,
           fill="#F5F7FA", colour=pal[["navy"]], linewidth=.7) +
  annotate("text", x=6.0, y=.58,
           label="Scientific fidelity depends on the pair (reconstruction, downstream QoI operator)",
           fontface="bold", size=3.85, colour=pal[["navy"]]) +
  annotate("text", x=6.0, y=.32,
           label="Density fidelity ≠ scientific fidelity", size=3.15, colour=muted)

png_path <- file.path(outdir,"figure1_qoi_contract_R.png")
pdf_path <- file.path(outdir,"figure1_qoi_contract_R.pdf")
svg_path <- file.path(outdir,"figure1_qoi_contract_R.svg")

ggsave(png_path, p, width=11.8, height=6.9, dpi=360, bg=bg)
ggsave(pdf_path, p, width=11.8, height=6.9, bg=bg, device=cairo_pdf)
ggsave(svg_path, p, width=11.8, height=6.9, bg=bg, device=svglite::svglite)
message("Rendered: ", svg_path)

# Figure 1 — measurement contract for scientific compression
suppressPackageStartupMessages({
  library(ggplot2)
  library(grid)
})

if (!requireNamespace("svglite", quietly=TRUE)) stop("Package 'svglite' is required for SVG export.")

root <- getwd()
outdir <- file.path(root, "figures", "R", "rendered")
dir.create(outdir, recursive=TRUE, showWarnings=FALSE)

bg <- "#FFFFFF"
ink <- "#1F2328"
muted <- "#626A73"
navy <- "#3E5F7D"
blue <- "#5A8FA8"
green <- "#63A75C"
orange <- "#D88732"
red <- "#B85C5C"
line <- "#D8DDE3"
soft_blue <- "#F3F7FA"
soft_green <- "#F3F8F1"
soft_orange <- "#FCF7EF"
soft_red <- "#FBF2F2"
soft_gray <- "#F6F7F8"

p <- ggplot() +
  coord_cartesian(xlim=c(0,13.4), ylim=c(0,8.0), expand=FALSE, clip="off") +
  theme_void() +
  theme(plot.background=element_rect(fill=bg, colour=NA),
        plot.margin=margin(18,22,16,22))

p <- p +
  annotate("text", x=.15, y=7.82, hjust=0, vjust=1,
           label="Figure 1 | A measurement contract for scientific compression",
           family="sans", fontface="bold", size=5.3, colour=ink) +
  annotate("text", x=.15, y=7.43, hjust=0, vjust=1,
           label="Reference-QoI stability is qualified before codec fidelity is interpreted.",
           family="sans", size=3.6, colour=muted)

box <- function(xmin,xmax,ymin,ymax,fill,border,lwd=.7) {
  annotate("rect", xmin=xmin,xmax=xmax,ymin=ymin,ymax=ymax,
           fill=fill, colour=border, linewidth=lwd)
}
arrow_seg <- function(x,xend,y,yend,colour=ink,lwd=.65) {
  annotate("segment", x=x,xend=xend,y=y,yend=yend, colour=colour, linewidth=lwd,
           arrow=arrow(length=unit(.09,"inches"), type="closed"))
}

p <- p + box(.25,2.20,4.72,6.35,soft_blue,blue,.8) +
  annotate("text", x=1.225, y=6.05, label="Scientific target", fontface="bold", size=3.7, colour=ink) +
  annotate("text", x=1.225, y=5.64, label="Reference density ρ", size=3.35, colour=navy) +
  annotate("text", x=1.225, y=5.27, label="Downstream QoI Q[ρ]", size=3.25, colour=ink) +
  annotate("text", x=1.225, y=4.91, label="Requested tolerance τ", size=3.15, colour=orange)

p <- p + arrow_seg(2.23,2.55,5.53,5.53) +
  box(2.58,4.77,4.55,6.50,soft_green,green,.8) +
  annotate("text", x=3.675, y=6.18, label="QoI Stability Qualification", fontface="bold", size=3.65, colour=ink) +
  annotate("text", x=3.675, y=5.76, label="5 pre-specified perturbations", size=3.08, colour=muted) +
  annotate("text", x=3.675, y=5.38, label="Re-derive downstream QoI", size=3.08, colour=muted) +
  annotate("text", x=3.675, y=4.93, label="stability floor  fₘ = max response", size=3.15, colour=green)

p <- p + arrow_seg(4.80,5.13,5.53,5.53) +
  box(5.17,6.63,4.90,6.15,"#FFFFFF",navy,.9) +
  annotate("text", x=5.90, y=5.75, label="Is fₘ < τ ?", fontface="bold", size=3.75, colour=ink) +
  annotate("text", x=5.90, y=5.30, label="reference-QoI
eligible?", size=2.85, colour=muted)

p <- p +
  annotate("segment", x=5.90,xend=5.90,y=4.88,yend=3.94, colour=red, linewidth=.75,
           arrow=arrow(length=unit(.09,"inches"), type="closed")) +
  annotate("text", x=6.12, y=4.34, label="NO", hjust=0, fontface="bold", size=3.0, colour=red) +
  box(4.62,7.22,2.55,3.88,soft_red,red,.8) +
  annotate("text", x=5.92, y=3.58, label="NON-EVALUABLE", fontface="bold", size=3.8, colour=red) +
  annotate("text", x=5.92, y=3.20, label="for robust scientific certification", size=3.0, colour=ink) +
  annotate("text", x=5.92, y=2.83, label="Fixed-pipeline codec agreement may still be reported.", size=2.75, colour=muted)

p <- p +
  arrow_seg(6.66,7.05,5.53,5.53,green,.75) +
  annotate("text", x=6.83, y=5.78, label="YES", fontface="bold", size=3.0, colour=green) +
  box(7.10,9.18,4.55,6.50,soft_blue,blue,.8) +
  annotate("text", x=8.14, y=6.18, label="Compression evaluation", fontface="bold", size=3.6, colour=ink) +
  annotate("text", x=8.14, y=5.76, label="ZFP  ·  SZ3  ·  SPERR", size=3.15, colour=navy) +
  annotate("text", x=8.14, y=5.37, label="decode density ρ̃", size=3.05, colour=muted) +
  annotate("text", x=8.14, y=4.95, label="re-derive Q[ρ̃]", size=3.05, colour=muted)

p <- p + arrow_seg(9.21,9.52,5.53,5.53) +
  box(9.56,10.92,4.90,6.15,"#FFFFFF",navy,.9) +
  annotate("text", x=10.24, y=5.75, label="Is |ΔQ| < τ ?", fontface="bold", size=3.6, colour=ink) +
  annotate("text", x=10.24, y=5.30, label="reconstruction
agreement?", size=2.8, colour=muted)

p <- p +
  arrow_seg(10.95,11.28,5.75,5.75,green,.75) +
  annotate("text", x=11.08, y=6.00, label="YES", fontface="bold", size=2.9, colour=green) +
  box(11.33,13.12,5.02,6.47,soft_green,green,.8) +
  annotate("text", x=12.225, y=6.08, label="CERTIFIED", fontface="bold", size=3.8, colour=green) +
  annotate("text", x=12.225, y=5.68, label="eligible + within", size=2.8, colour=ink) +
  annotate("text", x=12.225, y=5.37, label="scientific tolerance", size=2.8, colour=ink)

p <- p +
  annotate("segment", x=10.24,xend=10.24,y=4.88,yend=3.92, colour=orange, linewidth=.75,
           arrow=arrow(length=unit(.09,"inches"), type="closed")) +
  annotate("text", x=10.47, y=4.34, label="NO", hjust=0, fontface="bold", size=2.9, colour=orange) +
  box(8.90,11.60,2.55,3.88,soft_orange,orange,.8) +
  annotate("text", x=10.25, y=3.56, label="ELIGIBLE, NOT CERTIFIED", fontface="bold", size=3.5, colour=orange) +
  annotate("text", x=10.25, y=3.15, label="reference is measurable,", size=2.85, colour=ink) +
  annotate("text", x=10.25, y=2.84, label="reconstruction misses τ", size=2.85, colour=ink)

p <- p +
  box(.55,12.85,.48,1.75,soft_gray,line,.7) +
  annotate("text", x=.82, y=1.47, hjust=0, label="Two independent benchmark axes", fontface="bold", size=3.45, colour=navy) +
  annotate("text", x=.82, y=1.06, hjust=0, label="1  Reference stability:", fontface="bold", size=3.05, colour=ink) +
  annotate("text", x=2.62, y=1.06, hjust=0, label="Can the QoI support the requested tolerance?", size=3.0, colour=muted) +
  annotate("text", x=6.70, y=1.06, hjust=0, label="2  Reconstruction fidelity:", fontface="bold", size=3.05, colour=ink) +
  annotate("text", x=9.02, y=1.06, hjust=0, label="Does the decoded field satisfy it?", size=3.0, colour=muted) +
  annotate("text", x=6.70, y=.70, hjust=0,
           label="Do not collapse these axes into one binary codec label.", fontface="bold", size=3.05, colour=navy)

p <- p +
  annotate("text", x=.55, y=.20, hjust=0,
           label="QSQ is a finite-panel empirical qualification under the declared perturbation model, not a worst-case stability guarantee.",
           size=2.7, colour=muted)

png_path <- file.path(outdir,"figure1_qoi_contract_R.png")
pdf_path <- file.path(outdir,"figure1_qoi_contract_R.pdf")
svg_path <- file.path(outdir,"figure1_qoi_contract_R.svg")

ggsave(png_path, p, width=12.0, height=7.2, dpi=360, bg=bg)
ggsave(pdf_path, p, width=12.0, height=7.2, bg=bg, device=cairo_pdf)
ggsave(svg_path, p, width=12.0, height=7.2, bg=bg, device=svglite::svglite)

stopifnot(file.exists(png_path), file.exists(pdf_path), file.exists(svg_path))
message("Rendered Figure 1 measurement contract: PNG + PDF + SVG")

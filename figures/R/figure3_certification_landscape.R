# Figure 3 — certification landscape
suppressPackageStartupMessages({library(ggplot2);library(dplyr);library(tidyr);library(scales);library(patchwork)})
root<-getwd(); d<-read.csv(file.path(root,"benchmark","master_benchmark_full.csv"),check.names=FALSE)
pal<-c(SPERR="#56B4E9",SZ3="#0072B2",ZFP="#D55E00"); bg<-"#FAFAF8"; ink<-"#1A1A1A"
taus<-c("0.0001","0.001","0.01")
S<-bind_rows(lapply(names(pal),function(cc) bind_rows(lapply(taus,function(t){
 g<-d[d$codec==cc,]; cert<-paste0("certified_at_",t); elig<-paste0("eligible_A1_at_",t); ign<-paste0("certified_at_",t,"_ignoring_eligibility")
 z<-g%>%group_by(material_id)%>%summarise(cert=max(.data[[cert]],na.rm=TRUE),elig=max(.data[[elig]],na.rm=TRUE),ign=max(.data[[ign]],na.rm=TRUE),.groups="drop")
 data.frame(codec=cc,tau=t,cert=100*mean(z$cert),elig=100*mean(z$elig),ign=100*mean(z$ign))
}))))
S$tau<-factor(S$tau,levels=taus,labels=c("10^-4","10^-3","10^-2")); S$codec<-factor(S$codec,levels=names(pal))
th<-theme_minimal(base_size=10.5)+theme(plot.background=element_rect(fill=bg,colour=NA),panel.background=element_rect(fill=bg,colour=NA),panel.grid.minor=element_blank(),plot.title=element_text(face="bold",size=11),legend.position="top")
# Tile map: certification as a decision landscape
p1<-ggplot(S,aes(tau,codec,fill=cert))+geom_tile(colour=bg,linewidth=3)+geom_text(aes(label=sprintf("%.0f%%",cert)),fontface="bold",size=3.5)+scale_fill_gradientn(colours=c("#FDDBC7","#E69F00","#0072B2","#003366"),limits=c(0,100))+labs(title="Certified fraction",x="Chemical tolerance τ (e)",y=NULL,fill="Certified")+th
# Eligibility trajectories
p2<-ggplot(S,aes(tau,elig,group=codec,colour=codec))+geom_line(linewidth=1.1)+geom_point(size=2.8)+scale_colour_manual(values=pal)+scale_y_continuous(limits=c(0,100),labels=label_percent(scale=1))+labs(title="The observable stability floor sets the ceiling",x="Chemical tolerance τ (e)",y="Eligible materials")+th
# Dumbbell: apparent success versus protocol-valid success
long<-S%>%select(codec,tau,cert,ign)%>%pivot_longer(c(cert,ign),names_to="rule",values_to="rate")
p3<-ggplot(S,aes(y=interaction(codec,tau,lex.order=TRUE)))+geom_segment(aes(x=cert,xend=ign,yend=interaction(codec,tau,lex.order=TRUE)),colour="#B3B3B3",linewidth=1.4)+geom_point(aes(x=ign),shape=21,fill=bg,colour="#777777",size=3)+geom_point(aes(x=cert,colour=codec),size=3)+scale_colour_manual(values=pal)+scale_x_continuous(limits=c(0,100),labels=label_percent(scale=1))+labs(title="Ignoring eligibility overstates success",x="Material fraction",y="codec × τ")+th
fig<-(p1|p2|p3)+plot_annotation(title="Figure 3 | Chemical certification is a stability-aware decision problem",theme=theme(plot.title=element_text(face="bold",size=14)))
out<-file.path(root,"figures","R","rendered");dir.create(out,recursive=TRUE,showWarnings=FALSE);ggsave(file.path(out,"figure3_certification_landscape_R.png"),fig,width=12.4,height=4.6,dpi=360,bg=bg);ggsave(file.path(out,"figure3_certification_landscape_R.pdf"),fig,width=12.4,height=4.6,bg=bg)

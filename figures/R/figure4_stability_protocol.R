# Figure 4 — Protocol A -> A.1 stability floor
suppressPackageStartupMessages({library(ggplot2);library(dplyr);library(tidyr);library(scales);library(patchwork)})
root<-getwd(); a1<-read.csv(file.path(root,"stability","stability_floor_A1.csv")); a0<-read.csv(file.path(root,"stability","stability_floor_A_archived_float32.csv"))
bg<-"#FAFAF8"; ink<-"#1A1A1A"; blue<-"#0072B2"; verm<-"#D55E00"; orange<-"#E69F00"; navy<-"#003366"
oldcol<-setdiff(grep("floor",names(a0),value=TRUE),"material_id")[1]; m<-merge(a1[,c("material_id","stability_floor_A1_e")],a0[,c("material_id",oldcol)],by="material_id");names(m)[3]<-"archived";m<-m%>%filter(archived>0,stability_floor_A1_e>0)
th<-theme_minimal(base_size=10.5)+theme(plot.background=element_rect(fill=bg,colour=NA),panel.background=element_rect(fill=bg,colour=NA),panel.grid.minor=element_blank(),plot.title=element_text(face="bold",size=11),legend.position="top")
# paired slopegraph in log-space, one line per material
L<-m%>%mutate(id=row_number())%>%select(id,archived,A1=stability_floor_A1_e)%>%pivot_longer(c(archived,A1),names_to="protocol",values_to="floor")
p1<-ggplot(L,aes(protocol,floor,group=id))+geom_line(alpha=.12,colour="#8A8A86")+geom_point(data=L%>%filter(protocol=="archived"),colour="#B3B3B3",alpha=.35,size=.8)+geom_point(data=L%>%filter(protocol=="A1"),colour=blue,alpha=.4,size=.8)+scale_y_log10(labels=label_scientific())+labs(title="Changing the probe changes the inferred floor",x=NULL,y="Stability floor (e)")+th
# ECDF against chemically meaningful thresholds
p2<-ggplot(a1,aes(stability_floor_A1_e))+stat_ecdf(geom="step",linewidth=1.25,colour=navy)+geom_vline(xintercept=c(1e-4,1e-3,1e-2),linetype=2,colour=c(verm,orange,blue))+scale_x_log10(labels=label_scientific())+scale_y_continuous(labels=label_percent())+labs(title="Eligibility emerges from the floor distribution",x="Protocol A.1 stability floor (e)",y="Cumulative material fraction")+th
# distribution of correction factor
m<-m%>%mutate(ratio=stability_floor_A1_e/archived)
p3<-ggplot(m,aes(ratio))+geom_histogram(aes(y=after_stat(density)),bins=45,fill="#FDDBC7",colour=bg)+geom_density(colour=verm,linewidth=1.1,adjust=1.1)+geom_vline(xintercept=1,linetype=2,colour="#777777")+scale_x_log10(labels=label_number(suffix="×"))+labs(title="Protocol correction is strongly non-uniform",x="A.1 / archived stability floor",y="Density")+th
fig<-(p1|p2|p3)+plot_annotation(title="Figure 4 | Stability is a property of the observable and its measurement protocol",theme=theme(plot.title=element_text(face="bold",size=14)))
out<-file.path(root,"figures","R","rendered");dir.create(out,recursive=TRUE,showWarnings=FALSE);ggsave(file.path(out,"figure4_stability_protocol_R.png"),fig,width=12.4,height=4.6,dpi=360,bg=bg);ggsave(file.path(out,"figure4_stability_protocol_R.pdf"),fig,width=12.4,height=4.6,bg=bg)

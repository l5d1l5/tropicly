jc_americas = read.csv('/home/tobi/Documents/tropicly/data/proc/agg/textual/harmonization_sort_americas.csv')
americas = jc_americas[jc_americas[,1]!=0,]
americas = americas[,1:4]
#cor(americas[,1:4])
summary(americas[,1:4])

jc_africa = read.csv('/home/tobi/Documents/tropicly/data/proc/agg/textual/harmonization_sort_africa.csv')
africa = jc_africa[jc_africa[,1]!=0,]
africa = africa[,1:4]
#cor(africa[,1:4])
summary(africa[,1:4])

jc_asia = read.csv('/home/tobi/Documents/tropicly/data/proc/agg/textual/harmonization_sort_asia.csv')
asia = jc_asia[jc_asia[,1]!=0,]
asia = asia[,1:4]
#cor(asia[,1:4])
summary(asia[,1:4])

all_regions = rbind(americas, asia)
all_regions = rbind(all_regions, africa)

equal = data.frame(JC00=double(),
                   JC10=double(),
                   JC20=double(),
                   JC30=double())
greater = data.frame(JC00=double(),
                     JC10=double(),
                     JC20=double(),
                     JC30=double())
less = data.frame(JC00=double(),
                  JC10=double(),
                  JC20=double(),
                  JC30=double())
for(i in 1:4) {
  for(j in 1:4) {
    equal[j, i] = wilcox.test(asia[,i], asia[,j], paired = TRUE, alternative = 'two.sided')$p.value
    greater[j, i] = wilcox.test(asia[,i], asia[,j], paired = TRUE, alternative = 'greater')$p.value
    less[j, i] = wilcox.test(asia[,i], asia[,j], paired = TRUE, alternative = 'less')$p.value
  }
}

png('/home/tobi/Documents/tropicly/data/proc/fig/jaccard_tiles_africa.png', width=11.7, height=8.3, units='in', res=300)
x_range = 1:length(africa$JC00)
plot(x_range, africa$JC00, pch=1, ylim=0:1, xlab='AISM tile', ylab='Jaccard Index')
par(new=TRUE)
plot(x_range, africa$JC10, axes=FALSE, pch=0, xlab='', ylab='')
par(new=TRUE)
plot(x_range, africa$JC20, axes=FALSE, pch=2, xlab='', ylab='')
par(new=TRUE)
plot(x_range, africa$JC30, axes=FALSE, pch=3, xlab='', ylab='')
par(new=FALSE)
dev.off()

# americas, asia, africa, global
vec_for_pairwise = c(all_regions$JC00, all_regions$JC10, all_regions$JC20, all_regions$JC30)
labels = rep(c('JI0', 'JI1', 'JI2', 'JI3'), each=length(all_regions$JC00))
pairwise.wilcox.test(vec_for_pairwise, labels, p.adjust.method="holm", paired = TRUE, alternative='greater')

# regional comparison
vec_for_pairwise = c(americas$JC00, americas$JC10, americas$JC20, americas$JC30,
                     asia$JC00, asia$JC10, asia$JC20, asia$JC30, 
                     africa$JC00, africa$JC10, africa$JC20, africa$JC30)

labels_americas = rep(c('Americas_JI0', 'Americas_JI1', 'Americas_JI2', 'Americas_JI3'), each=length(americas$JC00))
labels_asia = rep(c('Asia_JI0', 'Asia_JI1', 'Asia_JI2', 'Asia_JI3'), each=length(asia$JC00))
labels_africa = rep(c('Africa_JI0', 'Africa_JI1', 'Africa_JI2', 'Africa_JI3'), each=length(africa$JC00))

labels = append(labels_americas, labels_asia)
labels = append(labels, labels_africa)

pairwise.wilcox.test(vec_for_pairwise, labels, p.adjust.method="BH", alternative='greater')

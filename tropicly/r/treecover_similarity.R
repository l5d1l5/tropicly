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


test = c(americas$JC00, americas$JC10, americas$JC20, americas$JC30)
labels = rep(c('JI0', 'JI1', 'JI2', 'JI3'), each=length(americas$JC00))

pairwise.wilcox.test(test, labels, p.adjust.method="holm", paired = TRUE, alternative='less')
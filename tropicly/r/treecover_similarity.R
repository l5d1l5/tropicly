jc_americas = read.csv('/home/tobi/Desktop/proj/data/proc/ana/harmonization_americas.csv')
americas = jc_americas[jc_americas[,1]!=0,]
americas = americas[,1:4]
#cor(americas[,1:4])
summary(americas[,1:4])

jc_africa = read.csv('/home/tobi/Desktop/proj/data/proc/ana/harmonization_africa.csv')
africa = jc_africa[jc_africa[,1]!=0,]
africa = africa[,1:4]
#cor(africa[,1:4])
summary(africa[,1:4])

jc_asia = read.csv('/home/tobi/Desktop/proj/data/proc/ana/harmonization_asia.csv')
asia = jc_asia[jc_asia[,1]!=0,]
asia = asia[,1:4]
#cor(asia[,1:4])
summary(asia[,1:4])

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
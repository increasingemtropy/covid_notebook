library(ggplot2)
# get up to date coronavirus data
coronavirus_data <- read.csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv", na.strings = "", fileEncoding = "UTF-8-BOM")
data_subset <- subset(coronavirus_data,countriesAndTerritories %in% c("United_Kingdom","Germany","France","Spain","Japan","South_Korea"))

# plot the cases vs date for UK vs USA

plt <- ggplot(data_subset,aes(x=as.Date(dateRep,format = "%d/%m/%y"),y=Cumulative_number_for_14_days_of_COVID.19_cases_per_100000,color=countriesAndTerritories)) +
  geom_line(size=1) +
  coord_cartesian(xlim=c(as.Date('2020-03-15'),Sys.Date())) +
  labs(title ="14 day total cases per 10k population", x = "Date", y = "14 day case sum per 10k pop")+
  theme(legend.position = "top")+
  scale_color_brewer(name="",breaks=c("United_Kingdom","Germany","France","Spain","Japan","South_Korea"),labels=c("UK","Germany","France","Spain","Japan","South Korea"),palette = "Dark2")
plt

filename = paste("coronavirus_plot_",Sys.Date(),".png",sep='')

ggsave(filename, width = 8, height = 5)

devtools::install_github("Jean-Romain/lidRviewer")
library(sf)
library(lidR)
library(lidRviewer)
library(dplyr)
library(mmand)
library(mapview)
library(qgisprocess)
library(terra)
source("https://raw.githubusercontent.com/Jean-Romain/lidRviewer/master/sdl.R")


library(lidR)

help(decimate_points)

View(decimate_points)

rm(list = ls())

path0= "C:\\Users\\Lenovo\\Documents\\LAZ"
path_in=paste0(path0,"\\input")
path_out=paste0(path0,"\\output")

las = readLAS(paste0(path_in,"\\demo.laz"),select = "xyzirc")
las_orig<- las
plot(las, backend = "lidRviewer")
summary(las)


las<- las_orig
T1<-Sys.time()
thinned1 <- decimate_points(las, random(1))
T2<-Sys.time()
summary(las)
summary(thinned1)
plot(thinned1)


Tdiff= difftime(T2, T1)
(Tdiff)

T1<-Sys.time()
thinned2 <- decimate_points(las, homogenize(1,5))
T2<-Sys.time()
summary(thinned2)
plot(thinned2)

Tdiff= difftime(T2, T1)
(Tdiff)


T1<-Sys.time()
thinned3 = decimate_points(las, highest(5))
T2<-Sys.time()
summary(thinned3)
plot(thinned3)


las<- thinned3
las_orig<- las


Tdiff= difftime(T2, T1)
(Tdiff)

plot(las, color = "Classification")
summary(las)
las<- las_orig 


las<- classify_ground(las,algorithm = pmf(ws = 5, th = 3), last_returns = FALSE)
las_ground <- las
plot(las_ground, color = "Classification")
summary(las_ground)

las_ground_normalized<- normalize_height(las_ground,knnidw(k=20,p=2))
plot(las_ground_normalized)
summary(las_ground_normalized)
las_ground_bak<- las_ground

las_ground_normalized<- filter_poi(las_ground_normalized,(Z >= 0))
las_ground_normalized<- filter_poi(las_ground_normalized,(Z < 2))

lasunngrd<- grid_metrics(las_ground_normalized, func=min(Zref), 2)
summary(lasunngrd)
writeRaster(lasunngrd, filename = file.path(path_out,"treeainZ4.tif"), format="GTiff", overwrite=TRUE)
plot(las_ground_normalized,color="Z")
plot(las_ground_normalized,color="Zref")


las<- las_orig
plot(las)

dtm1<-grid_terrain(las, res = 0.25, algorithm = knnidw(k=5,p = 0.5), keep_lowest = TRUE)
plot(dtm1)
writeRaster(dtm1 ,filename = file.path(path_out,"dtm5_05.tif"), format="GTiff",overwrite=TRUE)

chm <- grid_canopy(las, res = 1, pitfree(c(0,2,5,10,15), c(0, 1.5)))
plot(chm)
writeRaster(chm,filename = file.path(path_out,"chm_1m.tif"), format="GTiff",overwrite=TRUE)

ttops = locate_trees(las_ground_normalized, lmf(ws=2, hmin=1, shape = "circular"))

writeOGR(obj=ttops,dsn=path_out, layer="ttops2", driver="ESRI Shapefile", overwrite=TRUE)

library(dplyr)
las<- segment_trees(las,li2012(R=3,speed_up = 5))
col <- pastel.colors(200)
plot(las, color = "treeID", colorPalette = col,backend = "lidRviewer")
metric<- tree_metrics(las,.stdtreemetrics)
length(unique(las$treeID) |> na.omit())
summary(metric)
nrows()
count(metric, "treeID")



#### Construction de cartes ####
# Référence : https://lrouviere.github.io/TUTO_VISU/correction/faire-des-cartes-avec-r.html
# Document : "Tutoriel_VisualisationDesDonnees.pdf" à télécharger sur Moodle

library(dplyr)
library(tidyverse)

#### page 73 ####

# De nombreuses données comportent des informations de géolocalisation. 
# Il est alors naturel d'utiliser des cartes pour les visualiser.

# Le package ggmap
library(ggmap)
# ggmap nécessite désormais une API key, 
# et qui reste gratuit pour un usage non commercial,
# voir  https://client.stadiamaps.com/signup/ pour obtenir un API key

register_stadiamaps("e4b0c396-492c-4dad-9e84-411015c4d226")

# Pour tracer la carte des Etats Unis :
## On renseigne les coordonnées géographiques : les longitudes et les latitudes
us<-c(left=-125, bottom=25.75, right=-67, top=49) 
map<-get_stadiamap(us, zoom=5, maptype="stamen_toner_background") # la carte US
ggmap(map) # trace la carte US

##### page 74  ####
# Pour tracer la carte de l'Europe :
europe<-c(left=-12, bottom=35, right=30, top=63)
get_stadiamap(europe, zoom=5, maptype="stamen_terrain")%>%ggmap()

##### page 75 ####
# On peut également changer le fond de carte :
get_stadiamap(europe, zoom=5, maptype="stamen_toner_background")%>%ggmap()

# Pour tracer la carte de France :
fr<-c(left=-6, bottom=41, right=10, top=52)
get_stadiamap(fr, zoom=5, maptype="stamen_toner_lite")%>%ggmap()

# Pour tracer la carte de l'Afrique :
Africa<-c(left=-18.5, bottom=-35, right=52, top=38)
get_stadiamap(Africa, zoom=4, messaging=TRUE)%>%ggmap()

##### page 76  ####
# La fonction "geocode()" de "ggmap" qui permettait de récupérer des longitudes 
# et latitudes nécessite désormais une API key, ce qui contraint son utilisation. 

# Nous proposons d'utiliser la fonction suivante :
if(!(require(jsonlite)))install.packages("jsonlite")
mygeocode<-function(adresses){
  # adresses est un vecteur contenant toutes les adresses sous forme de chaîne de caractères
  nominatim_osm<-function(address=NULL){
    ## details: http://wiki.openstreetmap.org/wiki/Nominatim
    ## fonction nominatim_osm proposée par D.Kisler
    if(suppressWarnings(is.null(address)))  return(data.frame())
    tryCatch(
      d<-jsonlite::fromJSON(
        gsub('\\@addr\\@', gsub('\\s+', '\\%20', address),
             'http://nominatim.openstreetmap.org/search?q=@addr@&format=json&addressdetails=0&limit=1')
      ), error=function(c) return(data.frame())
    )
    if(length(d)==0) return(data.frame())
    return(c(as.numeric(d$lon), as.numeric(d$lat)))
  }
  tableau<-t(sapply(adresses,nominatim_osm))
  colnames(tableau)<-c("lon", "lat")
  return(tableau)
}

# Cette fonction permet de récupérer les latitudes et longitudes de lieux à spécifier
# (Noms pour lieux connus, et adresses) :

##### page 77 ####
mygeocode("the white house")
# on obtient le résultat suivant :
#                    lon     lat
# the white housse -77.03655 38.8977

mygeocode("Paris")
# on obtient le résultat suivant :
#          lon     lat
# Paris 2.351462 48.8567

mygeocode("Rennes")
# on obtient le résultat suivant :
#           lon     lat
# Rennes -1.68002 48.11134

mygeocode("51100 Reims, France")
# on obtient le résultat suivant :
#                         lon     lat
# 51100 Reims, France  4.026549 49.26027

mygeocode("Moulin de la Housse, 51100 Reims, France")

#### Exercice 2.1 (Populations des grandes villes de France) ####
# 1. Récupérer les latitudes et longitudes de Paris, Lyon et Marseille et 
# représenter ces 3 villes sur une carte de la France.
V <- c("Paris","Lyon","Marseille")
A <- mygeocode(V)
A

A%>%as_tibble()%>%mutate(Villes=V)->A
A
fr<-c(left=-6, bottom=41, right=10, top=52)
fond<-get_stadiamap(fr, zoom=5, maptype="stamen_terrain_background") 
ggmap(fond)+geom_point(data=A, aes(x=lon, y=lat), color="red")

# 2. Le fichier villes_fr.csv contient les populations des 30 plus grandes villes 
# de France. Représenter à l'aide d'un point les 30 plus grandes villes de France. 
# On fera varier la taille du point en fonction de la population (en 2014) :
##### page 78 ####
# importer le fichier de données  "villes_fr.csv"
df<-read_csv(file.choose())

# Attention, la ville de Lille n'est pas bien écrite! Il faut la renommer :
df$Commune[10]
df$Commune[10] <- "Lille"

# On calcule les coordonnées avec mygeocode() et on représente les villes. 
# Pour la taille des points, il suffit d'ajouter l'argument size=`2014` 
# dans l'aes() du geom_point() :
coord<-mygeocode(as.character(df$Commune))%>%as_tibble()
df1<-bind_cols(df,coord)

# si ça ne marche pas,
# importer le fichier "villes_fr_coord.csv" (avec les cordonnées des villes):
df1<-read_csv(file.choose())  

View(df1)
  
ggmap(fond)+geom_point(data=df1, aes(x=lon, y=lat), color="red")

# On fait varier la taille des points en fonction de la population en 2014, 
# variable `2014` de la base :
ggmap(fond)+geom_point(data=df1, aes(x=lon, y=lat, size=`2014`), color="red")

# On fait varier la taille des points en fonction de la population en 2014, 
# variable `2014` de la base,
# et on ajoute aussi les noms des villes:
fr<-c(left=-6, bottom=41, right=10, top=52)
fond<-get_stadiamap(fr, zoom=5, maptype="stamen_terrain_background") 
ggmap(fond)+geom_point(data=df1, aes(x=lon, y=lat, size=`2014`), color="red")+
          annotate("text", x=df1$lon, y=df1$lat+0.15, 
                                      label=df1$Commune, size=2.1)

#### Les cartes avec contours, le format shapefile
### page 79 ###
# ggmap permet de récupérer facilement des fonds de cartes et de placer des points dessus 
# avec la syntaxe ggplot. Cependant, de nombreuses fonctions de ce package nécessitent 
# une API et il est difficile de définir des contours (frontières de pays, départements 
# ou régions) avec ggmap. Nous proposons ici de présenter brièvement le package sf 
# qui va nous permettre de créer des cartes “avancées”, en gérant les contours 
# à l'aide d'objets particuliers mais aussi en prenant en compte différents systèmes 
# de coordonnées. En effet, la terre n'est pas plate… mais une carte est souvent 
# visualisée en 2D, il faut par conséquent réaliser des projections
# pour représenter des lieux définis par une coordonnée (comme la latitude et la longitude) 
# sur une carte 2D.
# Ces projections sont généralement gérées par les packages qui permettent 
# de faire de la cartographie comme sf. 
# On pourra trouver de la documentation sur ce package aux url suivantes :
#   — https://statnmap.com/fr/2018-07-14-initiation-a-la-cartographie-avec-sf-et-compagnie/
#   — dans les vignettes sur la page du cran de ce package : 
#     https://cran.r-project.org/web/packages/sf/index.html

# Ce package propose de définir un nouveau format sf adapté à la cartographie. 
# Regardons par exemple l'objet nc
library(sf)
nc<-st_read(system.file("shape/nc.shp", package="sf"), quiet=TRUE)
class(nc)
nc

# Ces données contiennent des informations sur les morts subites de nourissons dans 
# des villes de Caroline du Nord. On remarque que l'objet nc est au format sf et data.frame. 
# On peut donc l'utiliser comme un data.frame classique. Le format sf permet l'ajout 
# d'une colonne particulière (geometry) qui délimitera les villes à l'aide de polygones. 
# Une fois l'objet obtenu au format sf, il est facile de visualiser 
# la carte avec un plot classique :
plot(st_geometry(nc))

# ou en utilisant le verbe geom_sf() si on veut faire du ggplot :
ggplot(nc)+geom_sf()

# Il devient dès lors facile de colorier des villes et d'ajouter leurs noms :
ggplot(nc[1:3,])+
  geom_sf(aes(fill=AREA))+ 
   geom_sf_label(aes(label=NAME))

# La colonne geometry de nc est au format MULTIPOLYGON, elle permettra donc de délimiter 
# les frontières des villes. Si maintenant on souhaite représenter une ville à l'aide 
# d'un point défini par sa latitude et longitude, il va falloir modifier le format 
# de cette colonne geometry. On peut le faire de la manière suivante :

# 1. On récupère les latitudes et longitudes de chaque ville :   
coord.ville.nc<-mygeocode(paste(as.character(nc$NAME),"NC"))
coord.ville.nc<-as.data.frame(coord.ville.nc)
names(coord.ville.nc)<-c("lon","lat")

# Si ça ne marche pas, importer le fichier de données "coord_ville_nc.csv":
coord.ville.nc <- read_csv(file.choose())

View(coord.ville.nc)

# 2. On met ces coordonnées au format MULTIPOINT 
coord.ville1.nc<-coord.ville.nc%>%as.tibble()%>%
       filter(lon<=-77 & lon>=-85 & lat>=33 & lat<=37)%>% 
        as.matrix()%>%st_multipoint()%>%st_geometry()%>%st_cast(to="POINT")

# 3. On indique que ces coordonnées sont des latitudes et longitude et on ajoute 
# la colonne aux données initiales
st_crs(coord.ville1.nc) <- 4326 

# 4. On peut enfin représenter la carte avec les frontières et les points :
ggplot(nc)+geom_sf()+geom_sf(data=coord.ville1.nc)

# Le package sf possède également des fonctions très utiles pour traiter des données 
# cartographiques, on peut citer par exemple :
#   — st_distance qui permet de calculer des distances entre coordonnées ;
#   — st_centroid pour calculer le centre d'une région.
# On peut ainsi représenter les centres des villes délimitées par les polygones 
# des données nc avec
nc2<-nc%>%mutate(centre=st_centroid(nc)$geometry)
ggplot(nc2)+geom_sf()+geom_sf(aes(geometry=centre))

##### page 83 ####
# Exercice 2.2 (Première carte avec le package sf)
# Nous nous servons de la carte GEOFLAR proposée par l'Institut Géographique National 
# pour récupérer un fond de carte contenant les frontières des départements français. 
# Cette carte est disponible sur le site http://professionnels.ign.fr/ au format shapefile, 
# elle se trouve dans l'archive dpt.zip. Il faut décompresser pour reproduire la carte. 
# Grâce au package sf, cette carte, contenue dans la série de fichiers departement du
# répertoire dpt, peut être importée dans un objet R :

# Importer les fichiers contenus dans le répertoire "dpt"
lien<-"/Users/amorkeziou/Documents/DisqueExterne/Enseignement/2025_2026/INFO0803_VisualisationDesdonnees/Data/dpt"
dpt<-read_sf(lien)
ggplot(dpt)+geom_sf()

# Refaire la carte de l'exercice 2.1 sur ce fond de carte.
# On définit tout d'abord un geometry au format MULTIPOINT. 
# On le transforme ensuite en un “vecteur” de longueur 30 au format POINT 
# que l'on ajoute dans le dataframe qui contient les coordonnées des villes :
coord.ville1<-data.frame(df1[, c("lon", "lat")]) %>%
                  as.matrix() %>% st_multipoint() %>% st_geometry()
coord.ville2<-st_cast(coord.ville1, to="POINT")
coord.ville1
coord.ville2

# On peut maintenant visualiser la carte demandée :
st_geometry(df1)<-coord.ville2
st_crs(df1)<-4326
ggplot(dpt)+geom_sf(fill="white")+
  geom_sf(data=df1, aes(size=`2014`), color="red")+theme_void()

##### page 85 ####
# Exercice 2.3 (Visualisation de taux de chômage avec le package sf)
# Nous souhaitons visualiser graphiquement les différences de taux de chômage 
# par département entre deux années. Pour cela, nous disposons de chaque taux mesuré 
# aux premiers trimestres des années 2006 et 2011 (variables TCHOMB1T06, TCHOMB1T11) 
# qui se trouvent dans le jeu de données tauxchomage.csv.
# On procède comme suit :

# 1. importer le fichier de données "tauxchomage.csv"
chomage<-read_delim(file.choose(), delim=";")

# 2. Faire la jointure de cette table avec celle des départements. 
# On pourra utiliser ``inner_join()''
dpt<-read_sf(lien)
dpt2<-inner_join(dpt, chomage, by="CODE_DEPT")

# 3. Comparer les taux de chômage en 2006 et 2011 : 
# On fera une carte avec les taux en 2006 et une autre
# avec les taux en 2011.
dpt3<-dpt2 %>% select(A2006=TCHOMB1T06, A2011=TCHOMB1T11, geometry) %>%
      pivot_longer(-geometry, names_to="Annee", values_to="TxChomage") %>% st_as_sf()

ggplot(dpt3) + aes(fill=TxChomage)+geom_sf() +
  facet_wrap(~Annee, nrow=1)+
  scale_fill_gradient(low="white", high="brown")+theme_bw()

##### page 86 ####
# Challenge (carte des températures avec le package sf) : 
# On souhaite ici faire une carte permettant de visualiser 
# les température en France à un moment donné. 
# Les données se trouvent sur le site des données publiques de météo france.
# On peut notamment récupérer
# — les températures observées dans certaines stations en France les 15 derniers jours 
#   dans le lien téléchargement. On utilisera uniquement les identifiants de la station 
#   ainsi que la température observée (colonne t).
# — la géolocalisation de ces stations dans le lien documentation

# 1. Importer les 2 bases nécessaires. On pourra les lire directement sur le site. 
# Convertir les degrés Kelvin en degrés Celsius et faire la jointure de ces deux bases:

# importer le fichier de données "synop.2021031912.csv"
donnees <- read_delim(file.choose(), 
                       delim=";", col_types=cols(t=col_double()))
# importer le fichier de données "postesSynop.csv"
station <- read_delim(file.choose(), delim=";")

donnees$t <- donnees$t-273.15 #on passe en degrés celcius
temp <- donnees %>% select(numer_sta,t)
names(temp)[1] <- c("ID")

# faire la jointure
D <- inner_join(temp, station, by=c("ID"))

# 2. Eliminer les stations d’outre mer (on pourra conserver uniquement les stations 
# qui ont une longitude entre -20 et 25). On appellera ce tableau station1. 
# Visualiser les stations sur la carte contenant les frontières des départements français
station1<- D %>% filter(Longitude<25 & Longitude>-20) %>% na.omit()
station4326<-st_multipoint(as.matrix(station1[,5:4])) %>% st_geometry()
st_crs(station4326) <- 4326
ggplot(dpt)+geom_sf()+geom_sf(data=station4326)

# 3. Créer un dataframe au format sf qui contient les températures des stations ainsi 
# que leurs coordonnées dans la colonne geometry. On pourra commencer avec
station2<-station1 %>% select(Longitude,Latitude) %>%
             as.matrix() %>% st_multipoint() %>% st_geometry()
st_crs(station2)<-4326
station2<-st_cast(station2, to="POINT")

df<-data.frame(temp=station1$t)
st_geometry(df)<-station2

# 4. Représenter les stations sur une carte de France. 
# On pourra mettre un point de couleur différente en
# fonction de la température
ggplot(dpt)+geom_sf(fill="white")+
  geom_sf(data=df,aes(color=temp),size=2)+
  scale_color_continuous(low="yellow",high="red")

# 5. On obtient les coordonnées des centroïdes des départements 
# à l'aide de
centro<-st_centroid(dpt$geometry)
centro<-st_transform(centro,crs=4326)

# On déduit les distances entre ces centroïdes et les stations 
# avec (df étant la table sf obtenue à la question 3) :
library(lwgeom)
DD<-st_distance(df,centro)

# Prédire la température de chaque département à l'aide de la règle du 1 plus proche voisin, 
# la température du département i sera celle de la station 
# la plus proche du centroïde de i) : 
NN<-apply(DD,2,order)[1,]
t_prev<-station1[NN,2]

# 6. Colorier les départements en fonction de la température 
# prédite dans le département. On pourra faire
# varier le dégradé de couleur du jaune (pour les faibles 
# températures) au rouge (pour les fortes)
dpt1 <- dpt %>% mutate(t_prev=as.matrix(t_prev))
ggplot(dpt1)+geom_sf(aes(fill=t_prev)) +
  scale_fill_continuous(low="yellow",high="red")+theme_void()

# On peut supprimer les lignes de frontières avec
ggplot(dpt1)+geom_sf(aes(fill=t_prev,color=t_prev))+
  scale_fill_continuous(low="yellow",high="red")+
  scale_color_continuous(low="yellow",high="red")+theme_void()

##### page 89 ####
#### Trouver des cartes au format shapefile ####
# Le plus souvent on ne va pas construire les fonds de carte au format shapefile “à la main” 
# et il est bien entendu important de récupérer ces fonds de carte au préalable. 
# La méthode la plus courante consiste à taper les bons mots clefs sur 
# un moteur de recherche… On pourra par exemple utiliser des packages R, comme rnaturalearth :
install.packages("rnaturalearthdata")
world <- rnaturalearth::ne_countries(scale="medium", returnclass="sf")
class(world)

ggplot(data=world) +
  geom_sf(aes(fill=pop_est)) +
   scale_fill_viridis_c(option="plasma", trans="sqrt")+theme_void()

# On peut aussi visualiser la terre comme une sphère :
ggplot(data=world)+
  geom_sf()+
  coord_sf(crs="+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs")

# Voir https://www.r-spatial.org/r/2018/10/25/ggplot2-sf.html pour plus de détails.
# On peut aussi utiliser le web, par exemple le site data gouv :
lien2<-"/Users/amorkeziou/Documents/DisqueExterne/Enseignement/2025_2026/INFO0803_VisualisationDesdonnees/Data/regions-20180101-shp/"
regions <- read_sf(lien2)
# Attention, la taille des objets peut être très (trop) grande
format(object.size(regions),units="Mb")
# et la construction de la carte peut dans ce cas prendre beaucoup de temps… 
# On peut réduire la taille avec ce type d'outils :
library(rmapshaper)
regions1 <- ms_simplify(regions)
format(object.size(regions1),units="Mb")

ggplot(regions1)+geom_sf()+
  coord_sf(xlim = c(-5.5,10),ylim=c(41,51))+theme_void()

##### page 91 ####
#### Cartes interactives avec le package leaflet ####
# Leaflet est un package permettant de faire de la cartographie interactive. 
# On pourra consulter un descriptif synthétique sur le site 
# (https://rstudio.github.io/leaflet/). Le principe est similaire à ce qui a été présenté 
# précédemment : les cartes sont construites à partir de couches qui se superposent. 
# Un fond de carte s'obtient avec les fonctions leaflet() et addTiles()

library(leaflet)
leaflet() %>% addTiles()

# On dispose de plusieurs styles de fonds de cartes, 
# on trouve quelques exemples dans (http://leaflet-extras.github.io/leaflet-providers/preview/)  
Paris <- mygeocode("paris")
m2 <- leaflet() %>% setView(lng=Paris[1], lat=Paris[2], zoom=12) %>%
       addTiles()
m2 %>% addProviderTiles("Stamen.Toner")

##### p 93 ####
m2 %>% addProviderTiles("Wikimedia")

##### p 94 ####
m2 %>% addProviderTiles("Esri.NatGeoWorldMap")

##### p 95 ####
m2 %>%
  addProviderTiles("Stamen.Watercolor") %>%
  addProviderTiles("Stamen.TonerHybrid")

# Il est fréquemment utile de repérer des lieux sur une carte à l’aide de symboles. 
# On pourra effectuer cela à l'aide des fonctions addMarkers et addCircles…
data(quakes)
str(quakes)
leaflet(data = quakes[1:20,]) %>% addTiles() %>% 
  addMarkers(~long, ~lat, popup=~as.character(mag), label=~as.character(mag))

# On remarque que l'on utilise ici un tilde pour spécifier qu'on utilise des variables 
# dans un dataframe. Le caractère interactif de la carte permet d'ajouter de l'information 
# lorsqu'on clique sur un marker (grâce à l'option popup). 
# On peut également ajouter des popups qui contiennent plus d'information, voire des liens
# vers des sites web :
content <- paste(sep="<br/>",
                 "<b><a href='http://www.samurainoodle.com'>Samurai Noodle</a></b>",
                 "606 5th Ave. S",
                 "Seattle, WA 98138")

leaflet() %>% addTiles() %>%
  addPopups(-122.327298, 47.597131, content,
            options=popupOptions(closeButton=FALSE))

##### P 98 ####
# Exercice 2.4 (Popup avec leaflet)
# Placer un popup localisant l’Université Rennes 2 (Campus Villejean). 
# On ajoutera un lien renvoyant sur le site de l'Université.
R2 <- mygeocode("Universite Rennes 2 Villejean") %>% as_tibble()

info <- paste(sep="<br/>",
              "<b><a href='https://www.univ-rennes2.fr'>Universite Rennes 2</a></b>",
              "Campus Villejean")
leaflet() %>% addTiles() %>%
  addPopups(R2[1]$lon, R2[2]$lat, info, options=popupOptions(closeButton=FALSE))

# Challenge 2 : Visualisation des stations velib à Paris
# Plusieurs villes dans le monde ont accepté de mettre en ligne les données 
# sur l'occupation des stations velib.
# Ces données sont facilement accessibles et mises à jour en temps réel. 
# On dispose généralement de la taille
# et la localisation des stations, la proportion de vélos disponibles… 

# 1. Récupérer les données actuelles de velib disponibles pour la ville de Paris : 
# https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/information/. 
# On pourra utiliser la fonction read_delim avec l’option delim=";".
lien <- "https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/export/?disjunctive.name&disjunctive.is_installed&disjunctive.is_renting&disjunctive.is_returning&disjunctive.nom_arrondissement_communes/velib-disponibilite-en-temps-reel"
sta.Paris <- read_delim(lien,delim=";")

# si ça ne marche pas, importer le fichier de données "velib-disponibilite-en-temps-reel.csv"
sta.Paris <- read_delim(file.choose(), delim=";")

# 2.  Décrire les variables du jeu de données.
# Nous avons de l'information sur la disponibilité, 
# le remplissage… de stations velib parisiennes

# 3. Créer une variable latitude et une variable longitude à partir de la variable geo.
sta.Paris1 <- sta.Paris %>% separate(`Coordonnées géographiques`,
                                     into=c("lat","lon"),sep=",") %>%
                        mutate(lat=as.numeric(lat),lon=as.numeric(lon))


# 4. Visualiser les positions des stations sur une carte leaflet.  
map.velib1 <- leaflet(data=sta.Paris1) %>%
  addTiles() %>%
  addCircleMarkers(~lon, ~lat,radius=3,
                   stroke=FALSE, fillOpacity=0.5, color="red")

map.velib1

# 5. Ajouter un popup qui permet de connaitre le nombre 
# de vélos disponibles (électriques+mécanique) quand on clique sur la station 
# (on pourra utiliser l'option popup dans la fonction addCircleMarkers). 
map.velib2 <- leaflet(data=sta.Paris1) %>%
              addTiles() %>%
               addCircleMarkers(~lon, ~lat, radius=3, stroke=FALSE,
                   fillOpacity=0.7, color="red",
                   popup=~sprintf("<b> Vélos dispos: %s</b>",
                            as.character(`Nombre total vélos disponibles`)))

map.velib2

#ou sans sprintf
map.velib2 <- leaflet(data=sta.Paris1) %>%
              addTiles() %>%
              addCircleMarkers(~lon, ~lat, radius=3, stroke=FALSE, fillOpacity=0.7, color="red",
              popup=~paste("Vélos dispos :", as.character(`Nombre total vélos disponibles`)))

map.velib2

# 6. Ajouter le nom de la station dans le popup.
map.velib3 <- leaflet(data=sta.Paris1) %>%
              addTiles() %>%
              addCircleMarkers(~lon, ~lat, radius=3, stroke=FALSE,
                   fillOpacity=0.7, color="red",
                   popup=~paste(as.character(`Nom station`), ", Vélos dispos :",
                                   as.character(`Nombre total vélos disponibles`),
                                   sep=""))
map.velib3

# 7. Faire de même en utilisant des couleurs différentes en fonction de la proportion 
# de vélos disponibles dans la station. On pourra utiliser les palettes de couleur
ColorPal1 <- colorNumeric(scales::seq_gradient_pal(low = "#132B43", high = "#56B1F7",
                                                   space = "Lab"), domain = c(0,1))
ColorPal2 <- colorNumeric(scales::seq_gradient_pal(low = "red", high = "black",
                                                   space = "Lab"), domain = c(0,1))

map.velib4 <- leaflet(data = sta.Paris1) %>%
           addTiles() %>%
            addCircleMarkers(~ lon, ~ lat,radius=3,stroke = FALSE, fillOpacity = 0.7,
                   color=~ColorPal1(`Nombre total vélos disponibles`/
                                      `Capacité de la station`),
                   popup = ~ paste(as.character(`Nom station`),", Vélos dispos :",
                                   as.character(`Nombre total vélos disponibles`),
                                   sep=""))

map.velib4

map.velib5 <- leaflet(data = sta.Paris1) %>%
  addTiles() %>%
  addCircleMarkers(~ lon, ~ lat,stroke = FALSE, fillOpacity = 0.7,
                   color=~ColorPal2(`Nombre total vélos disponibles`/
                                      `Capacité de la station`),
                   radius=~(`Nombre total vélos disponibles`/
                              `Capacité de la station`)*8,
                   popup = ~ paste(as.character(`Nom station`),", Vélos dispos :",
                                   as.character(`Nombre total vélos disponibles`),
                                   sep=""))

map.velib5

# 8. Créer une fonction local.station qui permette de visualiser quelques stations 
# autours d'une station choisie. 
nom.station <- "Jussieu - Fossés Saint-Bernard"
local.station <- function(nom.station){
  df <- sta.Paris1 %>% filter(`Nom station`==nom.station)
  leaflet(data = sta.Paris1) %>% setView(lng=df$lon,lat=df$lat,zoom=15) %>%
    addTiles() %>%
    addCircleMarkers(~ lon, ~ lat,stroke = FALSE, fillOpacity = 0.7,
                     popup = ~ paste(as.character(`Nom station`),", Vélos dispos :",
                                     as.character(`Nombre total vélos disponibles`),
                                     sep="")) %>%
    addMarkers(lng=df$lon,lat=df$lat,
               popup = ~ paste(nom.station,", Vélos dispos :",
                               as.character(df$`Nombre total vélos disponibles`),
                               sep=""),
               popupOptions = popupOptions(noHide = T))
}

# La fonction devra par exemple renvoyer
local.station("Jussieu - Fossés Saint-Bernard")
local.station("Gare Montparnasse - Arrivée")

## Carte des températures avec leaflet 
# Exercice 5 :  
# Refaire la carte des températures du premier challenge (voir section 2.2.1) 
# en utilisant leaflet. On utilisera la table construite dans le challenge 1 et 
# la fonction addPolygons. On pourra également ajouter un popup qui permet de 
# visualiser le nom du département ainsi que la température prévue lorsqu'on clique dessus.

dpt2 <- st_transform(dpt1, crs = 4326)
dpt2$t_prev <- round(dpt2$t_prev)
pal <- colorNumeric(scales::seq_gradient_pal(low = "yellow", high = "red",
                                             space = "Lab"), domain = dpt2$t_prev)
m <- leaflet() %>% addTiles() %>%
  addPolygons(data = dpt2,color=~pal(t_prev),fillOpacity = 0.6,
              stroke = TRUE, weight=1,
              popup=~paste(as.character(NOM_DEPT),as.character(t_prev),sep=" : ")) %>%
  addLayersControl(options=layersControlOptions(collapsed = FALSE))
m

# ou avec une autre palette de couleur
pal1 <- colorNumeric(palette = c("inferno"),domain = dpt2$t_prev)
m1 <- leaflet() %>% addTiles() %>%
  addPolygons(data = dpt2,color=~pal1(t_prev),fillOpacity = 0.6,
              stroke = TRUE,weight=1,
              popup=~paste(as.character(NOM_DEPT),as.character(t_prev),sep=" : ")) %>%
  addLayersControl(options=layersControlOptions(collapsed = FALSE))
m1


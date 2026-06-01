#Cocu Ethan
#Projet_CAC40
library(ggplot2)
library(dplyr)
library(tidyr)
library(scales)
library(ggrepel)
library(patchwork)
library(GGally)
library(quadprog)
library(tseries)
library(rugarch)
library(sf)
library(ggdendro)

dir.create("figures", showWarnings = FALSE, recursive = TRUE)

#---------------------------------------------------------
# (1) Chargement des données CAC40 (2010-2020)
#---------------------------------------------------------

donnees_brutes <- read.csv("data/preprocessed_CAC40.csv",
                            stringsAsFactors = FALSE)
names(donnees_brutes) <- c("idx", "Entreprise", "Date", "Ouverture",
                            "Cloture", "Haut", "Bas", "Volume")
donnees_brutes$Date       <- as.Date(donnees_brutes$Date)
donnees_brutes$Annee      <- as.integer(format(donnees_brutes$Date, "%Y"))
donnees_brutes$Entreprise <- trimws(donnees_brutes$Entreprise)

#---------------------------------------------------------
# (2) Simplification des noms longs d'entreprises
#---------------------------------------------------------

noms_courts <- c(
  "Cap Gemini"                                                   = "Capgemini",
  "Engie (ex GDF Suez"                                          = "Engie",
  "Hermès (Hermes International"                                = "Hermès",
  "LEGRAND"                                                      = "Legrand",
  "LOréal"                                                     = "L'Oréal",
  "LVMH Moet Hennessy Louis Vuitton"                            = "LVMH",
  "Michelin (Compagnie Générale d Etablissements Michelin SCPA" = "Michelin",
  "Société Générale (Societe Generale"                        = "Société Générale",
  "SAFRAN"                                                       = "Safran",
  "TOTAL"                                                        = "Total",
  "VINCI"                                                        = "Vinci",
  "Veolia Environnement"                                         = "Veolia",
  "Worldline SA"                                                 = "Worldline"
)

for (ancien in names(noms_courts)) {
  donnees_brutes$Entreprise[donnees_brutes$Entreprise == ancien] <- unname(noms_courts[ancien])
}

cac40 <- donnees_brutes[donnees_brutes$Entreprise != "Name", ]

#---------------------------------------------------------
# (3) Classification sectorielle des 38 entreprises
#---------------------------------------------------------

secteurs <- data.frame(
  Entreprise = c(
    "AXA", "BNP Paribas", "Crédit Agricole", "Société Générale",
    "Total", "Engie",
    "Air Liquide", "Airbus", "Safran", "Vinci", "Bouygues",
    "Saint-Gobain", "Schneider Electric", "Legrand",
    "LVMH", "Hermès", "Kering", "L'Oréal", "Pernod Ricard",
    "Danone", "Sodexo", "Accor", "Vivendi", "Publicis",
    "Capgemini", "Atos", "STMicroelectronics", "Dassault Systèmes", "Worldline",
    "ArcelorMittal", "Michelin",
    "Orange",
    "Sanofi", "EssilorLuxottica",
    "Unibail-Rodamco",
    "Peugeot", "Renault",
    "Veolia"
  ),
  Secteur = c(
    rep("Finance", 4),
    rep("Energie", 2),
    rep("Industrie", 8),
    rep("Luxe/Conso.", 10),
    rep("Technologie", 5),
    rep("Materiaux", 2),
    "Telecom",
    "Sante", "Sante",
    "Immobilier",
    "Automobile", "Automobile",
    "Services env."
  ),
  stringsAsFactors = FALSE
)

cac40 <- left_join(cac40, secteurs, by = "Entreprise")

#---------------------------------------------------------
# (4) Calcul des rendements journaliers par action
#---------------------------------------------------------

cac40 <- cac40 %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise) %>%
  mutate(Rendement = (Cloture / lag(Cloture) - 1) * 100) %>%
  ungroup()

couleur_secteur <- c(
  "Finance"      = "#1f77b4",
  "Energie"      = "#d62728",
  "Industrie"    = "#2ca02c",
  "Luxe/Conso."  = "#9467bd",
  "Technologie"  = "#ff7f0e",
  "Materiaux"    = "#8c564b",
  "Telecom"      = "#e377c2",
  "Sante"        = "#17becf",
  "Immobilier"   = "#bcbd22",
  "Automobile"   = "#7f7f7f",
  "Services env."= "#aec7e8"
)

#---------------------------------------------------------
# Figure 1 - Evolution des cours normalises (base 100 en 2010)
#---------------------------------------------------------

# 8 entreprises representatives de secteurs differents
selection <- c("LVMH", "Sanofi", "Total", "Renault",
               "AXA", "Airbus", "Orange", "STMicroelectronics")

cours_norm <- cac40 %>%
  filter(Entreprise %in% selection) %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise) %>%
  mutate(Prix_norm = Cloture / first(Cloture) * 100) %>%
  ungroup()

etiquettes <- cours_norm %>%
  group_by(Entreprise) %>%
  slice_max(Date, n = 1) %>%
  ungroup()

ggplot(cours_norm, aes(x = Date, y = Prix_norm, color = Entreprise)) +
  geom_line(linewidth = 0.65) +
  geom_hline(yintercept = 100, linetype = "dashed",
             color = "gray50", linewidth = 0.4) +
  geom_vline(xintercept = as.Date("2020-03-17"),
             linetype = "dotted", color = "firebrick", linewidth = 0.6) +
  annotate("text", x = as.Date("2020-03-17"), y = Inf,
           label = "Confinement\n(mars 2020)", vjust = 1.4, hjust = -0.05,
           color = "firebrick", size = 2.8) +
  geom_text_repel(data = etiquettes, aes(label = Entreprise),
                  nudge_x = 50, size = 2.8, direction = "y",
                  hjust = 0, segment.size = 0.25, segment.color = "gray60") +
  scale_x_date(date_breaks = "1 year", date_labels = "%Y",
               expand = expansion(mult = c(0.01, 0.18))) +
  scale_y_continuous(labels = label_number()) +
  labs(title = "Evolution des cours normalises - Selection CAC40 (2010-2020)",
       subtitle = "Base 100 a la premiere seance de janvier 2010",
       x = NULL, y = "Indice (base 100)") +
  theme_bw(base_size = 11) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("figures/fig1_evolution_normalisee.png",
       width = 10, height = 5.5, dpi = 150)

#---------------------------------------------------------
# Figure 2 - Heatmap des rendements annuels (toutes entreprises)
#---------------------------------------------------------

rend_annuel <- cac40 %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise, Secteur, Annee) %>%
  summarise(Rend = (last(Cloture) / first(Cloture) - 1) * 100,
            .groups = "drop")

ordre_ent <- rend_annuel %>%
  arrange(Secteur, Entreprise) %>%
  pull(Entreprise) %>%
  unique()

rend_annuel$Entreprise <- factor(rend_annuel$Entreprise, levels = rev(ordre_ent))

ggplot(rend_annuel, aes(x = factor(Annee), y = Entreprise, fill = Rend)) +
  geom_tile(color = "white", linewidth = 0.25) +
  geom_text(aes(label = sprintf("%.0f", Rend)), size = 1.9, color = "gray10") +
  scale_fill_gradient2(low = "#d73027", mid = "white", high = "#1a9850",
                        midpoint = 0, limits = c(-60, 80), oob = squish,
                        name = "Rend. (%)") +
  labs(title = "Rendements annuels des 38 actions du CAC40 (2010-2020)",
       subtitle = "2020 : donnees jusqu'au T1 (crise COVID incluse)",
       x = "Annee", y = NULL) +
  theme_minimal(base_size = 9) +
  theme(axis.text.y = element_text(size = 7.5),
        panel.grid  = element_blank(),
        legend.position = "right")

ggsave("figures/fig2_heatmap_rendements.png",
       width = 13, height = 10, dpi = 150)

#---------------------------------------------------------
# Figure 3 - Distribution des rendements journaliers par secteur
#---------------------------------------------------------

rend_secteur <- cac40 %>%
  filter(!is.na(Rendement), !is.na(Secteur))

# Ordre par volatilite croissante
ordre_vol <- rend_secteur %>%
  group_by(Secteur) %>%
  summarise(ecart_type = sd(Rendement, na.rm = TRUE), .groups = "drop") %>%
  arrange(ecart_type) %>%
  pull(Secteur)

rend_secteur$Secteur <- factor(rend_secteur$Secteur, levels = ordre_vol)

ggplot(rend_secteur, aes(x = Secteur, y = Rendement, fill = Secteur)) +
  geom_violin(alpha = 0.55, trim = TRUE, scale = "width") +
  geom_boxplot(width = 0.12, outlier.size = 0.2, outlier.alpha = 0.25,
               fill = "white", color = "gray30") +
  scale_fill_manual(values = couleur_secteur) +
  scale_y_continuous(limits = c(-15, 15), oob = squish) +
  coord_flip() +
  labs(title = "Distribution des rendements journaliers par secteur (2010-2020)",
       subtitle = "Axe tronque a +/-15% — secteurs ordonnes par volatilite croissante",
       x = NULL, y = "Rendement journalier (%)") +
  theme_bw(base_size = 11) +
  theme(legend.position = "none")

ggsave("figures/fig3_distribution_rendements.png",
       width = 9, height = 6, dpi = 150)

#---------------------------------------------------------
# Figure 4 - Profil Risque / Rendement
#---------------------------------------------------------

# Volatilite annualisee = ecart-type journalier x racine(252)
profil <- cac40 %>%
  filter(!is.na(Rendement), !is.na(Secteur)) %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise, Secteur) %>%
  summarise(
    Volatilite = sd(Rendement, na.rm = TRUE) * sqrt(252),
    Rend_total = (last(Cloture) / first(Cloture) - 1) * 100,
    .groups = "drop"
  )

ggplot(profil, aes(x = Volatilite, y = Rend_total,
                    color = Secteur, label = Entreprise)) +
  geom_point(size = 3.5, alpha = 0.85) +
  geom_text_repel(size = 2.5, max.overlaps = 30,
                  segment.size = 0.25, segment.color = "gray60") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  scale_color_manual(values = couleur_secteur) +
  labs(title = "Profil Risque / Rendement - Actions CAC40 (2010-2020)",
       subtitle = "Volatilite annualisee = ecart-type journalier x racine(252)",
       x = "Volatilite annualisee (%)",
       y = "Rendement total (%)",
       color = "Secteur") +
  theme_bw(base_size = 11) +
  theme(legend.position = "right")

ggsave("figures/fig4_risque_rendement.png",
       width = 10, height = 7, dpi = 150)

#---------------------------------------------------------
# Figure 5 - Matrice de correlation des rendements journaliers
#---------------------------------------------------------

# Format large : une colonne par entreprise
tableau_large <- cac40 %>%
  filter(!is.na(Rendement)) %>%
  select(Date, Entreprise, Rendement) %>%
  pivot_wider(names_from = Entreprise, values_from = Rendement,
              values_fn = mean)

matrice_cor <- cor(tableau_large[, -1], use = "pairwise.complete.obs")

# Ordre des entreprises par secteur pour la heatmap
ordre_sec <- secteurs %>%
  arrange(Secteur, Entreprise) %>%
  filter(Entreprise %in% colnames(matrice_cor)) %>%
  pull(Entreprise)

cor_long <- as.data.frame(as.table(matrice_cor))
names(cor_long) <- c("Ent1", "Ent2", "Correlation")
cor_long$Ent1 <- factor(cor_long$Ent1, levels = ordre_sec)
cor_long$Ent2 <- factor(cor_long$Ent2, levels = rev(ordre_sec))

ggplot(cor_long, aes(x = Ent1, y = Ent2, fill = Correlation)) +
  geom_tile() +
  scale_fill_gradient2(low = "#d73027", mid = "white", high = "#1a9850",
                        midpoint = 0, limits = c(-1, 1), name = "Correlation") +
  labs(title = "Matrice de correlation des rendements journaliers - CAC40",
       subtitle = "Actions triees par secteur d'activite",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 8) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5, size = 7),
        axis.text.y = element_text(size = 7),
        panel.grid  = element_blank())

ggsave("figures/fig5_correlation.png",
       width = 11, height = 10, dpi = 150)

#---------------------------------------------------------
# Figure 6 - Impact de la crise COVID-19 (janvier - avril 2020)
#---------------------------------------------------------

# Indice normalise par entreprise puis moyenne par secteur
covid <- cac40 %>%
  filter(Annee == 2020, !is.na(Secteur)) %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise) %>%
  mutate(Prix_norm = Cloture / first(Cloture) * 100) %>%
  ungroup() %>%
  group_by(Date, Secteur) %>%
  summarise(Indice = mean(Prix_norm, na.rm = TRUE), .groups = "drop")

ggplot(covid, aes(x = Date, y = Indice, color = Secteur)) +
  geom_line(linewidth = 0.75) +
  geom_hline(yintercept = 100, linetype = "dashed",
             color = "gray50", linewidth = 0.4) +
  geom_vline(xintercept = as.Date("2020-03-17"),
             linetype = "dotted", color = "firebrick", linewidth = 0.6) +
  annotate("text", x = as.Date("2020-03-17"), y = Inf,
           label = "Confinement\nnational (17/03)", vjust = 1.4, hjust = -0.05,
           color = "firebrick", size = 2.8) +
  scale_color_manual(values = couleur_secteur) +
  scale_x_date(date_breaks = "2 weeks", date_labels = "%d %b") +
  labs(title = "Impact de la crise COVID-19 sur les secteurs du CAC40",
       subtitle = "Indice moyen par secteur, base 100 au 2 janvier 2020",
       x = NULL, y = "Indice (base 100)",
       color = "Secteur") +
  theme_bw(base_size = 11) +
  theme(axis.text.x    = element_text(angle = 45, hjust = 1),
        legend.position = "right")

ggsave("figures/fig6_covid.png",
       width = 11, height = 6.5, dpi = 150)

#---------------------------------------------------------
# Figure 7 - Performance totale 2010-2020 par entreprise
#---------------------------------------------------------

perf_totale <- cac40 %>%
  filter(!is.na(Secteur)) %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise, Secteur) %>%
  summarise(Perf = (last(Cloture) / first(Cloture) - 1) * 100,
            .groups = "drop") %>%
  arrange(Perf) %>%
  mutate(Entreprise = factor(Entreprise, levels = Entreprise))

ggplot(perf_totale, aes(x = Entreprise, y = Perf, fill = Secteur)) +
  geom_col() +
  geom_text(aes(label = sprintf("%.0f%%", Perf),
                hjust  = ifelse(Perf >= 0, -0.1, 1.1)),
            size = 2.4, color = "gray20") +
  scale_fill_manual(values = couleur_secteur) +
  scale_y_continuous(labels = label_percent(scale = 1),
                     expand = expansion(mult = 0.18)) +
  coord_flip() +
  labs(title = "Performance totale des actions du CAC40 (2010-2020)",
       x = NULL, y = "Performance totale (%)",
       fill = "Secteur") +
  theme_bw(base_size = 10) +
  theme(legend.position = "right")

ggsave("figures/fig7_performance_totale.png",
       width = 10, height = 11, dpi = 150)

#---------------------------------------------------------
# Figure 8 - Evolution de la volatilite annualisee par secteur
#---------------------------------------------------------

vol_annuelle <- cac40 %>%
  filter(!is.na(Rendement), !is.na(Secteur)) %>%
  group_by(Secteur, Annee) %>%
  summarise(Vol = sd(Rendement, na.rm = TRUE) * sqrt(252),
            .groups = "drop")

ggplot(vol_annuelle, aes(x = Annee, y = Vol,
                          color = Secteur, group = Secteur)) +
  geom_line(linewidth = 0.7) +
  geom_point(size = 1.8) +
  scale_color_manual(values = couleur_secteur) +
  scale_x_continuous(breaks = 2010:2020) +
  labs(title = "Evolution de la volatilite annualisee par secteur (2010-2020)",
       subtitle = "Ecart-type des rendements journaliers x racine(252)",
       x = "Annee", y = "Volatilite annualisee (%)",
       color = "Secteur") +
  theme_bw(base_size = 11) +
  theme(axis.text.x    = element_text(angle = 45, hjust = 1),
        legend.position = "right")

ggsave("figures/fig8_volatilite_annuelle.png",
       width = 10, height = 6, dpi = 150)

#---------------------------------------------------------
# Figure 9 - Camembert de la composition sectorielle du CAC40
#---------------------------------------------------------

composition <- secteurs %>%
  group_by(Secteur) %>%
  summarise(Nb = n(), .groups = "drop") %>%
  arrange(desc(Nb)) %>%
  mutate(Pct = Nb / sum(Nb) * 100,
         Etiquette = paste0(Secteur, "\n", Nb, " (", sprintf("%.0f", Pct), "%)"))

ggplot(composition, aes(x = "", y = Nb, fill = Secteur)) +
  geom_bar(stat = "identity", width = 1, color = "white", linewidth = 0.5) +
  coord_polar("y", start = 0) +
  geom_text(aes(label = Etiquette),
            position = position_stack(vjust = 0.5), size = 2.8) +
  scale_fill_manual(values = couleur_secteur) +
  labs(title = "Composition du CAC40 par secteur d'activite",
       subtitle = "Repartition des 38 entreprises dans le jeu de donnees") +
  theme_void(base_size = 11) +
  theme(legend.position = "none")

ggsave("figures/fig9_camembert_secteurs.png",
       width = 8, height = 8, dpi = 150)

#---------------------------------------------------------
# Figure 10 - Histogrammes des rendements + loi normale theorique
#---------------------------------------------------------

# 4 entreprises aux profils risque/rendement tres differents
sel_histo <- c("LVMH", "Sanofi", "Renault", "ArcelorMittal")

rend_histo <- cac40 %>%
  filter(Entreprise %in% sel_histo, !is.na(Rendement))

# Courbe normale theorique ajustee aux parametres empiriques de chaque entreprise
densite_normale <- rend_histo %>%
  group_by(Entreprise) %>%
  summarise(mu    = mean(Rendement, na.rm = TRUE),
            sigma = sd(Rendement, na.rm = TRUE), .groups = "drop") %>%
  rowwise() %>%
  mutate(x = list(seq(-15, 15, length.out = 300)),
         y = list(dnorm(seq(-15, 15, length.out = 300), mu, sigma))) %>%
  unnest(cols = c(x, y))

ggplot(rend_histo, aes(x = Rendement)) +
  geom_histogram(aes(y = after_stat(density)), bins = 60,
                 fill = "steelblue", color = "white", alpha = 0.7) +
  geom_line(data = densite_normale, aes(x = x, y = y),
            color = "firebrick", linewidth = 0.9) +
  facet_wrap(~ Entreprise, scales = "free_y") +
  scale_x_continuous(limits = c(-15, 15), oob = squish) +
  labs(title = "Distribution des rendements journaliers vs loi normale theorique",
       subtitle = "Courbe rouge = N(mu, sigma^2) ajustee — queues epaisses visibles",
       x = "Rendement journalier (%)", y = "Densite") +
  theme_bw(base_size = 11)

ggsave("figures/fig10_histogrammes_normale.png",
       width = 10, height = 7, dpi = 150)

#---------------------------------------------------------
# Figure 11 - Comparaison de trois methodes de normalisation (LVMH)
#---------------------------------------------------------

lvmh_norm <- cac40 %>%
  filter(Entreprise == "LVMH") %>%
  arrange(Date) %>%
  mutate(
    Base100 = Cloture / first(Cloture) * 100,
    Zscore  = (Cloture - mean(Cloture)) / sd(Cloture),
    MinMax  = (Cloture - min(Cloture)) / (max(Cloture) - min(Cloture))
  ) %>%
  select(Date, Base100, Zscore, MinMax) %>%
  pivot_longer(cols = c(Base100, Zscore, MinMax),
               names_to = "Methode", values_to = "Valeur")

etiquettes_methodes <- c(
  Base100 = "Base 100  :  x / x0 * 100",
  Zscore  = "Z-score   :  (x - mu) / sigma",
  MinMax  = "Min-Max   :  (x - min) / (max - min)"
)

lvmh_norm$Methode <- factor(lvmh_norm$Methode,
                             levels = c("Base100", "Zscore", "MinMax"))

ggplot(lvmh_norm, aes(x = Date, y = Valeur)) +
  geom_line(color = "#9467bd", linewidth = 0.65) +
  geom_hline(yintercept = 0, linetype = "dashed",
             color = "gray50", linewidth = 0.4) +
  facet_wrap(~ Methode, scales = "free_y", ncol = 1,
             labeller = labeller(Methode = etiquettes_methodes)) +
  scale_x_date(date_breaks = "1 year", date_labels = "%Y") +
  labs(title = "Trois methodes de normalisation appliquees au cours de LVMH",
       subtitle = "Meme serie temporelle, trois lectures differentes",
       x = NULL, y = "Valeur normalisee") +
  theme_bw(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("figures/fig11_normalisations.png",
       width = 10, height = 9, dpi = 150)

#---------------------------------------------------------
# Figure 12 - Regression lineaire entre deux actions correlees
#---------------------------------------------------------

# LVMH et Kering : meme secteur Luxe, correlation elevee attendue
rend_lk <- cac40 %>%
  filter(Entreprise %in% c("LVMH", "Kering"), !is.na(Rendement)) %>%
  select(Date, Entreprise, Rendement) %>%
  pivot_wider(names_from = Entreprise, values_from = Rendement) %>%
  drop_na()

modele_lk <- lm(LVMH ~ Kering, data = rend_lk)
r2 <- summary(modele_lk)$r.squared

ggplot(rend_lk, aes(x = Kering, y = LVMH)) +
  geom_point(alpha = 0.3, size = 0.9, color = "#9467bd") +
  geom_smooth(method = "lm", se = TRUE,
              color = "firebrick", fill = "pink", alpha = 0.2) +
  annotate("text", x = -Inf, y = Inf,
           label = paste0("R² = ", sprintf("%.3f", r2)),
           hjust = -0.2, vjust = 1.8, size = 4.5, fontface = "bold") +
  labs(title = "Regression lineaire : rendements journaliers LVMH vs Kering",
       subtitle = "Deux acteurs du secteur Luxe — periode 2010-2020",
       x = "Rendement Kering (%)", y = "Rendement LVMH (%)") +
  theme_bw(base_size = 11)

ggsave("figures/fig12_regression.png",
       width = 8, height = 7, dpi = 150)

#---------------------------------------------------------
# Figure 13 - Illustration du TCL : portefeuille vs action individuelle
#---------------------------------------------------------

# Rendement du portefeuille equi-pondere = moyenne des 38 rendements journaliers
rend_portefeuille <- cac40 %>%
  filter(!is.na(Rendement)) %>%
  group_by(Date) %>%
  summarise(Rendement = mean(Rendement, na.rm = TRUE), .groups = "drop") %>%
  mutate(Entreprise = "Portefeuille CAC40\n(moyenne 38 actions)")

# Actions individuelles volatiles pour la comparaison
rend_indiv <- cac40 %>%
  filter(Entreprise %in% c("ArcelorMittal", "Renault"), !is.na(Rendement)) %>%
  select(Date, Entreprise, Rendement)

comp_tcl <- bind_rows(rend_indiv, rend_portefeuille)
comp_tcl$Entreprise <- factor(comp_tcl$Entreprise,
                               levels = c("ArcelorMittal", "Renault",
                                         "Portefeuille CAC40\n(moyenne 38 actions)"))

couleur_tcl <- c(
  "ArcelorMittal"                          = "#8c564b",
  "Renault"                                 = "#7f7f7f",
  "Portefeuille CAC40\n(moyenne 38 actions)"= "#1f77b4"
)

ggplot(comp_tcl, aes(x = Rendement, color = Entreprise, fill = Entreprise)) +
  geom_density(alpha = 0.25, linewidth = 0.9) +
  scale_color_manual(values = couleur_tcl) +
  scale_fill_manual(values  = couleur_tcl) +
  scale_x_continuous(limits = c(-12, 12), oob = squish) +
  labs(title = "Illustration du Theoreme Central Limite (TCL)",
       subtitle = "Le portefeuille a une distribution plus etroite et plus normale que les actions seules",
       x = "Rendement journalier (%)", y = "Densite",
       color = NULL, fill = NULL) +
  theme_bw(base_size = 11) +
  theme(legend.position = "right",
        legend.text = element_text(size = 9))

ggsave("figures/fig13_tcl.png",
       width = 9, height = 6, dpi = 150)

#---------------------------------------------------------
# Figure 14 - Composition patchwork : tableau de bord sectoriel
#---------------------------------------------------------

p_distrib <- ggplot(rend_secteur, aes(x = Secteur, y = Rendement, fill = Secteur)) +
  geom_violin(alpha = 0.55, trim = TRUE, scale = "width") +
  geom_boxplot(width = 0.12, outlier.size = 0.2, outlier.alpha = 0.25,
               fill = "white", color = "gray30") +
  scale_fill_manual(values = couleur_secteur) +
  scale_y_continuous(limits = c(-15, 15), oob = squish) +
  coord_flip() +
  labs(title = "Distributions par secteur",
       x = NULL, y = "Rendement journalier (%)") +
  theme_bw(base_size = 9) +
  theme(legend.position = "none")

p_risque <- ggplot(profil, aes(x = Volatilite, y = Rend_total,
                                color = Secteur, label = Entreprise)) +
  geom_point(size = 2.2, alpha = 0.85) +
  geom_text_repel(size = 2, max.overlaps = 20,
                  segment.size = 0.2, segment.color = "gray60") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  scale_color_manual(values = couleur_secteur) +
  labs(title = "Risque / Rendement",
       x = "Volatilite annualisee (%)", y = "Rendement total (%)") +
  theme_bw(base_size = 9) +
  theme(legend.position = "none")

p_vol <- ggplot(vol_annuelle, aes(x = Annee, y = Vol,
                                   color = Secteur, group = Secteur)) +
  geom_line(linewidth = 0.6) +
  geom_point(size = 1.4) +
  scale_color_manual(values = couleur_secteur) +
  scale_x_continuous(breaks = 2010:2020) +
  labs(title = "Volatilite annualisee par secteur",
       x = "Annee", y = "Volatilite (%)") +
  theme_bw(base_size = 9) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.key.size = unit(0.4, "cm"),
        legend.text = element_text(size = 7))

p_camembert <- ggplot(composition, aes(x = "", y = Nb, fill = Secteur)) +
  geom_bar(stat = "identity", width = 1, color = "white", linewidth = 0.5) +
  coord_polar("y", start = 0) +
  geom_text(aes(label = Etiquette),
            position = position_stack(vjust = 0.5), size = 2.2) +
  scale_fill_manual(values = couleur_secteur) +
  labs(title = "Composition sectorielle") +
  theme_void(base_size = 9) +
  theme(legend.position = "none")

grille_composite <- (p_distrib | p_risque) / (p_vol | p_camembert) +
  plot_annotation(
    title = "Tableau de bord sectoriel CAC40 (2010-2020)",
    theme = theme(plot.title = element_text(size = 14, face = "bold"))
  )

ggsave("figures/fig14_patchwork_sectoriel.png",
       plot = grille_composite, width = 16, height = 12, dpi = 150)

#---------------------------------------------------------
# Figure 15 - Coordonnees paralleles : profil multi-dimensionnel
#---------------------------------------------------------

# (1)
profil_complet <- cac40 %>%
  filter(!is.na(Rendement), !is.na(Secteur)) %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise, Secteur) %>%
  summarise(
    Rend_total  = (last(Cloture) / first(Cloture) - 1) * 100,
    Volatilite  = sd(Rendement, na.rm = TRUE) * sqrt(252),
    Skewness    = {
      x <- Rendement[!is.na(Rendement)]
      mean((x - mean(x))^3) / sd(x)^3
    },
    Kurtosis    = {
      x <- Rendement[!is.na(Rendement)]
      mean((x - mean(x))^4) / sd(x)^4 - 3
    },
    DrawdownMax = {
      r <- Rendement[!is.na(Rendement)] / 100
      prix_cum <- cumprod(1 + r)
      min(prix_cum / cummax(prix_cum) - 1) * 100
    },
    .groups = "drop"
  )

# (2)
names(profil_complet)[3:7] <- c("Rendement\ntotal(%)",
                                  "Volatilite\n(%/an)",
                                  "Skewness",
                                  "Kurtosis\nexces",
                                  "Drawdown\nmax(%)")

ggparcoord(
  data       = profil_complet,
  columns    = 3:7,
  groupColumn = "Secteur",
  scale      = "uniminmax",
  alphaLines = 0.65
) +
  scale_color_manual(values = couleur_secteur) +
  labs(
    title    = "Coordonnees paralleles des actions CAC40 (2010-2020)",
    subtitle = "Chaque ligne = une entreprise  |  Axes normalises [0,1]",
    x = NULL, y = "Valeur normalisee [0, 1]",
    color = "Secteur"
  ) +
  theme_bw(base_size = 11) +
  theme(axis.text.x = element_text(size = 9))

ggsave("figures/fig15_coordonnees_paralleles.png",
       width = 12, height = 7, dpi = 150)

#---------------------------------------------------------
# Figure 16 - Tests de normalite (Shapiro-Wilk, Jarque-Bera) et stationnarite (ADF)
#---------------------------------------------------------

# (1)
entreprises_liste <- unique(cac40$Entreprise[!is.na(cac40$Secteur)])

test_shapiro <- sapply(entreprises_liste, function(ent) {
  x <- cac40$Rendement[cac40$Entreprise == ent & !is.na(cac40$Rendement)]
  tryCatch(shapiro.test(x[seq_len(min(5000L, length(x)))])$p.value, error = function(e) NA_real_)
})

test_jb <- sapply(entreprises_liste, function(ent) {
  x <- cac40$Rendement[cac40$Entreprise == ent & !is.na(cac40$Rendement)]
  tryCatch(tseries::jarque.bera.test(x)$p.value, error = function(e) NA_real_)
})

test_adf <- sapply(entreprises_liste, function(ent) {
  x <- cac40$Cloture[cac40$Entreprise == ent & !is.na(cac40$Cloture)]
  tryCatch(tseries::adf.test(x)$p.value, error = function(e) NA_real_)
})

# (2)
resultats_tests <- data.frame(
  Entreprise = entreprises_liste,
  Shapiro_p  = as.numeric(test_shapiro),
  JB_p       = as.numeric(test_jb),
  ADF_p      = as.numeric(test_adf),
  stringsAsFactors = FALSE
)
resultats_tests <- left_join(resultats_tests, secteurs, by = "Entreprise")

# Figure 16a — heatmap p-valeurs normalite
tests_long <- resultats_tests %>%
  select(Entreprise, Secteur, Shapiro_p, JB_p) %>%
  pivot_longer(cols = c(Shapiro_p, JB_p),
               names_to = "Test", values_to = "p_valeur") %>%
  mutate(Test = recode(Test, Shapiro_p = "Shapiro-Wilk", JB_p = "Jarque-Bera"),
         Entreprise = factor(Entreprise,
                             levels = resultats_tests %>%
                               arrange(Secteur, Entreprise) %>%
                               pull(Entreprise)))

ggplot(tests_long, aes(x = Test, y = Entreprise, fill = p_valeur)) +
  geom_tile(color = "white") +
  geom_text(aes(label = ifelse(p_valeur < 0.001, "<0.001",
                                sprintf("%.3f", p_valeur))),
            size = 2.1) +
  scale_fill_gradient2(low = "#d73027", mid = "#ffffbf", high = "#1a9850",
                        midpoint = 0.05, limits = c(0, 0.2), oob = squish,
                        name = "p-valeur") +
  labs(title = "Tests de normalite des rendements journaliers - CAC40",
       subtitle = "p < 0.05 (rouge) : rejet de la loi normale",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 9) +
  theme(panel.grid = element_blank(),
        axis.text.x = element_text(size = 10, face = "bold"))

ggsave("figures/fig16a_tests_normalite.png",
       width = 7, height = 11, dpi = 150)

# Figure 16b — barres ADF
resultats_tests_adf <- resultats_tests %>%
  arrange(ADF_p) %>%
  mutate(Entreprise  = factor(Entreprise, levels = Entreprise),
         Stationnaire = ADF_p < 0.05)

ggplot(resultats_tests_adf, aes(x = Entreprise, y = ADF_p, fill = Stationnaire)) +
  geom_col() +
  geom_hline(yintercept = 0.05, linetype = "dashed",
             color = "firebrick", linewidth = 0.7) +
  annotate("text", x = Inf, y = 0.05,
           label = "Seuil 5%", hjust = 1.1, vjust = -0.4,
           color = "firebrick", size = 3) +
  scale_fill_manual(values = c("TRUE" = "#1a9850", "FALSE" = "#d73027"),
                    labels = c("TRUE" = "Stationnaire", "FALSE" = "Racine unitaire")) +
  scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.12))) +
  coord_flip() +
  labs(title = "Test de stationnarite ADF sur les cours de cloture (CAC40)",
       subtitle = "Vert : serie stationnaire (p < 5%)  |  Rouge : racine unitaire probable",
       x = NULL, y = "p-valeur ADF", fill = NULL) +
  theme_bw(base_size = 9)

ggsave("figures/fig16b_test_adf.png",
       width = 9, height = 11, dpi = 150)

#---------------------------------------------------------
# Figure 17 - Frontiere efficiente de Markowitz (CAC40)
#---------------------------------------------------------

# (1) Matrice de covariance et rendements moyens annualises
rendements_mat <- tableau_large[, -1]
rendements_mat <- rendements_mat[complete.cases(rendements_mat), ]

mu_actifs <- colMeans(rendements_mat) * 252
Sigma      <- cov(rendements_mat) * 252
n_actifs   <- ncol(rendements_mat)

Dmat <- 2 * (Sigma + diag(1e-8, n_actifs))
dvec <- rep(0, n_actifs)

# Amat : colonne 1 = rendement cible (egalite), col 2 = somme des poids (egalite),
#        colonnes 3..n+2 = poids >= 0 (inegalite)
Amat <- cbind(mu_actifs, rep(1, n_actifs), diag(n_actifs))

# (2) Balayage de la frontiere
cibles    <- seq(min(mu_actifs) * 1.01, max(mu_actifs) * 0.99, length.out = 200)
frontiere <- data.frame(Rendement = numeric(200), Risque = numeric(200))

for (i in seq_along(cibles)) {
  bvec <- c(cibles[i], 1, rep(0, n_actifs))
  sol  <- tryCatch(
    quadprog::solve.QP(Dmat, dvec, Amat, bvec, meq = 2),
    error = function(e) NULL
  )
  if (!is.null(sol)) {
    w <- sol$solution
    frontiere$Rendement[i] <- sum(w * mu_actifs) * 100
    frontiere$Risque[i]    <- sqrt(as.numeric(t(w) %*% Sigma %*% w)) * 100
  } else {
    frontiere$Rendement[i] <- NA_real_
    frontiere$Risque[i]    <- NA_real_
  }
}
frontiere <- frontiere[!is.na(frontiere$Risque), ]

# (3) Portefeuille a variance minimale (PVM)
Amat_mvp <- cbind(rep(1, n_actifs), diag(n_actifs))
bvec_mvp <- c(1, rep(0, n_actifs))
sol_mvp  <- quadprog::solve.QP(Dmat, dvec, Amat_mvp, bvec_mvp, meq = 1)
poids_mvp <- sol_mvp$solution
mvp <- data.frame(
  Rendement = sum(poids_mvp * mu_actifs) * 100,
  Risque    = sqrt(as.numeric(t(poids_mvp) %*% Sigma %*% poids_mvp)) * 100
)

# (4) Portefeuille tangent (max Sharpe, taux sans risque = 0%)
idx_tang <- which.max(frontiere$Rendement / frontiere$Risque)
portefeuille_tangent <- frontiere[idx_tang, ]

# (5) Actifs individuels
actifs_indiv <- data.frame(
  Entreprise = names(mu_actifs),
  Rendement  = mu_actifs * 100,
  Risque     = sqrt(diag(Sigma)) * 100,
  stringsAsFactors = FALSE
)
actifs_indiv <- left_join(actifs_indiv, secteurs, by = "Entreprise")

ggplot() +
  geom_point(data = actifs_indiv,
             aes(x = Risque, y = Rendement, color = Secteur),
             size = 2.5, alpha = 0.8) +
  geom_text_repel(data = actifs_indiv,
                  aes(x = Risque, y = Rendement, label = Entreprise, color = Secteur),
                  size = 2.2, max.overlaps = 25,
                  segment.size = 0.2, segment.color = "gray60") +
  geom_path(data = frontiere,
            aes(x = Risque, y = Rendement),
            color = "black", linewidth = 1.3) +
  geom_point(data = mvp, aes(x = Risque, y = Rendement),
             color = "firebrick", size = 5, shape = 18) +
  geom_point(data = portefeuille_tangent, aes(x = Risque, y = Rendement),
             color = "darkgreen", size = 5, shape = 17) +
  annotate("text", x = mvp$Risque, y = mvp$Rendement,
           label = "PVM", hjust = -0.25, color = "firebrick",
           size = 3.5, fontface = "bold") +
  annotate("text", x = portefeuille_tangent$Risque,
           y = portefeuille_tangent$Rendement,
           label = "Tangent\n(max Sharpe)", hjust = -0.1,
           color = "darkgreen", size = 3.2) +
  scale_color_manual(values = couleur_secteur) +
  labs(title = "Frontiere efficiente de Markowitz - CAC40 (2010-2020)",
       subtitle = "Long-only (poids >= 0)  |  Taux sans risque = 0%  |  PVM = Portefeuille a Variance Minimale",
       x = "Risque : volatilite annualisee (%)",
       y = "Rendement annualise (%)",
       color = "Secteur") +
  theme_bw(base_size = 11)

ggsave("figures/fig17_frontiere_efficiente.png",
       width = 11, height = 8, dpi = 150)

#---------------------------------------------------------
# Figure 18 - Carte choroplèthe : sieges sociaux CAC40 par region
#---------------------------------------------------------

# (1) Mapping entreprise → region
region_cie <- data.frame(
  Entreprise = c(
    "AXA", "BNP Paribas", "Crédit Agricole", "Société Générale",
    "Total", "Engie", "Air Liquide", "Safran", "Vinci", "Bouygues",
    "Saint-Gobain", "Schneider Electric", "LVMH", "Hermès", "Kering",
    "L'Oréal", "Pernod Ricard", "Danone", "Sodexo", "Accor", "Vivendi",
    "Publicis", "Capgemini", "Atos", "Dassault Systèmes", "Worldline",
    "ArcelorMittal", "Orange", "Sanofi", "EssilorLuxottica",
    "Unibail-Rodamco", "Peugeot", "Renault", "Veolia",
    "Airbus",
    "Michelin", "STMicroelectronics",
    "Legrand"
  ),
  Region_nom = c(
    rep("Île-de-France", 34),
    "Occitanie",
    "Auvergne-Rhône-Alpes", "Auvergne-Rhône-Alpes",
    "Nouvelle-Aquitaine"
  ),
  stringsAsFactors = FALSE
)

# (2) Agregation par region : nb entreprises, volatilite moyenne, rendement moyen
stats_region <- region_cie %>%
  left_join(profil[, c("Entreprise", "Volatilite", "Rend_total")],
            by = "Entreprise") %>%
  group_by(Region_nom) %>%
  summarise(
    Nb_cies  = n(),
    Vol_moy  = mean(Volatilite, na.rm = TRUE),
    Rend_moy = mean(Rend_total, na.rm = TRUE),
    .groups  = "drop"
  )

# (3) Shapefile France metropolitaine (13 regions, code_insee 2 chiffres)
codes_metro <- c("11", "24", "27", "28", "32", "44",
                 "52", "53", "75", "76", "84", "93", "94")

carte_regions <- sf::read_sf(
  "C:/Users/cocue/Documents/Fac/803/Data/Data/regions-20180101-shp/regions-20180101.shp"
)
carte_metro <- carte_regions %>%
  filter(code_insee %in% codes_metro)

# (4) Jointure shapefile ↔ statistiques
carte_metro <- carte_metro %>%
  left_join(stats_region, by = c("nom" = "Region_nom")) %>%
  mutate(Nb_cies = replace_na(Nb_cies, 0L))

# (5) Centroides pour bulles et labels (uniquement regions avec au moins 1 entreprise)
centroides <- carte_metro %>%
  filter(Nb_cies > 0) %>%
  mutate(
    centroid = sf::st_centroid(geometry),
    Lon = sf::st_coordinates(centroid)[, 1],
    Lat = sf::st_coordinates(centroid)[, 2]
  ) %>%
  sf::st_drop_geometry()

ggplot() +
  geom_sf(data = carte_metro, aes(fill = Nb_cies),
          color = "white", linewidth = 0.4) +
  scale_fill_gradient(low = "#c7e9c0", high = "#00441b",
                      name = "Nombre\nd'entreprises",
                      breaks = c(0, 1, 2, 34),
                      labels = c("0", "1", "2", "34")) +
  geom_point(data = centroides,
             aes(x = Lon, y = Lat, size = Vol_moy),
             color = "firebrick", alpha = 0.75, shape = 16) +
  scale_size(range = c(3, 14), name = "Volatilite\nmoyenne (%)") +
  geom_label_repel(data = centroides,
                   aes(x = Lon, y = Lat,
                       label = paste0(nom, "\n",
                                      Nb_cies,
                                      ifelse(Nb_cies > 1, " entreprises", " entreprise"))),
                   size = 2.8, alpha = 0.88, label.padding = unit(0.2, "lines"),
                   segment.size = 0.3, segment.color = "gray40",
                   min.segment.length = 0) +
  labs(
    title    = "Repartition des sieges sociaux CAC40 par region (France metropolitaine)",
    subtitle = "Couleur = nombre d'entreprises  |  Bulle rouge = volatilite annualisee moyenne (2010-2020)",
    x = NULL, y = NULL
  ) +
  theme_void(base_size = 11) +
  theme(legend.position  = "right",
        plot.title       = element_text(face = "bold", size = 11),
        plot.subtitle    = element_text(size = 8.5, color = "gray40"),
        plot.margin      = margin(10, 10, 10, 10))

ggsave("figures/fig18_carte_regions_cac40.png",
       width = 11, height = 9, dpi = 150)

#---------------------------------------------------------
# Figure 19 - Modeles GARCH(1,1) et EGARCH(1,1) - volatilite conditionnelle
#---------------------------------------------------------

# (1) Specifications des modeles
sel_garch <- c("LVMH", "ArcelorMittal", "Total", "Renault")

spec_garch <- ugarchspec(
  variance.model     = list(model = "sGARCH", garchOrder = c(1, 1)),
  mean.model         = list(armaOrder = c(0, 0), include.mean = TRUE),
  distribution.model = "norm"
)

spec_egarch <- ugarchspec(
  variance.model     = list(model = "eGARCH", garchOrder = c(1, 1)),
  mean.model         = list(armaOrder = c(0, 0), include.mean = TRUE),
  distribution.model = "norm"
)

# (2) Ajustement sur les 4 entreprises selectionnees
fit_garch  <- list()
fit_egarch <- list()
vol_cond   <- data.frame()

for (ent in sel_garch) {
  r <- cac40$Rendement[cac40$Entreprise == ent & !is.na(cac40$Rendement)] / 100
  d <- cac40$Date[cac40$Entreprise == ent & !is.na(cac40$Rendement)]

  fit_garch[[ent]]  <- ugarchfit(spec_garch,  data = r, solver = "hybrid")
  fit_egarch[[ent]] <- ugarchfit(spec_egarch, data = r, solver = "hybrid")

  vol_cond <- rbind(vol_cond, data.frame(
    Date         = d,
    Entreprise   = ent,
    Vol_GARCH    = as.numeric(sigma(fit_garch[[ent]]))  * sqrt(252) * 100,
    Vol_EGARCH   = as.numeric(sigma(fit_egarch[[ent]])) * sqrt(252) * 100,
    Vol_realisee = abs(r) * sqrt(252) * 100,
    stringsAsFactors = FALSE
  ))
}

# Figure 19a — Volatilite conditionnelle dans le temps
vol_long <- vol_cond %>%
  pivot_longer(cols = c(Vol_GARCH, Vol_EGARCH, Vol_realisee),
               names_to = "Modele", values_to = "Volatilite") %>%
  mutate(Modele = recode(Modele,
    Vol_GARCH    = "GARCH(1,1)",
    Vol_EGARCH   = "EGARCH(1,1)",
    Vol_realisee = "Realisee (|r| x sqrt252)"
  ))

ggplot(vol_long, aes(x = Date, y = Volatilite, color = Modele)) +
  geom_line(linewidth = 0.45, alpha = 0.85) +
  scale_color_manual(values = c(
    "GARCH(1,1)"               = "#1f77b4",
    "EGARCH(1,1)"              = "#ff7f0e",
    "Realisee (|r| x sqrt252)" = "gray55"
  )) +
  facet_wrap(~ Entreprise, scales = "free_y", ncol = 2) +
  labs(title    = "Volatilite conditionnelle GARCH(1,1) et EGARCH(1,1)",
       subtitle = "Annualisee (x racine(252)), comparee a la volatilite realisee",
       x = NULL, y = "Volatilite annualisee (%)", color = NULL) +
  theme_bw(base_size = 10) +
  theme(legend.position  = "bottom",
        axis.text.x      = element_text(angle = 45, hjust = 1))

ggsave("figures/fig19a_volatilite_conditionnelle.png",
       width = 12, height = 9, dpi = 150)

# Figure 19b — Courbes d'impact des nouvelles (NIC)
nic_data <- data.frame()

for (ent in sel_garch) {
  nic_g <- newsimpact(fit_garch[[ent]])
  nic_e <- newsimpact(fit_egarch[[ent]])
  nic_data <- rbind(nic_data,
    data.frame(Choc = nic_g$zx, Variance = nic_g$zy,
               Modele = "GARCH(1,1)", Entreprise = ent,
               stringsAsFactors = FALSE),
    data.frame(Choc = nic_e$zx, Variance = nic_e$zy,
               Modele = "EGARCH(1,1)", Entreprise = ent,
               stringsAsFactors = FALSE)
  )
}

ggplot(nic_data, aes(x = Choc, y = Variance, color = Modele)) +
  geom_line(linewidth = 0.9) +
  geom_vline(xintercept = 0, linetype = "dashed",
             color = "gray50", linewidth = 0.5) +
  scale_color_manual(values = c(
    "GARCH(1,1)"  = "#1f77b4",
    "EGARCH(1,1)" = "#ff7f0e"
  )) +
  facet_wrap(~ Entreprise, scales = "free_y", ncol = 2) +
  labs(title    = "Courbes d'impact des nouvelles (NIC) - GARCH vs EGARCH",
       subtitle = "EGARCH : asymetrie — un choc negatif genere plus de variance qu'un choc positif (effet de levier)",
       x = "Choc (innovation normalisee)", y = "Variance conditionnelle", color = NULL) +
  theme_bw(base_size = 10) +
  theme(legend.position = "bottom")

ggsave("figures/fig19b_news_impact_curve.png",
       width = 11, height = 9, dpi = 150)

#---------------------------------------------------------
# Figure 20 - Dendrogramme de clustering hierarchique
#---------------------------------------------------------

# (1) Donnees pour le clustering : 5 variables par entreprise
donnees_cluster <- profil_complet
colnames(donnees_cluster)[3:7] <- c("Rend_total", "Volatilite", "Skewness", "Kurtosis", "DrawdownMax")

mat_scale <- scale(donnees_cluster[, 3:7])
rownames(mat_scale) <- donnees_cluster$Entreprise

# (2) Clustering hierarchique Ward.D2 + coupure en 4 groupes
hc          <- hclust(dist(mat_scale), method = "ward.D2")
clusters_hc <- cutree(hc, k = 4)

# (3) Extraction des donnees du dendrogramme et coloration des feuilles
dend_data   <- dendro_data(hc, type = "rectangle")
labels_clus <- data.frame(
  label   = names(clusters_hc),
  Cluster = factor(paste0("C", clusters_hc))
)
dend_labels <- merge(dend_data$labels, labels_clus, by = "label")

ggplot() +
  geom_segment(data = segment(dend_data),
               aes(x = x, y = y, xend = xend, yend = yend),
               color = "gray40", linewidth = 0.4) +
  geom_text(data = dend_labels,
            aes(x = x, y = -0.5, label = label, color = Cluster),
            hjust = 1, size = 2.5) +
  scale_color_brewer(palette = "Set1") +
  coord_flip() +
  scale_y_reverse(expand = expansion(mult = c(0.35, 0.02))) +
  labs(title    = "Clustering hierarchique des 38 actions CAC40 (Ward.D2)",
       subtitle = "Variables : rendement total, volatilite, skewness, kurtosis, drawdown max  |  k = 4 groupes",
       x = NULL, y = "Distance (inertie Ward)",
       color = "Cluster") +
  theme_bw(base_size = 10) +
  theme(axis.text.y  = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid   = element_blank())

ggsave("figures/fig20_dendrogramme.png",
       width = 10, height = 9, dpi = 150)

#---------------------------------------------------------
# Figure 21 - ACP + kmeans : scatter PC1 / PC2
#---------------------------------------------------------

# (1) Kmeans (k=4) et ACP
set.seed(42)
km  <- kmeans(mat_scale, centers = 4, nstart = 25)
acp <- prcomp(mat_scale)

pct_var <- round(summary(acp)$importance[2, 1:2] * 100, 1)

df_acp <- data.frame(
  Entreprise = rownames(mat_scale),
  PC1        = acp$x[, 1],
  PC2        = acp$x[, 2],
  Cluster    = factor(paste0("C", km$cluster)),
  Secteur    = donnees_cluster$Secteur
)

# (2) Scatter ACP colore par cluster kmeans
ggplot(df_acp, aes(x = PC1, y = PC2, color = Cluster, label = Entreprise)) +
  stat_ellipse(aes(group = Cluster), type = "norm",
               linetype = "dashed", linewidth = 0.5, alpha = 0.6) +
  geom_point(size = 3, alpha = 0.9) +
  geom_text_repel(size = 2.5, max.overlaps = 30,
                  segment.size = 0.25, segment.color = "gray60") +
  scale_color_brewer(palette = "Set1") +
  labs(
    title    = "ACP + kmeans (k=4) : profil statistique des actions CAC40",
    subtitle = "Axes = composantes principales des 5 indicateurs de risque/rendement",
    x        = paste0("PC1 (", pct_var[1], "% de variance)"),
    y        = paste0("PC2 (", pct_var[2], "% de variance)"),
    color    = "Cluster"
  ) +
  theme_bw(base_size = 11)

ggsave("figures/fig21_acp_kmeans.png",
       width = 10, height = 8, dpi = 150)

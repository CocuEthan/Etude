import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import threading

# --- Agents IA (optionnels — dégradation gracieuse si absents) ---
try:
    from agents.court_terme import AgentCourtTerme
    from agents.long_terme import AgentLongTerme
    from agents.dividendes import AgentDividendes
    from data.market import get_court_terme_data, get_long_terme_data, get_dividend_data
    from models.confirmateur import Confirmateur
    _IA_DISPONIBLE = True
except Exception:
    _IA_DISPONIBLE = False

# Nom du fichier de sauvegarde
FICHIER_DONNEES = "mon_portefeuille.json"

# Liste de surveillance (CAC 40 + SBF 120 principaux)
LISTE_MARCHE_PARIS = [
    "AC.PA", "AI.PA", "AIR.PA", "MT.PA", "ATO.PA", "CS.PA", "BNP.PA", "EN.PA", "CAP.PA", "CA.PA", 
    "ACA.PA", "BN.PA", "DSY.PA", "ENGI.PA", "EL.PA", "ERF.PA", "RMS.PA", "KER.PA", "LR.PA", 
    "OR.PA", "MC.PA", "ML.PA", "ORA.PA", "RI.PA", "PUB.PA", "RNO.PA", "SAF.PA", "SGO.PA", 
    "SAN.PA", "SU.PA", "GLE.PA", "STLAM.PA", "STM.PA", "TEP.PA", "HO.PA", "TTE.PA", "URW.PA", 
    "VIE.PA", "DG.PA", "VIV.PA", "WLN.PA", "TFI.PA", "FDR.PA", "FR.PA", "NK.PA", "DIM.PA", 
    "RUI.PA", "SK.PA", "SW.PA", "VLA.PA", "VIRP.PA"
]

class BourseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Station de Trading - Version 12 (Tri & Market Analysis)")
        self.root.geometry("1600x900")

        self.donnees = self.charger_donnees()
        self.market_data_cache = [] 

        # --- Styles ---
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))

        # --- Onglets ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Onglet 1 : Portefeuille
        self.frame_portefeuille = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_portefeuille, text="Portefeuille")
        self.creer_tableau_portefeuille()

        # Onglet 2 : Historique
        self.frame_historique = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_historique, text="Historique Ventes")
        self.creer_tableau_historique()

        # Onglet 3 : ANALYSE (Détail)
        self.frame_analyse = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_analyse, text="Analyse Mes Actions")
        self.creer_interface_analyse()

        # Onglet 4 : EXPLORATEUR MARCHE (Scanner)
        self.frame_market = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_market, text="🌍 Explorateur Marché (Euronext)")
        self.creer_interface_market()

        # --- Boutons Principaux ---
        frame_boutons = tk.Frame(root, bg="#f0f0f0", pady=10)
        frame_boutons.pack(fill="x")

        btn_acheter = tk.Button(frame_boutons, text="➕ ACHETER", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.ouvrir_fenetre_achat)
        btn_acheter.pack(side=tk.LEFT, padx=15)

        btn_vendre = tk.Button(frame_boutons, text="💰 VENDRE", bg="#FF9800", fg="white", font=("Arial", 10, "bold"), command=self.vendre_action)
        btn_vendre.pack(side=tk.LEFT, padx=15)

        btn_suppr = tk.Button(frame_boutons, text="🗑️ SUPPRIMER", bg="#D32F2F", fg="white", font=("Arial", 9), command=self.supprimer_action_erreur)
        btn_suppr.pack(side=tk.LEFT, padx=15)

        btn_maj = tk.Button(frame_boutons, text="🔄 ACTUALISER TOUT", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=self.mettre_a_jour_tout)
        btn_maj.pack(side=tk.RIGHT, padx=20)

        # Initialisation
        self.rafraichir_tableaux()
        self.mettre_a_jour_liste_analyse()

    # ==========================================
    #             TRI COLONNES (CORRIGÉ)
    # ==========================================
    def trier_colonne(self, tree, col, reverse):
        """Trie le tableau en convertissant les chiffres proprement"""
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        def conversion_tri(val):
            s = val[0]
            try:
                # Nettoyage pour conversion numérique
                clean_s = s.replace('€', '').replace('%', '').replace(' ', '').strip()
                # Gestion des cas spécifiques ESG (ex: "15.4 - Faible") -> on garde le chiffre
                if " - " in clean_s:
                    clean_s = clean_s.split(" - ")[0]
                return float(clean_s)
            except:
                return s.lower()

        l.sort(key=conversion_tri, reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        # Réassigne la commande pour le prochain clic (inverse le tri)
        tree.heading(col, command=lambda: self.trier_colonne(tree, col, not reverse))

    # ==========================================
    #            UTILITAIRES TEXTE
    # ==========================================
    def get_esg_text(self, score):
        if score == "N/A" or score is None: return "N/A"
        try:
            s = float(score)
            if s < 10: return f"{s} - Négligeable"
            elif s < 20: return f"{s} - Faible"
            elif s < 30: return f"{s} - Moyen"
            elif s < 40: return f"{s} - Élevé"
            else: return f"{s} - Sévère"
        except: return str(score)

    def get_reco_text(self, key):
        mapping = {
            'strong_buy': "ACHETER FORT", 'buy': "ACHETER",
            'hold': "CONSERVER", 'underperform': "ALLÉGER",
            'sell': "VENDRE", 'none': "-"
        }
        return mapping.get(str(key).lower(), str(key).upper())

    # ==========================================
    #            GESTION DES DONNEES
    # ==========================================
    def charger_donnees(self):
        if os.path.exists(FICHIER_DONNEES):
            try:
                with open(FICHIER_DONNEES, 'r') as f:
                    return json.load(f)
            except: return {"portefeuille": [], "historique": []}
        return {"portefeuille": [], "historique": []}

    def sauvegarder_donnees(self):
        with open(FICHIER_DONNEES, 'w') as f:
            json.dump(self.donnees, f, indent=4)

    def rechercher_ticker_yahoo(self, query, prefer_france=True):
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {"q": query, "quotesCount": 5, "newsCount": 0}
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r = requests.get(url, params=params, headers=headers)
            data = r.json()
            if "quotes" not in data or len(data["quotes"]) == 0: return None, None
            quotes = data["quotes"]
            if prefer_france:
                for q in quotes:
                    if q.get("symbol", "").endswith(".PA"):
                        return q.get("symbol"), q.get("shortname", query)
            return quotes[0].get("symbol"), quotes[0].get("shortname", query)
        except: return None, None

    def calculer_dividendes_cumules(self, symbole, date_achat_str, qte):
        try:
            ticker = yf.Ticker(symbole)
            divs = ticker.dividends
            if divs.empty: return 0.0
            divs.index = divs.index.tz_localize(None)
            date_achat = datetime.strptime(date_achat_str, "%Y-%m-%d")
            return round(divs[divs.index >= date_achat].sum() * qte, 2)
        except: return 0.0

    # ==========================================
    #       ONGLET 1 : PORTEFEUILLE
    # ==========================================
    def creer_tableau_portefeuille(self):
        cols = ("Date", "Nom", "Qté", "Prix Achat", "Actuel", "Frais Achat", "Frais Vente (Est.)", "Gain Action (Net)", "Dividendes", "TOTAL NET")
        self.tree_portefeuille = ttk.Treeview(self.frame_portefeuille, columns=cols, show='headings', height=18)
        wid = [80, 180, 50, 80, 80, 80, 110, 110, 100, 100]
        for c, w in zip(cols, wid):
            self.tree_portefeuille.column(c, width=w, anchor="center")
            # TRI ACTIVÉ
            self.tree_portefeuille.heading(c, text=c, command=lambda _c=c: self.trier_colonne(self.tree_portefeuille, _c, False))
        self.tree_portefeuille.pack(expand=True, fill="both", padx=10, pady=10)

    # ==========================================
    #       ONGLET 2 : HISTORIQUE
    # ==========================================
    def creer_tableau_historique(self):
        self.lbl_total_gains = tk.Label(self.frame_historique, text="Bilan Réalisé: 0.00 €", font=("Arial", 16, "bold"))
        self.lbl_total_gains.pack(pady=10)
        cols = ("Date Vente", "Nom", "Qté", "Achat", "Vente", "Div. Encaissés", "Frais Totaux", "Gain Action", "Gain Total")
        self.tree_historique = ttk.Treeview(self.frame_historique, columns=cols, show='headings')
        for c in cols:
            self.tree_historique.column(c, width=100, anchor="center")
            # TRI ACTIVÉ
            self.tree_historique.heading(c, text=c, command=lambda _c=c: self.trier_colonne(self.tree_historique, _c, False))
        self.tree_historique.pack(expand=True, fill="both", padx=10, pady=10)

    # ==========================================
    #       ONGLET 3 : ANALYSE (Expert)
    # ==========================================
    def creer_interface_analyse(self):
        frame_top = tk.Frame(self.frame_analyse, bg="#e1e1e1", pady=10)
        frame_top.pack(fill="x")
        tk.Label(frame_top, text="Action à analyser :", bg="#e1e1e1").pack(side=tk.LEFT, padx=10)
        self.combo_actions = ttk.Combobox(frame_top, state="readonly", width=30)
        self.combo_actions.pack(side=tk.LEFT, padx=10)
        self.combo_actions.bind("<<ComboboxSelected>>", self.charger_analyse_action)

        paned = tk.PanedWindow(self.frame_analyse, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # GAUCHE
        f_info = tk.LabelFrame(paned, text="Fondamentaux", padx=10, pady=10, width=400)
        paned.add(f_info)
        self.lbl_ana_prix = tk.Label(f_info, text="Prix: --", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_ana_prix.pack(anchor="w", pady=5)
        
        tk.Label(f_info, text="Risque ESG :", font=("Arial", 10, "underline")).pack(anchor="w")
        self.lbl_ana_esg_level = tk.Label(f_info, text="--", font=("Arial", 11, "bold"))
        self.lbl_ana_esg_level.pack(anchor="w")

        tk.Frame(f_info, height=2, bd=1, relief="sunken").pack(fill="x", pady=10)
        tk.Label(f_info, text="Dividendes :", font=("Arial", 10, "underline")).pack(anchor="w")
        self.lbl_ana_div = tk.Label(f_info, text="--")
        self.lbl_ana_div.pack(anchor="w")
        self.lbl_ana_yield = tk.Label(f_info, text="--", fg="green", font=("Arial", 10, "bold"))
        self.lbl_ana_yield.pack(anchor="w")

        tk.Frame(f_info, height=2, bd=1, relief="sunken").pack(fill="x", pady=10)
        tk.Label(f_info, text="Consensus :", font=("Arial", 10, "underline")).pack(anchor="w")
        self.lbl_ana_target = tk.Label(f_info, text="--")
        self.lbl_ana_target.pack(anchor="w")
        self.lbl_ana_pot = tk.Label(f_info, text="--")
        self.lbl_ana_pot.pack(anchor="w")
        self.lbl_ana_reco = tk.Label(f_info, text="--", font=("Arial", 12, "bold"))
        self.lbl_ana_reco.pack(anchor="w", pady=10)

        # DROITE
        f_graph = tk.Frame(paned, bg="white")
        paned.add(f_graph)
        f_p = tk.Frame(f_graph)
        f_p.pack(fill="x")
        for p in ["1d", "5d", "1mo", "6mo", "1y", "5y", "max"]:
            tk.Button(f_p, text=p, command=lambda c=p: self.update_graph_analyse(c)).pack(side=tk.LEFT)

        self.fig_a = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax_a = self.fig_a.add_subplot(111)
        self.canvas_a = FigureCanvasTkAgg(self.fig_a, f_graph)
        self.canvas_a.get_tk_widget().pack(fill="both", expand=True)
        self.current_ana_sym = None

        # --- Section Analyse IA -------------------------------------------
        f_ia = tk.LabelFrame(self.frame_analyse, text="Analyse IA (Gemini + ML)", padx=10, pady=8)
        f_ia.pack(fill="x", padx=10, pady=(0, 8))

        # Stratégie selector
        f_strat = tk.Frame(f_ia)
        f_strat.pack(fill="x")
        tk.Label(f_strat, text="Stratégie :").pack(side=tk.LEFT)
        self.var_agent_type = tk.StringVar(value="court_terme")
        for val, lbl in [("court_terme", "📈 Court Terme"), ("long_terme", "🏦 Long Terme"), ("dividendes", "💰 Dividendes")]:
            tk.Radiobutton(f_strat, text=lbl, variable=self.var_agent_type, value=val).pack(side=tk.LEFT, padx=6)

        self.btn_ia = tk.Button(
            f_ia, text="🤖 Analyser avec IA", bg="#673AB7", fg="white",
            font=("Arial", 10, "bold"), command=self.analyser_action_ia,
            state="normal" if _IA_DISPONIBLE else "disabled",
        )
        self.btn_ia.pack(fill="x", pady=4)

        if not _IA_DISPONIBLE:
            tk.Label(f_ia, text="⚠ modules agents/models non disponibles", fg="red").pack(anchor="w")

        self.lbl_ia_status = tk.Label(f_ia, text="", fg="grey", font=("Arial", 9))
        self.lbl_ia_status.pack(anchor="w")

        # Confirmateur badge
        self.frm_badge = tk.Frame(f_ia, bg="#f0f0f0", relief="groove", bd=1, pady=4)
        self.frm_badge.pack(fill="x", pady=2)
        self.lbl_badge_verdict = tk.Label(self.frm_badge, text="", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.lbl_badge_verdict.pack(side=tk.LEFT, padx=8)
        self.lbl_badge_statut = tk.Label(self.frm_badge, text="", font=("Arial", 10), bg="#f0f0f0")
        self.lbl_badge_statut.pack(side=tk.LEFT, padx=6)
        self.lbl_badge_conf = tk.Label(self.frm_badge, text="", fg="grey", bg="#f0f0f0", font=("Arial", 9))
        self.lbl_badge_conf.pack(side=tk.LEFT)

        # LLM response text box
        f_txt = tk.Frame(f_ia)
        f_txt.pack(fill="both", expand=True)
        sb = tk.Scrollbar(f_txt)
        sb.pack(side=tk.RIGHT, fill="y")
        self.txt_ia = tk.Text(f_txt, height=7, yscrollcommand=sb.set, state="disabled",
                               font=("Courier", 9), wrap="word")
        self.txt_ia.pack(fill="both", expand=True)
        sb.config(command=self.txt_ia.yview)

    def mettre_a_jour_liste_analyse(self):
        liste = [f"{item['symbole']} - {item.get('nom', '')}" for item in self.donnees["portefeuille"]]
        self.combo_actions['values'] = liste
        if liste: self.combo_actions.current(0)

    def charger_analyse_action(self, event=None):
        sel = self.combo_actions.get()
        if not sel: return
        sym = sel.split(" - ")[0]
        self.current_ana_sym = sym
        self.update_graph_analyse("1y")
        try:
            inf = yf.Ticker(sym).info
            p = inf.get('currentPrice', 0)
            dev = inf.get('currency', 'EUR')
            self.lbl_ana_prix.config(text=f"Prix: {p} {dev}")
            
            rate = inf.get('dividendRate', 0)
            yld = (rate/p)*100 if p>0 and rate else 0
            self.lbl_ana_div.config(text=f"Montant: {rate} {dev}")
            self.lbl_ana_yield.config(text=f"Rendement: {yld:.2f}%")

            tgt = inf.get('targetMeanPrice')
            pot = ((tgt-p)/p)*100 if tgt and p else 0
            self.lbl_ana_target.config(text=f"Obj: {tgt} {dev}")
            self.lbl_ana_pot.config(text=f"Potentiel: {pot:+.2f}%", fg="green" if pot>0 else "red")
            
            rk = inf.get('recommendationKey', 'none')
            self.lbl_ana_reco.config(text=f"Avis: {self.get_reco_text(rk)}", fg="purple")

            try:
                tkr = yf.Ticker(sym)
                esg = tkr.sustainability.loc['totalEsg', 'esgScores'] if tkr.sustainability is not None else "N/A"
                txt_esg = self.get_esg_text(esg)
                # Couleur ESG
                col_esg = "grey"
                if "Négligeable" in txt_esg: col_esg = "darkgreen"
                elif "Faible" in txt_esg: col_esg = "green"
                elif "Moyen" in txt_esg: col_esg = "orange"
                elif "Élevé" in txt_esg: col_esg = "red"
                elif "Sévère" in txt_esg: col_esg = "darkred"
                self.lbl_ana_esg_level.config(text=txt_esg, fg=col_esg)
            except: self.lbl_ana_esg_level.config(text="ESG: N/A")
        except Exception as e: print(e)

    def update_graph_analyse(self, p):
        if not self.current_ana_sym: return
        try:
            h = yf.Ticker(self.current_ana_sym).history(period=p)
            self.ax_a.clear()
            self.ax_a.plot(h.index, h['Close'], color='blue')
            self.ax_a.grid(True, alpha=0.5)
            self.fig_a.autofmt_xdate()
            self.canvas_a.draw()
        except: pass

    # ==========================================
    #       ANALYSE IA + CONFIRMATEUR
    # ==========================================
    def analyser_action_ia(self):
        if not self.current_ana_sym:
            messagebox.showwarning("Analyse IA", "Sélectionnez d'abord une action.")
            return
        if not _IA_DISPONIBLE:
            return

        sym = self.current_ana_sym
        agent_type = self.var_agent_type.get()
        role_map = {"court_terme": "Court terme", "long_terme": "Long terme", "dividendes": "Dividendes"}

        self.lbl_ia_status.config(text="Analyse en cours…", fg="blue")
        self.btn_ia.config(state="disabled")
        self._reset_badge()

        def _run():
            try:
                if agent_type == "court_terme":
                    agent = AgentCourtTerme()
                    donnees = get_court_terme_data(sym)
                elif agent_type == "long_terme":
                    agent = AgentLongTerme()
                    donnees = get_long_terme_data(sym)
                else:
                    agent = AgentDividendes()
                    donnees = get_dividend_data(sym)

                nom = donnees.get("nom", sym)
                fake_entry = {"symbole": sym, "nom": nom, "role": role_map[agent_type]}
                llm_response = agent.analyser([fake_entry])

                conf = Confirmateur(agent_type)
                result = conf.evaluer(sym, donnees, llm_response)

                self.root.after(0, lambda: self._afficher_resultat_ia(llm_response, result))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._ia_erreur(err))

        threading.Thread(target=_run, daemon=True).start()

    def _reset_badge(self):
        self.lbl_badge_verdict.config(text="", bg="#f0f0f0")
        self.lbl_badge_statut.config(text="")
        self.lbl_badge_conf.config(text="")
        self.frm_badge.config(bg="#f0f0f0")

    def _afficher_resultat_ia(self, llm_response: str, result: dict):
        self.btn_ia.config(state="normal")

        # LLM text
        self.txt_ia.config(state="normal")
        self.txt_ia.delete("1.0", "end")
        self.txt_ia.insert("end", llm_response)
        self.txt_ia.config(state="disabled")

        # Confirmateur badge
        verdict = result.get("verdict", "?")
        statut = result.get("statut", "")
        conf_val = result.get("model_confiance")

        verdict_colors = {"ACHETER": "#1a7f37", "CONSERVER": "#9a6800", "VENDRE": "#b91c1c"}
        badge_bgs = {"ACHETER": "#d1fae5", "CONSERVER": "#fef9c3", "VENDRE": "#fee2e2"}

        col = verdict_colors.get(verdict, "#333")
        bg = badge_bgs.get(verdict, "#f0f0f0")

        verdict_icons = {"ACHETER": "🟢", "CONSERVER": "🟡", "VENDRE": "🔴"}
        icon = verdict_icons.get(verdict, "⚪")

        self.frm_badge.config(bg=bg)
        self.lbl_badge_verdict.config(text=f"{icon} {verdict}", fg=col, bg=bg)
        self.lbl_badge_statut.config(text=statut, bg=bg)

        conf_txt = ""
        if conf_val is not None:
            conf_txt = f"(confiance ML : {conf_val:.0%})"
        elif not result.get("modele_entraine"):
            conf_txt = "(modèle non entraîné)"
        self.lbl_badge_conf.config(text=conf_txt, bg=bg)

        self.lbl_ia_status.config(text="Analyse terminée.", fg="green")

    def _ia_erreur(self, msg: str):
        self.btn_ia.config(state="normal")
        self.lbl_ia_status.config(text=f"Erreur : {msg[:80]}", fg="red")

    # ==========================================
    #       ONGLET 4 : EXPLORATEUR MARCHE
    # ==========================================
    def creer_interface_market(self):
        frame_top = tk.Frame(self.frame_market, bg="#e1e1e1", pady=10)
        frame_top.pack(fill="x")

        tk.Label(frame_top, text="Secteur :", bg="#e1e1e1").pack(side=tk.LEFT, padx=10)
        self.combo_secteur = ttk.Combobox(frame_top, state="readonly", width=20)
        self.combo_secteur.pack(side=tk.LEFT)
        self.combo_secteur.bind("<<ComboboxSelected>>", self.filtrer_market_table)
        self.combo_secteur['values'] = ["Tous"]

        self.btn_scan = tk.Button(frame_top, text="📡 LANCER SCAN", bg="#673AB7", fg="white", command=self.lancer_thread_scan)
        self.btn_scan.pack(side=tk.LEFT, padx=20)
        self.lbl_status = tk.Label(frame_top, text="Prêt", bg="#e1e1e1", fg="grey")
        self.lbl_status.pack(side=tk.LEFT)

        paned = tk.PanedWindow(self.frame_market, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # TABLEAU
        f_tab = tk.Frame(paned)
        paned.add(f_tab, width=1050)
        
        # Ajout colonnes AVIS et ESG complet
        cols = ("Symbole", "Nom", "Secteur", "Prix", "Obj_3M", "Potentiel", "Rend.", "Avis", "ESG")
        self.tree_market = ttk.Treeview(f_tab, columns=cols, show='headings')
        wid = [70, 150, 110, 70, 70, 80, 70, 90, 120]
        for c, w in zip(cols, wid):
            self.tree_market.column(c, width=w, anchor="center")
            # TRI ACTIVÉ SUR L'EXPLORATEUR AUSSI
            self.tree_market.heading(c, text=c, command=lambda _c=c: self.trier_colonne(self.tree_market, _c, False))
        
        scroll = ttk.Scrollbar(f_tab, orient="vertical", command=self.tree_market.yview)
        self.tree_market.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree_market.pack(side="left", fill="both", expand=True)
        self.tree_market.bind("<<TreeviewSelect>>", self.on_market_select)

        self.tree_market.tag_configure("bon", foreground="green")
        self.tree_market.tag_configure("mauvais", foreground="red")

        # GRAPH
        f_gr = tk.Frame(paned, bg="white")
        paned.add(f_gr)
        f_pm = tk.Frame(f_gr)
        f_pm.pack(fill="x")
        for p in ["1d", "5d", "1mo", "6mo", "1y", "5y", "10y"]:
            tk.Button(f_pm, text=p, font=("Arial", 8), command=lambda c=p: self.update_graph_market(c)).pack(side=tk.LEFT)

        self.fig_m = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax_m = self.fig_m.add_subplot(111)
        self.canvas_m = FigureCanvasTkAgg(self.fig_m, f_gr)
        self.canvas_m.get_tk_widget().pack(fill="both", expand=True)
        self.selected_market_symbol = None

    def lancer_thread_scan(self):
        self.btn_scan.config(state="disabled", text="Scan...")
        self.lbl_status.config(text="Chargement...", fg="blue")
        threading.Thread(target=self.scanner_marche, daemon=True).start()

    def scanner_marche(self):
        data_temp = []
        secteurs = set()
        tot = len(LISTE_MARCHE_PARIS)
        
        for i, sym in enumerate(LISTE_MARCHE_PARIS):
            try:
                self.root.after(0, lambda x=i: self.lbl_status.config(text=f"Scan: {x+1}/{tot} ({sym})"))
                inf = yf.Ticker(sym).info
                nom = inf.get('shortName', sym)
                sec = inf.get('sector', 'Autre')
                secteurs.add(sec)
                px = inf.get('currentPrice', 0)
                tgt = inf.get('targetMeanPrice', 0)
                rate = inf.get('dividendRate', 0)
                pot = ((tgt-px)/px)*100 if tgt and px else 0
                yld = (rate/px)*100 if rate and px else 0
                
                # Récupération Reco
                reco_key = inf.get('recommendationKey', 'none')
                txt_reco = self.get_reco_text(reco_key)

                # Récupération ESG (Peut ralentir, mais nécessaire pour la demande)
                txt_esg = "N/A"
                try:
                    tkr = yf.Ticker(sym)
                    if tkr.sustainability is not None:
                        sc = tkr.sustainability.loc['totalEsg', 'esgScores']
                        txt_esg = self.get_esg_text(sc)
                except: pass
                
                data_temp.append({
                    "Symbole": sym, "Nom": nom, "Secteur": sec,
                    "Prix": round(px, 2), "Obj_3M": round(tgt, 2) if tgt else "-",
                    "Potentiel": round(pot, 2), "Rend.": round(yld, 2), 
                    "Avis": txt_reco, "ESG": txt_esg
                })
            except: pass
            
        self.market_data_cache = data_temp
        self.root.after(0, lambda: self.finaliser_scan(list(secteurs)))

    def finaliser_scan(self, lst_sec):
        self.btn_scan.config(state="normal", text="📡 RE-SCANNER")
        self.lbl_status.config(text="Terminé.", fg="green")
        lst_sec.sort()
        self.combo_secteur['values'] = ["Tous"] + lst_sec
        self.combo_secteur.current(0)
        self.afficher_market_data(self.market_data_cache)

    def afficher_market_data(self, data):
        for i in self.tree_market.get_children(): self.tree_market.delete(i)
        for row in data:
            tag = "neutre"
            if row["Potentiel"] > 10: tag = "bon"
            elif row["Potentiel"] < 0: tag = "mauvais"
            self.tree_market.insert("", "end", values=(
                row["Symbole"], row["Nom"], row["Secteur"],
                f"{row['Prix']} €", f"{row['Obj_3M']} €",
                f"{row['Potentiel']}%", f"{row['Rend.']}%", 
                row["Avis"], row["ESG"]
            ), tags=(tag,))

    def filtrer_market_table(self, e):
        ch = self.combo_secteur.get()
        d = self.market_data_cache if ch == "Tous" else [x for x in self.market_data_cache if x["Secteur"] == ch]
        self.afficher_market_data(d)

    def on_market_select(self, e):
        sel = self.tree_market.selection()
        if not sel: return
        self.selected_market_symbol = self.tree_market.item(sel)['values'][0]
        self.update_graph_market("1y")

    def update_graph_market(self, p):
        if not self.selected_market_symbol: return
        try:
            h = yf.Ticker(self.selected_market_symbol).history(period=p)
            self.ax_m.clear()
            self.ax_m.plot(h.index, h['Close'], color='#673AB7')
            self.fig_m.autofmt_xdate()
            self.canvas_m.draw()
        except: pass

    # ==========================================
    #            ACTIONS GLOBALES
    # ==========================================
    def rafraichir_tableaux(self):
        for i in self.tree_portefeuille.get_children(): self.tree_portefeuille.delete(i)
        for item in self.donnees["portefeuille"]:
            qte = item["qte"]
            p_ach = item["prix_achat"]
            p_cur = item.get("dernier_prix", p_ach)
            f_type = item.get("type_frais", "euro")
            f_taux = item.get("taux_frais", 0.0)
            f_vente_est = (qte * p_cur) * (f_taux / 100) if f_type == "pourcent" else f_taux
            cout_total = (qte * p_ach) + item["frais_achat"]
            net_vente = (qte * p_cur) - f_vente_est
            gain_act = net_vente - cout_total
            gain_div = item.get("dividendes_gagnes", 0.0)
            
            self.tree_portefeuille.insert("", "end", values=(
                item.get("date_achat", "?"), item.get("nom", item["symbole"]), qte,
                f"{p_ach} €", f"{p_cur} €", f"-{item['frais_achat']} €",
                f"-{round(f_vente_est, 2)} €", f"{gain_act:.2f} €",
                f"+{gain_div:.2f} €", f"{gain_act+gain_div:.2f} €"
            ))

        for i in self.tree_historique.get_children(): self.tree_historique.delete(i)
        tot = 0
        for item in self.donnees["historique"]:
            tot += item["gain_total"]
            self.tree_historique.insert("", "end", values=(
                item["date_vente"], item["nom"], item["qte"], f"{item['prix_achat']} €",
                f"{item['prix_vente']} €", f"+{item.get('dividendes_encaisses', 0):.2f}",
                f"-{item['frais_total']:.2f}", f"{item['gain_action_net']:.2f} €",
                f"{item['gain_total']:.2f} €"
            ))
        c = "green" if tot >= 0 else "red"
        self.lbl_total_gains.config(text=f"Bilan Réalisé Net: {tot:.2f} €", fg=c)

    def mettre_a_jour_tout(self):
        messagebox.showinfo("Mise à jour", "Actualisation des données en cours...")
        for item in self.donnees["portefeuille"]:
            try:
                tkr = yf.Ticker(item["symbole"])
                h = tkr.history(period="1d")
                if not h.empty: item["dernier_prix"] = round(h['Close'].iloc[-1], 2)
                item["dividendes_gagnes"] = self.calculer_dividendes_cumules(item["symbole"], item["date_achat"], item["qte"])
            except: pass
        self.sauvegarder_donnees()
        self.rafraichir_tableaux()
        self.mettre_a_jour_liste_analyse()
        messagebox.showinfo("OK", "Mise à jour terminée.")

    def supprimer_action_erreur(self):
        sel = self.tree_portefeuille.selection()
        if sel and messagebox.askyesno("Supprimer", "Voulez-vous supprimer cette ligne définitivement ?"):
            val = self.tree_portefeuille.item(sel)['values']
            for i, item in enumerate(self.donnees["portefeuille"]):
                if item.get("nom", item["symbole"]) == val[1] and str(item["prix_achat"]) in str(val[3]):
                    del self.donnees["portefeuille"][i]
                    break
            self.sauvegarder_donnees()
            self.rafraichir_tableaux()
            self.mettre_a_jour_liste_analyse()

    def vendre_action(self):
        sel = self.tree_portefeuille.selection()
        if not sel: return
        val = self.tree_portefeuille.item(sel)['values']
        idx = -1
        for i, item in enumerate(self.donnees["portefeuille"]):
            if item.get("nom", item["symbole"]) == val[1] and str(item["prix_achat"]) in str(val[3]):
                idx = i; break
        if idx == -1: return
        act = self.donnees["portefeuille"][idx]

        pv = simpledialog.askfloat("Vente", "Prix vente unitaire:")
        if not pv: return
        mt_v = act["qte"] * pv
        fd = (mt_v * (act["taux_frais"]/100)) if act.get("type_frais") == "pourcent" else act.get("taux_frais", 0)
        fv = simpledialog.askfloat("Frais", "Frais Vente Réels:", initialvalue=round(fd, 2))
        if fv is None: return

        cout = (act["qte"] * act["prix_achat"]) + act["frais_achat"]
        net_v = (act["qte"] * pv) - fv
        g_act = net_v - cout
        g_div = act.get("dividendes_gagnes", 0.0)
        
        self.donnees["historique"].append({
            "date_vente": datetime.now().strftime("%Y-%m-%d"),
            "nom": act["nom"], "qte": act["qte"], "prix_achat": act["prix_achat"],
            "prix_vente": pv, "dividendes_encaisses": g_div,
            "frais_total": round(act["frais_achat"]+fv, 2),
            "gain_action_net": round(g_act, 2), "gain_total": round(g_act+g_div, 2)
        })
        del self.donnees["portefeuille"][idx]
        self.sauvegarder_donnees()
        self.rafraichir_tableaux()
        self.mettre_a_jour_liste_analyse()
        messagebox.showinfo("Bilan", f"Gain Total: {round(g_act+g_div, 2)} €")

    def ouvrir_fenetre_achat(self):
        fen = tk.Toplevel(self.root)
        fen.title("Nouvel Achat")
        fen.geometry("450x750")

        var_rech = tk.StringVar()
        var_fr = tk.BooleanVar(value=True)
        var_sym = tk.StringVar()
        var_nom = tk.StringVar(value="...")
        var_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        var_px_info = tk.StringVar(value="...")
        var_qte = tk.IntVar(value=1)
        var_px_u = tk.DoubleVar(value=0.0)
        var_f_type = tk.StringVar(value="pourcent")
        var_f_val = tk.DoubleVar(value=0.5)

        # 1. RECHERCHE
        f_rech = tk.LabelFrame(fen, text="1. Recherche (Nom ou Ticker)", padx=10, pady=10)
        f_rech.pack(fill="x", padx=10, pady=5)
        tk.Entry(f_rech, textvariable=var_rech).pack(fill="x")
        tk.Checkbutton(f_rech, text="Priorité France (.PA)", variable=var_fr).pack(anchor="w")

        def lancer_recherche():
            q = var_rech.get().strip()
            if not q: return
            var_nom.set("Recherche...")
            fen.update()
            s, n = self.rechercher_ticker_yahoo(q, var_fr.get())
            if s:
                var_sym.set(s)
                var_nom.set(n)
                try:
                    inf = yf.Ticker(s).info
                    p = inf.get('currentPrice', 0)
                    var_px_info.set(f"{p} {inf.get('currency', 'EUR')}")
                    var_px_u.set(p)
                except: var_px_info.set("Prix ?")
            else:
                var_nom.set("Introuvable")
                var_sym.set("")

        tk.Button(f_rech, text="🔍 CHERCHER", bg="#2196F3", fg="white", command=lancer_recherche).pack(pady=5, fill="x")
        tk.Label(f_rech, text="Résultat :").pack(anchor="w")
        tk.Entry(f_rech, textvariable=var_sym, state="readonly", fg="blue", font="bold").pack(fill="x")
        tk.Label(f_rech, textvariable=var_nom, fg="green").pack()
        tk.Label(f_rech, textvariable=var_px_info).pack()

        # 2. DETAILS
        f_det = tk.LabelFrame(fen, text="2. Détails", padx=10, pady=10)
        f_det.pack(fill="x", padx=10)
        tk.Label(f_det, text="Date:").pack(anchor="w")
        tk.Entry(f_det, textvariable=var_date).pack(fill="x")
        tk.Label(f_det, text="Quantité:").pack(anchor="w")
        tk.Entry(f_det, textvariable=var_qte).pack(fill="x")
        tk.Label(f_det, text="Prix Unitaire:").pack(anchor="w")
        tk.Entry(f_det, textvariable=var_px_u).pack(fill="x")

        # 3. FRAIS
        f_fr = tk.LabelFrame(fen, text="3. Frais", padx=10, pady=10)
        f_fr.pack(fill="x", padx=10)
        tk.Radiobutton(f_fr, text="%", variable=var_f_type, value="pourcent").pack(anchor="w")
        tk.Radiobutton(f_fr, text="€", variable=var_f_type, value="euro").pack(anchor="w")
        tk.Entry(f_fr, textvariable=var_f_val).pack(fill="x")

        def valider():
            try:
                if not var_sym.get(): return
                q = var_qte.get()
                p = var_px_u.get()
                ft = var_f_type.get()
                fv = var_f_val.get()
                f_paye = (q*p)*(fv/100) if ft == "pourcent" else fv
                self.donnees["portefeuille"].append({
                    "symbole": var_sym.get(), "nom": var_nom.get(),
                    "date_achat": var_date.get(), "qte": q, "prix_achat": p,
                    "frais_achat": round(f_paye, 2), "type_frais": ft, "taux_frais": fv,
                    "dernier_prix": p, "dividendes_gagnes": 0.0
                })
                self.sauvegarder_donnees()
                self.rafraichir_tableaux()
                self.mettre_a_jour_liste_analyse()
                fen.destroy()
            except: messagebox.showerror("Erreur", "Données invalides")

        tk.Button(fen, text="VALIDER ACHAT", bg="green", fg="white", font="bold", command=valider).pack(pady=10, fill="x")

if __name__ == "__main__":
    root = tk.Tk()
    app = BourseApp(root)
    root.mainloop()
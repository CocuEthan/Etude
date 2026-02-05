import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_csv("energy_consumption.csv")
print(data.head())
print(data.info())
print(data.describe())


# Tracer l'histogramme de la consommation d'énergie par heure
plt.figure(figsize=(10, 6))

# Barre pour la consommation électrique
plt.bar(data['Heure'], data['Consommation_Electrique'], color='skyblue', label='Électrique')

# Barre pour la consommation de gaz
plt.bar(data['Heure'], data['Consommation_Gaz'], color='lightgreen', label='Gaz', alpha=0.5)

plt.xlabel('Heure')
plt.ylabel("Consommation d'énergie (moyenne)")
plt.title("Histogramme de la consommation d'énergie par heure")
plt.xticks(data['Heure'])
plt.legend()
plt.grid(True)
plt.show()


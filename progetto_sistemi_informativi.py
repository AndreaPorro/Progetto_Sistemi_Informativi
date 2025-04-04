#Importare tutte le librerie utili ai fini del progetto
import pandas as pd
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import streamlit as st

#Caricare il dataset per l'analisi
file_path = '/Users/carlo_air_2021/Desktop/Real estate valuation data set.xlsx'
df = pd.read_excel(file_path)
df.head()

#EDA - in questa parte cerchiamo di comprendere meglio il dataset che abbiamo in studio prima di procedere con la creazione dei modelli
df.size

df.info()

df.describe()

if df.isnull().any().sum() > 0:
    missing_vars = df.columns[df.isnull().any()].tolist()
    print(f"Le variabili con valori mancanti sono {missing_vars}")
else:
    print("Non ci sono variabili con valori mancanti")

# Procedo a dividere il dataset in Y per la variabile target e poi X1 per la latitudine e longitudine usata nel primo
# modello e invece "house age", "distance to the nearest MRT station" e "number of convenience store" per il modello 2
Y = df["Y house price of unit area"] # Variabile target
X1 = df[["X5 latitude", "X6 longitude"]]  # Variabili per il primo modello
X2 = df[["X2 house age", "X3 distance to the nearest MRT station", "X4 number of convenience stores"]]  # Variabili per il secondo modello

# Procedo tramite il train-test a dividere il dataset utilizzando
# un 80% per il train e un 20% per il test
X1_train, X1_test, Y_train, Y_test = train_test_split(X1, Y, test_size=0.2, random_state=42)
X2_train, X2_test, _, _ = train_test_split(X2, Y, test_size=0.2, random_state=42)

# ------- Modello 1 -------

# Creiamo una griglia nella quale stabiliamo gli iperparametri da calcolare
# per il nostro random forest e proseguiamo con l'utilizzo di un grid search
# per la stima dei migliori iperparametri. Il cv sarà pari a 5 e la metrica
# che ricerchiamo è r^2
param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}
grid_search_1 = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=5, scoring='r2')
grid_search_1.fit(X1_train, Y_train)
modello_1 = grid_search_1.best_estimator_
best_params_1 = grid_search_1.best_params_

y_pred_1 = modello_1.predict(X1_test)
mae_1 = mean_absolute_error(Y_test, y_pred_1)
r2_1 = r2_score(Y_test, y_pred_1)
mse_1 = mean_squared_error(Y_test, y_pred_1)
print(f"Modello_1 - MAE: {mae_1:.2f}, R2 Score: {r2_1:.2f}, MSE: {mse_1:.2f}")
print(f"Best Parameters for Modello_1: {best_params_1}")

# Si ottiene che il miglior modello ha:
# - Max_depth: none
# - Min_samples_split: 10
# - n_estimators: 100
# Procedo a salvare il modello

with open("Modello_1.pkl", "wb") as f:
    pickle.dump(modello_1, f)

# ------- Modello 2 -------
# Procedo a fare lo stesso anche per il modello 2
grid_search_2 = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=5, scoring='r2')
grid_search_2.fit(X2_train, Y_train)
modello_2 = grid_search_2.best_estimator_
best_params_2 = grid_search_2.best_params_

y_pred_2 = modello_2.predict(X2_test)
mae_2 = mean_absolute_error(Y_test, y_pred_2)
r2_2 = r2_score(Y_test, y_pred_2)
mse_2 = mean_squared_error(Y_test, y_pred_2)
print(f"Modello_2 - MAE: {mae_2:.2f}, R2 Score: {r2_2:.2f}, MSE: {mse_2:.2f}")
print(f"Best Parameters for Modello_2: {best_params_2}")

# In questo caso si è ottenuto:
# - Max_depth: 10
# - Min_samples_split: 5
# - n_estimators: 100
# Procedo anche sta volta a salvare il nostro modello

with open("Modello_2.pkl", "wb") as f:
    pickle.dump(modello_2, f)

# ------- Streamlit Web App -------
st.title("Real Estate Price Prediction")

# Carichiamo i modelli salvati precedentemente.
with open("Modello_1.pkl", "rb") as f:
    modello_1 = pickle.load(f)
with open("Modello_2.pkl", "rb") as f:
    modello_2 = pickle.load(f)

# Otteniamo per tutte le variabili il min e il max (ovvero il range dei nostri valori)
feature_ranges = {
    "latitude": (df["X5 latitude"].min(), df["X5 latitude"].max()),
    "longitude": (df["X6 longitude"].min(), df["X6 longitude"].max()),
    "house_age": (df["X2 house age"].min(), df["X2 house age"].max()),
    "distance": (df["X3 distance to the nearest MRT station"].min(), df["X3 distance to the nearest MRT station"].max()),
    "stores": (df["X4 number of convenience stores"].min(), df["X4 number of convenience stores"].max())
}


model_choice = st.radio("Selezionare un modello:", ["Modello_1 (Latitudine & Longitudine)", "Modello_2 (Età Casa, Distanza, Negozi)"])

if model_choice == "Modello_1 (Latitudine & Longitudine)":
    lat = st.number_input("Inserire la Latitudine:", min_value=feature_ranges["latitude"][0], max_value=feature_ranges["latitude"][1])
    lon = st.number_input("Inserire la Longitudine:", min_value=feature_ranges["longitude"][0], max_value=feature_ranges["longitude"][1])

    if st.button("Prezzo Predetto"):
        prediction = modello_1.predict(np.array([[lat, lon]]))[0]
        st.write(f"Prezzo stimato: {int(prediction)} per unità d'area")

elif model_choice == "Modello_2 (Età Casa, Distanza, Negozi)":
    age = st.number_input("Inserire l'età della Casa:", min_value=feature_ranges["house_age"][0], max_value=feature_ranges["house_age"][1])
    distance = st.number_input("Inserire la Distanza dalla MRT:", min_value=feature_ranges["distance"][0], max_value=feature_ranges["distance"][1])
    stores = st.number_input("Inserire il numero di Negozi di alimentari:", min_value=feature_ranges["stores"][0], max_value=feature_ranges["stores"][1])

    if st.button("Prezzo Predetto"):
        prediction = modello_2.predict(np.array([[age, distance, stores]]))[0]
        st.write(f"Prezzo stimato: {int(prediction)} per unità d'area")

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import pickle
from keras.models import save_model
import sys
sys.stdout.reconfigure(encoding='utf-8')
# Load the initial dataset for training
def load_data(csv_filename):
    df = pd.read_csv(csv_filename)
    X = df.iloc[:, :12].values
    y = df.iloc[:, 12:].values  # Assuming y represents green timings
    return X, y

base_path = 'C:/Users/kusha/Downloads/Traffix-Team-34-Capstone-Project-2025/training/manual'
csv_filename = f'{base_path}/inputs_and_green_timings.csv'
X, y = load_data(csv_filename)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Impute NaN values in y_train and y_test
imputer = SimpleImputer(strategy='mean')
y_train = imputer.fit_transform(y_train)
y_test = imputer.transform(y_test)

# Train SVM models
models = [SVR(kernel='rbf') for _ in range(y_train.shape[1])]
svm_outputs_train = []

for i in range(y_train.shape[1]):
    models[i].fit(X_train, y_train[:, i])
    svm_outputs_train.append(models[i].predict(X_train))

svm_outputs_train = np.array(svm_outputs_train).T

# Prepare LSTM input (reshape for sequential data)
X_train_lstm = np.reshape(svm_outputs_train, (svm_outputs_train.shape[0], 1, svm_outputs_train.shape[1]))

# Define and train the LSTM model
lstm_model = Sequential()
lstm_model.add(LSTM(128, return_sequences=True, input_shape=(X_train_lstm.shape[1], X_train_lstm.shape[2])))
lstm_model.add(Dropout(0.2))
lstm_model.add(LSTM(64))
lstm_model.add(Dense(y_train.shape[1]))  # Output layer
lstm_model.compile(optimizer=Adam(learning_rate=0.0005), loss='mean_squared_error')

lstm_model.fit(X_train_lstm, y_train, epochs=100, batch_size=16, verbose=1)

# Save the models, scaler, and imputer
with open(f'{base_path}/models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open(f'{base_path}/models/imputer.pkl', 'wb') as f:
    pickle.dump(imputer, f)

with open(f'{base_path}/models/svm_models.pkl', 'wb') as f:
    pickle.dump(models, f)

save_model(lstm_model, f'{base_path}/models/lstm_model.h5')

print("Models and preprocessors saved successfully.")

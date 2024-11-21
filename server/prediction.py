import numpy as np
import pandas as pd
import pickle
from keras.models import load_model
import logging
import os
import tensorflow as tf

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all logs except errors
os.environ['TF_ENABLE_OPEDNN_OPTS'] = '1'  # Enable CPU optimizations

# Configure logging to file
log_filename = 'logs/predictions.log'
logging.basicConfig(
    filename=log_filename,  # Log to a file
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

# Set TensorFlow logger to capture logs
tf_logger = tf.get_logger()
tf_logger.setLevel(logging.FATAL)  # Suppress all but fatal errors

# Load saved models and preprocessors
with open('models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('models/imputer.pkl', 'rb') as f:
    imputer = pickle.load(f)

with open('models/svm_models.pkl', 'rb') as f:
    models = pickle.load(f)

lstm_model = load_model('models/lstm_model.h5')

# Load and preprocess new data
def load_new_data(csv_filename):
    df = pd.read_csv(csv_filename)
    X_new = df.iloc[:, :12].values  # Assuming the same feature structure
    return X_new

# Directory containing the input CSV files
input_folder = 'temp/density/'
# List all CSV files in the input folder
csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# Process each CSV file
for idx, csv_file in enumerate(csv_files, start=1):  # Start counter at 1
    csv_path = os.path.join(input_folder, csv_file)
    try:
        # Load new data for prediction
        X_new = load_new_data(csv_path)

        # Preprocess the new data
        X_new_scaled = scaler.transform(X_new)

        # Generate intermediate output using trained SVM models
        svm_outputs_new = []
        for model in models:
            svm_outputs_new.append(model.predict(X_new_scaled))

        svm_outputs_new = np.array(svm_outputs_new).T

        # Reshape for LSTM input
        X_new_lstm = np.reshape(svm_outputs_new, (svm_outputs_new.shape[0], 1, svm_outputs_new.shape[1]))

        # Make predictions with the LSTM model
        y_pred_new = lstm_model.predict(X_new_lstm)

        # Convert predictions to integers
        y_pred_new_int = np.round(y_pred_new).astype(int)

        # Define output filename in the desired format
        output_text_filename = f'temp/timings/timings_client{idx}.txt'

        # Store predictions in a text file
        with open(output_text_filename, 'w') as f:
            for prediction in y_pred_new_int:
                f.write(f"{list(prediction)}\n")

        logger.info(f"Predictions saved to {output_text_filename}")

    except Exception as e:
        logger.error(f"Failed to process {csv_path}: {e}")

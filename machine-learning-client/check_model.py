from tensorflow.keras.models import load_model

# Load your trained model
model = load_model("model.h5")

# Print the summary of the model to the console
model.summary()

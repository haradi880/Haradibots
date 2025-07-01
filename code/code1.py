import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import random

# Load intents from JSON file
def load_intents(filename):
    with open(filename, 'r') as file:
        intents = json.load(file)
    return intents

# Function to create and train the chatbot model
def create_chatbot_model(intents):
    # Extract intent patterns and corresponding tags
    patterns = []
    tags = []
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            patterns.append(pattern)
            tags.append(intent['tag'])

    # Tokenize input data
    tokenizer = Tokenizer(oov_token="<OOV>")
    tokenizer.fit_on_texts(patterns)
    word_index = tokenizer.word_index

    # Pad sequences to ensure uniform input size
    sequences = tokenizer.texts_to_sequences(patterns)
    padded_sequences = pad_sequences(sequences, padding='post')

    # Encode tags using LabelEncoder
    label_encoder = LabelEncoder()
    encoded_tags = label_encoder.fit_transform(tags)

    # Define model architecture
    model = Sequential([
        Embedding(len(word_index) + 1, 16, input_length=max_len),
        GlobalAveragePooling1D(),
        Dense(16, activation='relu'),
        Dense(len(set(tags)), activation='softmax')
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Train the model
    model.fit(padded_sequences, np.array(encoded_tags), epochs=100, verbose=1)
    return model, tokenizer, label_encoder

# Function to generate a response
def generate_response(model, tokenizer, label_encoder, intents, user_input):  # Add 'intents' as an argument
    sequence = tokenizer.texts_to_sequences([user_input])
    padded_sequence = pad_sequences(sequence, padding='post', maxlen=max_len)
    prediction = model.predict(padded_sequence)[0]
    predicted_tag_index = np.argmax(prediction)
    predicted_tag = label_encoder.inverse_transform([predicted_tag_index])[0]
    for intent in intents['intents']:
        if intent['tag'] == predicted_tag:
            responses = intent['responses']
            return random.choice(responses)

# Main function to run the chatbot
def main():
    # Load intents from JSON file
    intents = load_intents('intents.json')

    # Create and train the chatbot model
    model, tokenizer, label_encoder = create_chatbot_model(intents)

    print("ChatBot: Hello! How can I assist you today?")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "bye":
            print("ChatBot: Goodbye!")
            break
        else:
            response = generate_response(model, tokenizer, label_encoder, intents, user_input)  # Pass 'intents' as an argument
            print("ChatBot:", response)

# Set maximum sequence length
max_len = 20

# Run the chatbot
if __name__ == "__main__":
    main()
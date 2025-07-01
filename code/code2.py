# Step 1: Import Libraries
import numpy as np
import pandas as pd
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping

# Step 2: Load Dataset
df = pd.read_csv('combined_qna.csv')

# Step 3: Preprocess Dataset
df['Answer'] = '<start> ' + df['Answer'] + ' <end>'

input_texts = df['Question'].values
target_texts = df['Answer'].values

tokenizer = Tokenizer(filters='')
tokenizer.fit_on_texts(np.concatenate((input_texts, target_texts)))

input_sequences = tokenizer.texts_to_sequences(input_texts)
target_sequences = tokenizer.texts_to_sequences(target_texts)

max_encoder_seq_length = max(len(seq) for seq in input_sequences)
max_decoder_seq_length = max(len(seq) for seq in target_sequences)
vocab_size = len(tokenizer.word_index) + 1

encoder_input_data = pad_sequences(input_sequences, maxlen=max_encoder_seq_length, padding='post')
decoder_input_data = pad_sequences(target_sequences, maxlen=max_decoder_seq_length, padding='post')

decoder_target_data = np.zeros((len(input_texts), max_decoder_seq_length, vocab_size), dtype='float32')

for i, seq in enumerate(target_sequences):
    for t, word_index in enumerate(seq):
        if t > 0:
            decoder_target_data[i, t - 1, word_index] = 1.0

# Step 4: Build Seq2Seq Model
latent_dim = 256

# Encoder
encoder_inputs = Input(shape=(None,))
enc_emb = Embedding(vocab_size, latent_dim)(encoder_inputs)
encoder_lstm, state_h, state_c = LSTM(latent_dim, return_state=True)(enc_emb)
encoder_states = [state_h, state_c]

# Decoder
decoder_inputs = Input(shape=(None,))
dec_emb = Embedding(vocab_size, latent_dim)(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(dec_emb, initial_state=encoder_states)
decoder_dense = Dense(vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Step 5: Train Model
early_stop = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)

model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
          batch_size=4, epochs=200, callbacks=[early_stop])

# Step 6: Inference Models
encoder_model = Model(encoder_inputs, encoder_states)

decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

dec_emb2 = Embedding(vocab_size, latent_dim)(decoder_inputs)
decoder_outputs2, state_h2, state_c2 = decoder_lstm(dec_emb2, initial_state=decoder_states_inputs)
decoder_states2 = [state_h2, state_c2]
decoder_outputs2 = decoder_dense(decoder_outputs2)

decoder_model = Model([decoder_inputs] + decoder_states_inputs, [decoder_outputs2] + decoder_states2)

# Step 7: Top-k Sampling Decoder
def top_k_sampling_decoder(input_seq, k=5, max_length=20):
    states_value = encoder_model.predict(input_seq)
    reverse_word_index = dict((index, word) for word, index in tokenizer.word_index.items())

    target_seq = np.zeros((1, 1))
    target_seq[0, 0] = tokenizer.word_index['<start>']

    stop_condition = False
    decoded_sentence = []

    while not stop_condition:
        output_tokens, h, c = decoder_model.predict([target_seq] + states_value)

        logits = output_tokens[0, -1, :]
        probs = np.exp(logits) / np.sum(np.exp(logits))

        top_k_indices = probs.argsort()[-k:][::-1]
        top_k_probs = probs[top_k_indices]
        top_k_probs /= np.sum(top_k_probs)

        sampled_index = np.random.choice(top_k_indices, p=top_k_probs)
        sampled_word = reverse_word_index.get(sampled_index, '')

        if (sampled_word == '<end>' or len(decoded_sentence) >= max_length):
            stop_condition = True
        else:
            decoded_sentence.append(sampled_word)

            target_seq = np.zeros((1, 1))
            target_seq[0, 0] = sampled_index

            states_value = [h, c]

    return ' '.join(decoded_sentence)

# Step 8: Chat Loop
print("\nChatbot is ready! Type 'bye' to exit.\n")

while True:
    input_text = input("You: ")
    if input_text.lower() == 'bye':
        print("Bot: Chal, milte hain phir!")
        break

    input_seq = tokenizer.texts_to_sequences([input_text])
    input_seq = pad_sequences(input_seq, maxlen=max_encoder_seq_length, padding='post')

    response = top_k_sampling_decoder(input_seq)
    print("Bot:", response)

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

def train():
    DATA_PATH = 'data'
    actions = sorted([f for f in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, f))])
    
    X, y = [], []
    for label, action in enumerate(actions):
        action_path = os.path.join(DATA_PATH, action)
        files = [f for f in os.listdir(action_path) if f.endswith('.npy')]
        for file in files:
            res = np.load(os.path.join(action_path, file))
            X.append(res)
            y.append(label)

    if not X: return print("No data found!")

    X = np.array(X)
    y = tf.keras.utils.to_categorical(y).astype(int)

    model = models.Sequential([
        layers.Input(shape=(63,)),
        layers.Dense(128, activation='relu'),
        layers.Dense(64, activation='relu'),
        layers.Dense(len(actions), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X, y, epochs=50, batch_size=32, verbose=1)
    model.save('gesture_model.h5')
    print("AI Retrained successfully!")

if __name__ == "__main__":
    train()
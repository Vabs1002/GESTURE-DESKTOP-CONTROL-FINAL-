import cv2
import mediapipe as mp
import numpy as np
import os
from tensorflow.keras.models import load_model

class GestureEngine:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        
        # Memory variables for smoothing
        self.prev_x, self.prev_y = 0, 0
        self.smooth = 0.2 
        
        # Load the "Brain"
        self.model = None
        self.actions = []
        if os.path.exists('gesture_model.h5'):
            self.model = load_model('gesture_model.h5')
            # Dynamically load action labels based on folders currently in 'data'
            if os.path.exists('data'):
                self.actions = sorted([f for f in os.listdir('data') if os.path.isdir(os.path.join('data', f))])

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        detected_action = None
        landmarks_data = None
        
        if res.multi_hand_landmarks:
            for hl in res.multi_hand_landmarks:
                # Visual feedback on the webcam feed
                self.mp_drawing.draw_landmarks(frame, hl, self.mp_hands.HAND_CONNECTIONS)
                
                # Extract 21 points (x,y,z)
                landmarks_data = [v for lm in hl.landmark for v in (lm.x, lm.y, lm.z)]
                
                if self.model and self.actions:
                    pred = self.model.predict(np.expand_dims(landmarks_data, axis=0), verbose=0)
                    confidence = np.max(pred)
                    
                    if confidence > 0.85:
                        detected_action = self.actions[np.argmax(pred)]
        
        return frame, res, detected_action, landmarks_data
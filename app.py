import cv2, os, shutil, numpy as np, subprocess
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from gesture_engine import GestureEngine
from actions_handler import ActionsHandler
from tensorflow.keras.models import load_model

app = Flask(__name__)
# Robust CORS: Explicitly allowing the common React port
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Initialize components
engine = GestureEngine()
handler = ActionsHandler()

recording_config = {"active": False, "gesture": "", "count": 0}

# 1. ADDED: The missing Init Route that React calls
@app.route('/init_folders')
def init_folders():
    actions = [
        "idle", "cursor_movement", "pinch_click", "screenshot", 
        "vol_up", "vol_down", "play_pause", "scroll_up", "scroll_down",
        "close_tab", "change_tabs", "brightness_up", "brightness_down"
    ]
    os.makedirs('data', exist_ok=True)
    for action in actions:
        os.makedirs(os.path.join('data', action), exist_ok=True)
    return jsonify({"status": "Success", "message": "All 12 folders created!"})

def reload_ai_brain():
    global engine
    print("🔄 Hot-Reloading AI Brain...")
    if os.path.exists('gesture_model.h5'):
        try:
            engine.model = load_model('gesture_model.h5')
            if os.path.exists('data'):
                engine.actions = sorted([f for f in os.listdir('data') if os.path.isdir(os.path.join('data', f))])
            print(f"✅ AI Brain updated! Actions recognized: {engine.actions}")
        except Exception as e:
            print(f"❌ Error loading new model: {e}")

@app.route('/video_feed')
def video_feed():
    def gen():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️ Camera not found.")
            return

        while True:
            success, frame = cap.read()
            if not success: break
            
            frame = cv2.flip(frame, 1)
            processed, res, action_detected, lms = engine.process_frame(frame)
            
            if res and res.multi_hand_landmarks:
                if recording_config["active"]:
                    path = os.path.join('data', recording_config["gesture"])
                    os.makedirs(path, exist_ok=True)
                    np.save(os.path.join(path, f"{len(os.listdir(path))}.npy"), np.array(lms))
                    recording_config["count"] += 1
                    if recording_config["count"] >= 300: 
                        recording_config["active"] = False
                
                elif action_detected:
                    if action_detected in ["cursor_movement", "idle"]:
                        handler.move_mouse(res.multi_hand_landmarks[0])
                    handler.execute(action_detected)

            _, buffer = cv2.imencode('.jpg', processed)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        cap.release()
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/train_model', methods=['POST'])
def train():
    print("🧠 Training started...")
    # Use 'python' or 'python3' depending on your environment
    process = subprocess.run(['python', 'train_model.py'], capture_output=True, text=True)
    
    if process.returncode == 0:
        reload_ai_brain()
        return jsonify({"status": "Success", "message": "AI Trained!"})
    else:
        return jsonify({"status": "Error", "message": process.stderr}), 500

@app.route('/get_progress')
def progress(): 
    return jsonify({"count": recording_config["count"]})

@app.route('/start_recording', methods=['POST'])
def start():
    data = request.json
    recording_config.update({"active": True, "gesture": data['gesture'], "count": 0})
    return jsonify({"status": "Recording Started"})

@app.route('/delete_gesture', methods=['POST'])
def delete():
    gesture = request.json.get('gesture')
    path = os.path.join('data', gesture)
    if os.path.exists(path):
        shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)
        return jsonify({"status": "Deleted"})
    return jsonify({"status": "Not Found"}), 404

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    if os.path.exists('gesture_model.h5'):
        reload_ai_brain()
    app.run(host='0.0.0.0', port=5000, threaded=True)
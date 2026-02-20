import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Trash2, Settings, Activity, Play, Video, CheckCircle, Loader2, AlertCircle } from 'lucide-react';

const API_BASE = "http://127.0.0.1:5000"; // Using IP for better Windows compatibility

function App() {
  const [action, setAction] = useState("idle");
  const [status, setStatus] = useState("CONNECTING...");
  const [progress, setProgress] = useState(0);
  const [isTraining, setIsTraining] = useState(false);
  const [videoKey, setVideoKey] = useState(0); // To force-refresh the video stream

  const actionsList = [
    "idle", "cursor_movement", "pinch_click", "screenshot", 
    "vol_up", "vol_down", "play_pause", "scroll_up", "scroll_down",
    "close_tab", "change_tabs", "brightness_up", "brightness_down"
  ];

  // Heartbeat to monitor the backend
  const checkServer = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/get_progress`);
      setProgress(res.data.count);
      
      if (isTraining) {
        setStatus("🧠 AI BRAIN UPDATING...");
      } else if (res.data.count > 0 && res.data.count < 300) {
        setStatus(`🔴 RECORDING: ${action.toUpperCase()}`);
      } else {
        setStatus("SYSTEM ONLINE");
      }
    } catch (e) {
      setStatus("OFFLINE: Check Terminal");
      setVideoKey(prev => prev + 1); // Reset video if connection drops
    }
  }, [action, isTraining]);

  useEffect(() => {
    const timer = setInterval(checkServer, 500);
    return () => clearInterval(timer);
  }, [checkServer]);

  const handleInit = async () => {
    try {
      const res = await axios.get(`${API_BASE}/init_folders`);
      alert(res.data.message);
    } catch (e) { alert("Initialization failed. Check Python terminal."); }
  };

  const handleRecord = async () => {
    try {
      await axios.post(`${API_BASE}/start_recording`, { gesture: action });
      setProgress(0);
    } catch (e) { alert("Recording failed to start."); }
  };

  const handleTrain = async () => {
    setIsTraining(true);
    try {
      const res = await axios.post(`${API_BASE}/train_model`);
      if (res.data.status === "Success") {
        alert("🎉 Model Trained! Hot-reload complete.");
      }
    } catch (e) {
      alert("Training Error: Ensure you have 300 samples for your gestures.");
    } finally {
      setIsTraining(false);
    }
  };

  const handleDelete = async (targetAction) => {
    if (window.confirm(`Wipe data for ${targetAction}?`)) {
      try {
        await axios.post(`${API_BASE}/delete_gesture`, { gesture: targetAction });
      } catch (e) { alert("Delete failed."); }
    }
  };

  return (
    <div style={{ background: '#020617', color: '#f8fafc', minHeight: '100vh', padding: '40px', fontFamily: '"Inter", sans-serif' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '32px', fontWeight: '900', letterSpacing: '-1px' }}>
            GESTURE<span style={{ color: '#3b82f6' }}>CONTROL</span> PRO
          </h1>
          <p style={{ color: '#64748b', fontWeight: '500' }}>Deep Learning OS Automation</p>
        </div>
        <button onClick={handleInit} style={{ background: '#1e293b', color: '#94a3b8', border: '1px solid #334155', padding: '12px 24px', borderRadius: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Settings size={18} />
          Init Workspace
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: '40px' }}>
        
        {/* Left: Vision Center */}
        <div style={{ background: '#0f172a', padding: '24px', borderRadius: '32px', border: '1px solid #1e293b' }}>
          <div style={{ position: 'relative', borderRadius: '24px', overflow: 'hidden', background: '#000', height: '480px', boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)' }}>
            {status !== "OFFLINE: Check Terminal" ? (
              <img 
                key={videoKey} 
                src={`${API_BASE}/video_feed`} 
                style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                alt="Feed" 
              />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '10px' }}>
                <AlertCircle size={48} color="#f87171" />
                <p style={{ color: '#64748b' }}>Waiting for Flask on Port 5000...</p>
              </div>
            )}
          </div>

          <div style={{ marginTop: '24px', padding: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#94a3b8' }}>SAMPLE CAPTURE</span>
              <span style={{ color: '#3b82f6', fontWeight: '800' }}>{Math.round((progress / 300) * 100)}%</span>
            </div>
            <div style={{ background: '#1e293b', height: '12px', borderRadius: '20px', overflow: 'hidden' }}>
              <div style={{ 
                width: `${(progress / 300) * 100}%`, 
                background: progress >= 300 ? '#10b981' : 'linear-gradient(90deg, #3b82f6, #60a5fa)', 
                height: '100%', 
                transition: 'width 0.3s ease-out' 
              }}></div>
            </div>
            <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '8px', color: status.includes("Online") ? "#10b981" : "#f87171" }}>
              <Activity size={18} />
              <span style={{ fontSize: '14px', fontWeight: '700', letterSpacing: '1px' }}>{status}</span>
            </div>
          </div>
        </div>

        {/* Right: AI Training Center */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ background: '#1e293b', padding: '30px', borderRadius: '32px', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Play size={20} fill="#3b82f6" color="#3b82f6" /> GESTURE TRAINER
            </h3>
            
            <select 
              value={action} 
              onChange={(e) => setAction(e.target.value)}
              style={{ width: '100%', padding: '16px', borderRadius: '16px', background: '#020617', color: 'white', border: '1px solid #334155', marginBottom: '20px' }}
            >
              {actionsList.map(a => <option key={a} value={a}>{a.toUpperCase().replace('_', ' ')}</option>)}
            </select>

            <button 
              onClick={handleRecord} 
              disabled={isTraining}
              style={{ width: '100%', background: '#3b82f6', color: 'white', padding: '18px', borderRadius: '16px', border: 'none', fontWeight: '800', cursor: 'pointer', marginBottom: '12px', transition: '0.3s' }}
              onMouseOver={(e) => e.target.style.background = '#2563eb'}
              onMouseOut={(e) => e.target.style.background = '#3b82f6'}
            >
              START RECORDING
            </button>

            <button 
              onClick={handleTrain} 
              disabled={isTraining}
              style={{ width: '100%', background: isTraining ? '#334155' : '#10b981', color: 'white', padding: '18px', borderRadius: '16px', border: 'none', fontWeight: '800', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}
            >
              {isTraining ? <Loader2 style={{ animation: 'spin 1s linear infinite' }} size={20} /> : <CheckCircle size={20} />}
              {isTraining ? "PROCESSING..." : "TRAIN AI MODEL"}
            </button>
          </div>

          <div style={{ background: '#0f172a', padding: '24px', borderRadius: '32px', border: '1px solid #1e293b', flexGrow: 1 }}>
            <p style={{ margin: '0 0 15px 0', fontSize: '12px', fontWeight: 'bold', color: '#475569', textTransform: 'uppercase' }}>Memory Library</p>
            <div style={{ maxHeight: '220px', overflowY: 'auto' }}>
              {actionsList.map(a => (
                <div key={a} style={{ display: 'flex', justifyContent: 'space-between', background: '#1e293b', padding: '12px 20px', borderRadius: '12px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px', fontWeight: '600' }}>{a}</span>
                  <Trash2 size={16} color="#f87171" style={{ cursor: 'pointer' }} onClick={() => handleDelete(a)} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

export default App;
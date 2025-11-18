import React, { useEffect, useState } from "react";
import { api } from "../api/api";
import { socket } from "../api/socket";

const LiveStatusCard = () => {
  const [status, setStatus] = useState({
    sleep: false,
    phone: false,
    away: false,
  });
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  // Initial load
  useEffect(() => {
    const fetchInitialStatus = async () => {
      try {
        const res = await api.get("/events/live/001");
        console.log("Initial status loaded:", res.data);
        setStatus(res.data);
      } catch (err) {
        console.error("Failed to fetch initial status:", err);
      }
    };

    fetchInitialStatus();

    // Refresh every 5 seconds even without socket
    const interval = setInterval(fetchInitialStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  // Socket updates (batch mode - every 5 seconds)
  useEffect(() => {
    const handleConnect = () => {
      console.log("✅ Socket connected!");
      setConnected(true);
    };

    const handleDisconnect = () => {
      console.log("❌ Socket disconnected!");
      setConnected(false);
    };

    const handleConnectError = (error: Error) => {
      console.error("Socket connection error:", error);
      setConnected(false);
    };

    // Batch status update handler (receives all states at once)
    const handleBatchUpdate = (data: any) => {
      console.log("📦 BATCH UPDATE RECEIVED:", data);
      const timestamp = new Date(data.timestamp).toLocaleTimeString();

      setStatus({
        sleep: data.sleep,
        phone: data.phone,
        away: data.away,
      });

      setLastUpdate(`Updated at ${timestamp}`);
    };

    // Register event listeners
    socket.on("connect", handleConnect);
    socket.on("disconnect", handleDisconnect);
    socket.on("connect_error", handleConnectError);
    socket.on("status_batch_update", handleBatchUpdate);

    // Check if already connected
    if (socket.connected) {
      setConnected(true);
    }

    // Cleanup
    return () => {
      socket.off("connect", handleConnect);
      socket.off("disconnect", handleDisconnect);
      socket.off("connect_error", handleConnectError);
      socket.off("status_batch_update", handleBatchUpdate);
    };
  }, []);

  const getStatusColor = (isActive: boolean) => {
    return isActive ? "#ff4444" : "#44ff44";
  };

  const getStatusIcon = (isActive: boolean) => {
    return isActive ? "🔴" : "🟢";
  };

  const getStatusEmoji = (type: string, isActive: boolean) => {
    if (!isActive) return "✅";

    switch(type) {
      case "sleep": return "😴";
      case "phone": return "📱";
      case "away": return "🚶";
      default: return "⚠️";
    }
  };

  return (
    <div className="card live-status" style={{
      padding: "20px",
      borderRadius: "10px",
      backgroundColor: "#1a1a1a",
      minWidth: "350px",
      border: "2px solid #333"
    }}>
      <h2 style={{ marginBottom: "20px" }}>
        📊 Live Status Monitor
      </h2>

      <div style={{
        padding: "10px",
        marginBottom: "15px",
        backgroundColor: connected ? "#004400" : "#440000",
        borderRadius: "5px",
        fontSize: "14px",
        fontWeight: "bold",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <span>{connected ? "🟢 Connected" : "🔴 Disconnected"}</span>
        <span style={{ fontSize: "12px", color: "#ccc" }}>
          Updates every 5s
        </span>
      </div>

      {lastUpdate && (
        <div style={{
          padding: "8px",
          marginBottom: "15px",
          backgroundColor: "#222",
          borderRadius: "5px",
          fontSize: "11px",
          color: "#999",
          textAlign: "center"
        }}>
          {lastUpdate}
        </div>
      )}

      <div style={{
        textAlign: "left",
        fontSize: "16px",
        display: "flex",
        flexDirection: "column",
        gap: "15px"
      }}>
        <div style={{
          padding: "15px",
          borderRadius: "8px",
          backgroundColor: status.sleep ? "#330000" : "#003300",
          border: `2px solid ${getStatusColor(status.sleep)}`,
          transition: "all 0.3s ease"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: "24px", marginRight: "10px" }}>
                {getStatusEmoji("sleep", status.sleep)}
              </span>
              <strong>Sleeping</strong>
            </div>
            <span style={{
              color: getStatusColor(status.sleep),
              fontWeight: "bold",
              fontSize: "18px"
            }}>
              {status.sleep ? "YES" : "No"}
            </span>
          </div>
        </div>

        <div style={{
          padding: "15px",
          borderRadius: "8px",
          backgroundColor: status.phone ? "#333300" : "#003300",
          border: `2px solid ${getStatusColor(status.phone)}`,
          transition: "all 0.3s ease"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: "24px", marginRight: "10px" }}>
                {getStatusEmoji("phone", status.phone)}
              </span>
              <strong>Phone Usage</strong>
            </div>
            <span style={{
              color: getStatusColor(status.phone),
              fontWeight: "bold",
              fontSize: "18px"
            }}>
              {status.phone ? "YES" : "No"}
            </span>
          </div>
        </div>

        <div style={{
          padding: "15px",
          borderRadius: "8px",
          backgroundColor: status.away ? "#000033" : "#003300",
          border: `2px solid ${getStatusColor(status.away)}`,
          transition: "all 0.3s ease"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: "24px", marginRight: "10px" }}>
                {getStatusEmoji("away", status.away)}
              </span>
              <strong>Away from Desk</strong>
            </div>
            <span style={{
              color: getStatusColor(status.away),
              fontWeight: "bold",
              fontSize: "18px"
            }}>
              {status.away ? "YES" : "No"}
            </span>
          </div>
        </div>
      </div>

      <div style={{
        marginTop: "20px",
        padding: "10px",
        backgroundColor: "#111",
        borderRadius: "5px",
        fontSize: "12px",
        color: "#666",
        textAlign: "center"
      }}>
        High Accuracy Mode • Updates: Delayed
      </div>
    </div>
  );
};

export default LiveStatusCard;
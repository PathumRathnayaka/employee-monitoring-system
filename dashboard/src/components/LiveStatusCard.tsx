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
  }, []);

  // Real-time updates
  useEffect(() => {
    // Connection event handlers
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

    // Status update handler
    const handleStatusUpdate = (data: any) => {
      console.log("📡 SOCKET RECEIVED:", data);
      const timestamp = new Date(data.timestamp).toLocaleTimeString();

      setStatus((prev) => ({
        ...prev,
        [data.event_type]: data.active,
      }));

      setLastUpdate(`${data.event_type.toUpperCase()}: ${data.active ? "ACTIVE" : "INACTIVE"} at ${timestamp}`);
    };

    // Register event listeners
    socket.on("connect", handleConnect);
    socket.on("disconnect", handleDisconnect);
    socket.on("connect_error", handleConnectError);
    socket.on("status_update", handleStatusUpdate);

    // Check if already connected
    if (socket.connected) {
      setConnected(true);
    }

    // Cleanup
    return () => {
      socket.off("connect", handleConnect);
      socket.off("disconnect", handleDisconnect);
      socket.off("connect_error", handleConnectError);
      socket.off("status_update", handleStatusUpdate);
    };
  }, []);

  const getStatusColor = (isActive: boolean) => {
    return isActive ? "#ff4444" : "#44ff44";
  };

  const getStatusIcon = (isActive: boolean) => {
    return isActive ? "🔴" : "🟢";
  };

  return (
    <div className="card live-status" style={{
      padding: "20px",
      borderRadius: "10px",
      backgroundColor: "#1a1a1a",
      minWidth: "300px"
    }}>
      <h2>🔴 Live Status</h2>

      <div style={{
        padding: "10px",
        marginBottom: "15px",
        backgroundColor: connected ? "#004400" : "#440000",
        borderRadius: "5px",
        fontSize: "14px",
        fontWeight: "bold"
      }}>
        {connected ? "🟢 Connected to Server" : "🔴 Disconnected from Server"}
      </div>

      {lastUpdate && (
        <div style={{
          padding: "8px",
          marginBottom: "15px",
          backgroundColor: "#333",
          borderRadius: "5px",
          fontSize: "12px",
          color: "#aaa"
        }}>
          Last Update: {lastUpdate}
        </div>
      )}

      <div style={{ textAlign: "left", fontSize: "18px" }}>
        <p style={{ padding: "10px 0" }}>
          <span style={{ marginRight: "10px" }}>{getStatusIcon(status.sleep)}</span>
          <strong>Sleeping:</strong>{" "}
          <span style={{
            color: getStatusColor(status.sleep),
            fontWeight: "bold",
            marginLeft: "10px"
          }}>
            {status.sleep ? "YES" : "No"}
          </span>
        </p>

        <p style={{ padding: "10px 0" }}>
          <span style={{ marginRight: "10px" }}>{getStatusIcon(status.phone)}</span>
          <strong>Phone Usage:</strong>{" "}
          <span style={{
            color: getStatusColor(status.phone),
            fontWeight: "bold",
            marginLeft: "10px"
          }}>
            {status.phone ? "YES" : "No"}
          </span>
        </p>

        <p style={{ padding: "10px 0" }}>
          <span style={{ marginRight: "10px" }}>{getStatusIcon(status.away)}</span>
          <strong>Away from Desk:</strong>{" "}
          <span style={{
            color: getStatusColor(status.away),
            fontWeight: "bold",
            marginLeft: "10px"
          }}>
            {status.away ? "YES" : "No"}
          </span>
        </p>
      </div>
    </div>
  );
};

export default LiveStatusCard;
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

  // Initial load
  useEffect(() => {
    api.get("/events/live/001")
      .then((res) => {
        setStatus(res.data);
      })
      .catch((err) => {
        console.error("Failed to fetch initial status:", err);
      });
  }, []);

  // Real-time updates
  useEffect(() => {
    // Connection event handlers
    socket.on("connect", () => {
      console.log("✅ Socket connected!");
      setConnected(true);
    });

    socket.on("disconnect", () => {
      console.log("❌ Socket disconnected!");
      setConnected(false);
    });

    socket.on("connect_error", (error) => {
      console.error("Socket connection error:", error);
      setConnected(false);
    });

    // Status update handler
    socket.on("status_update", (data) => {
      console.log("📡 SOCKET RECEIVED:", data);
      setStatus((prev) => ({
        ...prev,
        [data.event_type]: data.active,
      }));
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("connect_error");
      socket.off("status_update");
    };
  }, []);

  const getStatusColor = (isActive: boolean) => {
    return isActive ? "#ff4444" : "#44ff44";
  };

  const getStatusIcon = (isActive: boolean) => {
    return isActive ? "🔴" : "🟢";
  };

  return (
    <div className="card live-status">
      <h2>🔴 Live Status</h2>

      <div style={{
        padding: "10px",
        marginBottom: "15px",
        backgroundColor: connected ? "#004400" : "#440000",
        borderRadius: "5px",
        fontSize: "14px"
      }}>
        {connected ? "🟢 Connected" : "🔴 Disconnected"}
      </div>

      <div style={{ textAlign: "left", fontSize: "18px" }}>
        <p>
          <span style={{ marginRight: "10px" }}>{getStatusIcon(status.sleep)}</span>
          <strong>Sleeping:</strong>{" "}
          <span style={{ color: getStatusColor(status.sleep), fontWeight: "bold" }}>
            {status.sleep ? "YES" : "No"}
          </span>
        </p>

        <p>
          <span style={{ marginRight: "10px" }}>{getStatusIcon(status.phone)}</span>
          <strong>Phone Usage:</strong>{" "}
          <span style={{ color: getStatusColor(status.phone), fontWeight: "bold" }}>
            {status.phone ? "YES" : "No"}
          </span>
        </p>

        <p>
          <span style={{ marginRight: "10px" }}>{getStatusIcon(status.away)}</span>
          <strong>Away from Desk:</strong>{" "}
          <span style={{ color: getStatusColor(status.away), fontWeight: "bold" }}>
            {status.away ? "YES" : "No"}
          </span>
        </p>
      </div>
    </div>
  );
};

export default LiveStatusCard;
import React, { useEffect, useState } from "react";
import { api } from "../api/api";
import { socket } from "../api/socket";

const LiveStatusCard = () => {
  const [status, setStatus] = useState({
    sleep: false,
    phone: false,
    away: false,
  });

  // Initial load
  useEffect(() => {
    api.get("/events/live/001").then((res) => {
      setStatus(res.data);
    });
  }, []);

  // Real-time updates
  useEffect(() => {
    socket.on("status_update", (data) => {
      console.log("SOCKET RECEIVED:", data);
      setStatus((prev) => ({
        ...prev,
        [data.event_type]: data.active,
      }));
    });

    return () => {
      socket.off("status_update");
    };
  }, []);

  return (
    <div className="card live-status">
      <h2>Live Status</h2>

      <p><strong>Sleeping:</strong> {status.sleep ? "Yes" : "No"}</p>
      <p><strong>Phone Usage:</strong> {status.phone ? "Yes" : "No"}</p>
      <p><strong>Away:</strong> {status.away ? "Yes" : "No"}</p>
    </div>
  );
};

export default LiveStatusCard;

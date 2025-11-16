import React, { useEffect, useState } from "react";
import { api } from "../api/api";

const LiveStatusCard = () => {
  const [status, setStatus] = useState({
    sleep: false,
    phone: false,
    away: false,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      api.get("/events/live/001").then(res => {
        setStatus(res.data);
      });
    }, 2000); // refresh every 2 sec

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="card live-status">
      <h2>Live Status</h2>

      <div className="status-box">
        <p><strong>Sleeping:</strong> {status.sleep ? "Yes" : "No"}</p>
        <p><strong>Phone Usage:</strong> {status.phone ? "Yes" : "No"}</p>
        <p><strong>Away:</strong> {status.away ? "Yes" : "No"}</p>
      </div>
    </div>
  );
};

export default LiveStatusCard;

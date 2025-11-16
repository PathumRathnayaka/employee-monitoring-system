import React from "react";
import LiveStatusCard from "../components/LiveStatusCard";
import SummaryCard from "../components/SummaryCard";
import TimelineChart from "../components/TimelineChart";

const Dashboard = () => {
  return (
    <div style={{ padding: "25px" }}>
      <h1>Employee Monitoring Dashboard</h1>

      <div style={{ display: "flex", gap: "25px" }}>
        <LiveStatusCard />
        <SummaryCard />
      </div>

      <div style={{ marginTop: "25px" }}>
        <TimelineChart />
      </div>
    </div>
  );
};

export default Dashboard;

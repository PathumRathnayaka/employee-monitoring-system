import React, { useEffect, useState } from "react";
import { api } from "../api/api";

interface Summary {
  sleep_minutes: number;
  phone_minutes: number;
  away_minutes: number;
  productive_minutes: number;
  productivity_score: number;
  date: string;
}

const SummaryCard = () => {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api.get("/summary/today/001").then(res => {
      setSummary(res.data);
    });
  }, []);

  if (!summary) return <p>Loading summary...</p>;

  return (
    <div className="card summary-card">
      <h2>Daily Summary</h2>

      <p><strong>Date:</strong> {summary.date}</p>
      <p><strong>Phone Usage:</strong> {summary.phone_minutes} min</p>
      <p><strong>Sleep:</strong> {summary.sleep_minutes} min</p>
      <p><strong>Away:</strong> {summary.away_minutes} min</p>
      <p><strong>Productive:</strong> {summary.productive_minutes} min</p>
      <p><strong>Productivity Score:</strong> {summary.productivity_score}%</p>
    </div>
  );
};

export default SummaryCard;

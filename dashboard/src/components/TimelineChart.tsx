import React, { useEffect, useState } from "react";
import { api } from "../api/api";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

const TimelineChart = () => {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    api.get("/events/today/001").then((res) => {
      const data = Array.isArray(res.data) ? res.data : [];
      setEvents(data);
    });
  }, []);

  const data = events.map((e: any, index: number) => ({
    name: index,
    value:
      e.event_type === "phone"
        ? 3
        : e.event_type === "sleep"
        ? 2
        : e.event_type === "away"
        ? 1
        : 0,
  }));

  return (
    <div className="card">
      <h2>Timeline (Event Stream)</h2>

      <LineChart width={600} height={300} data={data}>
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#ff0000" />
      </LineChart>
    </div>
  );
};

export default TimelineChart;

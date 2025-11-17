import React, { useEffect, useState } from "react";
import { api } from "../api/api";
import { socket } from "../api/socket";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

interface TimelineEvent {
  event_type: string;
  status: string;
  timestamp: string;
}

const TimelineChart = () => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);

  // Load previous events from DB when page loads
  useEffect(() => {
    api.get("/events/today/001").then((res) => {
      const data = Array.isArray(res.data) ? res.data : [];
      setEvents(data);
    });
  }, []);

  // Real-time WebSocket updates
  useEffect(() => {
    socket.on("status_update", (data: any) => {
      const timelineEvent: TimelineEvent = {
        event_type: data.event_type,
        status: data.active ? "start" : "end",
        timestamp: data.timestamp,
      };

      setEvents((prev) => [...prev, timelineEvent]);
    });

    return () => {
      socket.off("status_update");
    };
  }, []);

  // Convert events to graph-friendly format
  const chartData = events.map((e, index) => ({
    name: index,
    value:
      e.event_type === "phone"
        ? 3
        : e.event_type === "sleep"
        ? 2
        : e.event_type === "away"
        ? 1
        : 0,
    status: e.status,
    timestamp: e.timestamp,
  }));

  return (
    <div className="card">
      <h2>Timeline (Real-Time Events)</h2>

      <LineChart width={600} height={300} data={chartData}>
        <XAxis dataKey="name" />
        <YAxis
          domain={[0, 3]}
          ticks={[0, 1, 2, 3]}
          tickFormatter={(tick) =>
            tick === 3 ? "Phone" : tick === 2 ? "Sleep" : tick === 1 ? "Away" : ""
          }
        />
        <Tooltip
          formatter={(value: number, _name: string, props: any) => {
            const evt = events[props.payload.name];
            return [
              evt.event_type.toUpperCase() +
                " " +
                (evt.status === "start" ? "START" : "END"),
              "Event",
            ];
          }}
        />
        <Line type="monotone" dataKey="value" stroke="#ff0000" strokeWidth={2} />
      </LineChart>

      {events.length === 0 && <p>No activity recorded yet today.</p>}
    </div>
  );
};

export default TimelineChart;

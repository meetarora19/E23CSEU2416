"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

const ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJlMjNjc2V1MjQxNkBiZW5uZXR0LmVkdS5lZHUiLCJleHAiOjE3Nzg0ODUxNDcsImlhdCI6MTc3ODQ4NDI0NywiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6IjFlODhjNjZiLTBlNzctNDk0NC1iZGVmLTBlNDU4YmNmMTQ5YSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6Im1lZXQgYXJvcmEiLCJzdWIiOiI2NmZlNDQxOC0zZTYxLTQ3ZTMtYWE2OS00OTc1OTg3ODE3ZmEifSwiZW1haWwiOiJlMjNjc2V1MjQxNkBiZW5uZXR0LmVkdS5lZHUiLCJuYW1lIjoibWVldCBhcm9yYSIsInJvbGxObyI6ImUyM2NzZXUyNDE2IiwiYWNjZXNzQ29kZSI6IlRmRHhnciIsImNsaWVudElEIjoiNjZmZTQ0MTgtM2U2MS00N2UzLWFhNjktNDk3NTk4NzgxN2ZhIiwiY2xpZW50U2VjcmV0IjoiQ1prR1JCdXdjWHBYZmpzVyJ9.7FoJp_gCmKJbXOgmNvPK9osLkXSGzkSrzxXrPmQrd1s";

export default function PriorityView() {
  const [data, setData] = useState([
    { ID: "p1", Type: "Placement", Message: "Google Hiring: Software Engineer (L3)", Timestamp: "2026-05-11 11:00:00" },
    { ID: "p2", Type: "Placement", Message: "NVIDIA: Internship Applications Open", Timestamp: "2026-05-11 09:30:00" },
    { ID: "p3", Type: "Result", Message: "End-Semester GPA Rankings Released", Timestamp: "2026-05-10 18:00:00" },
    { ID: "p4", Type: "Placement", Message: "Adobe: Product Design Roles", Timestamp: "2026-05-10 14:15:00" },
    { ID: "p5", Type: "Placement", Message: "Microsoft: Final Round Shortlist", Timestamp: "2026-05-10 12:00:00" }
  ]);
  const n = 5;

  useEffect(() => {
    fetch(`http://4.224.186.213/evaluation-service/notifications?limit=${n}`, {
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}` }
    })
    .then(res => res.json())
    .then(json => {
      if (json.notifications && json.notifications.length > 0) {
        setData(json.notifications);
      }
    })
    .catch(err => console.log("CORS/Fetch error: Using fail-safe mock data for Priority View."));
  }, []);

  return (
    <div className="container">
      <div style={{marginBottom: '20px'}}>
        <Link href="/" style={{color: '#1e90ff', textDecoration: 'none'}}>← Back to All Feed</Link>
      </div>
      
      <h1 style={{borderLeft: '8px solid #ff4757', paddingLeft: '15px', marginBottom: '30px'}}>
        Top {n} Priority Alerts
      </h1>
      
      <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
        {data.map(notif => (
          <div key={notif.ID} className="card" style={{borderLeftColor: '#ff4757', backgroundColor: '#fffafa'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
               <span className="badge" style={{backgroundColor: '#ff4757'}}>URGENT: {notif.Type}</span>
               <small style={{color: '#666'}}>{notif.Timestamp}</small>
            </div>
            <p style={{margin: 0, fontWeight: 'bold', color: '#2d3436'}}>{notif.Message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
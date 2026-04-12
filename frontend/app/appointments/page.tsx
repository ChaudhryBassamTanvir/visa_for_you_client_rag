"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/Sidebar"

type Appointment = {
  id: number; client_name: string; client_email: string;
  client_phone: string; preferred_date: string; preferred_time: string;
  purpose: string; status: string; trello_url: string; created_at: string
}

export default function AppointmentsPage() {
  const router = useRouter()
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    const user  = JSON.parse(localStorage.getItem("user") || "{}")
    if (!token || !user.is_admin) { router.push("/login"); return }

    fetch("http://127.0.0.1:8000/appointments", {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => { setAppointments(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const statusColor: Record<string, any> = {
    pending:   { bg: "#fffbeb", text: "#92400e", border: "#fde68a" },
    confirmed: { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" },
    cancelled: { bg: "#fef2f2", text: "#dc2626", border: "#fecaca" },
  }

  return (
    <div className="flex">
      <Sidebar />

      <main className="ml-[220px] flex-1 min-h-screen bg-[#f9f9f8] px-9 py-8">
        <div className="mb-6">
          <h1 className="text-[20px] font-medium tracking-[-0.3px] m-0">
            Appointments
          </h1>
          <p className="text-[13px] text-[#999] mt-1">
            {appointments.length} total appointments
          </p>
        </div>

        <div className="bg-white border border-[#e8e8e6] rounded-[10px] overflow-hidden">
          <div className="px-5 py-[14px] border-b border-[#e8e8e6] bg-[#f9f9f8] grid grid-cols-[1.5fr_1.5fr_1fr_1fr_1fr_80px] gap-3">
            {["Client", "Contact", "Date", "Time", "Purpose", "Status"].map(h => (
              <div
                key={h}
                className="text-[11px] text-[#999] font-medium uppercase tracking-[0.8px]"
              >
                {h}
              </div>
            ))}
          </div>

          {loading ? (
            <div className="p-10 text-center text-[13px] text-[#bbb]">
              Loading...
            </div>
          ) : appointments.length === 0 ? (
            <div className="p-10 text-center text-[13px] text-[#bbb]">
              No appointments yet.
            </div>
          ) : appointments.map((a, i) => (
            <div
              key={a.id}
              className="grid grid-cols-[1.5fr_1.5fr_1fr_1fr_1fr_80px] gap-3 px-5 py-[14px] items-center"
              style={{
                borderBottom:
                  i < appointments.length - 1
                    ? "0.5px solid #f0f0ef"
                    : "none"
              }}
            >
              <div>
                <div className="text-[13px] font-medium text-[#1a1a1a]">
                  {a.client_name}
                </div>
                <div className="text-[11px] text-[#999]">
                  {a.created_at}
                </div>
              </div>

              <div>
                <div className="text-xs text-[#444]">
                  {a.client_email}
                </div>
                <div className="text-xs text-[#999]">
                  {a.client_phone}
                </div>
              </div>

              <div className="text-xs text-[#1a1a1a]">
                {a.preferred_date}
              </div>

              <div className="text-xs text-[#1a1a1a]">
                {a.preferred_time}
              </div>

              <div className="text-xs text-[#666] overflow-hidden text-ellipsis whitespace-nowrap">
                {a.purpose}
              </div>

              // Replace the last column in appointments map
<div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
  <span style={{
    fontSize: "11px", padding: "3px 8px", borderRadius: "6px",
    background: statusColor[a.status]?.bg,
    color: statusColor[a.status]?.text,
    border: `0.5px solid ${statusColor[a.status]?.border}`,
    fontWeight: "500", textAlign: "center"
  }}>
    {a.status}
  </span>
  {a.trello_url && (
    <a href={a.trello_url} target="_blank" rel="noreferrer"
      style={{ fontSize: "10px", color: "#3b5bdb", textDecoration: "none", textAlign: "center" }}>
      Trello
    </a>
  )}
  <button
    onClick={async () => {
      if (!confirm("Delete this appointment?")) return
      const token = localStorage.getItem("token")
      await fetch(`http://127.0.0.1:8000/appointments/${a.id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      })
      setAppointments(prev => prev.filter(x => x.id !== a.id))
    }}
    style={{
      fontSize: "10px", padding: "3px 8px", borderRadius: "6px",
      background: "#fef2f2", color: "#dc2626",
      border: "0.5px solid #fecaca", cursor: "pointer"
    }}
  >
    Delete
  </button>
</div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
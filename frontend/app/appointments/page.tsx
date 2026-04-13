"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/Sidebar"

type Appointment = {
  id: number
  client_name: string
  client_email: string
  client_phone: string
  preferred_date: string
  preferred_time: string
  purpose: string
  status: string
  trello_url: string
  created_at: string
}

export default function AppointmentsPage() {
  const router = useRouter()
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)

  const fetchAppointments = async () => {
    const token = localStorage.getItem("token")
    try {
      const res = await fetch("http://127.0.0.1:8000/appointments", {
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await res.json()
      setAppointments(data)
    } catch (error) {
      console.error("Failed to fetch appointments", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleStatus = async (id: number, currentStatus: string) => {
    const newStatus = currentStatus === "done" ? "pending" : "done"
    try {
      await fetch(`http://127.0.0.1:8000/appointments/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ status: newStatus }),
      })
      setAppointments((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: newStatus } : a))
      )
    } catch (error) {
      console.error("Failed to update status", error)
    }
  }

  const deleteAppt = async (id: number) => {
    if (!confirm("Delete this appointment?")) return
    try {
      await fetch(`http://127.0.0.1:8000/appointments/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      setAppointments((prev) => prev.filter((a) => a.id !== id))
    } catch (error) {
      console.error("Delete failed", error)
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("token")
    const user = JSON.parse(localStorage.getItem("user") || "{}")
    if (!token || !user.is_admin) {
      router.push("/login")
      return
    }
    fetchAppointments()
  }, [router])

  const statusStyles: Record<string, { bg: string; text: string; dot: string }> = {
    pending:   { bg: "bg-amber-50  text-amber-700  border-amber-200",  dot: "bg-amber-400" },
    done:      { bg: "bg-emerald-50 text-emerald-700 border-emerald-200", dot: "bg-emerald-400" },
    confirmed: { bg: "bg-blue-50   text-blue-700   border-blue-200",   dot: "bg-blue-400" },
    cancelled: { bg: "bg-red-50    text-red-600    border-red-200",    dot: "bg-red-400" },
  }

  return (
    <div className="flex bg-white min-h-screen">
      <Sidebar />

      <main className="ml-[240px] flex-1 min-h-screen bg-gray-50 px-8 py-8">

        {/* Page header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">📅</span>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">Appointments</h1>
          </div>
          <p className="text-sm text-gray-400 ml-7">{appointments.length} total appointments</p>
        </div>

        {/* Summary chips */}
        <div className="flex gap-3 mb-6">
          {["pending", "confirmed", "done", "cancelled"].map((s) => {
            const count = appointments.filter(a => a.status === s).length
            const st = statusStyles[s]
            return (
              <div key={s} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ${st.bg}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} />
                {s.charAt(0).toUpperCase() + s.slice(1)} · {count}
              </div>
            )
          })}
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {/* Col headers */}
          <div className="grid grid-cols-[1.5fr_1.5fr_1fr_1fr_1.5fr_190px] px-5 py-2.5 border-b border-gray-100 bg-gray-50">
            {["Client", "Contact", "Date", "Time", "Purpose", "Actions"].map(h => (
              <div key={h} className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">{h}</div>
            ))}
          </div>

          {loading ? (
            <div className="p-12 text-center text-sm text-gray-300">Loading...</div>
          ) : appointments.length === 0 ? (
            <div className="p-12 text-center text-sm text-gray-300">No appointments yet.</div>
          ) : (
            appointments.map((a, i) => {
              const st = statusStyles[a.status] || statusStyles.pending
              return (
                <div
                  key={a.id}
                  className={`grid grid-cols-[1.5fr_1.5fr_1fr_1fr_1.5fr_190px] items-center px-5 py-4 hover:bg-gray-50 transition-colors ${
                    i < appointments.length - 1 ? "border-b border-gray-100" : ""
                  }`}
                >
                  {/* Client */}
                  <div>
                    <div className="text-sm font-medium text-gray-900">{a.client_name}</div>
                    <div className="text-[11px] text-gray-400 mt-0.5">{a.created_at}</div>
                  </div>

                  {/* Contact */}
                  <div>
                    <div className="text-xs text-gray-600">{a.client_email}</div>
                    <div className="text-xs text-gray-400 mt-0.5">{a.client_phone}</div>
                  </div>

                  {/* Date */}
                  <div className="text-xs font-medium text-gray-800">{a.preferred_date}</div>

                  {/* Time */}
                  <div className="text-xs font-medium text-gray-800">{a.preferred_time}</div>

                  {/* Purpose */}
                  <div className="text-xs text-gray-500 truncate pr-2">{a.purpose}</div>

                  {/* Actions */}
                  <div className="flex flex-col gap-1.5">
                    {/* Status badge */}
                    <span className={`inline-flex items-center gap-1.5 text-[10px] font-semibold px-2 py-1 rounded-md border w-fit ${st.bg}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} />
                      {a.status}
                    </span>

                    <div className="flex gap-1.5 flex-wrap">
                      {/* Toggle */}
                      <button
                        onClick={() => toggleStatus(a.id, a.status)}
                        className={`text-[10px] font-medium px-2 py-1 rounded-md border transition-colors ${
                          a.status === "done"
                            ? "bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100"
                            : "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100"
                        }`}
                      >
                        {a.status === "done" ? "↺ Pending" : "✓ Done"}
                      </button>

                      {/* Delete */}
                      <button
                        onClick={() => deleteAppt(a.id)}
                        className="text-[10px] font-medium px-2 py-1 rounded-md border bg-red-50 text-red-500 border-red-100 hover:bg-red-100 transition-colors"
                      >
                        Delete
                      </button>
                    </div>

                    {/* Trello */}
                    {a.trello_url && (
                      <a
                        href={a.trello_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] text-blue-500 hover:underline w-fit"
                      >
                        → View on Trello
                      </a>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </main>
    </div>
  )
}
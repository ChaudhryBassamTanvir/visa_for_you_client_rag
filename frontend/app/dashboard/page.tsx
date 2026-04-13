"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/Sidebar"

type Stats = {
  total_tasks: number
  total_clients: number
  pending_tasks: number
  done_tasks: number
}

type User = {
  id: number
  name: string
  email: string
  phone: string
  cgpa: string
  degree: string
  created_at: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<Stats>({
    total_tasks: 0,
    total_clients: 0,
    pending_tasks: 0,
    done_tasks: 0,
  })
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  const fetchAll = async () => {
    const token = localStorage.getItem("token")
    try {
      const [s, u] = await Promise.all([
        fetch("http://127.0.0.1:8000/stats").then((r) => r.json()),
        fetch("http://127.0.0.1:8000/users", {
          headers: { Authorization: `Bearer ${token}` },
        }).then((r) => r.json()),
      ])
      setStats(s)
      setUsers(u)
    } catch {
      console.error("fetch error")
    }
    setLoading(false)
  }

  useEffect(() => {
    const token = localStorage.getItem("token")
    const user = JSON.parse(localStorage.getItem("user") || "{}")
    if (!token || !user.is_admin) {
      router.push("/login")
      return
    }
    fetchAll()
    const interval = setInterval(fetchAll, 30000)
    return () => clearInterval(interval)
  }, [])

  const statCards = [
    { label: "Total Students", value: stats.total_clients, icon: "👥", color: "bg-blue-50 text-blue-700" },
    { label: "Portal Users",   value: users.length,        icon: "🖥️", color: "bg-violet-50 text-violet-700" },
    { label: "Pending Tasks",  value: stats.pending_tasks, icon: "⏳", color: "bg-amber-50 text-amber-700" },
    { label: "Completed",      value: stats.done_tasks,    icon: "✅", color: "bg-emerald-50 text-emerald-700" },
  ]

  return (
    <div className="flex bg-white min-h-screen">
      <Sidebar />

      <main className="ml-[240px] flex-1 min-h-screen bg-gray-50 px-8 py-8">

        {/* Page header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">🏠</span>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">Dashboard</h1>
          </div>
          <p className="text-sm text-gray-400 ml-7">Visa For You — Student Management</p>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {statCards.map(({ label, value, icon, color }) => (
            <div key={label} className="bg-white rounded-xl border border-gray-200 px-5 py-4 hover:shadow-sm transition-shadow">
              <div className={`inline-flex items-center justify-center w-8 h-8 rounded-lg text-base mb-3 ${color}`}>
                {icon}
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-0.5">{value}</div>
              <div className="text-xs text-gray-400 font-medium">{label}</div>
            </div>
          ))}
        </div>

        {/* Students table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {/* Table header bar */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-gray-100">
            <div>
              <span className="text-sm font-semibold text-gray-900">Registered Students</span>
              <span className="ml-2 text-xs text-gray-400">Portal users</span>
            </div>
            <span className="text-xs text-gray-400 bg-gray-50 border border-gray-200 px-2.5 py-1 rounded-full">
              {users.length} total
            </span>
          </div>

          {/* Column headers */}
          <div className="grid grid-cols-[2fr_2fr_1fr_1fr_1fr_120px] bg-gray-50 border-b border-gray-100 px-5 py-2.5">
            {["Name", "Email", "CGPA", "Degree", "Phone", "Joined"].map((h) => (
              <div key={h} className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">{h}</div>
            ))}
          </div>

          {/* Rows */}
          {loading ? (
            <div className="p-12 text-center text-sm text-gray-300">Loading...</div>
          ) : users.length === 0 ? (
            <div className="p-12 text-center text-sm text-gray-300">No registered students yet.</div>
          ) : (
            users.map((user, i) => (
              <div
                key={user.id}
                className={`grid grid-cols-[2fr_2fr_1fr_1fr_1fr_120px] items-center px-5 py-3.5 hover:bg-gray-50 transition-colors ${
                  i < users.length - 1 ? "border-b border-gray-100" : ""
                }`}
              >
                {/* Name + avatar */}
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center text-[10px] font-semibold text-blue-600 shrink-0">
                    {user.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()}
                  </div>
                  <span className="text-sm font-medium text-gray-900">{user.name}</span>
                </div>

                <div className="text-xs text-gray-500">{user.email}</div>

                <div className="text-xs font-semibold text-gray-900">
                  {user.cgpa || <span className="text-gray-300">—</span>}
                </div>

                <div className="text-xs text-gray-500 truncate">
                  {user.degree || <span className="text-gray-300">—</span>}
                </div>

                <div className="text-xs text-gray-500">
                  {user.phone || <span className="text-gray-300">—</span>}
                </div>

                <div className="text-xs text-gray-400">{user.created_at}</div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
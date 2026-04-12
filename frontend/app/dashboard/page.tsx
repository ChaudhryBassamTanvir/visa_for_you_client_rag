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

  return (
    <div className="flex">
      <Sidebar />

      <main className="ml-[220px] flex-1 min-h-screen bg-[#f9f9f8] px-9 py-8">
        <div className="mb-7">
          <h1 className="m-0 text-[20px] font-medium tracking-[-0.3px]">
            Dashboard
          </h1>
          <p className="mt-1 text-[13px] text-[#999]">
            Visa For You — Student Management
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-3 mb-7">
          {[
            { label: "Total Students", value: stats.total_clients },
            { label: "Portal Users", value: users.length },
            { label: "Pending Tasks", value: stats.pending_tasks },
            { label: "Completed", value: stats.done_tasks },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="rounded-[10px] border border-[#e8e8e6] bg-white px-5 py-4"
            >
              <div className="mb-2 text-[11px] text-[#999]">{label}</div>
              <div className="text-[24px] font-medium">{value}</div>
            </div>
          ))}
        </div>

        {/* Portal Users */}
        <div className="overflow-hidden rounded-[10px] border border-[#e8e8e6] bg-white">
          <div className="flex items-center justify-between border-b border-[#e8e8e6] px-5 py-4">
            <span className="text-[13px] font-medium">
              Registered Students (Portal)
            </span>
            <span className="text-[11px] text-[#999]">
              {users.length} total
            </span>
          </div>

          {/* Table header */}
          <div className="grid grid-cols-[2fr_2fr_1fr_1fr_1fr_100px] border-b border-[#f0f0f0] bg-[#f9f9f8] px-5 py-2.5">
            {["Name", "Email", "CGPA", "Degree", "Phone", "Joined"].map(
              (h) => (
                <div
                  key={h}
                  className="text-[11px] font-medium uppercase tracking-[0.8px] text-[#999]"
                >
                  {h}
                </div>
              )
            )}
          </div>

          {loading ? (
            <div className="p-10 text-center text-[13px] text-[#bbb]">
              Loading...
            </div>
          ) : users.length === 0 ? (
            <div className="p-10 text-center text-[13px] text-[#bbb]">
              No registered students yet.
            </div>
          ) : (
            users.map((user, i) => (
              <div
                key={user.id}
                className={`grid grid-cols-[2fr_2fr_1fr_1fr_1fr_100px] items-center px-5 py-[13px] ${
                  i < users.length - 1
                    ? "border-b border-[#f0f0ef]"
                    : ""
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[#e8f0fe] text-[10px] font-medium text-[#3b5bdb]">
                    {user.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()}
                  </div>

                  <span className="text-[13px] font-medium text-[#1a1a1a]">
                    {user.name}
                  </span>
                </div>

                <div className="text-[12px] text-[#666]">
                  {user.email}
                </div>

                <div className="text-[12px] font-medium text-[#1a1a1a]">
                  {user.cgpa || "—"}
                </div>

                <div className="truncate whitespace-nowrap text-[12px] text-[#666]">
                  {user.degree || "—"}
                </div>

                <div className="text-[12px] text-[#666]">
                  {user.phone || "—"}
                </div>

                <div className="text-[11px] text-[#bbb]">
                  {user.created_at}
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
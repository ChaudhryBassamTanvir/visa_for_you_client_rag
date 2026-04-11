"use client"
import { useEffect, useState } from "react"
import Sidebar from "@/components/Sidebar"
import { useRouter } from "next/navigation"

type Task = {
  id: number
  description: string
  status: string
  trello_url: string
  client: string
  created_at: string
}

type Client = {
  id: number
  name: string
  email: string
  phone: string
  company: string
  channel: string
  task_count: number
  created_at: string
}

type Stats = {
  total_tasks: number
  total_clients: number
  pending_tasks: number
  done_tasks: number
}

const statusColor: Record<string, { bg: string; text: string; border: string }> = {
  pending: { bg: "#fffbeb", text: "#92400e", border: "#fde68a" },
  in_progress: { bg: "#eff6ff", text: "#1e40af", border: "#bfdbfe" },
  done: { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" },
}

const channelColor: Record<string, { bg: string; text: string; border: string }> = {
  whatsapp: { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" },
  slack: { bg: "#eff6ff", text: "#1e40af", border: "#bfdbfe" },
  web: { bg: "#f5f3ff", text: "#6d28d9", border: "#ddd6fe" },
}

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [stats, setStats] = useState<Stats>({
    total_tasks: 0,
    total_clients: 0,
    pending_tasks: 0,
    done_tasks: 0,
  })
  const [loading, setLoading] = useState(true)
  const [isMobile, setIsMobile] = useState(false)
 const router = useRouter();
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }

    handleResize()
    window.addEventListener("resize", handleResize)

    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const fetchAll = async () => {
    try {
      const [t, c, s] = await Promise.all([
        fetch("http://127.0.0.1:8000/tasks").then((r) => r.json()),
        fetch("http://127.0.0.1:8000/clients").then((r) => r.json()),
        fetch("http://127.0.0.1:8000/stats").then((r) => r.json()),
      ])
      setTasks(t)
      setClients(c)
      setStats(s)
    } catch {
      console.error("Backend not reachable")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  // admin auth
// Add this at the top of useEffect in both dashboard and clients pages
useEffect(() => {
  const token = localStorage.getItem("token")
  const user  = JSON.parse(localStorage.getItem("user") || "{}")
  if (!token || !user.is_admin) {
    router.push("/login")
    return
  }
  // ... rest of your fetchAll code
}, [])



  // admin auth end 

useEffect(() => {
  fetchAll()
  const interval = setInterval(fetchAll, 30000) // refresh every 30s
  return () => clearInterval(interval)
}, [])


  const updateStatus = async (id: number, status: string) => {
    await fetch(`http://127.0.0.1:8000/tasks/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    })
    fetchAll()
  }

  const pill = (
    text: string,
    colors: { bg: string; text: string; border: string }
  ) => (
    <span
      style={{
        fontSize: "11px",
        padding: "3px 8px",
        borderRadius: "6px",
        background: colors.bg,
        color: colors.text,
        border: `0.5px solid ${colors.border}`,
        fontWeight: "500",
        whiteSpace: "nowrap",
      }}
    >
      {text}
    </span>
  )

if (loading)
  return (
    <div className="flex">
      <Sidebar />
      <main
        className={`${
          isMobile ? "ml-0 p-4" : "ml-[220px] p-0"
        } flex-1 flex items-center justify-center h-screen`}
      >
        <p className="text-[13px] text-[#999]">Loading...</p>
      </main>
    </div>
  )

return (
  <div className="flex">
    <Sidebar />

    <main
      className={`${
        isMobile ? "ml-0 p-4" : "ml-[220px] px-9 py-8"
      } flex-1 min-h-screen bg-[#f9f9f8]`}
    >
      {/* Header */}
      <div className="mb-7">
        <h1
          className={`${
            isMobile ? "text-[18px]" : "text-[20px]"
          } font-medium tracking-[-0.3px]`}
        >
          Dashboard
        </h1>
        <p className="text-[13px] text-[#999] mt-1">
          Live overview of clients and tasks
        </p>
      </div>

      {/* Stats */}
      <div
        className={`grid ${
          isMobile ? "grid-cols-2" : "grid-cols-4"
        } gap-3 mb-7`}
      >
        {[
          { label: "Total Tasks", value: stats.total_tasks },
          { label: "Total Clients", value: stats.total_clients },
          { label: "Pending", value: stats.pending_tasks },
          { label: "Completed", value: stats.done_tasks },
        ].map(({ label, value }) => (
          <div
            key={label}
            className="bg-white border border-[#e8e8e6] rounded-[10px] px-5 py-4"
          >
            <div className="text-[11px] text-[#999] mb-2">
              {label}
            </div>
            <div className="text-2xl font-medium">{value}</div>
          </div>
        ))}
      </div>

      {/* Tasks Table */}
      <div className="bg-white border border-[#e8e8e6] rounded-[10px] overflow-x-auto mb-6">
        <div className="px-5 py-4 border-b border-[#e8e8e6] flex justify-between items-center">
          <span className="text-[13px] font-medium">Tasks</span>
          <span className="text-[11px] text-[#999]">
            {tasks.length} total
          </span>
        </div>

        {tasks.length === 0 ? (
          <div className="p-10 text-center text-[13px] text-[#bbb]">
            No tasks yet.
          </div>
        ) : (
          tasks.map((task, i) => (
            <div
              key={task.id}
              className={`px-5 py-[14px] flex flex-wrap items-center gap-[14px] ${
                i < tasks.length - 1
                  ? "border-b border-[#f0f0ef]"
                  : ""
              }`}
            >
              <div className="w-[22px] h-[22px] rounded-full bg-[#f3f4f6] border border-[#e8e8e6] flex items-center justify-center text-[9px] text-[#999] shrink-0">
                {task.id}
              </div>

              <div className="flex-1 min-w-[180px]">
                <div className="text-[13px] text-[#1a1a1a] break-words">
                  {task.description}
                </div>
                <div className="text-[11px] text-[#999] mt-[2px]">
                  {task.client} · {task.created_at}
                </div>
              </div>

              {task.trello_url && (
                <a
                  href={task.trello_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-[#3b5bdb] no-underline"
                >
                  Trello
                </a>
              )}

              <select
                value={task.status}
                onChange={(e) =>
                  updateStatus(task.id, e.target.value)
                }
                className="text-[11px] px-2 py-1 rounded-md border border-[#e8e8e6] bg-[#f9f9f8] text-[#1a1a1a] cursor-pointer"
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>

              {pill(
                task.status.replace("_", " "),
                statusColor[task.status] || statusColor.pending
              )}
            </div>
          ))
        )}
      </div>

      {/* Clients Table */}
      <div className="bg-white border border-[#e8e8e6] rounded-[10px] overflow-x-auto">
        <div className="px-5 py-4 border-b border-[#e8e8e6] flex justify-between items-center">
          <span className="text-[13px] font-medium">Clients</span>
          <span className="text-[11px] text-[#999]">
            {clients.length} total
          </span>
        </div>

        {clients.length === 0 ? (
          <div className="p-10 text-center text-[13px] text-[#bbb]">
            No clients yet.
          </div>
        ) : (
          clients.map((client, i) => (
            <div
              key={client.id}
              className={`px-5 py-[14px] flex flex-wrap items-center gap-[14px] ${
                i < clients.length - 1
                  ? "border-b border-[#f0f0ef]"
                  : ""
              }`}
            >
              <div className="w-8 h-8 rounded-full bg-[#e8f0fe] flex items-center justify-center text-[11px] font-medium text-[#3b5bdb] shrink-0">
                {client.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .slice(0, 2)
                  .toUpperCase()}
              </div>

              <div className="flex-1 min-w-[180px]">
                <div className="text-[13px] font-medium text-[#1a1a1a]">
                  {client.name}
                </div>
                <div className="text-[11px] text-[#999]">
                  {client.company || client.email || client.phone}
                </div>
              </div>

              <div className="text-[11px] text-[#999]">
                {client.task_count} task
                {client.task_count !== 1 ? "s" : ""}
              </div>

              {pill(
                client.channel,
                channelColor[client.channel] || channelColor.web
              )}

              <div className="text-[11px] text-[#bbb]">
                {client.created_at}
              </div>
            </div>
          ))
        )}
      </div>
    </main>
  </div>
)}
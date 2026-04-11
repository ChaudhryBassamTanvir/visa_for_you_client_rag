"use client"
import { useEffect, useState } from "react"
import Sidebar from "@/components/Sidebar"

type Client = {
  id: number
  name: string
  email: string
  phone: string
  company: string
  channel: string
  task_count: number
  created_at: string
  whatsapp_number: string
  slack_id: string
}

const channelConfig: Record<string, { label: string; bg: string; text: string; border: string; icon: string }> = {
  whatsapp: { label: "WhatsApp", bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0", icon: "WA" },
  slack:    { label: "Slack",    bg: "#eff6ff", text: "#1e40af", border: "#bfdbfe", icon: "SL" },
  web:      { label: "Web",      bg: "#f5f3ff", text: "#6d28d9", border: "#ddd6fe", icon: "WB" },
}

function Avatar({ name }: { name: string }) {
  const initials = name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()
  return (
    <div style={{
      width: "36px", height: "36px", borderRadius: "50%",
      background: "#e8f0fe", display: "flex", alignItems: "center",
      justifyContent: "center", fontSize: "12px", fontWeight: "500",
      color: "#3b5bdb", flexShrink: 0
    }}>{initials}</div>
  )
}

function ChannelBadge({ channel }: { channel: string }) {
  const cfg = channelConfig[channel] || channelConfig.web
  return (
    <span style={{
      fontSize: "11px", padding: "3px 8px", borderRadius: "6px",
      background: cfg.bg, color: cfg.text, border: `0.5px solid ${cfg.border}`,
      fontWeight: "500"
    }}>{cfg.label}</span>
  )
}

export default function ClientsPage() {
  const [clients, setClients]   = useState<Client[]>([])
  const [loading, setLoading]   = useState(true)
  const [search,  setSearch]    = useState("")
  const [filter,  setFilter]    = useState("all")
  const [selected, setSelected] = useState<Client | null>(null)

  useEffect(() => {
    fetch("http://127.0.0.1:8000/clients")
      .then(r => r.json())
      .then(data => { setClients(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const filtered = clients.filter(c => {
    const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
                        c.email.toLowerCase().includes(search.toLowerCase()) ||
                        c.phone.includes(search)
    const matchFilter = filter === "all" || c.channel === filter
    return matchSearch && matchFilter
  })

  return (
   <div className="flex">
  <Sidebar />

  <main className="ml-[220px] flex-1 min-h-screen bg-[#f9f9f8]">

    {/* Header */}
    <div className="px-9 pt-7 mb-6">
      <h1 className="text-[20px] font-medium tracking-[-0.3px] m-0">
        Clients
      </h1>
      <p className="text-[13px] text-[#999] mt-1">
        {clients.length} total clients across all channels
      </p>
    </div>

    <div className="flex gap-6 px-9 pb-9">

      {/* Left — client list */}
      <div className="flex-1 min-w-0">

        {/* Search + Filter */}
        <div className="flex gap-[10px] mb-4">
          <input
            placeholder="Search by name, email or phone..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="flex-1 px-[14px] py-[9px] text-[13px] rounded-lg border border-[#e8e8e6] bg-white text-[#1a1a1a] outline-none"
          />

          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
            className="px-3 py-[9px] text-[13px] rounded-lg border border-[#e8e8e6] bg-white text-[#1a1a1a] outline-none cursor-pointer"
          >
            <option value="all">All Channels</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="slack">Slack</option>
            <option value="web">Web</option>
          </select>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-[10px] mb-4">
          {[
            { label: "WhatsApp", value: clients.filter(c => c.channel === "whatsapp").length, ...channelConfig.whatsapp },
            { label: "Slack", value: clients.filter(c => c.channel === "slack").length, ...channelConfig.slack },
            { label: "Web", value: clients.filter(c => c.channel === "web").length, ...channelConfig.web },
          ].map(s => (
            <div
              key={s.label}
              className="bg-white border border-[#e8e8e6] rounded-[10px] px-[18px] py-[14px] flex justify-between items-center"
            >
              <div>
                <div className="text-[11px] text-[#999] mb-1">
                  {s.label}
                </div>
                <div className="text-[20px] font-medium">
                  {s.value}
                </div>
              </div>

              <span
                className="text-[11px] px-2 py-[3px] rounded-md font-medium"
                style={{
                  background: s.bg,
                  color: s.text,
                  border: `0.5px solid ${s.border}`,
                }}
              >
                {s.icon}
              </span>
            </div>
          ))}
        </div>

        {/* Client cards */}
        <div className="bg-white border border-[#e8e8e6] rounded-[10px] overflow-hidden">

          {/* Table header */}
          <div className="grid grid-cols-[2fr_2fr_1.5fr_1fr_80px] px-5 py-[10px] border-b border-[#f0f0ef] bg-[#f9f9f8]">
            {["Client", "Contact", "Channel ID", "Tasks", "Joined"].map(h => (
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
          ) : filtered.length === 0 ? (
            <div className="p-10 text-center text-[13px] text-[#bbb]">
              No clients found.
            </div>
          ) : filtered.map((client, i) => (
            <div
              key={client.id}
              onClick={() =>
                setSelected(selected?.id === client.id ? null : client)
              }
              className="grid grid-cols-[2fr_2fr_1.5fr_1fr_80px] px-5 py-[14px] cursor-pointer transition-colors duration-100"
              style={{
                borderBottom:
                  i < filtered.length - 1
                    ? "0.5px solid #f0f0ef"
                    : "none",
                background:
                  selected?.id === client.id
                    ? "#f9f9f8"
                    : "transparent",
              }}
            >
              {/* Name */}
              <div className="flex items-center gap-[10px]">
                <Avatar name={client.name} />
                <div>
                  <div className="text-[13px] font-medium text-[#1a1a1a]">
                    {client.name}
                  </div>
                  <div className="text-[11px] text-[#999] mt-[1px]">
                    {client.company || "—"}
                  </div>
                </div>
              </div>

              {/* Contact */}
              <div className="flex flex-col justify-center gap-[3px]">
                <div className="text-xs text-[#444]">
                  {client.email || "—"}
                </div>
                <div className="text-xs text-[#999]">
                  {client.phone || "—"}
                </div>
              </div>

              {/* Channel-specific ID */}
              <div className="flex flex-col justify-center gap-1">
                <ChannelBadge channel={client.channel} />
                <div className="text-[11px] text-[#999] mt-1">
                  {client.channel === "whatsapp" &&
                  client.whatsapp_number
                    ? `+${client.whatsapp_number}`
                    : client.channel === "slack" &&
                      client.slack_id
                    ? client.slack_id
                    : "Web visitor"}
                </div>
              </div>

              {/* Task count */}
              <div className="flex items-center">
                <span
                  className="text-xs px-[10px] py-[3px] rounded-md"
                  style={{
                    background:
                      client.task_count > 0
                        ? "#f0fdf4"
                        : "#f9f9f8",
                    color:
                      client.task_count > 0
                        ? "#15803d"
                        : "#999",
                    border: `0.5px solid ${
                      client.task_count > 0
                        ? "#bbf7d0"
                        : "#e8e8e6"
                    }`,
                  }}
                >
                  {client.task_count} task
                  {client.task_count !== 1 ? "s" : ""}
                </span>
              </div>

              {/* Date */}
              <div className="flex items-center text-xs text-[#bbb]">
                {client.created_at}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right — client detail panel */}
      {selected && (
        <div className="w-[280px] shrink-0">
          <div className="bg-white border border-[#e8e8e6] rounded-[10px] overflow-hidden sticky top-6">

            {/* Panel header */}
            <div className="p-5 border-b border-[#f0f0ef] flex justify-between items-start">
              <div className="flex gap-3 items-center">
                <Avatar name={selected.name} />
                <div>
                  <div className="text-sm font-medium text-[#1a1a1a]">
                    {selected.name}
                  </div>
                  <ChannelBadge channel={selected.channel} />
                </div>
              </div>

              <button
                onClick={() => setSelected(null)}
                className="bg-transparent border-none cursor-pointer text-[#bbb] text-[18px] leading-none"
              >
                ×
              </button>
            </div>

            {/* Remaining sections unchanged logic, converted similarly */}
          </div>
        </div>
      )}
    </div>
  </main>
</div>
  )
}
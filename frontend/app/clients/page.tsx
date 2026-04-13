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
    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-[11px] font-semibold text-blue-600 shrink-0">
      {initials}
    </div>
  )
}

function ChannelBadge({ channel }: { channel: string }) {
  const cfg = channelConfig[channel] || channelConfig.web
  return (
    <span
      className="text-[11px] px-2 py-0.5 rounded-md font-medium border"
      style={{ background: cfg.bg, color: cfg.text, borderColor: cfg.border }}
    >
      {cfg.label}
    </span>
  )
}

export default function ClientsPage() {
  const [clients, setClients]   = useState<Client[]>([])
  const [loading, setLoading]   = useState(true)
  const [search,  setSearch]    = useState("")
  const [filter,  setFilter]    = useState("all")
  const [selected, setSelected] = useState<Client | null>(null)
  const [showAdd, setShowAdd]   = useState(false)
  const [newClient, setNewClient] = useState({
    name: "", email: "", phone: "", company: "",
    channel: "whatsapp", cgpa: "", degree: "", target_country: ""
  })

  const addClient = async () => {
    await fetch("http://127.0.0.1:8000/clients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newClient)
    })
    setShowAdd(false)
    setNewClient({ name: "", email: "", phone: "", company: "", channel: "whatsapp", cgpa: "", degree: "", target_country: "" })
    fetch("http://127.0.0.1:8000/clients").then(r => r.json()).then(setClients)
  }

  const deleteClient = async (id: number) => {
    if (!confirm("Delete this client?")) return
    await fetch(`http://127.0.0.1:8000/clients/${id}`, { method: "DELETE" })
    setClients(prev => prev.filter(c => c.id !== id))
    if (selected?.id === id) setSelected(null)
  }

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
    <div className="flex bg-white min-h-screen">
      <Sidebar />

      <main className="ml-[240px] flex-1 min-h-screen bg-gray-50">

        {/* Page header */}
        <div className="px-8 pt-8 mb-6">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">👥</span>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">Clients</h1>
          </div>
          <p className="text-sm text-gray-400 ml-7">{clients.length} total clients across all channels</p>
        </div>

        {/* Controls */}
        <div className="px-8 mb-5 flex items-center gap-3">
          <input
            placeholder="Search by name, email or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-4 py-2.5 text-sm rounded-lg border border-gray-200 bg-white outline-none focus:ring-2 focus:ring-gray-900 transition placeholder:text-gray-300"
          />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2.5 text-sm rounded-lg border border-gray-200 bg-white outline-none focus:ring-2 focus:ring-gray-900 transition text-gray-600"
          >
            <option value="all">All Channels</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="slack">Slack</option>
            <option value="web">Web</option>
          </select>
          <button
            onClick={() => setShowAdd(true)}
            className="px-4 py-2.5 bg-black text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition whitespace-nowrap"
          >
            + Add Client
          </button>
        </div>

        <div className="flex gap-5 px-8 pb-8">
          {/* Left */}
          <div className="flex-1 min-w-0">

            {/* Channel stats */}
            <div className="grid grid-cols-3 gap-3 mb-5">
              {[
                { label: "WhatsApp", value: clients.filter(c => c.channel === "whatsapp").length, ...channelConfig.whatsapp },
                { label: "Slack",    value: clients.filter(c => c.channel === "slack").length,    ...channelConfig.slack },
                { label: "Web",      value: clients.filter(c => c.channel === "web").length,      ...channelConfig.web },
              ].map((s) => (
                <div key={s.label} className="bg-white rounded-xl border border-gray-200 px-5 py-4 flex items-center justify-between hover:shadow-sm transition-shadow">
                  <div>
                    <div className="text-xs text-gray-400 mb-1">{s.label}</div>
                    <div className="text-2xl font-bold text-gray-900">{s.value}</div>
                  </div>
                  <span
                    className="text-[11px] px-2 py-1 rounded-md font-semibold border"
                    style={{ background: s.bg, color: s.text, borderColor: s.border }}
                  >
                    {s.icon}
                  </span>
                </div>
              ))}
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              {/* Col headers */}
              <div className="grid grid-cols-[2fr_2fr_1.5fr_1fr_110px] px-5 py-2.5 border-b border-gray-100 bg-gray-50">
                {["Client", "Contact", "Channel", "Tasks", "Joined"].map(h => (
                  <div key={h} className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">{h}</div>
                ))}
              </div>

              {loading ? (
                <div className="p-12 text-center text-sm text-gray-300">Loading...</div>
              ) : filtered.length === 0 ? (
                <div className="p-12 text-center text-sm text-gray-300">No clients found.</div>
              ) : (
                filtered.map((client, i) => (
                  <div
                    key={client.id}
                    onClick={() => setSelected(selected?.id === client.id ? null : client)}
                    className={`grid grid-cols-[2fr_2fr_1.5fr_1fr_110px] px-5 py-3.5 cursor-pointer hover:bg-gray-50 transition-colors ${
                      i < filtered.length - 1 ? "border-b border-gray-100" : ""
                    } ${selected?.id === client.id ? "bg-gray-50" : ""}`}
                  >
                    {/* Client */}
                    <div className="flex items-center gap-2.5">
                      <Avatar name={client.name} />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{client.name}</div>
                        <div className="text-[11px] text-gray-400">{client.company || "—"}</div>
                      </div>
                    </div>

                    {/* Contact */}
                    <div className="flex flex-col justify-center gap-0.5">
                      <div className="text-xs text-gray-600">{client.email || "—"}</div>
                      <div className="text-xs text-gray-400">{client.phone || "—"}</div>
                    </div>

                    {/* Channel */}
                    <div className="flex flex-col justify-center gap-1">
                      <ChannelBadge channel={client.channel} />
                      <div className="text-[10px] text-gray-400">
                        {client.channel === "whatsapp" ? `+${client.whatsapp_number}`
                          : client.channel === "slack" ? client.slack_id
                          : "Web visitor"}
                      </div>
                    </div>

                    {/* Tasks */}
                    <div className="flex items-center">
                      <span className="text-xs px-2.5 py-1 rounded-md border border-gray-200 text-gray-600 font-medium">
                        {client.task_count} tasks
                      </span>
                    </div>

                    {/* Joined + delete */}
                    <div className="flex flex-col gap-1.5 justify-center">
                      <div className="text-[11px] text-gray-400">{client.created_at}</div>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteClient(client.id) }}
                        className="text-[10px] text-red-500 border border-red-100 bg-red-50 hover:bg-red-100 rounded-md px-2 py-0.5 transition-colors w-fit"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Detail panel */}
          {selected && (
            <div className="w-[270px] shrink-0">
              <div className="bg-white border border-gray-200 rounded-xl sticky top-6">
                <div className="p-4 border-b border-gray-100 flex items-start justify-between">
                  <div className="flex gap-3 items-center">
                    <Avatar name={selected.name} />
                    <div>
                      <div className="text-sm font-semibold text-gray-900">{selected.name}</div>
                      <ChannelBadge channel={selected.channel} />
                    </div>
                  </div>
                  <button onClick={() => setSelected(null)} className="text-gray-300 hover:text-gray-500 text-xl leading-none transition-colors">×</button>
                </div>

                <div className="p-4 flex flex-col gap-3">
                  {[
                    { label: "Email",   value: selected.email   || "—" },
                    { label: "Phone",   value: selected.phone   || "—" },
                    { label: "Company", value: selected.company || "—" },
                    { label: "Tasks",   value: `${selected.task_count} tasks` },
                    { label: "Joined",  value: selected.created_at },
                  ].map(({ label, value }) => (
                    <div key={label} className="flex justify-between items-start gap-2">
                      <span className="text-xs text-gray-400">{label}</span>
                      <span className="text-xs text-gray-800 font-medium text-right max-w-[160px] truncate">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Add client modal */}
        {showAdd && (
          <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl border border-gray-200 shadow-xl w-full max-w-md p-6">
              <div className="flex items-center justify-between mb-5">
                <h2 className="text-base font-semibold text-gray-900">Add New Client</h2>
                <button onClick={() => setShowAdd(false)} className="text-gray-300 hover:text-gray-500 text-xl transition-colors">×</button>
              </div>
              <div className="flex flex-col gap-3">
                {[
                  { key: "name",           label: "Full Name",       type: "text",   placeholder: "Muhammad Ahmed" },
                  { key: "email",          label: "Email",           type: "email",  placeholder: "ahmed@example.com" },
                  { key: "phone",          label: "Phone",           type: "text",   placeholder: "+92 300 1234567" },
                  { key: "company",        label: "Company",         type: "text",   placeholder: "Company name" },
                  { key: "cgpa",           label: "CGPA",            type: "text",   placeholder: "3.2" },
                  { key: "degree",         label: "Degree",          type: "text",   placeholder: "BS Computer Science" },
                  { key: "target_country", label: "Target Country",  type: "text",   placeholder: "Germany" },
                ].map(f => (
                  <div key={f.key}>
                    <label className="block text-xs font-medium text-gray-600 mb-1">{f.label}</label>
                    <input
                      type={f.type}
                      placeholder={f.placeholder}
                      value={(newClient as any)[f.key]}
                      onChange={e => setNewClient({ ...newClient, [f.key]: e.target.value })}
                      className="w-full px-3.5 py-2 text-sm border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-gray-900 transition placeholder:text-gray-300"
                    />
                  </div>
                ))}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Channel</label>
                  <select
                    value={newClient.channel}
                    onChange={e => setNewClient({ ...newClient, channel: e.target.value })}
                    className="w-full px-3.5 py-2 text-sm border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-gray-900 transition text-gray-700"
                  >
                    <option value="whatsapp">WhatsApp</option>
                    <option value="slack">Slack</option>
                    <option value="web">Web</option>
                  </select>
                </div>
                <div className="flex gap-2 pt-1">
                  <button onClick={() => setShowAdd(false)} className="flex-1 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition">Cancel</button>
                  <button onClick={addClient} className="flex-1 py-2.5 bg-black text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition">Add Client</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
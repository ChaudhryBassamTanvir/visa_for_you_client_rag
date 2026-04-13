"use client"
import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Send, LogOut } from "lucide-react"

type Message = { role: string; content: string; created_at?: string }

export default function VisaChatPage() {
  const router  = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput]       = useState("")
  const [loading, setLoading]   = useState(false)
  const [user, setUser]         = useState<any>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const token    = localStorage.getItem("token")
    const userData = localStorage.getItem("user")
    if (!token) { router.push("/login"); return }
    const parsed = userData ? JSON.parse(userData) : {}
    setUser(parsed)
    if (parsed.is_admin) { router.push("/dashboard"); return }

    fetch("http://127.0.0.1:8000/visa/history", {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => {
        if (data.length === 0) {
          setMessages([{
            role: "ai",
            content: `Welcome to Visa For You! 🎓\n\nI'm your personal study abroad consultant. I'm here to help you plan your education journey abroad.\n\nTo get started, could you please share your CGPA and the degree you've completed?`
          }])
        } else {
          setMessages(data)
        }
      })
      .catch(() => {
        setMessages([{ role: "ai", content: "Welcome to Visa For You! 🎓 How can I help you today?" }])
      })
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const token = localStorage.getItem("token")
    const userMsg = input.trim()
    setInput("")
    setMessages(prev => [...prev, { role: "user", content: userMsg }])
    setLoading(true)

    try {
      const res  = await fetch("http://127.0.0.1:8000/visa/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ message: userMsg })
      })
      const data = await res.json()
      if (res.status === 401) { router.push("/login"); return }
      setMessages(prev => [...prev, { role: "ai", content: data.response }])
    } catch {
      setMessages(prev => [...prev, { role: "ai", content: "Connection error. Please try again." }])
    }
    setLoading(false)
  }

  const logout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    router.push("/login")
  }

  const initials = user?.name
    ?.split(" ")
    .map((n: string) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "U"

  return (
    <div className="flex h-screen bg-white overflow-hidden">

      {/* ── SIDEBAR ── */}
      <div className="w-[240px] bg-gray-50 border-r border-gray-200 flex flex-col shrink-0">

        {/* Logo */}
        <div className="px-4 py-4 border-b border-gray-200 flex items-center gap-2.5">
          <img src="/logo.jpg" alt="Visa For You" className="h-7 w-7 object-contain rounded-md" />
          <span className="text-sm font-semibold text-gray-900 tracking-tight">Visa For You</span>
        </div>

        {/* Nav items */}
        <div className="p-2 border-b border-gray-200">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-gray-200/70 text-xs text-gray-700 font-medium cursor-default">
            <span>💬</span> Visa Chat
          </div>
        </div>

        {/* Profile section */}
        <div className="p-3 flex-1">
          <p className="text-[10px] text-gray-400 uppercase tracking-widest mb-3 px-2 font-semibold">Your Profile</p>

          {/* Avatar card */}
          <div className="flex items-center gap-2.5 px-2 py-2 rounded-lg mb-4">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-xs font-semibold text-blue-600 shrink-0">
              {initials}
            </div>
            <div className="min-w-0">
              <div className="text-xs font-medium text-gray-900 truncate">{user?.name}</div>
              <div className="text-[10px] text-gray-400 truncate">{user?.email}</div>
            </div>
          </div>

          {/* Profile fields */}
          <div className="flex flex-col gap-1">
            {[
              { label: "CGPA",   value: user?.cgpa   || "Not set", icon: "📊" },
              { label: "Degree", value: user?.degree  || "Not set", icon: "🎓" },
              { label: "Phone",  value: user?.phone   || "Not set", icon: "📱" },
            ].map(({ label, value, icon }) => (
              <div key={label} className="flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-gray-100 transition-colors">
                <span className="flex items-center gap-1.5 text-xs text-gray-500">
                  <span className="text-[11px]">{icon}</span>
                  {label}
                </span>
                <span className="text-xs text-gray-700 font-medium max-w-[110px] truncate text-right">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Logout */}
        <div className="p-3 border-t border-gray-200">
          <button
            onClick={logout}
            className="w-full py-2 flex items-center justify-center gap-2 rounded-lg text-xs text-gray-500 hover:bg-gray-200 hover:text-gray-700 transition-colors"
          >
            <LogOut size={12} /> Sign out
          </button>
        </div>
      </div>

      {/* ── CHAT AREA ── */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Header */}
        <div className="px-6 py-3.5 bg-white border-b border-gray-200 flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold text-gray-900">Study Abroad Consultant</div>
            <div className="text-xs text-gray-400 mt-0.5">Powered by Visa For You AI</div>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-gray-400">Online</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-5">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 items-end ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {/* AI avatar */}
              {msg.role !== "user" && (
                <div className="w-7 h-7 rounded-full overflow-hidden shrink-0 border border-gray-200 mb-0.5">
                  <img src="/logo.jpg" alt="AI" className="w-full h-full object-cover" />
                </div>
              )}

              <div className={`flex flex-col gap-1 max-w-[65%] ${msg.role === "user" ? "items-end" : "items-start"}`}>
                {/* Role label */}
                <span className="text-[10px] text-gray-400 px-1">
                  {msg.role === "user" ? "You" : "Consultant"}
                </span>

                {/* Bubble */}
                <div
                  className={`px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-gray-900 text-white rounded-2xl rounded-br-sm"
                      : "bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-bl-sm shadow-sm"
                  }`}
                >
                  {msg.content}
                </div>

                {/* Timestamp */}
                {msg.created_at && (
                  <span className="text-[10px] text-gray-400 px-1">{msg.created_at}</span>
                )}
              </div>

              {/* User avatar */}
              {msg.role === "user" && (
                <div className="w-7 h-7 rounded-full bg-gray-900 flex items-center justify-center text-white text-[10px] font-semibold shrink-0 mb-0.5">
                  {initials}
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="flex gap-3 items-end">
              <div className="w-7 h-7 rounded-full overflow-hidden shrink-0 border border-gray-200">
                <img src="/logo.jpg" alt="AI" className="w-full h-full object-cover" />
              </div>
              <div className="flex flex-col gap-1 items-start">
                <span className="text-[10px] text-gray-400 px-1">Consultant</span>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-6 py-4 bg-white border-t border-gray-200">
          <div className="flex gap-3 items-center">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()}
              placeholder="Ask about study abroad, countries, scholarships..."
              className="flex-1 px-4 py-2.5 text-sm rounded-lg border border-gray-200 bg-gray-50 text-gray-900 outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition placeholder:text-gray-300"
            />
            <button
              onClick={sendMessage}
              disabled={loading}
              className="px-4 py-2.5 bg-black text-white rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-gray-800 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send size={14} />
              Send
            </button>
          </div>
          <p className="text-[11px] text-gray-400 mt-2.5 text-center">
            Last 60 messages are saved · Book appointments by asking the consultant
          </p>
        </div>
      </div>
    </div>
  )
}
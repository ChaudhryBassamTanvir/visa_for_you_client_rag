"use client"
import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Send, LogOut, User } from "lucide-react"

type Message = { role: string; content: string; created_at?: string }

export default function VisaChatPage() {
  const router  = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput]       = useState("")
  const [loading, setLoading]   = useState(false)
  const [user, setUser]         = useState<any>(null)
  const [showProfile, setShowProfile] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const token    = localStorage.getItem("token")
    const userData = localStorage.getItem("user")
    if (!token) { router.push("/login"); return }
    const parsed = userData ? JSON.parse(userData) : {}
    setUser(parsed)
    if (parsed.is_admin) { router.push("/dashboard"); return }

    // Load chat history
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

  return (
<div className="flex h-screen bg-[#f9f9f8]">

  {/* Sidebar */}
  <div className="w-[260px] bg-white border-r border-[#e8e8e6] flex flex-col shrink-0">

    {/* Logo */}
    <div className="p-5 border-b border-[#e8e8e6] text-center">
      <img
        src="/logo.jpg"
        alt="Visa For You"
        className="h-12 object-contain"
      />
    </div>

    {/* User profile */}
    <div className="p-4 border-b border-[#e8e8e6]">
      <div className="flex items-center gap-[10px] p-[10px] bg-[#f9f9f8] rounded-lg">
        <div className="w-9 h-9 rounded-full bg-[#e8f0fe] flex items-center justify-center text-[13px] font-medium text-[#3b5bdb] shrink-0">
          {user?.name
            ?.split(" ")
            .map((n: string) => n[0])
            .join("")
            .slice(0, 2)
            .toUpperCase() || "U"}
        </div>

        <div className="flex-1 min-w-0">
          <div className="text-[13px] font-medium text-[#1a1a1a] overflow-hidden text-ellipsis whitespace-nowrap">
            {user?.name}
          </div>
          <div className="text-[11px] text-[#999] overflow-hidden text-ellipsis whitespace-nowrap">
            {user?.email}
          </div>
        </div>
      </div>
    </div>

    {/* Profile info */}
    <div className="p-4 flex-1">
      <p className="text-[10px] text-[#bbb] uppercase tracking-[1px] mb-3 font-medium">
        Your Profile
      </p>

      {[
        { label: "CGPA", value: user?.cgpa || "Not set" },
        { label: "Degree", value: user?.degree || "Not set" },
        { label: "Phone", value: user?.phone || "Not set" },
      ].map(({ label, value }) => (
        <div
          key={label}
          className="flex justify-between mb-[10px]"
        >
          <span className="text-xs text-[#999]">
            {label}
          </span>
          <span className="text-xs text-[#1a1a1a] font-medium max-w-[140px] text-right overflow-hidden text-ellipsis whitespace-nowrap">
            {value}
          </span>
        </div>
      ))}
    </div>

    {/* Logout */}
    <div className="p-4 border-t border-[#e8e8e6]">
      <button
        onClick={logout}
        className="w-full py-[9px] flex items-center justify-center gap-2 bg-transparent border border-[#e8e8e6] rounded-lg text-[13px] text-[#666] cursor-pointer"
      >
        <LogOut size={13} /> Sign Out
      </button>
    </div>
  </div>

  {/* Chat area */}
  <div className="flex-1 flex flex-col overflow-hidden">

    {/* Header */}
    <div className="px-6 py-4 bg-white border-b border-[#e8e8e6] flex items-center justify-between">
      <div>
        <div className="text-sm font-medium text-[#1a1a1a]">
          Study Abroad Consultant
        </div>
        <div className="text-[11px] text-[#999]">
          Powered by Visa For You AI
        </div>
      </div>

      <div className="flex items-center gap-[6px]">
        <div className="w-[7px] h-[7px] rounded-full bg-[#22c55e]" />
        <span className="text-[11px] text-[#999]">
          Online
        </span>
      </div>
    </div>

    {/* Messages */}
    <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`flex gap-[10px] items-start ${
            msg.role === "user"
              ? "justify-end"
              : "justify-start"
          }`}
        >
          {msg.role !== "user" && (
            <div className="w-[30px] h-[30px] rounded-full overflow-hidden shrink-0 border border-[#e8e8e6]">
              <img
                src="/logo.jpg"
                alt="AI"
                className="w-full h-full object-cover"
              />
            </div>
          )}

          <div
            className={`max-w-[68%] px-[15px] py-[11px] text-[13px] leading-[1.7] whitespace-pre-wrap ${
              msg.role === "user"
                ? "bg-[#1a1a1a] text-white rounded-[12px_0_12px_12px]"
                : "bg-white text-[#1a1a1a] border border-[#e8e8e6] rounded-[0_12px_12px_12px]"
            }`}
          >
            {msg.content}

            {msg.created_at && (
              <div
                className="text-[10px] mt-[6px]"
                style={{
                  color:
                    msg.role === "user"
                      ? "rgba(255,255,255,0.5)"
                      : "#bbb",
                }}
              >
                {msg.created_at}
              </div>
            )}
          </div>
        </div>
      ))}

      {loading && (
        <div className="flex gap-[10px] items-start">
          <div className="w-[30px] h-[30px] rounded-full overflow-hidden shrink-0 border border-[#e8e8e6]">
            <img
              src="/logo.jpg"
              alt="AI"
              className="w-full h-full object-cover"
            />
          </div>

          <div className="bg-white border border-[#e8e8e6] rounded-[0_12px_12px_12px] px-[15px] py-[11px] text-[13px] text-[#999]">
            Consulting knowledge base...
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>

    {/* Input */}
    <div className="px-6 py-4 bg-white border-t border-[#e8e8e6]">
      <div className="flex gap-[10px]">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Ask about study abroad, countries, scholarships..."
          className="flex-1 px-4 py-[11px] text-[13px] rounded-lg border border-[#e8e8e6] bg-[#f9f9f8] text-[#1a1a1a] outline-none"
        />

        <button
          onClick={sendMessage}
          disabled={loading}
          className={`px-5 py-[11px] rounded-lg flex items-center gap-[6px] text-[13px] font-medium ${
            loading
              ? "bg-[#e0e0e0] text-[#999] cursor-not-allowed"
              : "bg-[#1a1a1a] text-white cursor-pointer"
          }`}
        >
          <Send size={13} /> Send
        </button>
      </div>

      <p className="text-[11px] text-[#bbb] mt-2 text-center">
        Last 60 messages are saved · Book appointments by asking the consultant
      </p>
    </div>
  </div>
</div>
  )
}
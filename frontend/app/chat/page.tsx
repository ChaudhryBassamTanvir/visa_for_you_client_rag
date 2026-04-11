"use client"
import { useState, useRef, useEffect } from "react"
import Sidebar from "@/components/Sidebar"
import { Send } from "lucide-react"

type Message = {
  role: "user" | "ai"
  content: string
  isTask?: boolean
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "ai", content: "Hello! I'm your AI assistant. Tell me about your project and I'll gather all requirements before creating a task for the team." }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput("")
    setMessages(prev => [...prev, { role: "user", content: userMsg }])
    setLoading(true)

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, user_id: "web_user", channel: "web" }),
      })
      const data = await res.json()
      const reply = data.response || "Sorry, something went wrong."
      const isTask = reply.includes("Trello") || reply.includes("✅")
      setMessages(prev => [...prev, { role: "ai", content: reply, isTask }])
    } catch {
      setMessages(prev => [...prev, { role: "ai", content: "Connection error. Make sure the backend is running." }])
    } finally {
      setLoading(false)
    }
  }

  return (
  <div className="flex">
  <Sidebar />

  <main className="ml-[220px] flex-1 flex flex-col h-screen">
    
    {/* Header */}
    <div className="px-7 py-4 border-b border-[#e8e8e6] flex items-center justify-between bg-white">
      <div>
        <div className="text-sm font-medium">Client Chat</div>
        <div className="text-[11px] text-[#999]">AI Agent is online</div>
      </div>

      <div className="flex items-center gap-[6px]">
        <div className="w-[7px] h-[7px] rounded-full bg-[#22c55e]" />
        <span className="text-[11px] text-[#999]">Connected</span>
      </div>
    </div>

    {/* Messages */}
    <div className="flex-1 overflow-y-auto px-7 py-6 flex flex-col gap-4 bg-white">
      {messages.map((msg, i) => (
        <div key={i}>
          {msg.isTask && (
            <div
              className="flex items-center gap-2 px-[14px] py-2 bg-[#f0fdf4] border border-[#bbf7d0] rounded-lg mb-2"
            >
              <span className="text-xs text-[#15803d] font-medium">
                Task created in Trello · Team notified on Slack
              </span>
            </div>
          )}

          <div
            className={`flex gap-[10px] items-start ${
              msg.role === "user"
                ? "justify-end"
                : "justify-start"
            }`}
          >
            {msg.role === "ai" && (
              <div
                className="w-7 h-7 rounded-full bg-[#f3f4f6] border border-[#e8e8e6] flex items-center justify-center text-[10px] font-medium text-[#666] shrink-0"
              >
                AI
              </div>
            )}

            <div
              className={`max-w-[68%] px-[14px] py-[10px] text-[13px] leading-[1.7] whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-[#1a1a1a] text-white rounded-[12px_0_12px_12px]"
                  : "bg-[#f9f9f8] text-[#1a1a1a] border border-[#e8e8e6] rounded-[0_12px_12px_12px]"
              }`}
            >
              {msg.content}
            </div>
          </div>
        </div>
      ))}

      {loading && (
        <div className="flex gap-[10px] items-start">
          <div className="w-7 h-7 rounded-full bg-[#f3f4f6] border border-[#e8e8e6] flex items-center justify-center text-[10px] text-[#666]">
            AI
          </div>

          <div className="bg-[#f9f9f8] border border-[#e8e8e6] rounded-[0_12px_12px_12px] px-4 py-3 text-[13px] text-[#999]">
            Thinking...
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>

    {/* Input */}
    <div className="px-7 py-4 border-t border-[#e8e8e6] bg-white">
      <div className="flex gap-[10px] items-center">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Type your message..."
          className="flex-1 px-[14px] py-[10px] text-[13px] rounded-lg border border-[#e8e8e6] bg-[#f9f9f8] text-[#1a1a1a] outline-none"
        />

        <button
          onClick={sendMessage}
          disabled={loading}
          className={`px-[18px] py-[10px] rounded-lg text-[13px] font-medium flex items-center gap-[6px] ${
            loading
              ? "bg-[#e0e0e0] text-[#999] cursor-not-allowed"
              : "bg-[#1a1a1a] text-white cursor-pointer"
          }`}
        >
          <Send size={13} /> Send
        </button>
      </div>
    </div>
  </main>
</div>
  )
}
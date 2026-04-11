import Link from "next/link"
import Footer from "@/components/Footer"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col justify-between bg-gradient-to-br from-gray-50 to-gray-100">

      {/* MAIN SECTION */}
      <div className="flex flex-col items-center justify-center flex-1 px-6 text-center">
        
        {/* Badge */}
        <span className="mb-4 px-4 py-1 text-xs bg-black text-white rounded-full">
          AI Powered Automation
        </span>

        {/* Heading */}
        <h1 className="text-4xl md:text-5xl font-medium tracking-tight text-gray-900">
          AI Client Management Agent
        </h1>

        {/* Subtext */}
        <p className="mt-4 text-gray-500 max-w-xl text-base">
          Automate client communication, task creation, and billing with a powerful AI agent built using LangChain and Ollama.
        </p>
  
        {/* Buttons */}
        <div className="mt-8 flex gap-4">
          <Link
            href="/chat"
            className="px-6 py-3 bg-black text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition"
          >
            Open Chat
          </Link>

          <Link
            href="/dashboard"
            className="px-6 py-3 bg-white text-gray-900 border border-gray-300 rounded-lg text-sm hover:bg-gray-100 transition"
          >
            Dashboard
          </Link>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 max-w-5xl w-full">
          
          <div className="p-6 bg-white rounded-2xl shadow-sm border hover:shadow-md transition">
            <h3 className="text-lg font-medium">💬 Smart Chat</h3>
            <p className="text-sm text-gray-500 mt-2">
              Talk to clients automatically via Slack or Web Chat.
            </p>
          </div>

          <div className="p-6 bg-white rounded-2xl shadow-sm border hover:shadow-md transition">
            <h3 className="text-lg font-medium">📋 Task Automation</h3>
            <p className="text-sm text-gray-500 mt-2">
              Convert client messages into actionable tasks instantly.
            </p>
          </div>

          <div className="p-6 bg-white rounded-2xl shadow-sm border hover:shadow-md transition">
            <h3 className="text-lg font-medium">💰 Billing Ready</h3>
            <p className="text-sm text-gray-500 mt-2">
              Handle pricing queries and generate billing workflows.
            </p>
          </div>

        </div>
      </div>

      {/* FOOTER */}
      <Footer />
    </div>
  )
}
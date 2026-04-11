"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import Link from "next/link"

export default function LoginPage() {
  const router = useRouter()
  const [form, setForm] = useState({ email: "", password: "" })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true); setError("")
    try {
      const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail); setLoading(false); return }
      localStorage.setItem("token", data.token)
      localStorage.setItem("user", JSON.stringify(data))
      if (data.is_admin) router.push("/dashboard")
      else router.push("/visa-chat")
    } catch { setError("Connection error") }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-[#f9f9f8] flex items-center justify-center p-5">
      <div className="bg-white border border-[#e8e8e6] rounded-2xl p-10 w-full max-w-[400px]">

        {/* Logo */}
        <div className="text-center mb-8">
          <img
            src="/logo.jpg"
            alt="Visa For You"
            className="h-[60px] object-contain mb-3"
          />
          <p className="text-[13px] text-[#999] m-0">
            Sign in to your account
          </p>
        </div>

        {error && (
          <div className="py-[10px] px-[14px] bg-[#fef2f2] border border-[#fecaca] rounded-lg text-[13px] text-[#dc2626] mb-4">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-[14px]">
          <div>
            <label className="text-xs text-[#666] block mb-[6px]">
              Email
            </label>
            <input
              type="email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              onKeyDown={e => e.key === "Enter" && handleSubmit()}
              placeholder="your@email.com"
              className="w-full py-[10px] px-[14px] text-sm rounded-lg border border-[#e8e8e6] bg-[#f9f9f8] outline-none box-border"
            />
          </div>

          <div>
            <label className="text-xs text-[#666] block mb-[6px]">
              Password
            </label>
            <input
              type="password"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              onKeyDown={e => e.key === "Enter" && handleSubmit()}
              placeholder="••••••••"
              className="w-full py-[10px] px-[14px] text-sm rounded-lg border border-[#e8e8e6] bg-[#f9f9f8] outline-none box-border"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`py-[11px] text-white border-none rounded-lg text-sm font-medium mt-1 ${
              loading
                ? "bg-[#ccc] cursor-not-allowed"
                : "bg-[#1a1a1a] cursor-pointer"
            }`}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </div>

        <p className="text-center text-[13px] text-[#999] mt-6">
          Don't have an account?{" "}
          <Link
            href="/signup"
            className="text-[#1a1a1a] font-medium no-underline"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
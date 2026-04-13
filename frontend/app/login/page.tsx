"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"

export default function LoginPage() {
  const router = useRouter()
  const [form, setForm] = useState({ email: "", password: "" })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

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
    <div className="min-h-screen bg-white flex">

      {/* ── Left branding panel ── */}
      <div className="hidden lg:flex lg:w-[45%] bg-gray-950 flex-col justify-between p-10">

        {/* Logo */}
        <div className="flex items-center gap-3">
          <img src="/logo.jpg" alt="Visa For You" className="h-8 w-8 object-contain rounded-lg" />
          <span className="text-white font-semibold text-sm tracking-tight">Visa For You</span>
        </div>

        {/* Quote */}
        <div>
          <blockquote className="text-gray-300 text-2xl font-medium leading-snug tracking-tight mb-6">
            "Your visa journey,<br />simplified."
          </blockquote>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
              V
            </div>
            <div>
              <div className="text-white text-sm font-medium">Visa For You Portal</div>
              <div className="text-gray-500 text-xs">Manage your applications & clients</div>
            </div>
          </div>
        </div>

        {/* Feature list */}
        <div className="flex flex-col gap-3">
          {[
            "AI-powered visa guidance",
            "Real-time application tracking",
            "Secure client management",
          ].map((item) => (
            <div key={item} className="flex items-center gap-3">
              <div className="w-5 h-5 rounded-full border border-gray-700 flex items-center justify-center flex-shrink-0">
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <path d="M2 5l2 2 4-4" stroke="#6ee7b7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <span className="text-gray-400 text-sm">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="flex-1 flex flex-col justify-center items-center px-6 py-12">

        {/* Mobile logo */}
        <div className="lg:hidden mb-10 flex flex-col items-center gap-2">
          <img src="/logo.jpg" alt="Visa For You" className="h-12 object-contain" />
        </div>

        <div className="w-full max-w-sm">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Welcome back</h1>
            <p className="text-sm text-gray-500 mt-1">Sign in to your account</p>
          </div>

          {/* Error */}
          {error && (
            <div className="py-2.5 px-3.5 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600 mb-5">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-4">
            {/* Email */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Email address</label>
              <input
                type="email"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                onKeyDown={e => e.key === "Enter" && handleSubmit()}
                placeholder="your@email.com"
                className="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition bg-white placeholder:text-gray-300"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPass ? "text" : "password"}
                  value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })}
                  onKeyDown={e => e.key === "Enter" && handleSubmit()}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 pr-14 text-sm border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition bg-white placeholder:text-gray-300"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 hover:text-gray-600 transition select-none"
                >
                  {showPass ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="mt-1 w-full py-2.5 bg-black text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Signing in...
                </>
              ) : (
                "Sign in →"
              )}
            </button>
          </div>

          <p className="mt-6 text-center text-xs text-gray-400">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-gray-900 font-medium hover:underline">
              Sign up
            </Link>
          </p>
        </div>

        <div className="mt-12 text-center">
          <p className="text-[11px] text-gray-300">
            By signing in, you agree to our{" "}
            <Link href="#" className="underline underline-offset-2 hover:text-gray-500 transition">Terms</Link>
            {" "}and{" "}
            <Link href="#" className="underline underline-offset-2 hover:text-gray-500 transition">Privacy Policy</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
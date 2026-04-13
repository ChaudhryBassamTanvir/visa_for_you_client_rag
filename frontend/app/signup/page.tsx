"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"

export default function SignupPage() {
  const router = useRouter()
  const [form, setForm]       = useState({ name: "", email: "", password: "", cgpa: "", degree: "", phone: "" })
  const [error, setError]     = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true); setError("")
    try {
      const res  = await fetch("http://127.0.0.1:8000/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail); setLoading(false); return }
      localStorage.setItem("token", data.token)
      localStorage.setItem("user",  JSON.stringify(data))

      // Save profile info
      if (form.cgpa || form.degree || form.phone) {
        await fetch("http://127.0.0.1:8000/user/profile", {
          method: "PUT",
          headers: { "Content-Type": "application/json", "Authorization": `Bearer ${data.token}` },
          body: JSON.stringify({ cgpa: form.cgpa, degree: form.degree, phone: form.phone })
        })
      }
      router.push("/visa-chat")
    } catch { setError("Connection error") }
    setLoading(false)
  }

  const fields = [
    { key: "name",     label: "Full Name",      type: "text",     placeholder: "Muhammad Ahmed",    col: "full" },
    { key: "email",    label: "Email",           type: "email",    placeholder: "ahmed@example.com", col: "full" },
    { key: "password", label: "Password",        type: "password", placeholder: "Min 6 characters",  col: "full" },
    { key: "phone",    label: "Phone Number",    type: "text",     placeholder: "+92 300 1234567",   col: "full" },
    { key: "cgpa",     label: "CGPA",            type: "text",     placeholder: "e.g. 3.2",          col: "half" },
    { key: "degree",   label: "Last Degree",     type: "text",     placeholder: "BS Computer Science", col: "half" },
  ]

  return (
    <div className="min-h-screen bg-white flex">

      {/* ── Left branding panel ── */}
      <div className="hidden lg:flex lg:w-[42%] bg-gray-950 flex-col justify-between p-10">

        {/* Logo */}
        <div className="flex items-center gap-3">
          <img src="/logo.jpg" alt="Visa For You" className="h-8 w-8 object-contain rounded-lg" />
          <span className="text-white font-semibold text-sm tracking-tight">Visa For You</span>
        </div>

        {/* Quote */}
        <div>
          <blockquote className="text-gray-300 text-2xl font-medium leading-snug tracking-tight mb-6">
            "Start your visa journey<br />the smart way."
          </blockquote>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center text-white text-sm font-bold">
              V
            </div>
            <div>
              <div className="text-white text-sm font-medium">Create your free account</div>
              <div className="text-gray-500 text-xs">No credit card required</div>
            </div>
          </div>
        </div>

        {/* Feature list */}
        <div className="flex flex-col gap-3">
          {[
            "AI-powered visa guidance",
            "Real-time application tracking",
            "Secure document management",
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
      <div className="flex-1 flex flex-col justify-center items-center px-6 py-12 overflow-y-auto">

        {/* Mobile logo */}
        <div className="lg:hidden mb-8 flex flex-col items-center gap-2">
          <img src="/logo.jpg" alt="Visa For You" className="h-12 object-contain" />
        </div>

        <div className="w-full max-w-sm">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Create your account</h1>
            <p className="text-sm text-gray-500 mt-1">Free to start. No credit card required.</p>
          </div>

          {/* Error */}
          {error && (
            <div className="py-2.5 px-3.5 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600 mb-5">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-4">
            {/* Full-width fields */}
            {fields.filter(f => f.col === "full").map((f) => (
              <div key={f.key}>
                <label className="block text-xs font-medium text-gray-700 mb-1.5">{f.label}</label>
                <input
                  type={f.type}
                  placeholder={f.placeholder}
                  value={(form as any)[f.key]}
                  onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                  className="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition bg-white placeholder:text-gray-300"
                />
              </div>
            ))}

            {/* Half-width fields (CGPA + Degree) */}
            <div className="grid grid-cols-2 gap-3">
              {fields.filter(f => f.col === "half").map((f) => (
                <div key={f.key}>
                  <label className="block text-xs font-medium text-gray-700 mb-1.5">{f.label}</label>
                  <input
                    type={f.type}
                    placeholder={f.placeholder}
                    value={(form as any)[f.key]}
                    onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition bg-white placeholder:text-gray-300"
                  />
                </div>
              ))}
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
                  Creating account...
                </>
              ) : (
                "Create account →"
              )}
            </button>
          </div>

          <p className="mt-6 text-center text-xs text-gray-400">
            Already have an account?{" "}
            <Link href="/login" className="text-gray-900 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>

        <div className="mt-10 text-center">
          <p className="text-[11px] text-gray-300">
            By signing up, you agree to our{" "}
            <Link href="#" className="underline underline-offset-2 hover:text-gray-500 transition">Terms</Link>
            {" "}and{" "}
            <Link href="#" className="underline underline-offset-2 hover:text-gray-500 transition">Privacy Policy</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
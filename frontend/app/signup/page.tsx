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
    { key: "name",     label: "Full Name",       type: "text",     placeholder: "Muhammad Ahmed" },
    { key: "email",    label: "Email",            type: "email",    placeholder: "ahmed@example.com" },
    { key: "password", label: "Password",         type: "password", placeholder: "Min 6 characters" },
    { key: "phone",    label: "Phone Number",     type: "text",     placeholder: "+92 300 1234567" },
    { key: "cgpa",     label: "CGPA (e.g. 3.2)",  type: "text",     placeholder: "3.2" },
    { key: "degree",   label: "Last Degree",      type: "text",     placeholder: "BS Computer Science" },
  ]

  return (
   <div className="min-h-screen bg-[#f9f9f8] flex items-center justify-center p-5">
      <div className="bg-white border border-[#e8e8e6] rounded-2xl p-10 w-full max-w-[420px]">
        
        <div className="text-center mb-7">
          <img
            src="/logo.jpg"
            alt="Visa For You"
            className="h-[60px] object-contain mx-auto mb-3"
          />
          <p className="text-[13px] text-gray-400 m-0">
            Create your free account
          </p>
        </div>

        {error && (
          <div className="px-4 py-2.5 bg-red-50 border border-red-200 rounded-lg text-[13px] text-red-600 mb-4">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-3">
          {fields.map((f) => (
            <div key={f.key}>
              <label className="text-xs text-gray-500 block mb-1">
                {f.label}
              </label>

              <input
                type={f.type}
                placeholder={f.placeholder}
                value={(form as any)[f.key]}
                onChange={(e) =>
                  setForm({ ...form, [f.key]: e.target.value })
                }
                className="w-full px-4 py-2.5 text-[13px] rounded-lg border border-[#e8e8e6] bg-[#f9f9f8] outline-none box-border"
              />
            </div>
          ))}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`py-3 rounded-lg text-sm font-medium mt-1 text-white transition ${
              loading
                ? "bg-gray-300 cursor-not-allowed"
                : "bg-[#1a1a1a] hover:bg-black cursor-pointer"
            }`}
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </div>

        <p className="text-center text-[13px] text-gray-400 mt-5">
          Already have an account?{" "}
          <Link
            href="/login"
            className="text-[#1a1a1a] font-medium no-underline"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
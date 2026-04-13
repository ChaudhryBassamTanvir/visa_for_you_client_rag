import Link from "next/link"
import Navbar from "@/components/Navbar"
import Footer from "@/components/Footer"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <Navbar />

      <main className="flex-1 pt-14">

        {/* ── HERO ── */}
        <section className="max-w-4xl mx-auto px-6 pt-24 pb-20 text-center">
          <div className="inline-flex items-center gap-2 mb-7 px-3 py-1 rounded-full border border-gray-200 bg-gray-50 text-xs text-gray-500 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            AI-powered · Visa guidance made simple
          </div>

          <h1 className="text-5xl md:text-6xl font-bold tracking-[-0.03em] text-gray-950 leading-[1.1]">
            Your visa journey,
            <br />
            <span className="text-gray-400">effortlessly guided.</span>
          </h1>

          <p className="mt-6 text-lg text-gray-500 max-w-xl mx-auto leading-relaxed">
            AI-powered visa consultation, real-time application tracking, and expert client management — all in one workspace.
          </p>

          <div className="mt-8 flex items-center justify-center gap-3">
            <Link href="/signup" className="px-5 py-2.5 bg-black text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition shadow-sm">
              Get started free →
            </Link>
            <Link href="/login" className="px-5 py-2.5 bg-white text-gray-700 text-sm font-medium rounded-lg border border-gray-200 hover:bg-gray-50 transition">
              Sign in
            </Link>
          </div>
          <p className="mt-5 text-xs text-gray-400">No credit card required · Free to start</p>
        </section>

        {/* ── PRODUCT PREVIEW ── */}
        <section className="max-w-5xl mx-auto px-6 mb-24">
          <div className="rounded-2xl border border-gray-200 overflow-hidden shadow-lg shadow-gray-100">
            <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-200">
              <span className="w-3 h-3 rounded-full bg-red-400" />
              <span className="w-3 h-3 rounded-full bg-yellow-400" />
              <span className="w-3 h-3 rounded-full bg-green-400" />
              <span className="ml-4 flex-1 bg-white border border-gray-200 rounded-md px-3 py-1 text-xs text-gray-400">
                visaforyou.app/dashboard
              </span>
            </div>

            <div className="flex h-[340px] bg-white">
              {/* Sidebar */}
              <div className="w-52 border-r border-gray-100 bg-gray-50 p-3 flex flex-col gap-0.5">
                <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-gray-200/70 text-xs text-gray-700 font-medium">
                  <span>🏠</span> Dashboard
                </div>
                {["💬 Visa Chat", "📋 Applications", "👥 Clients", "📄 Documents", "⚙️ Settings"].map((item) => (
                  <div key={item} className="flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-gray-500 hover:bg-gray-200/50 cursor-pointer">
                    {item}
                  </div>
                ))}
                <div className="mt-auto pt-3 border-t border-gray-200 px-2 flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-black text-white text-[9px] flex items-center justify-center font-bold">A</div>
                  <span className="text-xs text-gray-500">Admin</span>
                </div>
              </div>

              {/* Main */}
              <div className="flex-1 p-6 overflow-hidden">
                <div className="text-xs text-gray-400 mb-1 font-medium uppercase tracking-wider">Overview</div>
                <div className="text-xl font-semibold text-gray-900 mb-5">Welcome back 👋</div>

                <div className="grid grid-cols-3 gap-3 mb-5">
                  {[
                    { label: "Active Applications", value: "18",  color: "bg-blue-50 text-blue-700" },
                    { label: "Pending Reviews",     value: "5",   color: "bg-amber-50 text-amber-700" },
                    { label: "Approved Visas",      value: "142", color: "bg-emerald-50 text-emerald-700" },
                  ].map((s) => (
                    <div key={s.label} className={`rounded-lg p-3 ${s.color}`}>
                      <div className="text-lg font-bold">{s.value}</div>
                      <div className="text-[10px] opacity-70 mt-0.5">{s.label}</div>
                    </div>
                  ))}
                </div>

                <div className="text-xs font-medium text-gray-400 mb-2">Recent Applications</div>
                <div className="flex flex-col gap-1.5">
                  {[
                    { name: "Ahmed Khan", type: "Student Visa", status: "In Review", dot: "bg-blue-400" },
                    { name: "Sara Malik", type: "Work Permit",  status: "Approved",  dot: "bg-emerald-400" },
                    { name: "Bilal Raza", type: "Visit Visa",   status: "Pending",   dot: "bg-amber-400" },
                  ].map((a) => (
                    <div key={a.name} className="flex items-center justify-between bg-gray-50 rounded-md px-3 py-2">
                      <div className="flex items-center gap-2">
                        <span className={`w-1.5 h-1.5 rounded-full ${a.dot}`} />
                        <span className="text-xs text-gray-700 font-medium">{a.name}</span>
                        <span className="text-[10px] text-gray-400">· {a.type}</span>
                      </div>
                      <span className="text-[10px] text-gray-400">{a.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── SERVICES ── */}
        <section id="services" className="max-w-5xl mx-auto px-6 pb-24">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Everything you need</h2>
            <p className="text-gray-500 mt-2 text-base">One platform for your entire visa workflow.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { icon: "💬", tag: "AI Assistant", title: "Smart Visa Chat",        desc: "Get instant AI-powered answers to visa queries, eligibility checks, and document requirements." },
              { icon: "📋", tag: "Tracking",     title: "Application Management", desc: "Track every application in real time — from submission to approval, with full history." },
              { icon: "📄", tag: "Documents",    title: "Document Handling",      desc: "Upload, organize, and verify required documents securely within one workspace." },
            ].map((f) => (
              <div key={f.title} className="group p-6 bg-white rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all cursor-default">
                <div className="w-10 h-10 rounded-lg bg-gray-50 border border-gray-100 flex items-center justify-center text-xl mb-4 group-hover:scale-110 transition-transform">
                  {f.icon}
                </div>
                <div className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold mb-1">{f.tag}</div>
                <h3 className="text-base font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── HOW IT WORKS ── */}
        <section id="how" className="max-w-4xl mx-auto px-6 pb-24">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 tracking-tight">How it works</h2>
            <p className="text-gray-500 mt-2 text-base">Three simple steps to get started.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Create an account", desc: "Sign up for free and complete your profile with your academic and personal details." },
              { step: "02", title: "Chat with our AI",  desc: "Ask anything about visa requirements, eligibility, and documentation instantly." },
              { step: "03", title: "Track & apply",     desc: "Submit your application and monitor its progress in real time from your dashboard." },
            ].map((s) => (
              <div key={s.step} className="flex flex-col gap-3">
                <div className="text-4xl font-bold text-gray-100 tracking-tight">{s.step}</div>
                <h3 className="text-base font-semibold text-gray-900">{s.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── CTA BANNER ── */}
        <section className="max-w-5xl mx-auto px-6 pb-24">
          <div className="bg-gray-950 rounded-2xl px-8 py-12 text-center">
            <h2 className="text-3xl font-bold text-white tracking-tight mb-3">Ready to start your journey?</h2>
            <p className="text-gray-400 mb-8 text-base">Join thousands of applicants who trust Visa For You.</p>
            <Link href="/signup" className="inline-block px-6 py-3 bg-white text-gray-900 text-sm font-semibold rounded-lg hover:bg-gray-100 transition">
              Create free account →
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
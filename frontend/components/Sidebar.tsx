"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LogOut, MessageSquare, LayoutDashboard, Users, Calendar } from "lucide-react"
import { useRouter } from "next/navigation"

export default function Sidebar() {
  const path = usePathname()
  const router = useRouter()

  const logout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    router.push("/login")
  }

  const links = [
    { href: "/dashboard",    label: "Dashboard",    icon: LayoutDashboard },
    { href: "/clients",      label: "Clients",      icon: Users },
    { href: "/appointments", label: "Appointments", icon: Calendar },
    { href: "/chat",         label: "Test Chat",    icon: MessageSquare },
  ]

  return (
    <aside className="w-[240px] shrink-0 bg-gray-50 border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0">

      {/* Logo / Brand */}
      <div className="px-4 py-4 border-b border-gray-200 flex items-center gap-2.5">
        <img src="/logo.jpg" alt="Visa For You" className="h-7 w-7 object-contain rounded-md" />
        <div>
          <div className="text-sm font-semibold text-gray-900 tracking-tight leading-none">Visa For You</div>
          <div className="text-[10px] text-gray-400 mt-0.5">Agent Dashboard</div>
        </div>
      </div>

      {/* Page label */}
      <div className="px-4 pt-4 pb-1">
        <p className="text-[10px] text-gray-400 uppercase tracking-widest font-semibold px-2">Navigation</p>
      </div>

      {/* Nav */}
      <nav className="px-2 flex-1 flex flex-col gap-0.5">
        {links.map(({ href, label, icon: Icon }) => {
          const active = path === href
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-sm no-underline transition-all ${
                active
                  ? "bg-white border border-gray-200 text-gray-900 font-medium shadow-sm"
                  : "text-gray-500 hover:bg-gray-100 hover:text-gray-800 font-normal border border-transparent"
              }`}
            >
              <Icon size={14} className={active ? "text-gray-900" : "text-gray-400"} />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Bottom: user + logout */}
      <div className="px-3 py-3 border-t border-gray-200 flex flex-col gap-1">
        <button
          onClick={logout}
          className="w-full px-3 py-2 flex items-center gap-2 text-sm text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors cursor-pointer border-none bg-transparent"
        >
          <LogOut size={13} /> Sign out
        </button>

        <div className="flex items-center gap-2.5 px-2 py-1.5">
          <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center text-[11px] font-semibold text-blue-600 shrink-0">
            CB
          </div>
          <div>
            <div className="text-xs font-medium text-gray-900">Bassam</div>
            <div className="text-[10px] text-gray-400">Admin</div>
          </div>
        </div>
      </div>
    </aside>
  )
}
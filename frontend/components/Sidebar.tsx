"use client"
import Link from "next/link"
import { usePathname }  from "next/navigation";
import { LogOut } from "lucide-react"
import { useRouter } from "next/navigation"
import { MessageSquare, LayoutDashboard, Users, Calendar } from "lucide-react"

export default function Sidebar() {
  const path = usePathname()
const router = useRouter()
const logout = () => {
  localStorage.removeItem("token")
  localStorage.removeItem("user")
  router.push("/login")
}

const links = [
  { href: "/chat",         label: "Chat",         icon: MessageSquare },
  { href: "/dashboard",    label: "Dashboard",    icon: LayoutDashboard },
  { href: "/clients",      label: "Clients",      icon: Users },
  { href: "/appointments", label: "Appointments", icon: Calendar },
]

  return (
   <aside className="w-[220px] shrink-0 bg-[#fafaf9] border-r border-[#e8e8e6] flex flex-col h-screen fixed left-0 top-0">
  
  <div className="p-5 border-b border-[#e8e8e6]">
    <div className="text-[15px] font-medium tracking-[-0.3px]">
      DS Technologies
    </div>
    <div className="text-[11px] text-[#999] mt-[2px]">
      Agent Dashboard
    </div>
  </div>

  <nav className="p-3 flex-1">
    {links.map(({ href, label, icon: Icon }) => (
      <Link
        key={href}
        href={href}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg mb-[2px] text-[13px] no-underline ${
          path === href
            ? "bg-white border border-[#e8e8e6] text-[#1a1a1a] font-medium"
            : "bg-transparent border border-transparent text-[#888] font-normal"
        }`}
      >
        <Icon size={14} />
        {label}
      </Link>
    ))}
  </nav>

  <div className="px-5 py-4 border-t border-[#e8e8e6]">
    
    {/* Logout Button */}
    <button
      onClick={logout}
      className="w-full px-3 py-2 flex items-center gap-2 bg-transparent border-none cursor-pointer text-[13px] text-[#999] rounded-lg mb-2"
    >
      <LogOut size={13} /> Sign Out
    </button>

    <div className="flex items-center gap-2">
      <div className="w-7 h-7 rounded-full bg-[#e8f0fe] flex items-center justify-center text-[11px] font-medium text-[#3b5bdb]">
        CB
      </div>

      <div>
        <div className="text-xs font-medium">
          Bassam
        </div>
        <div className="text-[10px] text-[#999]">
          Admin
        </div>
      </div>
    </div>
  </div>
</aside>
  )
}
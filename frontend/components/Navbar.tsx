"use client"

import Link from "next/link"
import { useState } from "react"

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200/80">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <img
              src="/logo.jpg"
              alt="Visa For You"
              className="h-7 w-7 object-contain rounded-md group-hover:scale-95 transition-transform"
            />
            <span className="text-sm font-semibold text-gray-900 tracking-tight">Visa For You</span>
          </Link>

          {/* Center Nav Links */}
          <div className="hidden md:flex items-center gap-1">
            {[
              { label: "Home",         href: "/" },
              { label: "Services",     href: "#services" },
              { label: "How It Works", href: "#how" },
              { label: "Contact",      href: "#contact" },
            ].map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-all"
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Right Side */}
          <div className="hidden md:flex items-center gap-2">
            <Link
              href="/login"
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-all"
            >
              Sign in
            </Link>
            <Link
              href="/signup"
              className="px-3.5 py-1.5 text-sm bg-black text-white rounded-md hover:bg-gray-800 transition-all shadow-sm font-medium"
            >
              Get started →
            </Link>
          </div>

          {/* Mobile Hamburger */}
          <button
            className="md:hidden p-2 rounded-md hover:bg-gray-100 transition"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <div className="flex flex-col gap-1.5 w-5">
              <span className={`h-0.5 bg-gray-700 rounded block transition-all duration-200 ${menuOpen ? "rotate-45 translate-y-2" : ""}`} />
              <span className={`h-0.5 bg-gray-700 rounded block transition-all duration-200 ${menuOpen ? "opacity-0" : ""}`} />
              <span className={`h-0.5 bg-gray-700 rounded block transition-all duration-200 ${menuOpen ? "-rotate-45 -translate-y-2" : ""}`} />
            </div>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white px-4 py-3 flex flex-col gap-1">
          {["Home", "Services", "How It Works", "Contact"].map((item) => (
            <Link
              key={item}
              href="#"
              className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition"
              onClick={() => setMenuOpen(false)}
            >
              {item}
            </Link>
          ))}
          <div className="border-t border-gray-100 mt-2 pt-2 flex flex-col gap-1">
            <Link href="/login"  className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition">Sign in</Link>
            <Link href="/signup" className="px-3 py-2 text-sm bg-black text-white rounded-md text-center font-medium">Get started →</Link>
          </div>
        </div>
      )}
    </nav>
  )
}
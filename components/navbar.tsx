"use client"

import Image from "next/image"
import { useState } from "react"
import Link from "next/link"

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [mobileProductOpen, setMobileProductOpen] = useState(false)

  if (status === "loading") return <div>Loading...</div>

  return (
    <>
      <header className="fixed top-0 left-0 w-full bg-gray-900 font-bold text-[10px] tracking-tight z-50 border-b border-gray-600">
        <nav className="mx-auto max-w-7xl py-4 flex items-center justify-between">

          {/* LEFT */}
          <div className="flex items-center px-5">
            <Link href="/#about">
              <Image
                src="/logo.png"
                alt="logo"
                width={30}
                height={23}
                className="invert"
              />
            </Link>
          </div>

          {/* CENTER (desktop only) */}
          <div className="hidden sm:flex gap-9 text-white">
            <Link href="/#home" className="hover:text-gray-300">
              หน้าหลัก
            </Link>

            <Link href="/history" className="hover:text-gray-300">
              ประวัติ
            </Link>
            
            <Link href="/saved" className="hover:text-gray-300">
              บันทึก
            </Link>

            <Link href="/user" className="hover:text-gray-300">
              ผู้ใช้
            </Link>
          </div>

          {/* RIGHT */}
          <div className="text-white px-5">

            {/* desktop */}

            <div>
              <Link href="/login" className="hover:text-gray-300">
              เข้าสู่ระบบ
            </Link>
            </div>

            {/* mobile hamburger */}
            <button
              onClick={() => setMenuOpen(true)}
              className="sm:hidden flex flex-col justify-center gap-1"
            >
              <span className="block w-4 h-[1.5px] bg-white"></span>
              <span className="block w-4 h-[1.5px] bg-white"></span>
              <span className="block w-4 h-[1.5px] bg-white"></span>
            </button>
          </div>
        </nav>
      </header>

      {/* Sidebar (mobile) */}
      {menuOpen && (
        <div className="fixed inset-0 z-50 flex">

          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setMenuOpen(false)}
          />

          <div className="relative ml-auto w-64 bg-gray-800 border-l border-gray-600 h-full pt-3 pl-1 pr-1 text-white">

            <button
              onClick={() => setMenuOpen(false)}
              className="absolute top-4 right-6 text-md"
            >
              ✕
            </button>

            <div className="mt-12 border-t border-b border-gray-600 pt-6 pb-6 mb-6 space-y-2">

              <Link
                href="/#home"
                className="block text-xs font-semibold text-white py-2 rounded-lg hover:bg-gray-700 transition"
                onClick={() => setMenuOpen(false)}
              >
                <p className="ml-6">หน้าหลัก</p>
              </Link>

              <Link
                href="/history"
                className="block text-xs font-semibold text-white py-2 rounded-lg hover:bg-gray-700 transition"
                onClick={() => setMenuOpen(false)}
              >
                <p className="ml-6">ประวัติ</p>
              </Link>
              
              <Link
                href="/saved"
                className="block text-xs font-semibold text-white py-2 rounded-lg hover:bg-gray-700 transition"
                onClick={() => setMenuOpen(false)}
              >
                <p className="ml-6">บันทึก</p>
              </Link>

              <Link
                href="/user"
                className="block text-xs font-semibold text-white py-2 rounded-lg hover:bg-gray-700 transition"
                onClick={() => setMenuOpen(false)}
              >
                <p className="ml-6">ผู้ใช้</p>
              </Link>
            </div>
            <div>
              <Link href="/login" className="ml-6">
                  Log In
                </Link>
            </div>

          </div>
        </div>
      )}
    </>
  )
}
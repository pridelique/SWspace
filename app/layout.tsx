import { Geist } from "next/font/google"
import { Poppins } from "next/font/google"
import { Inter } from "next/font/google"
import { Manrope } from "next/font/google"
import type { ReactNode } from "react"
import Navbar from "@/components/navbar"


import "./globals.css"

const geist = Geist({
  subsets: ["latin"],
})
const poppins = Poppins({ subsets: ["latin"], weight: ["400","600"] })
const inter = Inter({ subsets: ["latin"] })
const manrope = Manrope({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en">
      <body className={manrope.className}>
          <Navbar/>
          <main className="p-0">
            {children}
          </main>

      </body>
    </html>
  )
}
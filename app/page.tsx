"use client"

import { ThemeProvider } from "@/components/theme-provider"
import CVDashboard from "../cv-dashboard"

export default function Page() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <CVDashboard />
    </ThemeProvider>
  )
}

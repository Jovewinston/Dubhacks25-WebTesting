"use client"
import { TestDashboard } from "@/components/test-dashboard"
import { Toaster } from "@/components/ui/toaster"

export default function Home() {
  return (
    <>
      <TestDashboard />
      <Toaster />
    </>
  )
}

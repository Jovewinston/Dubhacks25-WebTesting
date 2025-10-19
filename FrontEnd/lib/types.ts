// Shared types for the test dashboard application

export interface TestStep {
  name: string
  duration: string
  status: "passed" | "failed"
  thought?: string
  action?: string
  actionDescription?: string
  systemMessage?: string
  userMessage?: string
  elementOutput?: string
  llmOutput?: string
}

export interface AnalyticsData {
  load_time_ms?: string
  dom_interactive_time_ms?: string
  redirect_count?: string
  transfer_bytes?: string
  first_contentful_paint_time_ms?: string
  effective_connection_type?: string
  downlink_mbps?: string
  downlink_kbps?: string
  city?: string
  state?: string
  country?: string
}

export interface TestResult {
  totalSteps: number
  passed: number
  failed: number
  passRate: number
  breakdown: Array<{
    browser: string
    device: string
    status: "passed" | "failed"
  }>
  issues: string[]
  steps: TestStep[]
  combinations: Array<{
    browser: string
    device: string
    status: "passed" | "failed"
    steps: TestStep[]
    totalSteps: number
    runtimeSec: number
    success: boolean
    gptOutput?: string
    explanation?: string
    analytics?: AnalyticsData
  }>
  // StatSig performance metrics
  performanceMetrics?: {
    load_time_ms?: string
    dom_interactive_time_ms?: string
    redirect_count?: string
    transfer_bytes?: string
    first_contentful_paint_time_ms?: string
    effective_connection_type?: string
    downlink_mbps?: string
    downlink_kbps?: string
    city?: string
    state?: string
    country?: string
  }
  performanceData?: {
    fetch_timestamp: string
    performance_event?: any
    web_vitals_event?: any
    summary: {
      has_performance_data: boolean
      has_web_vitals_data: boolean
      total_events_found: number
    }
  }
}

export interface TestHistory {
  id: string
  runDate: string
  passRate: number
  totalSteps: number
  passed: number
  failed: number
  status: "passed" | "failed"
  breakdown: Array<{
    browser: string
    device: string
    status: "passed" | "failed"
  }>
  issues: string[]
  steps: TestStep[]
}

export interface Test {
  id: string
  name: string
  description: string
  url: string
  expectedBehavior: string
  status: "draft" | "running" | "completed"
  passRate?: number
  createdAt: string
  browsers: string[]
  devices: string[]
  results?: TestResult
  history?: TestHistory[]
  username?: string
  password?: string
}

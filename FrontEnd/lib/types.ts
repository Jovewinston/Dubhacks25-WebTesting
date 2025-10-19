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

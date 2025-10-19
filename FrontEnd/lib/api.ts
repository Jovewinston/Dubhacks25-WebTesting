// API utility functions for communicating with the backend

export interface TestData {
  url: string
  task: string
  steps: string
  expected_behavior: string
  devices: string[]
  browsers: string[]
}

export interface TestResponse {
  success: boolean
  message?: string
  job_id?: string
  error?: string
}

export interface TestStatusResponse {
  job_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: number
  message?: string
  created_at: string
  completed_at?: string
  error?: string
  // Include metadata fields directly (not nested under results)
  episode_name?: string
  task?: string
  url?: string
  steps?: string
  expected_behavior?: string
  combinations?: Array<{
    goal: string
    eps_name: string
    task: {
      steps: string[]
    }
    start_url: string
    browser_context: {
      os: string
      viewport: string
      cookies_enabled: boolean
    }
    success: boolean
    total_steps: number
    runtime_sec: number
    total_tokens: number
    gpt_output?: string
    wrong_behavior?: boolean
    explanation?: string
    expected_behavior?: string
    device: string
    browser: string
  }>
}

export interface BackendTestResult {
  episode_name: string
  task: string
  url: string
  steps: string
  expected_behavior: string
  combinations: Array<{
    goal: string
    eps_name: string
    task: {
      steps: string[]
    }
    start_url: string
    browser_context: {
      os: string
      viewport: string
      cookies_enabled: boolean
    }
    success: boolean
    total_steps: number
    runtime_sec: number
    total_tokens: number
    gpt_output?: string
    wrong_behavior?: boolean
    explanation?: string
    expected_behavior?: string
    device: string
    browser: string
  }>
}

/**
 * Sends test data to the backend API
 * @param testData - The test data to send
 * @returns Promise<TestResponse> - The response from the backend
 */
export async function sendTestToBackend(testData: TestData): Promise<TestResponse> {
  try {
    const response = await fetch('http://localhost:8000/api/v1/run-pipeline', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    return {
      success: true,
      message: result.message || 'Test submitted successfully',
      job_id: result.job_id,
    }
  } catch (error) {
    console.error('Error sending test to backend:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    }
  }
}

/**
 * Formats test data from the dashboard format to the backend format
 * @param test - The test object from the dashboard
 * @returns TestData - Formatted data for the backend
 */
export function formatTestDataForBackend(test: {
  name: string
  description: string
  url: string
  expectedBehavior: string
  browsers: string[]
  devices: string[]
  username?: string
  password?: string
}): TestData {
  // Create steps string based on test data
  let steps = ''
  
  if (test.username && test.password) {
    steps = `1. Login to the page first with the email '${test.username}' and password '${test.password}' 2. ${test.description}`
  } else {
    steps = test.description
  }

  return {
    url: test.url,
    task: test.name,
    steps: steps,
    expected_behavior: test.expectedBehavior,
    devices: test.devices.map(device => device.toLowerCase()),
    browsers: test.browsers.map(browser => browser.toLowerCase()),
  }
}

/**
 * Parses backend test result data and converts it to frontend format
 * @param backendResult - The result data from the backend
 * @returns Parsed test result data for the frontend
 */
export function parseBackendTestResult(backendResult: BackendTestResult) {
  const { combinations } = backendResult
  
  // Calculate overall statistics
  const totalSteps = combinations.reduce((sum, combo) => sum + combo.total_steps, 0)
  const passedCombinations = combinations.filter(combo => combo.success)
  const failedCombinations = combinations.filter(combo => !combo.success)
  const passed = passedCombinations.length
  const failed = failedCombinations.length
  const passRate = Math.round((passed / combinations.length) * 100)
  
  // Create breakdown by browser/device
  const breakdown = combinations.map(combo => ({
    browser: combo.browser.charAt(0).toUpperCase() + combo.browser.slice(1),
    device: combo.device.charAt(0).toUpperCase() + combo.device.slice(1),
    status: combo.success ? "passed" as const : "failed" as const
  }))
  
  // Collect issues from failed combinations
  const issues = failedCombinations.map(combo => 
    `${combo.browser} ${combo.device}: ${combo.gpt_output}`
  )
  
  // Create test steps from the first successful combination (or first if none successful)
  const referenceCombo = passedCombinations[0] || combinations[0]
  const steps = referenceCombo.task.steps.map((step, index) => ({
    name: step,
    duration: `${Math.round(referenceCombo.runtime_sec / referenceCombo.total_steps)}s`,
    status: "passed" as const,
    thought: `Step ${index + 1}: ${step}`,
    action: step,
    actionDescription: step
  }))
  
  return {
    totalSteps,
    passed,
    failed,
    passRate,
    breakdown,
    issues,
    steps
  }
}

/**
 * Polls the backend for test status updates
 * @param testId - The test ID to poll for
 * @returns Promise<TestStatusResponse> - Current test status
 */
export async function pollTestStatus(jobId: string): Promise<TestStatusResponse> {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/status/${jobId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error polling test status:', error)
    throw error
  }
}

/**
 * Starts periodic polling for a test and calls update callback
 * @param testId - The test ID to poll for
 * @param onUpdate - Callback function called with each status update
 * @param onComplete - Callback function called when test completes
 * @param onError - Callback function called on error
 * @returns Function to stop polling
 */
export function startTestPolling(
  jobId: string,
  onUpdate: (status: TestStatusResponse) => void,
  onComplete: (results: BackendTestResult) => void,
  onError: (error: string) => void
): () => void {
  let isPolling = true
  let pollInterval: NodeJS.Timeout | null = null

  const poll = async () => {
    if (!isPolling) return

    try {
      const status = await pollTestStatus(jobId)
      onUpdate(status)

      if (status.status === 'completed' && status.combinations) {
        isPolling = false
        if (pollInterval) clearInterval(pollInterval)
        // Convert status response to BackendTestResult format
        const results: BackendTestResult = {
          episode_name: status.episode_name || '',
          task: status.task || '',
          url: status.url || '',
          steps: status.steps || '',
          expected_behavior: status.expected_behavior || '',
          combinations: status.combinations || []
        }
        onComplete(results)
      } else if (status.status === 'failed') {
        isPolling = false
        if (pollInterval) clearInterval(pollInterval)
        onError(status.error || 'Test failed')
      }
    } catch (error) {
      console.error('Polling error:', error)
      onError(error instanceof Error ? error.message : 'Unknown polling error')
    }
  }

  // Start polling immediately
  poll()
  
  // Then poll every 1 second
  pollInterval = setInterval(poll, 1000)

  // Return stop function
  return () => {
    isPolling = false
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }
}


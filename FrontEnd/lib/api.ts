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
  testId?: string
  error?: string
}

/**
 * Sends test data to the backend API
 * @param testData - The test data to send
 * @returns Promise<TestResponse> - The response from the backend
 */
export async function sendTestToBackend(testData: TestData): Promise<TestResponse> {
  try {
    // TODO: Replace with actual backend URL when available
    const response = await fetch('/api/tests', {
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
      testId: result.testId,
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

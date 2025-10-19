# Real-Time Test Polling System

This document explains the implementation of the periodic polling system for real-time test updates.

## Overview

The frontend now polls the backend endpoint every 1 second to get real-time updates on test progress. This provides users with live feedback on test execution status, current step, and progress percentage.

## Implementation Details

### 1. API Layer (`Frontend/lib/api.ts`)

#### New Interfaces
```typescript
export interface TestStatusResponse {
  testId: string
  status: 'running' | 'completed' | 'failed'
  progress?: number
  currentStep?: string
  results?: BackendTestResult
  error?: string
}
```

#### New Functions
- `pollTestStatus(testId: string)`: Single poll request to backend
- `startTestPolling(testId, onUpdate, onComplete, onError)`: Starts periodic polling with callbacks

### 2. Frontend Integration (`Frontend/components/test-dashboard.tsx`)

#### New State Management
```typescript
const [testStatuses, setTestStatuses] = useState<Record<string, TestStatusResponse>>({})
const [pollingStoppers, setPollingStoppers] = useState<Record<string, () => void>>({})
```

#### Real-Time Updates
- **Progress Display**: Shows percentage and current step in test cards
- **Toast Notifications**: Displays progress updates as toasts
- **Status Updates**: Updates test status in real-time
- **Automatic Cleanup**: Stops polling when test completes or fails

## Backend Requirements

### 1. Test Submission Endpoint
**POST** `http://localhost:8000/api/v1/run-pipeline`

**Request Body:**
```json
{
  "url": "https://www.linkedin.com",
  "task": "Message Samuel Purnama on LinkedIn",
  "steps": "1. Login to the page first...",
  "expected_behavior": "You should see a sent message...",
  "devices": ["desktop", "mobile"],
  "browsers": ["chrome", "safari"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test submitted successfully",
  "job_id": "job_12345"
}
```

### 2. Test Status Polling Endpoint
**GET** `http://localhost:8000/api/v1/status/{job_id}`

**Response (Running):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "progress": 50,
  "message": "Running pipeline across devices and browsers...",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": null,
  "error": null,
  "episode_name": null,
  "task": null,
  "url": null,
  "steps": null,
  "expected_behavior": null,
  "combinations": null
}
```

**Response (Completed):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": 100,
  "message": "Pipeline completed successfully",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:35:00Z",
  "error": null,
  "episode_name": "message_samuel_purnama_a1b2c3d4",
  "task": "Message Samuel Purnama on LinkedIn",
  "url": "https://www.linkedin.com",
  "steps": "1. Login to the page first...",
  "expected_behavior": "You should see a sent message...",
  "combinations": [
    {
      "goal": "Message Samuel Purnama on LinkedIn",
      "eps_name": "message_samuel_purnama_a1b2c3d4/mobile_chrome",
      "task": {
        "steps": ["Click the 'Sign in with email' link...", "..."]
      },
      "start_url": "https://www.linkedin.com",
      "browser_context": {
        "os": "darwin",
        "viewport": "375x667",
        "cookies_enabled": true
      },
      "success": true,
      "total_steps": 9,
      "runtime_sec": 80.65,
      "total_tokens": 37624,
      "gpt_output": "Found a chat conversation with Samuel Purnama...",
      "wrong_behavior": false,
      "explanation": "The final state matches the expected behavior...",
      "expected_behavior": "You should see a sent message...",
      "device": "mobile",
      "browser": "chrome"
    }
  ]
}
```

**Response (Failed):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "failed",
  "progress": 60,
  "message": "Pipeline failed",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:33:00Z",
  "error": "Failed to locate the message button on Samuel Purnama's profile",
  "episode_name": null,
  "task": null,
  "url": null,
  "steps": null,
  "expected_behavior": null,
  "combinations": null
}
```

## Polling Behavior

### 1. Polling Frequency
- **Interval**: 1 second (1000ms)
- **Immediate**: First poll happens immediately when polling starts
- **Automatic Stop**: Polling stops when status is 'completed' or 'failed'

### 2. Error Handling
- **Network Errors**: Displayed as toast notifications
- **Backend Errors**: Handled gracefully with error messages
- **Cleanup**: Polling stops and test status resets to 'draft' on error

### 3. State Management
- **Test Status**: Updated in real-time based on polling response
- **Progress Display**: Shows percentage and current step in UI
- **Memory Management**: Polling stops are cleaned up automatically

## User Experience

### 1. Visual Feedback
- **Running Badge**: Shows "Running" status with progress info
- **Progress Percentage**: Displays completion percentage
- **Current Step**: Shows what the test is currently doing
- **Toast Notifications**: Brief progress updates

### 2. Real-Time Updates
- **Live Progress**: Users see test progress in real-time
- **Step-by-Step**: Current step is displayed and updated
- **Automatic Completion**: Test results appear automatically when done

## Example Usage Flow

1. **User clicks "Run Test"**
2. **Frontend sends test data to backend**
3. **Backend returns job_id**
4. **Frontend starts polling every 1 second**
5. **Backend returns progress updates**
6. **Frontend displays real-time progress**
7. **Test completes, polling stops**
8. **Results are displayed automatically**

## Benefits

- **Real-Time Feedback**: Users see test progress immediately
- **Better UX**: No need to refresh or wait for completion
- **Transparency**: Users know exactly what the test is doing
- **Efficient**: Automatic cleanup prevents memory leaks
- **Robust**: Handles errors gracefully

## Development Notes

- **Polling Control**: Each test has its own polling instance
- **Cleanup**: Component unmount automatically stops all polling
- **State Sync**: Test status stays in sync with backend state

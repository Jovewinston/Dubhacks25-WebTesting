# Web Testing Pipeline API

A FastAPI backend for running web testing automation across multiple devices and browsers.

## Features

- **Async Pipeline Execution**: Run long-running web testing pipelines in the background
- **Multi-Device/Browser Support**: Test across different devices (mobile/desktop) and browsers (Chrome/Firefox/Safari)
- **Real-time Status Updates**: Track pipeline progress and get results when complete
- **RESTful API**: Clean, documented API endpoints
- **CORS Support**: Ready for frontend integration

## Quick Start

### 1. Install Dependencies

```bash
cd Backend
pip install -r requirements_api.txt
```

### 2. Start the API Server

```bash
python start_api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Start Pipeline
```http
POST /api/v1/run-pipeline
Content-Type: application/json

{
  "url": "https://www.linkedin.com",
  "task": "Message Samuel Purnama on LinkedIn",
  "steps": "1. Login to the page first with the email and password from the accounts list 2. Click on the search bar, 3. Search for 'Samuel Purnama' in the search bar, 6. Click on Samuel Purnama's profile from the drop down, 5. Click the 'Message' button, 7. Type 'Hi' in the message box, 8. Send the message",
  "expected_behavior": "You should see a sent message to Samuel Purnama in your LinkedIn messages, and our chat conversation should have a message called 'Hi'",
  "devices": ["mobile", "desktop"],
  "browsers": ["chrome", "firefox", "safari"]
}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Pipeline started successfully",
  "status": "pending"
}
```

### Check Job Status
```http
GET /api/v1/status/{job_id}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "progress": 50,
  "message": "Running pipeline across devices and browsers...",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": null,
  "result": null,
  "error": null
}
```

### Get Results
```http
GET /api/v1/results/{job_id}
```

**Response:**
```json
{
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
  ],
  "total_combinations": 6,
  "successful_combinations": 5,
  "failed_combinations": 1,
  "total_runtime_sec": 450.2,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### List All Jobs
```http
GET /api/v1/jobs
```

### Delete Job
```http
DELETE /api/v1/jobs/{job_id}
```

## Frontend Integration

### React Example

```javascript
// Start a pipeline
const startPipeline = async (instruction) => {
  const response = await fetch('http://localhost:8000/api/v1/run-pipeline', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(instruction)
  });
  return response.json();
};

// Check status
const checkStatus = async (jobId) => {
  const response = await fetch(`http://localhost:8000/api/v1/status/${jobId}`);
  return response.json();
};

// Get results
const getResults = async (jobId) => {
  const response = await fetch(`http://localhost:8000/api/v1/results/${jobId}`);
  return response.json();
};

// Poll for completion
const pollForCompletion = async (jobId) => {
  const checkStatus = async () => {
    const status = await checkStatus(jobId);
    if (status.status === 'completed') {
      const results = await getResults(jobId);
      return results;
    } else if (status.status === 'failed') {
      throw new Error(status.error);
    } else {
      // Still running, check again in 2 seconds
      setTimeout(checkStatus, 2000);
    }
  };
  return checkStatus();
};
```

## Configuration

The API can be configured by modifying `main.py`:

- **Host**: Change `host="0.0.0.0"` to bind to specific interface
- **Port**: Change `port=8000` to use different port
- **CORS**: Modify `allow_origins` in CORS middleware for production

## Development

### Running in Development Mode

```bash
python start_api.py
```

The server will automatically reload when you make changes to the code.

### Testing

Use the interactive API documentation at http://localhost:8000/docs to test endpoints.

## Production Deployment

For production deployment, consider:

1. **Process Manager**: Use PM2, systemd, or similar
2. **Reverse Proxy**: Use Nginx or Apache
3. **Database**: Add persistent storage for job history
4. **Authentication**: Add API authentication
5. **Monitoring**: Add logging and monitoring
6. **Scaling**: Use multiple workers with a load balancer

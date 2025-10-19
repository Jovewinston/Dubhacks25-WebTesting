# Calculator App with StatSig Integration

This is a dummy calculator website that demonstrates proper StatSig integration using the exact API from the official documentation.

## 🧮 Features

- **Beautiful Calculator UI** - Modern, responsive design
- **Full Calculator Functionality** - Addition, subtraction, multiplication, division
- **StatSig Integration** - Session replay and custom event logging
- **Real-time Event Logging** - See events being captured in real-time
- **Auto-capture** - Automatically captures clicks, scrolls, and interactions

## 🚀 Quick Start

### 1. Start the Calculator Server

```bash
cd dummy_web
python3 server.py
```

The calculator will be available at: http://localhost:8000

### 2. Test StatSig Integration

```bash
# In another terminal
cd dummy_web
python3 test_calculator_statsig.py
```

## 📊 StatSig Integration Details

### **Exact Implementation (matches official docs):**

```html
<!-- CDN Script -->
<script src="https://cdn.jsdelivr.net/npm/@statsig/js-client@3/build/statsig-js-client+session-replay+web-analytics.min.js?apikey=YOUR_CLIENT_KEY"></script>
```

```javascript
// Initialization (exactly as per documentation)
import { StatsigClient } from "@statsig/js-client";
import { runStatsigSessionReplay } from "@statsig/session-replay";
import { runStatsigAutoCapture } from "@statsig/web-analytics";

const client = new StatsigClient(
  sdkKey,
  { userID: "some_user_id" },
  { environment: { tier: "production" } }
);
runStatsigSessionReplay(client);
runStatsigAutoCapture(client);
await client.initializeAsync();

// Event logging
client.logEvent("add_to_cart", "SKU_12345", {
  price: "9.99",
  item_name: "diet_coke_48_pack",
});
await client.flush(); // optional, but will send events immediately
```

### **Custom Events Captured:**

- `app_initialized` - When StatSig connects
- `button_clicked` - Every calculator button press
- `calculation_started` - When calculation begins
- `calculation_completed` - When calculation finishes
- `clear_clicked` - When clear button is pressed
- `delete_clicked` - When delete button is pressed
- `operator_selected` - When operator is selected
- `ui_interaction` - General UI interactions
- `page_loaded` - When page loads
- `page_scrolled` - When user scrolls

## 🎯 What You'll See in StatSig

### **Real-time Events (2-5 minutes):**
- Go to: https://console.statsig.com/analytics
- Look for calculator events
- See event properties and metadata

### **Session Replay (~1 hour):**
- Go to: https://console.statsig.com/session-replay
- Watch full calculator interactions
- See button clicks, calculations, scrolling

## 🔧 Configuration

Make sure your `.env` file contains:
```bash
STATSIG_CLIENT_KEY=your_client_key_here
```

## 🎨 Calculator Features

- **Basic Operations**: +, -, ×, ÷
- **Decimal Support**: Handles decimal numbers
- **Clear Functions**: Clear all (C) and delete last (⌫)
- **Error Handling**: Division by zero protection
- **Responsive Design**: Works on desktop and mobile

## 📱 User Experience

1. **Beautiful UI** - Modern gradient background, clean design
2. **Smooth Animations** - Button hover effects and transitions
3. **Real-time Feedback** - Immediate display updates
4. **Event Logging** - See StatSig events in real-time
5. **Status Indicators** - Visual feedback for StatSig connection

## 🧪 Testing

The test script (`test_calculator_statsig.py`) will:
1. Navigate to the calculator
2. Wait for StatSig to initialize
3. Perform various calculations
4. Test all calculator functions
5. Scroll and interact with the page
6. Verify event logging

## 🎉 Benefits

This calculator app demonstrates:
- **Proper StatSig Integration** - Using exact official API
- **Rich Event Capture** - Detailed interaction logging
- **Session Replay** - Full user journey recording
- **Real-time Analytics** - Immediate event visibility
- **Production-ready** - Clean, maintainable code

Perfect for testing and validating StatSig integration! 🚀

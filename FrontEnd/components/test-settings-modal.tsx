"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { X } from "lucide-react"
import type { JSX } from "react"
import type { Test } from "@/lib/types"

interface TestSettingsModalProps {
  test: Test
  onClose: () => void
  onSave: (test: Test) => void
  onRun: (test: Test) => void
  onDuplicate: (test: Test) => void
  isRunning?: boolean
}

const ChromeLogo = () => (
  <img 
    src="/Google_Chrome_icon_(2011).png" 
    alt="Chrome" 
    className="w-5 h-5"
  />
)

const FirefoxLogo = () => (
  <img 
    src="/Firefox_logo,_2019.png" 
    alt="Firefox" 
    className="w-5 h-5"
  />
)

const SafariLogo = () => (
  <img 
    src="/Safari_browser_logo.svg.png" 
    alt="Safari" 
    className="w-5 h-5"
  />
)

const BROWSER_LOGOS: Record<string, () => JSX.Element> = {
  Chrome: ChromeLogo,
  Firefox: FirefoxLogo,
  Safari: SafariLogo,
}

const BROWSERS = ["Chrome", "Firefox", "Safari"]
const DEVICES = ["Desktop", "Mobile"]

export function TestSettingsModal({ test, onClose, onSave, onRun, onDuplicate, isRunning = false }: TestSettingsModalProps) {
  const [editedTest, setEditedTest] = useState(test)

  const toggleBrowser = (browser: string) => {
    const browsers = editedTest.browsers.includes(browser)
      ? editedTest.browsers.filter((b) => b !== browser)
      : [...editedTest.browsers, browser]
    setEditedTest({ ...editedTest, browsers })
  }

  const toggleDevice = (device: string) => {
    const devices = editedTest.devices.includes(device)
      ? editedTest.devices.filter((d) => d !== device)
      : [...editedTest.devices, device]
    setEditedTest({ ...editedTest, devices })
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-2xl p-6 max-w-4xl w-full shadow-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-2xl font-semibold text-foreground">Test Settings</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="space-y-6">
          <div>
            <Label htmlFor="edit-name">Test Name</Label>
            <Input
              id="edit-name"
              value={editedTest.name}
              onChange={(e) => setEditedTest({ ...editedTest, name: e.target.value })}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="edit-description">Description</Label>
            <Textarea
              id="edit-description"
              value={editedTest.description}
              onChange={(e) => setEditedTest({ ...editedTest, description: e.target.value })}
              className="mt-1"
              rows={3}
            />
          </div>

          <div>
            <Label htmlFor="edit-url">Website URL</Label>
            <Input
              id="edit-url"
              type="url"
              value={editedTest.url}
              onChange={(e) => setEditedTest({ ...editedTest, url: e.target.value })}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="edit-expected-behavior">Expected Behavior</Label>
            <Textarea
              id="edit-expected-behavior"
              value={editedTest.expectedBehavior}
              onChange={(e) => setEditedTest({ ...editedTest, expectedBehavior: e.target.value })}
              className="mt-1"
              rows={3}
            />
          </div>

          <div className="border border-border rounded-lg p-4 space-y-4">
            <div>
              <Label className="text-base font-semibold">Login Credentials (Optional)</Label>
              <p className="text-sm text-muted-foreground mt-1">
                Add credentials if the website requires authentication
              </p>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-username">Username</Label>
                <Input
                  id="edit-username"
                  placeholder="username@example.com"
                  value={editedTest.username || ""}
                  onChange={(e) => setEditedTest({ ...editedTest, username: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="edit-password">Password</Label>
                <Input
                  id="edit-password"
                  type="password"
                  placeholder="••••••••"
                  value={editedTest.password || ""}
                  onChange={(e) => setEditedTest({ ...editedTest, password: e.target.value })}
                  className="mt-1"
                />
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <Label className="mb-3 block">Browsers</Label>
              <div className="space-y-2">
                {BROWSERS.map((browser) => {
                  const BrowserLogo = BROWSER_LOGOS[browser]
                  return (
                    <div key={browser} className="flex items-center gap-2">
                      <Checkbox
                        id={`browser-${browser}`}
                        checked={editedTest.browsers.includes(browser)}
                        onCheckedChange={() => toggleBrowser(browser)}
                      />
                      <Label htmlFor={`browser-${browser}`} className="cursor-pointer flex items-center gap-2">
                        <BrowserLogo />
                        {browser}
                      </Label>
                    </div>
                  )
                })}
              </div>
            </div>

            <div>
              <Label className="mb-3 block">Devices</Label>
              <div className="space-y-2">
                {DEVICES.map((device) => (
                  <div key={device} className="flex items-center gap-2">
                    <Checkbox
                      id={`device-${device}`}
                      checked={editedTest.devices.includes(device)}
                      onCheckedChange={() => toggleDevice(device)}
                    />
                    <Label htmlFor={`device-${device}`} className="cursor-pointer">
                      {device}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-3 pt-4 border-t border-border">
            <Button 
              onClick={() => onRun(editedTest)} 
              disabled={isRunning}
              className="bg-success hover:bg-success/90 text-white disabled:opacity-50"
            >
              {isRunning ? "Running..." : "Run Test"}
            </Button>
            <Button
              onClick={() => onSave(editedTest)}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              Save
            </Button>
            <Button onClick={onClose} variant="ghost">
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { TestSettingsModal } from "@/components/test-settings-modal"
import { TestResultsModal } from "@/components/test-results-modal"
import { Play, Settings, Copy, Trash2, CheckSquare, Square } from "lucide-react"
import { sendTestToBackend, formatTestDataForBackend } from "@/lib/api"
import type { Test, TestHistory, TestResult, TestStep } from "@/lib/types"

const STORAGE_KEY = "tm_dashboard_v0_tests"

export function TestDashboard() {
  const [tests, setTests] = useState<Test[]>([])
  const [newTest, setNewTest] = useState({
    name: "",
    description: "",
    url: "",
    expectedBehavior: "",
    username: "",
    password: "",
  })
  const [selectedTests, setSelectedTests] = useState<Set<string>>(new Set())
  const [settingsModalTest, setSettingsModalTest] = useState<Test | null>(null)
  const [resultsModalTest, setResultsModalTest] = useState<Test | null>(null)
  const [runningTests, setRunningTests] = useState<Set<string>>(new Set())
  const { toast } = useToast()

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      setTests(JSON.parse(stored))
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tests))
  }, [tests])

  const createTest = () => {
    if (!newTest.name.trim()) {
      toast({
        title: "Error",
        description: "Test name is required",
        variant: "destructive",
      })
      return
    }

    if (!newTest.description.trim()) {
      toast({
        title: "Error",
        description: "Description is required",
        variant: "destructive",
      })
      return
    }

    if (!newTest.url.trim()) {
      toast({
        title: "Error",
        description: "Website URL is required",
        variant: "destructive",
      })
      return
    }

    if (!newTest.url.match(/^https?:\/\/.+/)) {
      toast({
        title: "Error",
        description: "Please enter a valid URL (must start with http:// or https://)",
        variant: "destructive",
      })
      return
    }

    if (!newTest.expectedBehavior.trim()) {
      toast({
        title: "Error",
        description: "Expected behavior is required",
        variant: "destructive",
      })
      return
    }

    const test: Test = {
      id: Date.now().toString(),
      name: newTest.name,
      description: newTest.description,
      url: newTest.url,
      expectedBehavior: newTest.expectedBehavior,
      status: "draft",
      createdAt: new Date().toISOString(),
      browsers: ["Chrome"],
      devices: ["Desktop"],
      username: newTest.username,
      password: newTest.password,
    }

    setTests([...tests, test])
    setNewTest({ name: "", description: "", url: "", expectedBehavior: "", username: "", password: "" })
    toast({
      title: "✅ Test created successfully!",
      description: `${test.name} has been added to your tests`,
    })
  }

  const deleteTest = (id: string) => {
    setTests(tests.filter((t) => t.id !== id))
    toast({
      title: "Test deleted",
      description: "The test has been removed",
    })
  }

  const duplicateTest = (test: Test) => {
    const newTest: Test = {
      ...test,
      id: Date.now().toString(),
      name: `${test.name} (Copy)`,
      status: "draft",
      createdAt: new Date().toISOString(),
      results: undefined,
    }
    setTests([...tests, newTest])
    toast({
      title: "Test duplicated",
      description: `${newTest.name} has been created`,
    })
  }

  const runTest = async (test: Test) => {
    const updatedTest = { ...test, status: "running" as const }
    setTests(tests.map((t) => (t.id === test.id ? updatedTest : t)))
    setRunningTests(prev => new Set(prev).add(test.id))

    toast({
      title: "Running test...",
      description: `${test.name} is now running`,
    })

    // Format test data for backend
    const testData = formatTestDataForBackend({
      name: test.name,
      description: test.description,
      url: test.url,
      expectedBehavior: test.expectedBehavior,
      browsers: test.browsers,
      devices: test.devices,
      username: test.username,
      password: test.password,
    })

    // Send test data to backend
    const backendResponse = await sendTestToBackend(testData)
    
    if (!backendResponse.success) {
      toast({
        title: "Error",
        description: backendResponse.error || "Failed to send test to backend",
        variant: "destructive",
      })
      
      // Reset test status to draft on error
      const errorTest = { ...test, status: "draft" as const }
      setTests(tests.map((t) => (t.id === test.id ? errorTest : t)))
      setRunningTests(prev => {
        const newSet = new Set(prev)
        newSet.delete(test.id)
        return newSet
      })
      return
    }

    toast({
      title: "Test sent to backend",
      description: backendResponse.message || "Test is being processed",
    })

    // Simulate test execution (this will be replaced by actual backend response)
    await new Promise((resolve) => setTimeout(resolve, 3000))

    const testSteps = generateTestSteps(test)
    const totalSteps = testSteps.length
    const failedStepsCount = Math.floor(Math.random() * 3) // 0-2 failed steps
    const passedStepsCount = totalSteps - failedStepsCount
    const passRate = Math.floor((passedStepsCount / totalSteps) * 100)

    const stepsWithStatus = testSteps.map((step, index) => ({
      ...step,
      status: (index < totalSteps - failedStepsCount ? "passed" : "failed") as "passed" | "failed",
    }))

    const results: TestResult = {
      totalSteps,
      passed: passedStepsCount,
      failed: failedStepsCount,
      passRate,
      breakdown: test.browsers.flatMap((browser) =>
        test.devices.map((device) => ({
          browser,
          device,
          status: (Math.random() > 0.15 ? "passed" : "failed") as "passed" | "failed",
        })),
      ),
      issues:
        failedStepsCount > 0
          ? [
              "Expected 5 remaining POI elements (places only, not hotels), but found 8",
              "Timeout waiting for element to be visible",
            ]
          : [],
      steps: stepsWithStatus,
    }

    const historyEntry: TestHistory = {
      id: Date.now().toString(),
      runDate: new Date().toISOString(),
      passRate,
      totalSteps,
      passed: passedStepsCount,
      failed: failedStepsCount,
      status: passRate >= 80 ? "passed" : "failed",
      breakdown: results.breakdown,
      issues: results.issues,
      steps: stepsWithStatus,
    }

    const updatedHistory = [historyEntry, ...(test.history || [])].slice(0, 10)

    const completedTest = {
      ...test,
      status: "completed" as const,
      passRate,
      results,
      history: updatedHistory,
    }
    setTests(tests.map((t) => (t.id === test.id ? completedTest : t)))
    setRunningTests(prev => {
      const newSet = new Set(prev)
      newSet.delete(test.id)
      return newSet
    })

    toast({
      title: passRate >= 80 ? "✅ Test completed successfully!" : "⚠️ Test completed with failures",
      description: `Pass rate: ${passRate}%`,
    })
  }

  const runSelectedTests = async () => {
    if (selectedTests.size === 0) return

    for (const testId of selectedTests) {
      const test = tests.find((t) => t.id === testId)
      if (test) {
        await runTest(test)
      }
    }
    setSelectedTests(new Set())
  }

  const toggleTestSelection = (id: string) => {
    const newSelection = new Set(selectedTests)
    if (newSelection.has(id)) {
      newSelection.delete(id)
    } else {
      newSelection.add(id)
    }
    setSelectedTests(newSelection)
  }

  const toggleSelectAll = () => {
    if (selectedTests.size === tests.length) {
      setSelectedTests(new Set())
    } else {
      setSelectedTests(new Set(tests.map((t) => t.id)))
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-sm border-b border-border px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <img 
            src="/WebVoyantLogo.png" 
            alt="WebVoyant Logo" 
            className="w-8 h-8 object-contain"
          />
          <h1 className="text-xl font-semibold text-foreground tracking-tight">WebVoyant</h1>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">Welcome back, Tester</span>
          <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-semibold border border-border">
            TU
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <Card className="p-8 shadow-refined border-border">
          <h2 className="text-lg font-semibold mb-6 text-foreground">Create New Test</h2>
          <div className="space-y-5">
            <div>
              <Label htmlFor="test-name" className="text-sm font-medium text-foreground">
                Test Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="test-name"
                placeholder="e.g. Complete Event Workflow - Mobile"
                value={newTest.name}
                onChange={(e) => setNewTest({ ...newTest, name: e.target.value })}
                className="mt-2 h-10 border-border focus:border-foreground transition-colors"
              />
            </div>
            <div>
              <Label htmlFor="test-description" className="text-sm font-medium text-foreground">
                Description <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="test-description"
                placeholder="Describe what this test does..."
                value={newTest.description}
                onChange={(e) => setNewTest({ ...newTest, description: e.target.value })}
                className="mt-2 border-border focus:border-foreground transition-colors resize-none"
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="test-url" className="text-sm font-medium text-foreground">
                Website URL <span className="text-red-500">*</span>
              </Label>
              <Input
                id="test-url"
                type="url"
                placeholder="https://example.com"
                value={newTest.url}
                onChange={(e) => setNewTest({ ...newTest, url: e.target.value })}
                className="mt-2 h-10 border-border focus:border-foreground transition-colors"
              />
            </div>
            <div>
              <Label htmlFor="test-expected-behavior" className="text-sm font-medium text-foreground">
                Expected Behavior <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="test-expected-behavior"
                placeholder="Describe what should happen when the test runs successfully..."
                value={newTest.expectedBehavior}
                onChange={(e) => setNewTest({ ...newTest, expectedBehavior: e.target.value })}
                className="mt-2 border-border focus:border-foreground transition-colors resize-none"
                rows={3}
              />
            </div>
            <Button
              onClick={createTest}
              className="bg-foreground hover:bg-foreground/90 text-background h-10 px-6 font-medium shadow-refined transition-all hover:shadow-refined-lg"
            >
              Create Test
            </Button>
          </div>
        </Card>

        <Card className="p-8 shadow-refined border-border">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-foreground">Your Tests</h2>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={toggleSelectAll}
                className="flex items-center gap-2 h-9 border-border hover:bg-muted transition-colors bg-transparent"
              >
                {selectedTests.size === tests.length ? (
                  <CheckSquare className="w-4 h-4" />
                ) : (
                  <Square className="w-4 h-4" />
                )}
                Select All
              </Button>
              <Button
                onClick={runSelectedTests}
                disabled={selectedTests.size === 0 || runningTests.size > 0}
                style={{ backgroundColor: selectedTests.size === 0 ? "#F2F2F2" : "#F2F2F2" }}
                className="hover:opacity-90 disabled:text-muted-foreground text-foreground h-9 px-4 font-medium shadow-refined transition-all hover:shadow-refined-lg"
                size="sm"
              >
                <Play className="w-4 h-4 mr-2" />
                {runningTests.size > 0 ? "Running..." : "Run Selected Tests"}
              </Button>
            </div>
          </div>

          {tests.length === 0 ? (
            <div className="text-center py-20 text-muted-foreground">
              <p className="text-5xl mb-4">📋</p>
              <p className="text-base font-medium">No tests yet — create one above!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {tests.map((test) => (
                <Card
                  key={test.id}
                  className="p-5 hover:shadow-refined-lg hover:border-foreground/20 transition-all cursor-pointer border-border bg-card"
                  onClick={() => test.status === "completed" && setResultsModalTest(test)}
                >
                  <div className="flex items-start gap-4">
                    <Checkbox
                      checked={selectedTests.has(test.id)}
                      onCheckedChange={() => toggleTestSelection(test.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-foreground text-balance">{test.name}</h3>
                          {test.description && (
                            <p className="text-sm text-muted-foreground mt-2 text-pretty leading-relaxed">
                              {test.description}
                            </p>
                          )}
                          <p className="text-xs text-muted-foreground mt-3">
                            Created {new Date(test.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {test.status === "draft" && (
                            <Badge variant="secondary" className="font-medium">
                              Draft
                            </Badge>
                          )}
                          {test.status === "running" && (
                            <Badge className="bg-warning/15 text-warning border-warning/30 font-medium">Running</Badge>
                          )}
                          {test.status === "completed" && (
                            <Badge
                              style={{ backgroundColor: "#F2F2F2" }}
                              className={
                                (test.passRate ?? 0) >= 80
                                  ? "text-success border-success/30 font-medium"
                                  : "text-destructive border-destructive/30 font-medium"
                              }
                            >
                              {test.passRate}% Pass
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setSettingsModalTest(test)}
                        title="Settings"
                        className="h-9 w-9 hover:bg-muted transition-colors"
                      >
                        <Settings className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => duplicateTest(test)}
                        title="Duplicate"
                        className="h-9 w-9 hover:bg-muted transition-colors"
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteTest(test.id)}
                        title="Delete"
                        className="h-9 w-9 hover:bg-destructive/10 hover:text-destructive transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Card>
      </main>

      {settingsModalTest && (
        <TestSettingsModal
          test={settingsModalTest}
          onClose={() => setSettingsModalTest(null)}
          onSave={(updatedTest) => {
            setTests(tests.map((t) => (t.id === updatedTest.id ? updatedTest : t)))
            setSettingsModalTest(null)
            toast({
              title: "Test updated",
              description: "Your changes have been saved",
            })
          }}
          onRun={(test) => {
            setSettingsModalTest(null)
            runTest(test)
          }}
          onDuplicate={(test) => {
            duplicateTest(test)
            setSettingsModalTest(null)
          }}
          isRunning={runningTests.has(settingsModalTest.id)}
        />
      )}

      {resultsModalTest && (
        <TestResultsModal
          test={resultsModalTest}
          onClose={() => setResultsModalTest(null)}
          onRunAgain={(test) => {
            setResultsModalTest(null)
            runTest(test)
          }}
        />
      )}
    </div>
  )
}

function generateTestSteps(test: Test): TestStep[] {
  return [
    {
      name: "Before Hooks",
      duration: "656ms",
      status: "passed",
    },
    {
      name: `Navigate to "${test.url || "https://example.com"}"`,
      duration: "338ms",
      status: "passed",
    },
    {
      name: "Wait for timeout",
      duration: "2.0s",
      status: "passed",
    },
    {
      name: "Click getByRole('textbox', { name: 'Email address' })",
      duration: "44ms",
      status: "passed",
      thought: 'I need to click the "Email" input field.',
      action: "click(getByRole='textbox', name='Email address')",
      actionDescription: "Click on the email input field to focus it for data entry.",
    },
    {
      name: `Fill '${test.username || "samuelberry9973@gmail.com"}' getByRole('textbox', { name: 'Email address' })`,
      duration: "5ms",
      status: "passed",
      thought: "I need to enter the email address into the focused field.",
      action: `fill('${test.username || "samuelberry9973@gmail.com"}')`,
      actionDescription: "Type the email address into the email input field.",
    },
    {
      name: "Click getByRole('textbox', { name: 'Password' })",
      duration: "44ms",
      status: "passed",
    },
    {
      name: `Fill '${test.password || "@!Lalala123"}' getByRole('textbox', { name: 'Password' })`,
      duration: "14ms",
      status: "passed",
    },
    {
      name: "Click getByRole('button', { name: 'Continue', exact: true })",
      duration: "647ms",
      status: "passed",
      thought: 'I need to click the "Continue" button to submit the form.',
      action: "click(getByRole='button', name='Continue')",
      actionDescription: "Click the Continue button to proceed with the login process.",
    },
    {
      name: "After Hooks",
      duration: "1.2s",
      status: "passed",
    },
    {
      name: "Worker Cleanup",
      duration: "20ms",
      status: "passed",
    },
  ]
}

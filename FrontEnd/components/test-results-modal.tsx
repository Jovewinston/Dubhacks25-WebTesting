"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { X, ChevronDown, ChevronRight, CheckCircle2, XCircle, Clock, History, Monitor, Smartphone, BarChart3 } from "lucide-react"
import type { Test, TestStep, TestResult, TestHistory, AnalyticsData } from "@/lib/types"

interface TestResultsModalProps {
  test: Test
  onClose: () => void
  onRunAgain: (test: Test) => void
}

export function TestResultsModal({ test, onClose, onRunAgain }: TestResultsModalProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set())
  const [showErrors, setShowErrors] = useState(true)
  const [showSteps, setShowSteps] = useState(true)
  const [showPerformanceMetrics, setShowPerformanceMetrics] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [expandedHistory, setExpandedHistory] = useState<Set<string>>(new Set())
  const [expandedHistorySteps, setExpandedHistorySteps] = useState<Record<string, Set<number>>>({})
  const [selectedCombination, setSelectedCombination] = useState<string>("")

  const results = test.results

  if (!results) return null

  // Initialize selected combination to first combination if not set
  const combinations = results.combinations || []
  const currentCombination = selectedCombination 
    ? combinations.find(combo => `${combo.browser}-${combo.device}` === selectedCombination)
    : combinations[0]
  
  const currentSteps = currentCombination?.steps || results.steps

  const toggleStep = (index: number) => {
    const newExpanded = new Set(expandedSteps)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSteps(newExpanded)
  }

  const toggleHistoryExpansion = (historyId: string) => {
    const newExpanded = new Set(expandedHistory)
    if (newExpanded.has(historyId)) {
      newExpanded.delete(historyId)
    } else {
      newExpanded.add(historyId)
    }
    setExpandedHistory(newExpanded)
  }

  const toggleHistoryStep = (historyId: string, stepIndex: number) => {
    const currentSteps = expandedHistorySteps[historyId] || new Set()
    const newSteps = new Set(currentSteps)
    if (newSteps.has(stepIndex)) {
      newSteps.delete(stepIndex)
    } else {
      newSteps.add(stepIndex)
    }
    setExpandedHistorySteps({ ...expandedHistorySteps, [historyId]: newSteps })
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-2xl p-6 max-w-6xl w-full shadow-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-foreground text-balance">{test.name}</h2>
            <p className="text-sm text-muted-foreground mt-1">{test.url}</p>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4 bg-muted/50">
            <p className="text-sm text-muted-foreground">Total Steps</p>
            <p className="text-2xl font-bold text-foreground">{results.totalSteps}</p>
          </Card>
          <Card className="p-4 bg-success/10">
            <p className="text-sm text-success">Passed</p>
            <p className="text-2xl font-bold text-success">{results.passed}</p>
          </Card>
          <Card className="p-4 bg-destructive/10">
            <p className="text-sm text-destructive">Failed</p>
            <p className="text-2xl font-bold text-destructive">{results.failed}</p>
          </Card>
          <Card className="p-4 bg-primary/10">
            <p className="text-sm text-primary">Pass Rate</p>
            <p className="text-2xl font-bold text-primary">{results.passRate}%</p>
          </Card>
        </div>

        {/* Breakdown by Browser/Device */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-foreground">Test Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {results.breakdown.map((item, index) => (
              <Card key={index} className="p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-foreground">{item.browser}</p>
                    <p className="text-xs text-muted-foreground">{item.device}</p>
                  </div>
                  {item.status === "passed" ? (
                    <CheckCircle2 className="w-5 h-5 text-success" />
                  ) : (
                    <XCircle className="w-5 h-5 text-destructive" />
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Errors Section */}
        {results.issues.length > 0 && (
          <div className="mb-6">
            <button
              onClick={() => setShowErrors(!showErrors)}
              className="flex items-center gap-2 text-lg font-semibold mb-3 text-foreground hover:text-primary transition-colors"
            >
              {showErrors ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
              Errors
            </button>
            {showErrors && (
              <Card className="p-4 bg-destructive/5 border-destructive/20">
                {results.issues.map((issue, index) => (
                  <div key={index} className="mb-2 last:mb-0">
                    <p className="text-sm font-mono text-destructive">{issue}</p>
                  </div>
                ))}
              </Card>
            )}
          </div>
        )}

        {/* Test Steps */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <button
              onClick={() => setShowSteps(!showSteps)}
              className="flex items-center gap-2 text-lg font-semibold text-foreground hover:text-primary transition-colors"
            >
              {showSteps ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
              Test Steps
            </button>
            
            {combinations.length > 1 && showSteps && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Browser/Device:</span>
                <Select value={selectedCombination || `${combinations[0]?.browser}-${combinations[0]?.device}`} onValueChange={setSelectedCombination}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Select combination" />
                  </SelectTrigger>
                  <SelectContent>
                    {combinations.map((combo, index) => (
                      <SelectItem key={`${combo.browser}-${combo.device}`} value={`${combo.browser}-${combo.device}`}>
                        <div className="flex items-center gap-2">
                          {combo.device.toLowerCase() === 'mobile' ? (
                            <Smartphone className="w-4 h-4" />
                          ) : (
                            <Monitor className="w-4 h-4" />
                          )}
                          <span>{combo.browser} • {combo.device}</span>
                          {combo.status === "passed" ? (
                            <CheckCircle2 className="w-4 h-4 text-success ml-auto" />
                          ) : (
                            <XCircle className="w-4 h-4 text-destructive ml-auto" />
                          )}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
          
          {showSteps && (
            <div className="space-y-3">
              {/* Current combination info */}
              {currentCombination && (
                <Card className="p-3 bg-muted/30">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {currentCombination.device.toLowerCase() === 'mobile' ? (
                        <Smartphone className="w-5 h-5 text-muted-foreground" />
                      ) : (
                        <Monitor className="w-5 h-5 text-muted-foreground" />
                      )}
                      <div>
                        <p className="text-sm font-medium text-foreground">
                          {currentCombination.browser} • {currentCombination.device}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {currentCombination.totalSteps} steps • {Math.round(currentCombination.runtimeSec)}s runtime
                        </p>
                        {currentCombination.explanation && (
                          <p className="text-xs text-muted-foreground mt-1 italic">
                            {currentCombination.explanation}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {currentCombination.status === "passed" ? (
                        <CheckCircle2 className="w-5 h-5 text-success" />
                      ) : (
                        <XCircle className="w-5 h-5 text-destructive" />
                      )}
                      <Badge 
                        className={
                          currentCombination.status === "passed" 
                            ? "bg-success/20 text-success border-success/30" 
                            : "bg-destructive/20 text-destructive border-destructive/30"
                        }
                      >
                        {currentCombination.status.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                </Card>
              )}
              
              <div className="space-y-2">
                {currentSteps.map((step, index) => (
                <Card key={index} className="overflow-hidden">
                  <button
                    onClick={() => toggleStep(index)}
                    className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors text-left"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      {step.status === "passed" ? (
                        <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-destructive flex-shrink-0" />
                      )}
                      <span
                        className={`text-sm font-medium truncate ${
                          step.status === "failed" ? "text-destructive" : "text-foreground"
                        }`}
                      >
                        {step.name}
                      </span>
                      {step.status === "failed" && (
                        <Badge className="bg-destructive/20 text-destructive border-destructive/30 text-xs">
                          FAILED
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {step.duration}
                      </span>
                      {expandedSteps.has(index) ? (
                        <ChevronDown className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                      )}
                    </div>
                  </button>

                  {expandedSteps.has(index) && (step.thought || step.action || step.actionDescription) && (
                    <div className="px-4 pb-4 space-y-3 border-t border-border bg-muted/30">
                      {step.thought && (
                        <div className="pt-3">
                          <p className="text-xs font-semibold text-muted-foreground mb-1">Thought</p>
                          <p className="text-sm text-foreground bg-card p-3 rounded-lg">{step.thought}</p>
                        </div>
                      )}
                      {step.action && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-1">Action</p>
                          <code className="text-sm text-primary bg-card p-3 rounded-lg block font-mono">
                            {step.action}
                          </code>
                        </div>
                      )}
                      {step.actionDescription && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-1">Action Description</p>
                          <p className="text-sm text-foreground bg-card p-3 rounded-lg">{step.actionDescription}</p>
                        </div>
                      )}
                      {currentCombination?.explanation && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-1">Explanation</p>
                          <p className="text-sm text-foreground bg-card p-3 rounded-lg">{currentCombination.explanation}</p>
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              ))}
              </div>
            </div>
          )}
        </div>

        {/* Performance Metrics Section */}
        <div className="mb-6">
          <button
            onClick={() => setShowPerformanceMetrics(!showPerformanceMetrics)}
            className="flex items-center gap-2 text-lg font-semibold mb-3 text-foreground hover:text-primary transition-colors"
          >
            {showPerformanceMetrics ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
            <BarChart3 className="w-5 h-5" />
            Performance Metrics
          </button>
          {showPerformanceMetrics && (
            <Card className="p-4 bg-muted/30">
              <div className="space-y-4">
                <div className="text-sm text-muted-foreground mb-3">
                  Detailed performance and network metrics for the selected browser/device combination
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Performance Metrics */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-semibold text-foreground">Performance Data</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">load_time_ms</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">dom_interactive_time_ms</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">first_contentful_paint_time_ms</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">redirect_count</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">transfer_bytes</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Network & Location */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-semibold text-foreground">Network & Location</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">effective_connection_type</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">downlink_mbps</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">downlink_kbps</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">city</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">state</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-card rounded border">
                        <span className="text-sm text-muted-foreground">country</span>
                        <span className="text-sm font-mono text-muted-foreground italic">
                          ""
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>

        {test.history && test.history.length > 0 && (
          <div className="mb-6">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center gap-2 text-lg font-semibold mb-3 text-foreground hover:text-primary transition-colors"
            >
              {showHistory ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
              <History className="w-5 h-5" />
              Test History ({test.history.length})
            </button>
            {showHistory && (
              <div className="space-y-3">
                {test.history.map((historyItem) => {
                  const isExpanded = expandedHistory.has(historyItem.id)
                  const historySteps = expandedHistorySteps[historyItem.id] || new Set()
                  return (
                    <Card key={historyItem.id} className="overflow-hidden">
                      <button
                        onClick={() => toggleHistoryExpansion(historyItem.id)}
                        className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-muted-foreground" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-muted-foreground" />
                          )}
                          <div className="text-left">
                            <div className="font-medium text-sm">{new Date(historyItem.runDate).toLocaleString()}</div>
                            <div className="text-xs text-muted-foreground">
                              {historyItem.totalSteps} steps • {historyItem.passed} passed • {historyItem.failed} failed
                            </div>
                          </div>
                        </div>
                        <Badge
                          className={
                            historyItem.passRate >= 80
                              ? "bg-success/20 text-success border-success/30"
                              : "bg-destructive/20 text-destructive border-destructive/30"
                          }
                        >
                          {historyItem.passRate}%
                        </Badge>
                      </button>

                      {isExpanded && (
                        <div className="px-4 pb-4 space-y-4 border-t border-border bg-muted/30">
                          <div className="pt-4">
                            <h4 className="text-sm font-semibold mb-2">Browser & Device Breakdown</h4>
                            <div className="grid grid-cols-2 gap-2">
                              {historyItem.breakdown.map((item, idx) => (
                                <div
                                  key={idx}
                                  className="flex items-center justify-between p-2 bg-card rounded border border-border"
                                >
                                  <span className="text-xs">
                                    {item.browser} • {item.device}
                                  </span>
                                  {item.status === "passed" ? (
                                    <CheckCircle2 className="w-4 h-4 text-success" />
                                  ) : (
                                    <XCircle className="w-4 h-4 text-destructive" />
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>

                          {historyItem.issues.length > 0 && (
                            <div>
                              <h4 className="text-sm font-semibold mb-2 text-destructive">Issues Found</h4>
                              <div className="space-y-1">
                                {historyItem.issues.map((issue, idx) => (
                                  <div
                                    key={idx}
                                    className="text-xs text-muted-foreground bg-destructive/10 p-2 rounded font-mono"
                                  >
                                    {issue}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <div>
                            <h4 className="text-sm font-semibold mb-2">Test Steps</h4>
                            <div className="space-y-2">
                              {historyItem.steps && historyItem.steps.length > 0 ? (
                                historyItem.steps.map((step, stepIndex) => (
                                  <Card key={stepIndex} className="overflow-hidden">
                                    <button
                                      onClick={() => toggleHistoryStep(historyItem.id, stepIndex)}
                                      className="w-full p-3 flex items-center justify-between hover:bg-muted/50 transition-colors text-left"
                                    >
                                      <div className="flex items-center gap-3 flex-1 min-w-0">
                                        {step.status === "passed" ? (
                                          <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                                        ) : (
                                          <XCircle className="w-4 h-4 text-destructive flex-shrink-0" />
                                        )}
                                        <span
                                          className={`text-sm font-medium truncate ${
                                            step.status === "failed" ? "text-destructive" : "text-foreground"
                                          }`}
                                        >
                                          {step.name}
                                        </span>
                                        {step.status === "failed" && (
                                          <Badge className="bg-destructive/20 text-destructive border-destructive/30 text-xs">
                                            FAILED
                                          </Badge>
                                        )}
                                      </div>
                                      <div className="flex items-center gap-3">
                                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                                          <Clock className="w-3 h-3" />
                                          {step.duration}
                                        </span>
                                        {historySteps.has(stepIndex) ? (
                                          <ChevronDown className="w-4 h-4 text-muted-foreground" />
                                        ) : (
                                          <ChevronRight className="w-4 h-4 text-muted-foreground" />
                                        )}
                                      </div>
                                    </button>

                                    {historySteps.has(stepIndex) &&
                                      (step.thought || step.action || step.actionDescription) && (
                                        <div className="px-3 pb-3 space-y-3 border-t border-border bg-card">
                                          {step.thought && (
                                            <div className="pt-3">
                                              <p className="text-xs font-semibold text-muted-foreground mb-1">
                                                Thought
                                              </p>
                                              <p className="text-sm text-foreground bg-muted/30 p-3 rounded-lg">
                                                {step.thought}
                                              </p>
                                            </div>
                                          )}
                                          {step.action && (
                                            <div>
                                              <p className="text-xs font-semibold text-muted-foreground mb-1">Action</p>
                                              <code className="text-sm text-primary bg-muted/30 p-3 rounded-lg block font-mono">
                                                {step.action}
                                              </code>
                                            </div>
                                          )}
                                          {step.actionDescription && (
                                            <div>
                                              <p className="text-xs font-semibold text-muted-foreground mb-1">
                                                Action Description
                                              </p>
                                              <p className="text-sm text-foreground bg-muted/30 p-3 rounded-lg">
                                                {step.actionDescription}
                                              </p>
                                            </div>
                                          )}
                                        </div>
                                      )}
                                  </Card>
                                ))
                              ) : (
                                <p className="text-sm text-muted-foreground italic">No test steps recorded</p>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </Card>
                  )
                })}
              </div>
            )}
          </div>
        )}

        <div className="flex gap-3 pt-4 border-t border-border">
          <Button onClick={() => onRunAgain(test)} className="bg-primary hover:bg-primary/90 text-primary-foreground">
            Run Test Again
          </Button>
          <Button onClick={onClose} variant="outline">
            Close
          </Button>
        </div>
      </div>
    </div>
  )
}

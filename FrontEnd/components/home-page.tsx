"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Play, Zap, Shield, BarChart3, Users, Globe, Smartphone, Monitor, Chrome, Firefox, Safari } from "lucide-react"
import Image from "next/image"

interface HomePageProps {
  onGetStarted: () => void
}

export function HomePage({ onGetStarted }: HomePageProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    setIsVisible(true)
    
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleGetStarted = () => {
    onGetStarted()
  }

  const browserIcons = [
    { name: 'Chrome', icon: Chrome, color: 'text-blue-500' },
    { name: 'Firefox', icon: Firefox, color: 'text-orange-500' },
    { name: 'Safari', icon: Safari, color: 'text-blue-600' },
  ]

  const deviceIcons = [
    { name: 'Desktop', icon: Monitor, color: 'text-gray-600' },
    { name: 'Mobile', icon: Smartphone, color: 'text-purple-500' },
  ]

  const features = [
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Execute tests in seconds with our optimized automation engine"
    },
    {
      icon: Shield,
      title: "Reliable Results",
      description: "Get consistent, accurate test results every time"
    },
    {
      icon: BarChart3,
      title: "Detailed Analytics",
      description: "Comprehensive reports and insights for your testing"
    },
    {
      icon: Users,
      title: "Team Collaboration",
      description: "Share tests and results with your entire team"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background Animation */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-pink-600/10 animate-pulse"></div>
        
        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-blue-200/30 rounded-full animate-bounce delay-100"></div>
        <div className="absolute top-40 right-20 w-16 h-16 bg-purple-200/30 rounded-full animate-bounce delay-300"></div>
        <div className="absolute bottom-40 left-20 w-24 h-24 bg-pink-200/30 rounded-full animate-bounce delay-500"></div>
        
        <div className="container mx-auto px-6 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Side - Logo, Title, Description */}
            <div className={`space-y-8 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              {/* Logo and Title */}
              <div className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Image 
                      src="/WebVoyantLogo.png" 
                      alt="WebVoyant Logo" 
                      width={80} 
                      height={80}
                      className="animate-pulse hover:animate-spin transition-all duration-500"
                    />
                    <div className="absolute -inset-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full opacity-20 animate-ping"></div>
                  </div>
                  <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient">
                    WebVoyant
                  </h1>
                </div>
                
                <div className="space-y-4">
                  <h2 className="text-3xl font-semibold text-gray-800 leading-tight">
                    The Future of Web Testing
                  </h2>
                  <p className="text-xl text-gray-600 leading-relaxed max-w-lg">
                    Automate your web testing with AI-powered precision. Test across multiple browsers and devices with ease, and get detailed insights into your application's performance.
                  </p>
                </div>
              </div>

              {/* Get Started Button */}
              <div className="space-y-4">
                <Button 
                  onClick={handleGetStarted}
                  size="lg"
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 group"
                >
                  <Play className="w-6 h-6 mr-2 group-hover:animate-pulse" />
                  Get Started
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
                
                <p className="text-sm text-gray-500">
                  ✨ No setup required • Start testing in seconds
                </p>
              </div>
            </div>

            {/* Right Side - Browser & Device Icons */}
            <div className={`space-y-8 transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              {/* Browser Icons */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-700 text-center">Supported Browsers</h3>
                <div className="flex justify-center space-x-8">
                  {browserIcons.map((browser, index) => (
                    <div 
                      key={browser.name}
                      className={`group cursor-pointer transition-all duration-300 hover:scale-110 ${browser.color}`}
                      style={{ animationDelay: `${index * 200}ms` }}
                    >
                      <div className="w-16 h-16 bg-white rounded-2xl shadow-lg flex items-center justify-center group-hover:shadow-xl transition-all duration-300">
                        <browser.icon className="w-8 h-8" />
                      </div>
                      <p className="text-sm font-medium text-center mt-2">{browser.name}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Device Icons */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-700 text-center">Test on Any Device</h3>
                <div className="flex justify-center space-x-8">
                  {deviceIcons.map((device, index) => (
                    <div 
                      key={device.name}
                      className={`group cursor-pointer transition-all duration-300 hover:scale-110 ${device.color}`}
                      style={{ animationDelay: `${(index + 3) * 200}ms` }}
                    >
                      <div className="w-16 h-16 bg-white rounded-2xl shadow-lg flex items-center justify-center group-hover:shadow-xl transition-all duration-300">
                        <device.icon className="w-8 h-8" />
                      </div>
                      <p className="text-sm font-medium text-center mt-2">{device.name}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 pt-8">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">99.9%</div>
                  <div className="text-sm text-gray-600">Uptime</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">10k+</div>
                  <div className="text-sm text-gray-600">Tests Run</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-pink-600">50ms</div>
                  <div className="text-sm text-gray-600">Avg Response</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">Why Choose WebVoyant?</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Powerful features designed to make web testing effortless and efficient
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card 
                key={feature.title}
                className="p-6 text-center hover:shadow-xl transition-all duration-300 hover:-translate-y-2 bg-white/80 backdrop-blur-sm border-0"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="test-dashboard" className="py-20 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2">
              Live Demo
            </Badge>
            <h2 className="text-4xl font-bold text-gray-800 mb-4">Try WebVoyant Now</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience the power of automated web testing. Create your first test in minutes.
            </p>
          </div>
          
          <div className="max-w-6xl mx-auto">
            <Card className="p-8 bg-white/90 backdrop-blur-sm shadow-2xl border-0">
              <div className="text-center mb-8">
                <Globe className="w-16 h-16 text-blue-500 mx-auto mb-4" />
                <h3 className="text-2xl font-semibold text-gray-800 mb-2">Test Dashboard</h3>
                <p className="text-gray-600">Create, manage, and run your web tests with our intuitive dashboard</p>
              </div>
              
              {/* This will be replaced with the actual TestDashboard component */}
              <div className="bg-gray-50 rounded-xl p-8 text-center">
                <div className="text-gray-500 mb-4">
                  <Play className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Test Dashboard will load here...</p>
                </div>
                <Button 
                  onClick={handleGetStarted}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  Launch Dashboard
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-gray-900 text-white">
        <div className="container mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-4 mb-6">
            <Image 
              src="/WebVoyantLogo.png" 
              alt="WebVoyant Logo" 
              width={40} 
              height={40}
              className="opacity-80"
            />
            <span className="text-2xl font-bold">WebVoyant</span>
          </div>
          <p className="text-gray-400 mb-4">
            The future of web testing is here. Start your journey today.
          </p>
          <div className="flex justify-center space-x-6 text-sm text-gray-500">
            <span>© 2024 WebVoyant</span>
            <span>•</span>
            <span>Privacy Policy</span>
            <span>•</span>
            <span>Terms of Service</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

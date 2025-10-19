"use client"

import { useState, useEffect } from "react"
import { TestDashboard } from "@/components/test-dashboard"
import { Toaster } from "@/components/ui/toaster"
import { Button } from "@/components/ui/button"
import GradientText from "@/components/ui/gradient-text"
import { ArrowLeft, Play, Zap, Shield, BarChart3, Users, Globe, Monitor, Smartphone, ArrowRight, CheckCircle2 } from "lucide-react"
import Image from "next/image"

export default function Home() {
  const [showDashboard, setShowDashboard] = useState(false)
  const [currentIconIndex, setCurrentIconIndex] = useState(0)

  const icons = [
    { 
      name: 'Chrome', 
      component: () => <img src="/Google_Chrome_icon_(2011).png" alt="Chrome" className="w-12 h-12" />,
      bgColor: 'from-blue-500 to-blue-600'
    },
    { 
      name: 'Safari', 
      component: () => <img src="/Safari_browser_logo.svg.png" alt="Safari" className="w-12 h-12" />,
      bgColor: 'from-blue-600 to-blue-700'
    },
    { 
      name: 'Firefox', 
      component: () => <img src="/Firefox_logo,_2019.png" alt="Firefox" className="w-12 h-12" />,
      bgColor: 'from-orange-500 to-orange-600'
    },
    { 
      name: 'Desktop', 
      component: () => <Monitor className="w-12 h-12 text-white" />,
      bgColor: 'from-gray-600 to-gray-700'
    },
    { 
      name: 'Mobile', 
      component: () => <Smartphone className="w-12 h-12 text-white" />,
      bgColor: 'from-purple-500 to-purple-600'
    }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIconIndex((prevIndex) => (prevIndex + 1) % icons.length)
    }, 2000) // 每2秒切换一个图标

    return () => clearInterval(interval)
  }, [icons.length])

  const handleGetStarted = () => {
    setShowDashboard(true)
  }

  const handleBackToHome = () => {
    setShowDashboard(false)
  }

  if (showDashboard) {
    return (
      <>
        <div className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <Button 
              variant="ghost" 
              onClick={handleBackToHome}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Home</span>
            </Button>
            <h1 className="text-lg font-semibold text-gray-800">WebVoyant Test Dashboard</h1>
            <div></div>
          </div>
        </div>
        <TestDashboard />
        <Toaster />
      </>
    )
  }

  return (
    <>
      <div className="min-h-screen bg-white">
        {/* Premium Header */}
        <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/50 shadow-sm">
          <div className="container mx-auto px-8 py-6 flex justify-between items-center">
            <div className="flex items-center space-x-4 group">
              <div className="relative">
                <Image 
                  src="/WebVoyantLogo.png" 
                  alt="WebVoyant Logo" 
                  width={44} 
                  height={44}
                  className="rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300"
                />
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 bg-clip-text text-transparent tracking-tight">WebVoyant</span>
            </div>
            <div className="flex items-center space-x-6">
              <Button variant="ghost" className="text-slate-600 hover:text-slate-900 hover:bg-slate-100/50 font-medium transition-all duration-300">
                Documentation
              </Button>
              <Button variant="outline" className="border-slate-200 hover:border-slate-300 text-slate-700 hover:text-slate-800 hover:bg-slate-50/80 backdrop-blur-sm font-medium transition-all duration-300 shadow-sm hover:shadow-md">
                Sign In
              </Button>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center bg-white overflow-hidden">
          {/* Futuristic Background Effects */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-50/60 via-white to-blue-50/40"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-100/20 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-purple-100/20 via-transparent to-transparent"></div>
          
          {/* Floating Orbs */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-blue-400/25 to-cyan-400/25 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-purple-400/25 to-pink-400/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-r from-indigo-400/20 to-purple-400/20 rounded-full blur-2xl animate-pulse delay-500"></div>
          <div className="absolute top-1/3 right-1/3 w-48 h-48 bg-gradient-to-r from-pink-400/20 to-rose-400/20 rounded-full blur-2xl animate-pulse delay-300"></div>
          <div className="absolute bottom-1/3 left-1/3 w-48 h-48 bg-gradient-to-r from-cyan-400/20 to-blue-400/20 rounded-full blur-2xl animate-pulse delay-700"></div>
          
          {/* Subtle Grid Pattern */}
          <div className="absolute inset-0 opacity-[0.02] bg-[linear-gradient(90deg,_transparent_0%,_rgba(59,130,246,0.1)_50%,_transparent_100%)] bg-[length:20px_20px]"></div>
          
          <div className="container mx-auto px-8 text-center relative z-10">
            <div className="max-w-5xl mx-auto space-y-12">
              {/* Mobbin-style Cycling Icon with Shadow Stack */}
              <div className="flex justify-center mb-12">
                <div className="relative w-32 h-32">
                  {icons.map((icon, index) => {
                    const isActive = index === currentIconIndex
                    const isNext = index === (currentIconIndex + 1) % icons.length
                    const isPrev = index === (currentIconIndex - 1 + icons.length) % icons.length
                    
                    return (
                      <div 
                        key={icon.name}
                        className={`absolute transition-all duration-700 ease-in-out ${
                          isActive 
                            ? 'opacity-100 scale-100 z-20 top-0 left-0' 
                            : isNext
                            ? 'opacity-60 scale-90 z-10 top-2 left-2'
                            : isPrev
                            ? 'opacity-40 scale-85 z-5 top-4 left-4'
                            : 'opacity-20 scale-80 z-0 top-6 left-6'
                        }`}
                      >
                        <div className={`w-24 h-24 bg-gradient-to-br ${icon.bgColor} rounded-2xl flex items-center justify-center shadow-2xl ${
                          isActive ? 'shadow-blue-500/25' : 'shadow-gray-500/20'
                        }`}>
                          <div className="scale-125">
                            {icon.component()}
                          </div>
                        </div>
                        {/* Shadow layers for depth */}
                        <div className="absolute -inset-2 bg-gray-300 rounded-2xl opacity-20 blur-sm"></div>
                        <div className="absolute -inset-3 bg-gray-400 rounded-2xl opacity-10 blur-md"></div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Main Title with refined typography */}
              <div className="space-y-6">
                <h1 className="text-6xl md:text-7xl font-bold text-gray-900 leading-[1.0] tracking-tight">
                  Discover real-world
                  <br />
                  <GradientText 
                    colors={['#2563eb', '#9333ea', '#db2777', '#2563eb']}
                    animationSpeed={6}
                    className="text-6xl md:text-7xl font-bold leading-[0.9] tracking-tight"
                  >
                    testing automation
                  </GradientText>
                </h1>
                
                <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed font-light">
                  Featuring AI-powered web testing across Chrome, Firefox, Safari — Test on desktop and mobile devices with precision.
                </p>
              </div>

              {/* Premium CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-6 justify-center items-center pt-8">
                <Button 
                  onClick={handleGetStarted}
                  size="lg"
                  className="group relative bg-gradient-to-r from-slate-900 via-gray-900 to-slate-800 hover:from-slate-800 hover:via-gray-800 hover:to-slate-700 text-white px-12 py-6 text-lg font-semibold rounded-2xl shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-500 min-w-[220px] flex items-center space-x-3 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <span className="relative z-10">Get Started</span>
                  <ArrowRight className="w-5 h-5 relative z-10 group-hover:translate-x-1 transition-transform duration-300" />
                </Button>
                
                <Button 
                  variant="outline"
                  size="lg"
                  className="group relative border-2 border-slate-200 hover:border-slate-300 bg-white/80 backdrop-blur-sm text-slate-700 hover:text-slate-800 hover:bg-white px-12 py-6 text-lg font-semibold rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-500 min-w-[220px] flex items-center space-x-3"
                >
                  <Play className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                  <span>Watch Demo</span>
                </Button>
              </div>
              
              {/* Small text below Get Started */}
              <div className="text-center pt-4">
                <p className="text-sm text-gray-500 font-medium">
                  ✨ No setup required • Start testing in seconds
                </p>
              </div>
              
              {/* Features below buttons */}
              <div className="flex flex-col sm:flex-row gap-8 justify-center items-center pt-6">
                <div className="flex items-center space-x-2 text-gray-600">
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  <span className="text-sm font-medium">No setup required</span>
                </div>
                <div className="flex items-center space-x-2 text-gray-600">
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  <span className="text-sm font-medium">Start testing in seconds</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-32 bg-gradient-to-b from-white via-slate-50/30 to-white relative overflow-hidden">
          {/* Futuristic Background Effects */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-50/40 via-white to-blue-50/30"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-100/15 via-transparent to-purple-100/15"></div>
          
          {/* Floating Elements */}
          <div className="absolute top-0 left-1/3 w-80 h-80 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl animate-pulse delay-300"></div>
          <div className="absolute bottom-0 right-1/3 w-80 h-80 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse delay-700"></div>
          <div className="absolute top-1/2 left-1/4 w-64 h-64 bg-gradient-to-r from-emerald-400/15 to-teal-400/15 rounded-full blur-2xl animate-pulse delay-500"></div>
          
          {/* Subtle Pattern Overlay */}
          <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(45deg,_transparent_0%,_rgba(59,130,246,0.1)_50%,_transparent_100%)] bg-[length:30px_30px]"></div>
          
          <div className="container mx-auto px-8 relative z-10">
            <div className="text-center mb-20">
              <div className="flex justify-center mb-8">
                <div className="relative">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl">
                    <Zap className="w-10 h-10 text-white" />
                  </div>
                  <div className="absolute -inset-2 bg-gray-200 rounded-2xl opacity-30"></div>
                </div>
              </div>
              <h2 className="text-5xl font-bold text-gray-900 mb-6 tracking-tight">Why Choose WebVoyant?</h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed font-light">
                Powerful features designed to make web testing effortless and efficient
              </p>
            </div>
            
                   <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                     {/* Feature 1 */}
                     <div className="group relative">
                       <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-teal-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                       <div className="relative bg-white/60 backdrop-blur-sm border border-slate-200/50 rounded-3xl p-8 text-center space-y-6 group-hover:border-slate-300/50 group-hover:shadow-2xl group-hover:shadow-emerald-500/10 transition-all duration-500 group-hover:-translate-y-2">
                         <div className="flex justify-center">
                           <div className="relative">
                             <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl flex items-center justify-center shadow-xl group-hover:shadow-2xl group-hover:scale-110 transition-all duration-500">
                               <Shield className="w-10 h-10 text-white" />
                             </div>
                             <div className="absolute -inset-1 bg-gradient-to-br from-emerald-400/20 to-teal-400/20 rounded-3xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                           </div>
                         </div>
                         <h3 className="text-2xl font-bold text-slate-900 group-hover:text-emerald-700 transition-colors duration-300">Reliable Results</h3>
                         <p className="text-slate-600 leading-relaxed font-light group-hover:text-slate-700 transition-colors duration-300">Get consistent, accurate test results every time with our AI-powered engine</p>
                       </div>
                     </div>

                     {/* Feature 2 */}
                     <div className="group relative">
                       <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                       <div className="relative bg-white/60 backdrop-blur-sm border border-slate-200/50 rounded-3xl p-8 text-center space-y-6 group-hover:border-slate-300/50 group-hover:shadow-2xl group-hover:shadow-blue-500/10 transition-all duration-500 group-hover:-translate-y-2">
                         <div className="flex justify-center">
                           <div className="relative">
                             <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-3xl flex items-center justify-center shadow-xl group-hover:shadow-2xl group-hover:scale-110 transition-all duration-500">
                               <BarChart3 className="w-10 h-10 text-white" />
                             </div>
                             <div className="absolute -inset-1 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-3xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                           </div>
                         </div>
                         <h3 className="text-2xl font-bold text-slate-900 group-hover:text-blue-700 transition-colors duration-300">Detailed Analytics</h3>
                         <p className="text-slate-600 leading-relaxed font-light group-hover:text-slate-700 transition-colors duration-300">Comprehensive reports and insights for your testing performance</p>
                       </div>
                     </div>

                     {/* Feature 3 */}
                     <div className="group relative">
                       <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                       <div className="relative bg-white/60 backdrop-blur-sm border border-slate-200/50 rounded-3xl p-8 text-center space-y-6 group-hover:border-slate-300/50 group-hover:shadow-2xl group-hover:shadow-purple-500/10 transition-all duration-500 group-hover:-translate-y-2">
                         <div className="flex justify-center">
                           <div className="relative">
                             <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-600 rounded-3xl flex items-center justify-center shadow-xl group-hover:shadow-2xl group-hover:scale-110 transition-all duration-500">
                               <Users className="w-10 h-10 text-white" />
                             </div>
                             <div className="absolute -inset-1 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-3xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                           </div>
                         </div>
                         <h3 className="text-2xl font-bold text-slate-900 group-hover:text-purple-700 transition-colors duration-300">Team Collaboration</h3>
                         <p className="text-slate-600 leading-relaxed font-light group-hover:text-slate-700 transition-colors duration-300">Share tests and results with your entire team seamlessly</p>
                       </div>
                     </div>

                     {/* Feature 4 */}
                     <div className="group relative">
                       <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-red-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                       <div className="relative bg-white/60 backdrop-blur-sm border border-slate-200/50 rounded-3xl p-8 text-center space-y-6 group-hover:border-slate-300/50 group-hover:shadow-2xl group-hover:shadow-orange-500/10 transition-all duration-500 group-hover:-translate-y-2">
                         <div className="flex justify-center">
                           <div className="relative">
                             <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-red-600 rounded-3xl flex items-center justify-center shadow-xl group-hover:shadow-2xl group-hover:scale-110 transition-all duration-500">
                               <Globe className="w-10 h-10 text-white" />
                             </div>
                             <div className="absolute -inset-1 bg-gradient-to-br from-orange-400/20 to-red-400/20 rounded-3xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                           </div>
                         </div>
                         <h3 className="text-2xl font-bold text-slate-900 group-hover:text-orange-700 transition-colors duration-300">Cross-Platform</h3>
                         <p className="text-slate-600 leading-relaxed font-light group-hover:text-slate-700 transition-colors duration-300">Test across multiple browsers and devices with ease</p>
                       </div>
                     </div>
                   </div>
          </div>
        </section>


        {/* Premium Footer */}
        <footer className="py-20 bg-gradient-to-t from-slate-50/50 via-white to-white border-t border-slate-200/50 relative overflow-hidden">
          {/* Futuristic Background Effects */}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-50/40 via-white to-white"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-100/10 via-transparent to-purple-100/10"></div>
          
          {/* Floating Elements */}
          <div className="absolute top-0 left-1/4 w-64 h-64 bg-gradient-to-r from-blue-400/15 to-cyan-400/15 rounded-full blur-2xl animate-pulse delay-200"></div>
          <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-gradient-to-r from-purple-400/15 to-pink-400/15 rounded-full blur-2xl animate-pulse delay-600"></div>
          <div className="absolute top-1/2 right-1/3 w-48 h-48 bg-gradient-to-r from-pink-400/10 to-rose-400/10 rounded-full blur-xl animate-pulse delay-400"></div>
          
          {/* Subtle Pattern */}
          <div className="absolute inset-0 opacity-[0.02] bg-[linear-gradient(90deg,_transparent_0%,_rgba(59,130,246,0.1)_50%,_transparent_100%)] bg-[length:25px_25px]"></div>
          
          <div className="container mx-auto px-8 text-center relative z-10">
            <div className="flex items-center justify-center space-x-4 mb-10">
              <div className="relative">
                <Image 
                  src="/WebVoyantLogo.png" 
                  alt="WebVoyant Logo" 
                  width={56} 
                  height={56}
                  className="rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl blur opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <span className="text-4xl font-bold bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 bg-clip-text text-transparent tracking-tight">WebVoyant</span>
            </div>
            <p className="text-slate-600 mb-10 text-xl font-light max-w-3xl mx-auto leading-relaxed">
              The future of web testing is here. Start your journey today.
            </p>
            <div className="flex justify-center space-x-8 text-sm text-slate-500 font-medium">
              <span className="hover:text-slate-700 transition-colors duration-300 cursor-pointer">© 2024 WebVoyant</span>
              <span className="text-slate-300">•</span>
              <span className="hover:text-slate-700 transition-colors duration-300 cursor-pointer">Privacy Policy</span>
              <span className="text-slate-300">•</span>
              <span className="hover:text-slate-700 transition-colors duration-300 cursor-pointer">Terms of Service</span>
            </div>
          </div>
        </footer>
      </div>
      <Toaster />
    </>
  )
}
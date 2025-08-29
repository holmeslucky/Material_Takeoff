import { Outlet, Link, useLocation } from 'react-router-dom'
import { Building2, FileText, Database, Settings, User, Wrench, BookTemplate } from 'lucide-react'

export default function App() {
  const location = useLocation()

  const navigation = [
    { name: 'Projects', href: '/projects', icon: Building2 },
    { name: 'Materials', href: '/materials', icon: Database },
    { name: 'Templates', href: '/templates', icon: BookTemplate },
    { name: 'Labor Rates', href: '/labor', icon: Wrench },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <div className="h-screen bg-gray-950 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="bg-gray-900 border-b border-gray-800 px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo and Company */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Building2 className="w-8 h-8 text-blue-500" />
              <div>
                <h1 className="text-xl font-bold text-white">Capitol Takeoff</h1>
                <p className="text-xs text-gray-400">Professional Steel Estimating</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center gap-1">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User Menu */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-300">Blake Holmes</span>
            <button className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800">
              <User className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>

      {/* Status Bar */}
      <footer className="bg-gray-900 border-t border-gray-800 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center gap-4">
            <span>Capitol Engineering Company</span>
            <span>•</span>
            <span>Phoenix, AZ</span>
            <span>•</span>
            <span className="text-green-400">● Database Connected</span>
          </div>
          <div>
            Version 1.0.0 - Web
          </div>
        </div>
      </footer>
    </div>
  )
}
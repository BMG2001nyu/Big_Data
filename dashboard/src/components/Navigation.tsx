import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Activity, 
  BarChart3, 
  Map, 
  AlertTriangle, 
  Lightbulb, 
  Settings, 
  Bell,
  Search,
  User,
  ChevronDown,
  Menu,
  X
} from 'lucide-react';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity, path: '/' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/analytics' },
    { id: 'heatmap', label: 'Heat Map', icon: Map, path: '/heatmap' },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle, path: '/anomalies' },
    { id: 'insights', label: 'Insights', icon: Lightbulb, path: '/insights' },
  ];

  const handleNavClick = (path: string) => {
    navigate(path);
    setMobileMenuOpen(false);
  };

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <>
      <nav className="navigation">
        <div className="nav-container">
          {/* Logo Section */}
          <div className="nav-logo" onClick={() => navigate('/')}>
            <div className="logo-icon">
              <Activity size={24} strokeWidth={2.5} />
            </div>
            <div className="logo-text">
              <div className="logo-title">NYC Traffic</div>
              <div className="logo-subtitle">Analytics Platform</div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="nav-menu desktop-only">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                  onClick={() => handleNavClick(item.path)}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Right Section */}
          <div className="nav-actions">
            {/* Search */}
            <button 
              className="nav-action-btn"
              onClick={() => setSearchOpen(!searchOpen)}
            >
              <Search size={18} />
            </button>

            {/* Notifications */}
            <button className="nav-action-btn">
              <Bell size={18} />
              <span className="notification-badge">3</span>
            </button>

            {/* Settings */}
            <button className="nav-action-btn desktop-only">
              <Settings size={18} />
            </button>

            {/* User Profile */}
            <div className="nav-profile desktop-only">
              <div className="profile-avatar">
                <User size={18} />
              </div>
              <div className="profile-info">
                <div className="profile-name">Admin User</div>
                <div className="profile-role">Traffic Analyst</div>
              </div>
              <ChevronDown size={16} className="profile-chevron" />
            </div>

            {/* Mobile Menu Toggle */}
            <button 
              className="nav-mobile-toggle mobile-only"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Search Bar Dropdown */}
        {searchOpen && (
          <div className="search-dropdown">
            <div className="search-container">
              <Search size={18} className="search-icon" />
              <input
                type="text"
                placeholder="Search roads, boroughs, or insights..."
                className="search-input"
                autoFocus
              />
              <kbd className="search-kbd">⌘K</kbd>
            </div>
            <div className="search-suggestions">
              <div className="search-category">Quick Access</div>
              <button className="search-suggestion">
                <Map size={16} />
                <span>Manhattan Peak Hours</span>
              </button>
              <button className="search-suggestion">
                <AlertTriangle size={16} />
                <span>Latest Anomalies</span>
              </button>
              <button className="search-suggestion">
                <Lightbulb size={16} />
                <span>Top Recommendations</span>
              </button>
            </div>
          </div>
        )}

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="nav-mobile-menu">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={`nav-mobile-item ${isActive(item.path) ? 'active' : ''}`}
                  onClick={() => handleNavClick(item.path)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </button>
              );
            })}
            <div className="nav-mobile-divider" />
            <button className="nav-mobile-item">
              <Settings size={20} />
              <span>Settings</span>
            </button>
          </div>
        )}
      </nav>

      {/* Spacer to prevent content from going under fixed nav */}
      <div className="nav-spacer" />
    </>
  );
}

export default Navigation;

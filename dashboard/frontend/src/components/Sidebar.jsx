import { useState } from 'react';
import './Sidebar.css';

const Sidebar = () => {
    const [activeItem, setActiveItem] = useState('dashboard');

    const menuItems = [
        { id: 'dashboard', icon: '📊', label: 'Dashboard', badge: null },
        { id: 'threats', icon: '🛡️', label: 'Threats', badge: '12' },
        { id: 'alerts', icon: '🔔', label: 'Alerts', badge: '5' },
        { id: 'analytics', icon: '📈', label: 'Analytics', badge: null },
        { id: 'reports', icon: '📄', label: 'Reports', badge: null },
        { id: 'settings', icon: '⚙️', label: 'Settings', badge: null },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo">
                    <div className="logo-icon gradient-primary">A</div>
                    <div className="logo-text">
                        <h1 className="logo-title">AURA</h1>
                        <p className="logo-subtitle">Security Dashboard</p>
                    </div>
                </div>
            </div>

            <nav className="sidebar-nav">
                {menuItems.map((item) => (
                    <button
                        key={item.id}
                        className={`nav-item ${activeItem === item.id ? 'active' : ''}`}
                        onClick={() => setActiveItem(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                        {item.badge && (
                            <span className="nav-badge badge badge-danger">{item.badge}</span>
                        )}
                    </button>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="user-profile">
                    <div className="user-avatar gradient-purple">
                        <span>AD</span>
                    </div>
                    <div className="user-info">
                        <p className="user-name">Admin User</p>
                        <p className="user-role">Security Analyst</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;

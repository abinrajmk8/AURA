import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
    const location = useLocation();
    const [activeItem, setActiveItem] = useState('dashboard');
    const [pendingReviews, setPendingReviews] = useState(0);

    useEffect(() => {
        // Fetch pending review count
        fetch('http://localhost:5000/api/alerts/stats/review')
            .then(res => res.json())
            .then(data => setPendingReviews(data.pending || 0))
            .catch(err => console.error('Error fetching review stats:', err));
    }, []);

    const menuItems = [
        { id: 'dashboard', icon: '📊', label: 'Dashboard', badge: null, path: '/' },
        { id: 'control', icon: '🎛️', label: 'Control Center', badge: null, path: '/control-center' },
        { id: 'assess', icon: '✓', label: 'Assess', badge: pendingReviews > 0 ? pendingReviews.toString() : null, path: '/assess' },
        { id: 'settings', icon: '⚙️', label: 'Settings', badge: null, path: '/settings' },
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
                    <Link
                        key={item.id}
                        to={item.path}
                        className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                        onClick={() => setActiveItem(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                        {item.badge && (
                            <span className="nav-badge badge badge-danger">{item.badge}</span>
                        )}
                    </Link>
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

import './TopBar.css';

const TopBar = () => {
    return (
        <header className="topbar">
            <div className="topbar-left">
                <h2 className="page-title">Security Dashboard</h2>
                <p className="page-subtitle">Real-time threat monitoring and analytics</p>
            </div>

            <div className="topbar-right">
                <div className="search-box">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        placeholder="Search threats, IPs, domains..."
                        className="search-input"
                    />
                </div>

                <div className="topbar-actions">
                    <button className="action-btn" title="Notifications">
                        <span className="action-icon">🔔</span>
                        <span className="notification-dot"></span>
                    </button>

                    <button className="action-btn" title="Settings">
                        <span className="action-icon">⚙️</span>
                    </button>

                    <div className="status-indicator">
                        <span className="status-dot status-active"></span>
                        <span className="status-text">System Active</span>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default TopBar;

import './StatCard.css';

const StatCard = ({ title, value, change, trend, icon, gradient }) => {
    const trendIcon = trend === 'up' ? '📈' : trend === 'down' ? '📉' : '➡️';
    const trendClass = trend === 'up' ? 'trend-up' : trend === 'down' ? 'trend-down' : 'trend-neutral';

    return (
        <div className="stat-card card">
            <div className="stat-header">
                <div className="stat-info">
                    <p className="stat-title">{title}</p>
                    <h3 className="stat-value">{value}</h3>
                </div>
                <div className={`stat-icon ${gradient}`}>
                    <span>{icon}</span>
                </div>
            </div>

            <div className="stat-footer">
                <span className={`stat-trend ${trendClass}`}>
                    <span className="trend-icon">{trendIcon}</span>
                    <span className="trend-value">{change}</span>
                </span>
                <span className="stat-period">vs last period</span>
            </div>
        </div>
    );
};

export default StatCard;

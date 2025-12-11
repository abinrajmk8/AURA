import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import StatCard from '../components/StatCard';
import Chart from '../components/Chart';
import AlertsPanel from '../components/AlertsPanel';
import ThreatMap from '../components/ThreatMap';
import RecentActivity from '../components/RecentActivity';
import './Dashboard.css';

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalThreats: 0,
        activeAlerts: 0,
        blockedAttacks: 0,
        systemHealth: 0
    });

    const [threatTrend, setThreatTrend] = useState([]);
    const [activityData, setActivityData] = useState([]);

    useEffect(() => {
        // Fetch dashboard data from API
        const fetchDashboardData = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/dashboard');
                const data = await response.json();

                setStats({
                    totalThreats: data.total_threats || 0,
                    activeAlerts: data.active_alerts || 0,
                    blockedAttacks: data.blocked_attacks || 0,
                    systemHealth: data.system_health || 0
                });
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
                // Use mock data if API fails
                setStats({
                    totalThreats: 1247,
                    activeAlerts: 17,
                    blockedAttacks: 892,
                    systemHealth: 98
                });
            }
        };

        // Generate mock chart data
        const generateThreatTrend = () => {
            const data = [];
            for (let i = 0; i < 24; i++) {
                data.push({
                    label: `${i}:00`,
                    value: Math.floor(Math.random() * 100) + 20
                });
            }
            setThreatTrend(data);
        };

        const generateActivityData = () => {
            const data = [];
            const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            days.forEach(day => {
                data.push({
                    label: day,
                    value: Math.floor(Math.random() * 150) + 50
                });
            });
            setActivityData(data);
        };

        fetchDashboardData();
        generateThreatTrend();
        generateActivityData();

        // Refresh data every 30 seconds
        const interval = setInterval(() => {
            fetchDashboardData();
            generateThreatTrend();
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <main className="dashboard-main">
                <TopBar />

                <div className="dashboard-content">
                    {/* Stats Grid */}
                    <section className="stats-grid">
                        <StatCard
                            title="Total Threats Detected"
                            value={stats.totalThreats.toLocaleString()}
                            change="+12.5%"
                            trend="up"
                            icon="🛡️"
                            gradient="gradient-danger"
                        />
                        <StatCard
                            title="Active Alerts"
                            value={stats.activeAlerts}
                            change="-8.2%"
                            trend="down"
                            icon="🔔"
                            gradient="gradient-warning"
                        />
                        <StatCard
                            title="Blocked Attacks"
                            value={stats.blockedAttacks.toLocaleString()}
                            change="+23.1%"
                            trend="up"
                            icon="⚔️"
                            gradient="gradient-success"
                        />
                        <StatCard
                            title="System Health"
                            value={`${stats.systemHealth}%`}
                            change="+2.3%"
                            trend="up"
                            icon="💚"
                            gradient="gradient-info"
                        />
                    </section>

                    {/* Charts Section */}
                    <section className="charts-grid">
                        <div className="chart-large">
                            <Chart
                                title="Threat Detection Trend (24h)"
                                type="line"
                                data={threatTrend}
                            />
                        </div>
                        <div className="chart-medium">
                            <Chart
                                title="Weekly Activity"
                                type="bar"
                                data={activityData}
                            />
                        </div>
                    </section>

                    {/* Main Content Grid */}
                    <section className="content-grid">
                        <div className="content-left">
                            <ThreatMap />
                            <RecentActivity />
                        </div>
                        <div className="content-right">
                            <AlertsPanel />
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;

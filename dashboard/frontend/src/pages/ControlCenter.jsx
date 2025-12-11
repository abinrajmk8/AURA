import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import ServiceCard from '../components/ServiceCard';
import OSINTSearchPanel from '../components/OSINTSearchPanel';
import OSINTResults from '../components/OSINTResults';
import DetectionMonitor from '../components/DetectionMonitor';
import './ControlCenter.css';

const ControlCenter = () => {
    const [osintResults, setOsintResults] = useState(null);
    const [services, setServices] = useState({
        ids: {
            status: 'inactive',
            uptime: '0s',
            lastActivity: 'N/A',
            detectionCount: 0,
            metrics: {}
        },
        osint: {
            status: 'inactive',
            uptime: '0s',
            lastActivity: 'N/A',
            detectionCount: 0,
            metrics: {}
        },
        honeypot: {
            status: 'inactive',
            uptime: '0s',
            lastActivity: 'N/A',
            detectionCount: 0,
            metrics: {}
        }
    });

    // Fetch OSINT results
    useEffect(() => {
        const fetchOsintResults = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/osint/results');
                const data = await response.json();
                setOsintResults(data);
            } catch (error) {
                console.error('Failed to fetch OSINT results:', error);
            }
        };

        fetchOsintResults();
        const interval = setInterval(fetchOsintResults, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);


    const [osintData, setOsintData] = useState({
        activeRules: 5,
        lastScan: '2 hours ago'
    });

    // Fetch service status
    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/status/all');
                const data = await response.json();

                // Helper function to format last enabled time
                const formatLastEnabled = (lastStarted) => {
                    if (!lastStarted) return 'Never';
                    const date = new Date(lastStarted);
                    const now = new Date();
                    const diffMs = now - date;
                    const diffMins = Math.floor(diffMs / 60000);

                    if (diffMins < 60) return `${diffMins}m ago`;
                    const diffHours = Math.floor(diffMins / 60);
                    if (diffHours < 24) return `${diffHours}h ago`;
                    const diffDays = Math.floor(diffHours / 24);
                    return `${diffDays}d ago`;
                };

                // Update services with real data
                setServices({
                    ids: {
                        status: data.ids?.status || 'inactive',
                        uptime: data.ids?.uptime || 'Not running',
                        lastActivity: data.ids?.last_activity || 'N/A',
                        detectionCount: data.ids?.detection_count || 0,
                        metrics: {
                            'Last Enabled': formatLastEnabled(data.ids?.last_started),
                            'PID': data.ids?.pid || 'N/A',
                            'Detections': data.ids?.detection_count || 0
                        }
                    },
                    osint: {
                        status: data.osint?.status || 'inactive',
                        uptime: data.osint?.uptime || 'Not running',
                        lastActivity: data.osint?.last_activity || 'N/A',
                        detectionCount: data.osint?.detection_count || 0,
                        metrics: {
                            'Last Enabled': formatLastEnabled(data.osint?.last_started),
                            'PID': data.osint?.pid || 'N/A',
                            'Threats Found': data.osint?.detection_count || 0
                        }
                    },
                    honeypot: {
                        status: data.honeypot?.status || 'inactive',
                        uptime: data.honeypot?.uptime || 'Not running',
                        lastActivity: data.honeypot?.last_activity || 'N/A',
                        detectionCount: data.honeypot?.detection_count || 0,
                        metrics: {
                            'Last Enabled': formatLastEnabled(data.honeypot?.last_started),
                            'PID': data.honeypot?.pid || 'N/A',
                            'Captures': data.honeypot?.detection_count || 0
                        }
                    }
                });
            } catch (error) {
                console.error('Failed to fetch service status:', error);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 10000); // Refresh every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const handleServiceToggle = async (serviceName, enabled) => {
        console.log(`${enabled ? 'Starting' : 'Stopping'} ${serviceName}...`);

        try {
            const action = enabled ? 'start' : 'stop';
            const response = await fetch(`http://localhost:5000/api/control/${serviceName}/${action}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                // Refresh status after toggle
                const statusResponse = await fetch('http://localhost:5000/api/status/all');
                const data = await statusResponse.json();

                // Update the specific service
                setServices(prev => ({
                    ...prev,
                    [serviceName]: {
                        ...prev[serviceName],
                        status: data[serviceName]?.status || 'inactive',
                        uptime: data[serviceName]?.uptime || '0s'
                    }
                }));
            } else {
                alert(`Failed to ${action} ${serviceName}: ${result.error}`);
                throw new Error(result.error);
            }
        } catch (error) {
            console.error(`Failed to toggle ${serviceName}:`, error);
            throw error;
        }
    };

    const handleServiceRestart = async (serviceName) => {
        console.log(`Restarting ${serviceName}...`);

        try {
            // This will be replaced with real API call
            // await fetch(`http://localhost:5000/api/control/${serviceName}/restart`, {
            //     method: 'POST'
            // });

            alert(`${serviceName} restarted successfully`);
        } catch (error) {
            console.error(`Failed to restart ${serviceName}:`, error);
            throw error;
        }
    };

    const handleOSINTSearch = async (query) => {
        console.log('Searching OSINT for:', query);

        try {
            // This will be replaced with real API call
            // const response = await fetch('http://localhost:5000/api/osint/search', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ query })
            // });
            // const data = await response.json();
            // return data.results;

            // Mock results for now
            return [
                {
                    query: query,
                    threat: true,
                    description: 'IP address found in AbuseIPDB with high threat score',
                    sources: ['AbuseIPDB', 'VirusTotal']
                }
            ];
        } catch (error) {
            console.error('OSINT search failed:', error);
            return [];
        }
    };

    const handleOSINTSchedule = () => {
        console.log('Scheduling OSINT scan...');
        alert('OSINT scan scheduled successfully');
    };

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <main className="dashboard-main">
                <TopBar />

                <div className="control-center-content">
                    <div className="control-center-header">
                        <h1 className="page-title">🎛️ Control Center</h1>
                        <p className="page-description">
                            Manage and monitor all AURA security services from this central hub
                        </p>
                    </div>

                    {/* Service Cards Grid */}
                    <section className="services-grid">
                        <ServiceCard
                            serviceName="IDS"
                            icon="⚔️"
                            status={services.ids.status}
                            uptime={services.ids.uptime}
                            lastActivity={services.ids.lastActivity}
                            detectionCount={services.ids.detectionCount}
                            metrics={services.ids.metrics}
                            onToggle={(enabled) => handleServiceToggle('ids', enabled)}
                            onRestart={() => handleServiceRestart('IDS')}
                        />

                        <ServiceCard
                            serviceName="OSINT Harvester"
                            icon="🔍"
                            status={services.osint.status}
                            uptime={services.osint.uptime}
                            lastActivity={services.osint.lastActivity}
                            detectionCount={services.osint.detectionCount}
                            metrics={services.osint.metrics}
                            onToggle={(enabled) => handleServiceToggle('osint', enabled)}
                            onRestart={() => handleServiceRestart('OSINT')}
                        />

                        <ServiceCard
                            serviceName="Honeypot"
                            icon="🍯"
                            status={services.honeypot.status}
                            uptime={services.honeypot.uptime}
                            lastActivity={services.honeypot.lastActivity}
                            detectionCount={services.honeypot.detectionCount}
                            metrics={services.honeypot.metrics}
                            onToggle={(enabled) => handleServiceToggle('honeypot', enabled)}
                            onRestart={() => handleServiceRestart('Honeypot')}
                        />
                    </section>

                    {/* OSINT Search Panel */}
                    <section className="osint-section">
                        <OSINTSearchPanel
                            onSearch={handleOSINTSearch}
                            onSchedule={handleOSINTSchedule}
                            activeRules={osintData.activeRules}
                            lastScan={osintData.lastScan}
                        />
                        <OSINTResults results={osintResults} />
                    </section>

                    {/* Detection Monitor */}
                    <section className="detection-section">
                        <DetectionMonitor />
                    </section>
                </div>
            </main>
        </div>
    );
};

export default ControlCenter;

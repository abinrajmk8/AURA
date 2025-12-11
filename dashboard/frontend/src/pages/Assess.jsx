import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import './Assess.css';

const Assess = () => {
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, false_positive: 0, total: 0 });
    const [pagination, setPagination] = useState({ page: 1, per_page: 20, total: 0, pages: 0 });
    const [filters, setFilters] = useState({
        status: '',
        severity: '',
        alert_type: '',
        search: ''
    });
    const [selectedAlerts, setSelectedAlerts] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchStats();
        fetchAlerts();
    }, [pagination.page, filters]);

    const fetchStats = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/alerts/stats/assess');
            const data = await response.json();
            setStats(data);
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    };

    const fetchAlerts = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({
                page: pagination.page,
                per_page: pagination.per_page,
                ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
            });

            const response = await fetch(`http://localhost:5000/api/alerts/assess?${params}`);
            const data = await response.json();
            setAlerts(data.alerts || []);
            setPagination(data.pagination || pagination);
        } catch (error) {
            console.error('Error fetching alerts:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAssess = async (alertId, status) => {
        try {
            const response = await fetch(`http://localhost:5000/api/alerts/assess/${alertId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    review_status: status,
                    reviewed_by: 'admin'
                })
            });

            if (response.ok) {
                fetchAlerts();
                fetchStats();
            }
        } catch (error) {
            console.error('Error assessing alert:', error);
        }
    };

    const handleExport = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/alerts/export/assessed');
            const data = await response.json();

            if (data.success) {
                const blob = new Blob([data.data], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `aura_training_data_${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Error exporting data:', error);
        }
    };

    const handleBulkAssess = async (status) => {
        if (selectedAlerts.length === 0) return;

        try {
            const response = await fetch('http://localhost:5000/api/alerts/assess/bulk', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    alert_ids: selectedAlerts,
                    review_status: status,
                    reviewed_by: 'admin'
                })
            });

            if (response.ok) {
                fetchAlerts();
                fetchStats();
                setSelectedAlerts([]);
            }
        } catch (error) {
            console.error('Error bulk assessing:', error);
        }
    };

    const toggleSelectAlert = (id) => {
        setSelectedAlerts(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    const getSeverityClass = (severity) => {
        const severityMap = {
            'CRITICAL': 'critical',
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        };
        return severityMap[severity] || 'medium';
    };

    const getStatusClass = (status) => {
        const statusMap = {
            'pending': 'pending',
            'approved': 'approved',
            'rejected': 'rejected',
            'false_positive': 'false-positive'
        };
        return statusMap[status] || 'pending';
    };

    return (
        <div className="dashboard-layout">
            <Sidebar />
            <div className="dashboard-main">
                <TopBar />
                <div className="assess-page">
                    <div className="page-header">
                        <div className="header-content">
                            <div>
                                <h1>Alert Assessment</h1>
                                <p>Analyze alerts and label them for ML model retraining</p>
                            </div>
                            <button onClick={handleExport} className="btn btn-primary">
                                📥 Export for Training
                            </button>
                        </div>
                    </div>

                    {/* Statistics Cards */}
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-icon gradient-blue">📋</div>
                            <div className="stat-content">
                                <h3>{stats.total}</h3>
                                <p>Total Alerts</p>
                            </div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-icon gradient-orange">⏳</div>
                            <div className="stat-content">
                                <h3>{stats.pending}</h3>
                                <p>Pending Assessment</p>
                            </div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-icon gradient-green">✓</div>
                            <div className="stat-content">
                                <h3>{stats.approved}</h3>
                                <p>Actual Attacks</p>
                            </div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-icon gradient-purple">⚠</div>
                            <div className="stat-content">
                                <h3>{stats.false_positive}</h3>
                                <p>False Positives</p>
                            </div>
                        </div>
                    </div>

                    {/* Filters */}
                    <div className="filters-bar">
                        <input
                            type="text"
                            placeholder="Search by IP or description..."
                            value={filters.search}
                            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                            className="search-input"
                        />
                        <select
                            value={filters.status}
                            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                            className="filter-select"
                        >
                            <option value="">All Status</option>
                            <option value="pending">Pending</option>
                            <option value="approved">Actual Attack</option>
                            <option value="false_positive">False Positive</option>
                            <option value="rejected">Rejected (Ignored)</option>
                        </select>
                        <select
                            value={filters.severity}
                            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                            className="filter-select"
                        >
                            <option value="">All Severity</option>
                            <option value="CRITICAL">Critical</option>
                            <option value="HIGH">High</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="LOW">Low</option>
                        </select>
                    </div>

                    {/* Bulk Actions */}
                    {selectedAlerts.length > 0 && (
                        <div className="bulk-actions">
                            <span>{selectedAlerts.length} selected</span>
                            <button onClick={() => handleBulkAssess('approved')} className="btn btn-success">
                                ✓ Mark as Actual Attack
                            </button>
                            <button onClick={() => handleBulkAssess('false_positive')} className="btn btn-warning">
                                ⚠ Mark as False Positive
                            </button>
                            <button onClick={() => setSelectedAlerts([])} className="btn btn-secondary">
                                Clear Selection
                            </button>
                        </div>
                    )}

                    {/* Alerts Table */}
                    <div className="alerts-table-container">
                        {loading ? (
                            <div className="loading">Loading alerts...</div>
                        ) : (
                            <table className="alerts-table">
                                <thead>
                                    <tr>
                                        <th>
                                            <input
                                                type="checkbox"
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        setSelectedAlerts(alerts.map(a => a.id));
                                                    } else {
                                                        setSelectedAlerts([]);
                                                    }
                                                }}
                                                checked={selectedAlerts.length === alerts.length && alerts.length > 0}
                                            />
                                        </th>
                                        <th>Last Seen</th>
                                        <th>Count</th>
                                        <th>Source IP</th>
                                        <th>Type</th>
                                        <th>Severity</th>
                                        <th>Description</th>
                                        <th>Status</th>
                                        <th>Assessment</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {alerts.map(alert => (
                                        <tr key={alert.id}>
                                            <td>
                                                <input
                                                    type="checkbox"
                                                    checked={selectedAlerts.includes(alert.id)}
                                                    onChange={() => toggleSelectAlert(alert.id)}
                                                />
                                            </td>
                                            <td>{new Date(alert.timestamp).toLocaleString()}</td>
                                            <td>
                                                <span className="badge badge-count">{alert.count || 1}</span>
                                            </td>
                                            <td className="mono">{alert.src_ip}</td>
                                            <td>
                                                <span className="badge badge-type">{alert.alert_type}</span>
                                            </td>
                                            <td>
                                                <span className={`badge badge-${getSeverityClass(alert.severity)}`}>
                                                    {alert.severity}
                                                </span>
                                            </td>
                                            <td className="description-cell">{alert.description}</td>
                                            <td>
                                                <span className={`badge badge-${getStatusClass(alert.review_status)}`}>
                                                    {alert.review_status === 'approved' ? 'Actual Attack' :
                                                        alert.review_status === 'false_positive' ? 'False Positive' :
                                                            alert.review_status.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td>
                                                <div className="action-buttons">
                                                    <button
                                                        onClick={() => handleAssess(alert.id, 'approved')}
                                                        className={`btn btn-sm ${alert.review_status === 'approved' ? 'btn-success' : 'btn-secondary'}`}
                                                        title="Mark as Actual Attack"
                                                    >
                                                        ✓ Attack
                                                    </button>
                                                    <button
                                                        onClick={() => handleAssess(alert.id, 'false_positive')}
                                                        className={`btn btn-sm ${alert.review_status === 'false_positive' ? 'btn-warning' : 'btn-secondary'}`}
                                                        title="Mark as False Positive"
                                                    >
                                                        ⚠ False Positive
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>

                    {/* Pagination */}
                    <div className="pagination">
                        <button
                            onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
                            disabled={pagination.page === 1}
                            className="btn btn-secondary"
                        >
                            Previous
                        </button>
                        <span>
                            Page {pagination.page} of {pagination.pages}
                        </span>
                        <button
                            onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
                            disabled={pagination.page === pagination.pages}
                            className="btn btn-secondary"
                        >
                            Next
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Assess;

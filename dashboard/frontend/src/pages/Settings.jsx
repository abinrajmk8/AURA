import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import './Settings.css';

const Settings = () => {
    const [activeTab, setActiveTab] = useState('system');
    const [settings, setSettings] = useState({
        // System Configuration
        idsThreshold: 0.7,
        honeypotEnabled: true,
        osintEnabled: true,
        mlDetectionEnabled: true,
        autoBlock: true,

        // User Preferences
        notifications: true,
        emailAlerts: false,
        darkMode: true,
        alertSound: false,

        // Service Configuration
        osintInterval: 3600,
        honeypotPort: 22,
        maxAlerts: 1000,
        retentionDays: 30
    });

    const [saved, setSaved] = useState(false);

    const handleChange = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }));
        setSaved(false);
    };

    const handleSave = () => {
        // In a real implementation, this would save to backend
        console.log('Saving settings:', settings);
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    const handleExportSettings = () => {
        const dataStr = JSON.stringify(settings, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `aura_settings_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    const handleImportSettings = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const imported = JSON.parse(e.target.result);
                    setSettings(imported);
                    setSaved(false);
                } catch (error) {
                    alert('Invalid settings file');
                }
            };
            reader.readAsText(file);
        }
    };

    return (
        <div className="dashboard-layout">
            <Sidebar />
            <div className="dashboard-main">
                <TopBar />
                <div className="settings-page">
                    <div className="page-header">
                        <h1>Settings</h1>
                        <p>Configure AURA system preferences and parameters</p>
                    </div>

                    <div className="settings-container">
                        {/* Tabs */}
                        <div className="settings-tabs">
                            <button
                                className={`tab ${activeTab === 'system' ? 'active' : ''}`}
                                onClick={() => setActiveTab('system')}
                            >
                                <span className="tab-icon">⚙️</span>
                                System
                            </button>
                            <button
                                className={`tab ${activeTab === 'preferences' ? 'active' : ''}`}
                                onClick={() => setActiveTab('preferences')}
                            >
                                <span className="tab-icon">👤</span>
                                Preferences
                            </button>
                            <button
                                className={`tab ${activeTab === 'services' ? 'active' : ''}`}
                                onClick={() => setActiveTab('services')}
                            >
                                <span className="tab-icon">🔧</span>
                                Services
                            </button>
                            <button
                                className={`tab ${activeTab === 'data' ? 'active' : ''}`}
                                onClick={() => setActiveTab('data')}
                            >
                                <span className="tab-icon">💾</span>
                                Data
                            </button>
                        </div>

                        {/* Settings Content */}
                        <div className="settings-content">
                            {activeTab === 'system' && (
                                <div className="settings-section">
                                    <h2>System Configuration</h2>
                                    <p className="section-description">
                                        Configure core system detection and response parameters
                                    </p>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>IDS Detection Threshold</label>
                                            <p>Minimum confidence score for ML-based detection (0.0 - 1.0)</p>
                                        </div>
                                        <input
                                            type="number"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            value={settings.idsThreshold}
                                            onChange={(e) => handleChange('idsThreshold', parseFloat(e.target.value))}
                                            className="setting-input"
                                        />
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Honeypot Detection</label>
                                            <p>Enable honeypot-based threat detection</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.honeypotEnabled}
                                                onChange={(e) => handleChange('honeypotEnabled', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>OSINT Integration</label>
                                            <p>Enable OSINT-based threat intelligence</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.osintEnabled}
                                                onChange={(e) => handleChange('osintEnabled', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>ML Detection</label>
                                            <p>Enable machine learning-based anomaly detection</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.mlDetectionEnabled}
                                                onChange={(e) => handleChange('mlDetectionEnabled', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Auto-Block Threats</label>
                                            <p>Automatically block detected threats</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.autoBlock}
                                                onChange={(e) => handleChange('autoBlock', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'preferences' && (
                                <div className="settings-section">
                                    <h2>User Preferences</h2>
                                    <p className="section-description">
                                        Customize your dashboard experience
                                    </p>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Notifications</label>
                                            <p>Show in-app notifications for new alerts</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.notifications}
                                                onChange={(e) => handleChange('notifications', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Email Alerts</label>
                                            <p>Receive email notifications for critical alerts</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.emailAlerts}
                                                onChange={(e) => handleChange('emailAlerts', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Dark Mode</label>
                                            <p>Use dark theme for the dashboard</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.darkMode}
                                                onChange={(e) => handleChange('darkMode', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Alert Sound</label>
                                            <p>Play sound when new alerts are detected</p>
                                        </div>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={settings.alertSound}
                                                onChange={(e) => handleChange('alertSound', e.target.checked)}
                                            />
                                            <span className="toggle-slider"></span>
                                        </label>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'services' && (
                                <div className="settings-section">
                                    <h2>Service Configuration</h2>
                                    <p className="section-description">
                                        Configure service-specific parameters
                                    </p>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>OSINT Update Interval</label>
                                            <p>How often to fetch new threat intelligence (seconds)</p>
                                        </div>
                                        <input
                                            type="number"
                                            min="300"
                                            step="300"
                                            value={settings.osintInterval}
                                            onChange={(e) => handleChange('osintInterval', parseInt(e.target.value))}
                                            className="setting-input"
                                        />
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Honeypot SSH Port</label>
                                            <p>Port number for SSH honeypot service</p>
                                        </div>
                                        <input
                                            type="number"
                                            min="1"
                                            max="65535"
                                            value={settings.honeypotPort}
                                            onChange={(e) => handleChange('honeypotPort', parseInt(e.target.value))}
                                            className="setting-input"
                                        />
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Maximum Alerts</label>
                                            <p>Maximum number of alerts to store in database</p>
                                        </div>
                                        <input
                                            type="number"
                                            min="100"
                                            step="100"
                                            value={settings.maxAlerts}
                                            onChange={(e) => handleChange('maxAlerts', parseInt(e.target.value))}
                                            className="setting-input"
                                        />
                                    </div>

                                    <div className="setting-item">
                                        <div className="setting-info">
                                            <label>Data Retention Period</label>
                                            <p>Number of days to retain alert data</p>
                                        </div>
                                        <input
                                            type="number"
                                            min="7"
                                            step="7"
                                            value={settings.retentionDays}
                                            onChange={(e) => handleChange('retentionDays', parseInt(e.target.value))}
                                            className="setting-input"
                                        />
                                    </div>
                                </div>
                            )}

                            {activeTab === 'data' && (
                                <div className="settings-section">
                                    <h2>Data Management</h2>
                                    <p className="section-description">
                                        Manage system data and backups
                                    </p>

                                    <div className="data-actions">
                                        <div className="data-action-card">
                                            <h3>Export Settings</h3>
                                            <p>Download current configuration as JSON</p>
                                            <button onClick={handleExportSettings} className="btn btn-primary">
                                                📥 Export Settings
                                            </button>
                                        </div>

                                        <div className="data-action-card">
                                            <h3>Import Settings</h3>
                                            <p>Load configuration from JSON file</p>
                                            <label className="btn btn-primary file-upload-btn">
                                                📤 Import Settings
                                                <input
                                                    type="file"
                                                    accept=".json"
                                                    onChange={handleImportSettings}
                                                    style={{ display: 'none' }}
                                                />
                                            </label>
                                        </div>

                                        <div className="data-action-card">
                                            <h3>Database Backup</h3>
                                            <p>Create a backup of the alerts database</p>
                                            <button className="btn btn-secondary">
                                                💾 Backup Database
                                            </button>
                                        </div>

                                        <div className="data-action-card danger">
                                            <h3>Clear Old Alerts</h3>
                                            <p>Remove alerts older than retention period</p>
                                            <button className="btn btn-danger">
                                                🗑️ Clear Old Data
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Save Button */}
                        <div className="settings-footer">
                            {saved && (
                                <span className="save-indicator">✓ Settings saved successfully</span>
                            )}
                            <button onClick={handleSave} className="btn btn-primary btn-lg">
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Settings;

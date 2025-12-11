import { useState } from 'react';
import './OSINTSearchPanel.css';

const OSINTSearchPanel = () => {
    const [keyword, setKeyword] = useState('');
    const [severity, setSeverity] = useState('');
    const [options, setOptions] = useState({
        live: true,
        poc: false,
        correlate: false,
        forecast: false
    });
    const [isSearching, setIsSearching] = useState(false);
    const [lastSearch, setLastSearch] = useState(null);

    const handleSearch = async () => {
        setIsSearching(true);
        try {
            const response = await fetch('http://localhost:5000/api/osint/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    keyword: keyword || undefined,
                    severity: severity || undefined,
                    ...options
                })
            });

            const result = await response.json();

            if (result.success) {
                setLastSearch({
                    time: new Date().toLocaleString(),
                    params: result.parameters
                });
                alert(`OSINT search started!\nPID: ${result.pid}\nKeyword: ${result.parameters.keyword}\nSeverity: ${result.parameters.severity}`);
            } else {
                alert(`Search failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Search failed:', error);
            alert('Failed to start OSINT search');
        } finally {
            setIsSearching(false);
        }
    };

    const handleOptionChange = (option) => {
        setOptions(prev => ({
            ...prev,
            [option]: !prev[option]
        }));
    };

    return (
        <div className="osint-search-panel card">
            <div className="panel-header">
                <div>
                    <h3 className="panel-title">🔍 OSINT Search & Operations</h3>
                    <p className="panel-subtitle">Search CVEs and gather threat intelligence</p>
                </div>
            </div>

            <div className="search-section">
                <div className="search-controls">
                    <div className="input-group">
                        <label>Keyword (optional)</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="e.g., wordpress, iot, sql injection..."
                            value={keyword}
                            onChange={(e) => setKeyword(e.target.value)}
                            disabled={isSearching}
                        />
                    </div>

                    <div className="input-group">
                        <label>Severity Level</label>
                        <select
                            className="form-select"
                            value={severity}
                            onChange={(e) => setSeverity(e.target.value)}
                            disabled={isSearching}
                        >
                            <option value="">All Severities</option>
                            <option value="LOW">Low</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="HIGH">High</option>
                            <option value="CRITICAL">Critical</option>
                        </select>
                    </div>
                </div>

                <div className="options-grid">
                    <label className="option-checkbox">
                        <input
                            type="checkbox"
                            checked={options.live}
                            onChange={() => handleOptionChange('live')}
                            disabled={isSearching}
                        />
                        <span className="option-label">
                            <strong>Live Feeds</strong>
                            <small>Reddit, GitHub, CISA KEV</small>
                        </span>
                    </label>

                    <label className="option-checkbox">
                        <input
                            type="checkbox"
                            checked={options.poc}
                            onChange={() => handleOptionChange('poc')}
                            disabled={isSearching}
                        />
                        <span className="option-label">
                            <strong>PoC Parsing</strong>
                            <small>Parse GitHub PoC repos</small>
                        </span>
                    </label>

                    <label className="option-checkbox">
                        <input
                            type="checkbox"
                            checked={options.correlate}
                            onChange={() => handleOptionChange('correlate')}
                            disabled={isSearching}
                        />
                        <span className="option-label">
                            <strong>Correlation</strong>
                            <small>Correlate PoCs with feeds</small>
                        </span>
                    </label>

                    <label className="option-checkbox">
                        <input
                            type="checkbox"
                            checked={options.forecast}
                            onChange={() => handleOptionChange('forecast')}
                            disabled={isSearching}
                        />
                        <span className="option-label">
                            <strong>AI Forecasting</strong>
                            <small>Threat prediction analysis</small>
                        </span>
                    </label>
                </div>

                <button
                    className="btn btn-primary btn-large"
                    onClick={handleSearch}
                    disabled={isSearching}
                >
                    {isSearching ? (
                        <>
                            <span className="spinner"></span>
                            Running OSINT Harvester...
                        </>
                    ) : (
                        <>🚀 Start OSINT Search</>
                    )}
                </button>

                {lastSearch && (
                    <div className="last-search-info">
                        <div className="info-badge">
                            <span className="info-icon">🕐</span>
                            <span>Last Search: <strong>{lastSearch.time}</strong></span>
                        </div>
                        <div className="info-badge">
                            <span className="info-icon">🔍</span>
                            <span>Keyword: <strong>{lastSearch.params.keyword}</strong></span>
                        </div>
                        <div className="info-badge">
                            <span className="info-icon">⚠️</span>
                            <span>Severity: <strong>{lastSearch.params.severity}</strong></span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default OSINTSearchPanel;

import './OSINTResults.css';

const OSINTResults = ({ results }) => {
    if (!results) return null;

    const totalResults = (results.cves?.length || 0) +
        (results.reddit?.length || 0) +
        (results.github?.length || 0) +
        (results.cisa?.length || 0);

    if (totalResults === 0) {
        return (
            <div className="osint-results card">
                <div className="no-results">
                    <span className="no-results-icon">📭</span>
                    <p>No OSINT results yet. Run a search to see results here.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="osint-results card">
            <div className="results-header">
                <h3 className="results-title">📊 OSINT Search Results</h3>
                <span className="results-count">{totalResults} items found</span>
            </div>

            <div className="results-tabs">
                {results.cves && results.cves.length > 0 && (
                    <div className="result-section">
                        <h4 className="section-title">
                            <span className="section-icon">🔴</span>
                            CVEs ({results.cves.length})
                        </h4>
                        <div className="result-list">
                            {results.cves.slice(0, 10).map((cve, index) => (
                                <div key={index} className="result-item">
                                    <div className="result-header-row">
                                        <span className="cve-id">{cve.cve_id || cve.id}</span>
                                        <span className={`severity-badge severity-${(cve.severity || 'MEDIUM').toLowerCase()}`}>
                                            {cve.severity || 'MEDIUM'}
                                        </span>
                                    </div>
                                    <p className="result-description">
                                        {cve.description || cve.summary || 'No description available'}
                                    </p>
                                    {cve.published && (
                                        <span className="result-meta">Published: {cve.published}</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {results.cisa && results.cisa.length > 0 && (
                    <div className="result-section">
                        <h4 className="section-title">
                            <span className="section-icon">⚠️</span>
                            CISA KEV ({results.cisa.length})
                        </h4>
                        <div className="result-list">
                            {results.cisa.map((vuln, index) => (
                                <div key={index} className="result-item">
                                    <div className="result-header-row">
                                        <span className="cve-id">{vuln.cveID}</span>
                                        <span className="vendor-badge">{vuln.vendorProject}</span>
                                    </div>
                                    <p className="result-description">{vuln.vulnerabilityName}</p>
                                    {vuln.dateAdded && (
                                        <span className="result-meta">Added: {vuln.dateAdded}</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {results.github && results.github.length > 0 && (
                    <div className="result-section">
                        <h4 className="section-title">
                            <span className="section-icon">💻</span>
                            GitHub PoCs ({results.github.length})
                        </h4>
                        <div className="result-list">
                            {results.github.map((repo, index) => (
                                <div key={index} className="result-item">
                                    <div className="result-header-row">
                                        <span className="repo-name">{repo.name}</span>
                                        <span className="stars-badge">⭐ {repo.stars || 0}</span>
                                    </div>
                                    <p className="result-description">{repo.description || 'No description'}</p>
                                    <a href={repo.url} target="_blank" rel="noopener noreferrer" className="result-link">
                                        View on GitHub →
                                    </a>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {results.reddit && results.reddit.length > 0 && (
                    <div className="result-section">
                        <h4 className="section-title">
                            <span className="section-icon">🗨️</span>
                            Reddit Posts ({results.reddit.length})
                        </h4>
                        <div className="result-list">
                            {results.reddit.map((post, index) => (
                                <div key={index} className="result-item">
                                    <div className="result-header-row">
                                        <span className="post-title">{post.title}</span>
                                        <span className="score-badge">↑ {post.score || 0}</span>
                                    </div>
                                    <a href={post.url} target="_blank" rel="noopener noreferrer" className="result-link">
                                        View on Reddit →
                                    </a>
                                    {post.created && (
                                        <span className="result-meta">Posted: {post.created}</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {results.forecast && results.forecast.length > 0 && (
                    <div className="result-section">
                        <h4 className="section-title">
                            <span className="section-icon">🔮</span>
                            AI Threat Forecast ({results.forecast.length})
                        </h4>
                        <div className="result-list">
                            {results.forecast.map((prediction, index) => (
                                <div key={index} className="result-item forecast-item">
                                    <div className="result-header-row">
                                        <span className="cve-id">{prediction.cve_id}</span>
                                        <span className="confidence-badge">
                                            {Math.round((prediction.confidence || 0) * 100)}% confidence
                                        </span>
                                    </div>
                                    <p className="result-description">{prediction.prediction}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default OSINTResults;

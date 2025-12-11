import { useEffect, useRef } from 'react';
import './Chart.css';

const Chart = ({ title, type = 'line', data = [] }) => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        if (data.length === 0) return;

        // Simple line chart implementation
        if (type === 'line') {
            drawLineChart(ctx, width, height, data);
        } else if (type === 'bar') {
            drawBarChart(ctx, width, height, data);
        }
    }, [data, type]);

    const drawLineChart = (ctx, width, height, data) => {
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        const maxValue = Math.max(...data.map(d => d.value));
        const minValue = Math.min(...data.map(d => d.value));
        const range = maxValue - minValue || 1;

        // Draw grid lines
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }

        // Draw line
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        // Create gradient
        const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

        ctx.beginPath();
        data.forEach((point, index) => {
            const x = padding + (chartWidth / (data.length - 1)) * index;
            const normalizedValue = (point.value - minValue) / range;
            const y = height - padding - normalizedValue * chartHeight;

            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();

        // Fill area under line
        ctx.lineTo(width - padding, height - padding);
        ctx.lineTo(padding, height - padding);
        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw points
        ctx.fillStyle = '#6366f1';
        data.forEach((point, index) => {
            const x = padding + (chartWidth / (data.length - 1)) * index;
            const normalizedValue = (point.value - minValue) / range;
            const y = height - padding - normalizedValue * chartHeight;

            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();

            // Outer ring
            ctx.strokeStyle = 'rgba(99, 102, 241, 0.3)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(x, y, 7, 0, Math.PI * 2);
            ctx.stroke();
        });
    };

    const drawBarChart = (ctx, width, height, data) => {
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        const maxValue = Math.max(...data.map(d => d.value));
        const barWidth = chartWidth / data.length - 10;

        data.forEach((point, index) => {
            const x = padding + (chartWidth / data.length) * index + 5;
            const barHeight = (point.value / maxValue) * chartHeight;
            const y = height - padding - barHeight;

            // Create gradient for bar
            const gradient = ctx.createLinearGradient(0, y, 0, height - padding);
            gradient.addColorStop(0, '#8b5cf6');
            gradient.addColorStop(1, '#6366f1');

            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, barWidth, barHeight);

            // Add glow effect
            ctx.shadowColor = 'rgba(99, 102, 241, 0.5)';
            ctx.shadowBlur = 10;
            ctx.fillRect(x, y, barWidth, barHeight);
            ctx.shadowBlur = 0;
        });
    };

    return (
        <div className="chart-container card">
            <div className="panel-header">
                <h3 className="panel-title">{title}</h3>
            </div>
            <div className="chart-wrapper">
                <canvas
                    ref={canvasRef}
                    width={600}
                    height={300}
                    className="chart-canvas"
                />
            </div>
        </div>
    );
};

export default Chart;

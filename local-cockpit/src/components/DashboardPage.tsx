import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import KPICard from './KPICard';

const DashboardPage: React.FC = () => {
    const [metrics, setMetrics] = useState<any>({});

    useEffect(() => {
        const fetchMetrics = async () => {
            const result = await invoke('get_dashboard_metrics', { projectId: 1, iterationId: 1 });
            setMetrics(result);
        };
        fetchMetrics();
    }, []);

    return (
        <div className="dashboard">
            <KPICard title="Total Requirements" value={metrics.total_requirements} />
            <KPICard title="Accepted" value={metrics.accepted_count} />
            <KPICard title="Clarification Needed" value={metrics.clarification_needed_count} />
            <KPICard title="Rejected" value={metrics.rejected_count} />
        </div>
    );
};

export default DashboardPage;

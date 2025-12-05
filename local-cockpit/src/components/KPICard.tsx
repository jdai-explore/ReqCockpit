import React from 'react';

interface KPICardProps {
    title: string;
    value: number;
}

const KPICard: React.FC<KPICardProps> = ({ title, value }) => {
    return (
        <div className="kpi-card">
            <h3>{title}</h3>
            <p>{value}</p>
        </div>
    );
};

export default KPICard;

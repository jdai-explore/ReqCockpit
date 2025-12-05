import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { invoke } from '@tauri-apps/api/tauri';

const SupplierComparisonChart: React.FC = () => {
    const [data, setData] = useState<any[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            const result = await invoke('get_supplier_comparison_data', { projectId: 1, iterationId: 1 });
            setData(result as any[]);
        };
        fetchData();
    }, []);

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart
                layout="vertical"
                data={data}
                margin={{
                    top: 20, right: 30, left: 20, bottom: 5,
                }}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" />
                <Tooltip />
                <Legend />
                <Bar dataKey="Accepted" stackId="a" fill="#82ca9d" />
                <Bar dataKey="Clarification" stackId="a" fill="#8884d8" />
                <Bar dataKey="Rejected" stackId="a" fill="#ffc658" />
            </BarChart>
        </ResponsiveContainer>
    );
};

export default SupplierComparisonChart;

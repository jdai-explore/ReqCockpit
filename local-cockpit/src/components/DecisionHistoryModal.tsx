import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface DecisionHistoryModalProps {
    isOpen: boolean;
    onClose: () => void;
    requirementId: number;
}

const DecisionHistoryModal: React.FC<DecisionHistoryModalProps> = ({ isOpen, onClose, requirementId }) => {
    const [history, setHistory] = useState<any[]>([]);

    useEffect(() => {
        if (isOpen) {
            const fetchHistory = async () => {
                const result = await invoke('get_decision_history', { masterReqId: requirementId });
                setHistory(result as any[]);
            };
            fetchHistory();
        }
    }, [isOpen, requirementId]);

    if (!isOpen) {
        return null;
    }

    return (
        <div className="modal-backdrop">
            <div className="modal-content">
                <h2>Decision History</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Iteration</th>
                            <th>Date</th>
                            <th>User</th>
                            <th>Decision</th>
                            <th>Note</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map((item, index) => (
                            <tr key={index}>
                                <td>{item.iteration_id}</td>
                                <td>{item.date}</td>
                                <td>{item.user}</td>
                                <td>{item.status}</td>
                                <td>{item.note}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <button onClick={onClose}>Close</button>
            </div>
        </div>
    );
};

export default DecisionHistoryModal;

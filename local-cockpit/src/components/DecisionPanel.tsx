import React, { useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface DecisionPanelProps {
    requirement: any;
    iterationId: number;
}

const DecisionPanel: React.FC<DecisionPanelProps> = ({ requirement, iterationId }) => {
    const [status, setStatus] = useState('');
    const [note, setNote] = useState('');
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        try {
            await invoke('save_decision', {
                masterReqId: requirement.id,
                iterationId: iterationId,
                status: status,
                note: note,
                user: 'CurrentUser' // Replace with actual user management
            });
        } catch (error) {
            console.error("Failed to save decision", error);
        }
        setSaving(false);
    };

    return (
        <div className="decision-panel">
            <h3>Decision for {requirement.reqif_id}</h3>
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="">Select a decision</option>
                <option value="Accepted">Accepted</option>
                <option value="Rejected">Rejected</option>
                <option value="Modified">Modified</option>
                <option value="Deferred">Deferred</option>
            </select>
            <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Action Note..."
            />
            <button onClick={handleSave} disabled={saving}>
                {saving ? 'Saving...' : 'Save Decision'}
            </button>
        </div>
    );
};

export default DecisionPanel;

import React, { useState } from 'react';

interface IterationDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (iterationId: string) => void;
}

const IterationDialog: React.FC<IterationDialogProps> = ({ isOpen, onClose, onSubmit }) => {
    const [iterationId, setIterationId] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = () => {
        // Basic validation, more robust validation can be added
        if (!iterationId.match(/^I-\d{3}_.+$/)) {
            setError('Invalid format. Must be I-XXX_Description');
            return;
        }
        onSubmit(iterationId);
        onClose();
    };

    if (!isOpen) {
        return null;
    }

    return (
        <div className="modal-backdrop">
            <div className="modal-content">
                <h2>Set Iteration ID</h2>
                <input
                    type="text"
                    value={iterationId}
                    onChange={(e) => {
                        setIterationId(e.target.value);
                        setError('');
                    }}
                    placeholder="e.g., I-001_Initial_Feedback"
                />
                {error && <p className="error">{error}</p>}
                <button onClick={handleSubmit}>Submit</button>
                <button onClick={onClose}>Cancel</button>
            </div>
        </div>
    );
};

export default IterationDialog;

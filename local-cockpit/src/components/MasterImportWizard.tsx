import React, { useState } from 'react';
import { open } from '@tauri-apps/api/dialog';
import { invoke } from '@tauri-apps/api/tauri';

const MasterImportWizard: React.FC = () => {
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [importing, setImporting] = useState(false);
    const [importSummary, setImportSummary] = useState<string | null>(null);

    const handleFileSelect = async () => {
        const file = await open({
            multiple: false,
            filters: [{ name: 'ReqIF Files', extensions: ['reqif', 'reqifz'] }]
        });
        if (typeof file === 'string') {
            setSelectedFile(file);
        }
    };

    const handleImport = async () => {
        if (!selectedFile) return;

        setImporting(true);
        try {
            const result = await invoke('import_master_spec', { projectId: 1, filePath: selectedFile });
            setImportSummary(`Successfully imported ${result} requirements.`);
        } catch (error) {
            setImportSummary(`Error importing file: ${error}`);
        }
        setImporting(false);
    };

    return (
        <div>
            <h2>Import Master Specification</h2>
            <button onClick={handleFileSelect}>Select File</button>
            {selectedFile && <p>Selected file: {selectedFile}</p>}
            <button onClick={handleImport} disabled={!selectedFile || importing}>
                {importing ? 'Importing...' : 'Import'}
            </button>
            {importSummary && <p>{importSummary}</p>}
        </div>
    );
};

export default MasterImportWizard;

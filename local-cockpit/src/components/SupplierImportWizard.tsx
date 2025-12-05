import React, { useState } from 'react';
import { open } from '@tauri-apps/api/dialog';
import { invoke } from '@tauri-apps/api/tauri';

interface FileWithSupplier {
    path: string;
    supplierName: string;
}

const SupplierImportWizard: React.FC = () => {
    const [files, setFiles] = useState<FileWithSupplier[]>([]);
    const [importing, setImporting] = useState(false);
    const [iterationId, setIterationId] = useState('');
    const [importSummary, setImportSummary] = useState<string | null>(null);

    const handleFileSelect = async () => {
        const selected = await open({
            multiple: true,
            filters: [{ name: 'ReqIF Files', extensions: ['reqif', 'reqifz'] }]
        });
        if (Array.isArray(selected)) {
            setFiles(selected.map(path => ({ path, supplierName: '' })));
        }
    };

    const handleSupplierNameChange = (index: number, name: string) => {
        const newFiles = [...files];
        newFiles[index].supplierName = name;
        setFiles(newFiles);
    };

    const handleImport = async () => {
        if (files.length === 0 || !iterationId) return;

        setImporting(true);
        let totalImported = 0;
        try {
            for (const file of files) {
                const result = await invoke('import_supplier_feedback', {
                    projectId: 1,
                    iterationIdStr: iterationId,
                    supplierName: file.supplierName,
                    filePath: file.path
                });
                totalImported += result as number;
            }
            setImportSummary(`Successfully imported feedback for ${totalImported} requirements.`);
        } catch (error) {
            setImportSummary(`Error importing files: ${error}`);
        }
        setImporting(false);
    };

    return (
        <div>
            <h2>Import Supplier Responses</h2>
            <input
                type="text"
                value={iterationId}
                onChange={(e) => setIterationId(e.target.value)}
                placeholder="Iteration ID (e.g., I-001)"
            />
            <button onClick={handleFileSelect}>Select Files</button>
            {files.map((file, index) => (
                <div key={index}>
                    <p>{file.path}</p>
                    <input
                        type="text"
                        value={file.supplierName}
                        onChange={(e) => handleSupplierNameChange(index, e.target.value)}
                        placeholder="Supplier Name"
                    />
                </div>
            ))}
            <button onClick={handleImport} disabled={files.length === 0 || importing || !iterationId}>
                {importing ? 'Importing...' : 'Import All'}
            </button>
            {importSummary && <p>{importSummary}</p>}
        </div>
    );
};

export default SupplierImportWizard;

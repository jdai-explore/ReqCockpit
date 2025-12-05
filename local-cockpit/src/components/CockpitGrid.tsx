import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { ColDef } from 'ag-grid-community';
import { invoke } from '@tauri-apps/api/tauri';

const CockpitGrid: React.FC = () => {
    const [rowData, setRowData] = useState<any[]>([]);
    const [columnDefs, setColumnDefs] = useState<ColDef[]>([
        { field: 'reqif_id', headerName: 'ReqIF ID', pinned: 'left', filter: true },
        { field: 'text', headerName: 'Master Text', pinned: 'left', resizable: true, wrapText: true, autoHeight: true },
    ]);

    useEffect(() => {
        const fetchData = async () => {
            const data = await invoke('get_cockpit_data', { projectId: 1, iterationId: 1 });
            setRowData(data as any[]);

            if ((data as any[]).length > 0) {
                const firstRow = data[0] as any;
                const supplierNames = Object.keys(firstRow.suppliers);
                const newColumns = supplierNames.flatMap(name => ([
                    { field: `suppliers.${name}.status`, headerName: `${name} Status`, filter: true },
                    { field: `suppliers.${name}.comment`, headerName: `${name} Comment`, resizable: true },
                ]));
                setColumnDefs(prevCols => [...prevCols, ...newColumns]);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="ag-theme-alpine" style={{ height: '100%', width: '100%' }}>
            <AgGridReact
                rowData={rowData}
                columnDefs={columnDefs}
                defaultColDef={{
                    sortable: true,
                    resizable: true,
                }}
            />
        </div>
    );
};

export default CockpitGrid;

import React from 'react';

interface FilterToolbarProps {
    onFilter: (filter: string) => void;
    onStatusFilter: (status: string) => void;
}

const FilterToolbar: React.FC<FilterToolbarProps> = ({ onFilter, onStatusFilter }) => {
    return (
        <div className="filter-toolbar">
            <input
                type="text"
                placeholder="Search..."
                onChange={(e) => onFilter(e.target.value)}
            />
            <select onChange={(e) => onStatusFilter(e.target.value)}>
                <option value="">All Statuses</option>
                <option value="Accepted">Accepted</option>
                <option value="Clarification Needed">Clarification Needed</option>
                <option value="Rejected">Rejected</option>
                <option value="Conflict">Conflict</option>
            </select>
        </div>
    );
};

export default FilterToolbar;

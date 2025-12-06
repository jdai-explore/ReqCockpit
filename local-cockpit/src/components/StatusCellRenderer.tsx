const StatusCellRenderer = (props: any) => {
    const status = props.value;
    let color = 'gray';
    if (status === 'Accepted') color = 'green';
    if (status === 'Clarification Needed') color = 'yellow';
    if (status === 'Rejected') color = 'red';

    const style = {
        backgroundColor: color,
        padding: '5px',
        borderRadius: '5px',
        color: 'white'
    };

    return <span style={style}>{status}</span>;
};

export default StatusCellRenderer;

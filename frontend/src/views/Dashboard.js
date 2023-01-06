import * as React from 'react';
import {DataGrid} from '@mui/x-data-grid';
import {useAuth0, withAuthenticationRequired} from "@auth0/auth0-react";
import Loading from "../components/Loading";
import {useEffect} from "react";

const columns = [
    {field: 'id', headerName: 'ID', width: 8},
    {field: 'author', headerName: 'Author', width: 125},
    {field: 'quote', headerName: 'Quote', sortable: false, flex: 1},
    {field: 'category', headerName: 'Category', width: 125},
    {
        field: 'created_at',
        headerName: 'Created At',
        type: 'dateTime',
        flex: 0.3,
        valueGetter: ({value}) => value && new Date(value),
    },
];

const createRows = (data, i) => {
    return {
        id: i,
        author: data.author,
        quote: data.quote,
        category: data.category,
        created_at: data.created_at
    }
}

function EnhancedTable() {
    const {user} = useAuth0();
    const [rows, setRows] = React.useState([]);

    const getQuotes = async () => {
        const newRows = []
        try {
            const url = `http://127.0.0.1:8083/quotes/${user.email}`;
            const response = await fetch(url);
            const responseData = await response.json()
            responseData.data.forEach((quote, i) => {
                newRows.push(createRows(quote, i + 1))
            })
            setRows(newRows)
        } catch (error) {
            console.log(error)
        }
    };

    useEffect(() => {
        getQuotes()
    }, []);

    return (
        <div style={{height: 400, width: '100%'}}>
            <DataGrid
                autoHeight
                rows={rows}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
            />
        </div>
    );
}

export default withAuthenticationRequired(EnhancedTable, {
    onRedirecting: () => <Loading/>,
});

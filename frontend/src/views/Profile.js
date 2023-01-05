import React, {useEffect, useState} from "react";
import {Col, Container, Row} from "reactstrap";

import Highlight from "../components/Highlight";
import Loading from "../components/Loading";
import {useAuth0, withAuthenticationRequired} from "@auth0/auth0-react";
import {getConfig} from "../config";

export const ProfileComponent = () => {
    const { apiToken, domain } = getConfig();
    const {user} = useAuth0();
    const [state, setState] = useState({
        apiMessage: "",
        error: null,
    });
    const callApi = async () => {
            try {
                const url = `https://${domain}/api/v2/users/${user.sub}?fields=user_metadata&include_fields=true`;
                const response = await fetch(url, {
                    headers: {
                        Authorization: `Bearer ${apiToken}`,
                    },
                });
                const responseData = await response.json()
                setState({
                    ...state,
                    apiMessage: responseData.user_metadata,
                });
            } catch (error) {
                setState({
                    ...state,
                    error: error.error,
                });
            }
    };

    useEffect(() => {
        callApi();
    }, []);

    const newuser = {...user, phone_number: `+1${state.apiMessage.phone_number}`}

    const saveUserToDB = async () => {
        const to_save = {
            username: user.name,
            email: user.email,
            phone_number: `+1${state.apiMessage.phone_number}`,
        }
        console.log(to_save)
        try {
            const url = `http://127.0.0.1:8083/auth/register`;
            const response = await fetch(url, {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(to_save),
            });
            const responseData = await response.json()
            console.log(responseData)
        } catch (error) {
            console.log(error)
        }
    };

    useEffect(() => {
        saveUserToDB();
    }, []);

    return (
        <Container className="mb-5">
            <Row className="align-items-center profile-header mb-5 text-center text-md-left">
                <Col md={2}>
                    <img
                        src={newuser.picture}
                        alt="Profile"
                        className="rounded-circle img-fluid profile-picture mb-3 mb-md-0"
                    />
                </Col>
                <Col md>
                    <h2>{newuser.name}</h2>
                    <p className="lead text-muted">{newuser.email}</p>
                </Col>
            </Row>
            <Row>
                <Highlight>{JSON.stringify(newuser, null, 2)}</Highlight>
            </Row>
        </Container>
    );
};

export default withAuthenticationRequired(ProfileComponent, {
    onRedirecting: () => <Loading/>,
});

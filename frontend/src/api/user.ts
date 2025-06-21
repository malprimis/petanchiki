import axios from "axios";
import { API } from "../main";

export const getCurrentUser = async () => {
    const response = await axios.get(`${API}/users/me`);
    return response.data;
};

export const getUserById = async (userId: string) => {
    const response = await axios.get(`${API}/users/${userId}`);
    return response.data;
};


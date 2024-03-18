import { baseURL } from "../constants"
import { apiRequest } from "../utils/request";

import { 
    AuthorsResponse,
    Author  
} from "./types";

/**
 * @description function to access the /authors view API.
 */
export const apiGetAuthors = async (page: number, size: number, includeHost?: string, excludeHost?:string) 
    : Promise<AuthorsResponse> => 
{   
    let query: string = `page=${page}&size=${size}`;

    if (includeHost) {
        query += `&include_host=${encodeURIComponent(includeHost)}`;
    }
    if (excludeHost) {
        query += `&exclude_host=${encodeURIComponent(excludeHost)}`;
    }
    console.log("includeHost:", includeHost);
    console.log("excludeHost:", excludeHost);
    console.log("apiGetAuthors:", `${baseURL}/api/authors/?${query}`);
    const response = await apiRequest(`${baseURL}/api/authors/?${query}`);
    const data: AuthorsResponse = await response.json();

    return data;
}

/**
 * @description function to access the /authors/id view API.
 * @param id author id to retrieve
 */
export const apiGetAuthor = async (id: string): Promise<Author|null> => {
    const response = await apiRequest(`${baseURL}/api/authors/${id}/`);

    if (response.status === 404) {
        return null;
    }
    
    const data: Author = await response.json();
    return data;
};
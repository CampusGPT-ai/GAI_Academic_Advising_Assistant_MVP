 import { useState, useEffect, useRef } from 'react';
 import axios from 'axios';
 import { BaseUrl } from "./baseURL";

 // Define TypeScript interfaces for the expected data structure
 export interface Outcomes {
    name: string;
    description: string;
}

export interface GraphInsights {
    risks: Outcomes[];  // Define more specific types if the structure of risks is known
    opportunities: Outcomes[];
}

 
 const useGraphData = (
     messageText?: string, 
     user_id?: string,
     ) => {
    const [risks, setRisks] = useState<Outcomes[]>([]);
    const [opportunities, setOpportunities] = useState<Outcomes[]>([]);
    const userQuestionRef = useRef<string | null>(null);
     const [apiUrl, setApiUrl] = useState<string>('');
     const apiUrlRef = useRef<string | null>(null);
 
     const fetchData = async () => {
         try {
 
             const response = await axios.get<GraphInsights>(apiUrl);
             const data = response.data;
 
             // Update state variables with the data from the API
             setRisks(data.risks);
            setOpportunities(data.opportunities);
 
             console.log('Data fetched:', JSON.stringify(data));
         } catch (error) {
             console.error('Failed to fetch data:', error);
         }
 
     };
 
     useEffect(() => {
         if (messageText) {
             if (userQuestionRef.current === messageText) {
                 return;
             }
             else {
                  setApiUrl(`${BaseUrl()}/users/${user_id}/outcomes/${messageText}`)   
                 }
 
                 userQuestionRef.current = messageText;
             }
         }, [messageText, user_id]);
 
     useEffect(() => {
         if (apiUrl && apiUrlRef.current !== apiUrl) {
             apiUrlRef.current = apiUrl;
             console.log('Fetching outcomes from graph...');
             fetchData();
         }
     }, [apiUrl]);
 
     return { risks, opportunities};
 };
 
 export default useGraphData;
 
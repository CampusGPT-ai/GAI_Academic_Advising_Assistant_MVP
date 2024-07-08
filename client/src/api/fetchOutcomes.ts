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
    triggerFetch: boolean,
    setTriggerFetch: (triggerFetch: boolean) => void,
    setErrorMessage: (error: string) => void,
    setIsError: (isError: boolean) => void,
     conversationId?: string, 
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
         } catch (error: any) {
            if (axios.isAxiosError(error)) {
              console.error('API error:', error.response?.status, error.response?.data);
              if (error.response?.status === 401) {
                setIsError(true);
                setErrorMessage('Unauthorized'); // Specific handling for 401 error
              } else {
                // Optional: Handle other specific status codes if necessary
                console.error('Unhandled API error', error.response?.status);
                setIsError(true);
                setErrorMessage('Error fetching outcome data from API.  check the API URL');
              }
            } else {
              // Non-Axios error
              console.error('Error:', error.message);
              setIsError(true);
              setErrorMessage('An unexplained error occurred');
            }
          }
        };
 
     useEffect(() => {
         if (conversationId) {
             if (userQuestionRef.current === conversationId) {
                 return;
             }
             else {
              setApiUrl(`${BaseUrl()}/users/${user_id}/outcomes/${conversationId}`);   
        
                 }
 
                 userQuestionRef.current = conversationId;
             }
          else {
            setOpportunities([]);
            setRisks([]);
          }
         }, [conversationId, user_id]);

     useEffect(() => {
      if ((triggerFetch && apiUrl) || (apiUrl && apiUrlRef.current !== apiUrl)) {
        apiUrlRef.current = apiUrl;
        console.log('Fetching outcomes from graph with url ', apiUrl);
        fetchData();
        setTriggerFetch(false);
      }}, [triggerFetch, apiUrl]);
 
     return { risks, opportunities};
 };
 
 export default useGraphData;
 
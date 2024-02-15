import { Button } from '@mui/material';
import React, { FC } from 'react';

interface ChatCitationProps {
    text?: string;
    path?: string;
    onCitationClicked?: (path: string | undefined) => void;
}

const ChatCitation: FC<ChatCitationProps> = ({
    text,
    path,
    onCitationClicked
}) => {
    let buttonLabel = text && text.length > 3 ? text : path; 
    //console.log(`citation text: ${text}, citation path: ${path}, button label ${buttonLabel}`)
    return (
        <div>
            <Button variant="text" onClick={() => onCitationClicked?.(path)}  sx={{
    whiteSpace: 'normal', // Allows text to wrap
    textAlign: 'left',
    lineHeight: 'normal', // Adjust the line height as necessary
    maxWidth: '100%', // Max width is 100% of the parent container
    overflow: 'hidden', // Hide overflow
    textOverflow: 'ellipsis' // Add ellipsis for overflowing text
  }} >{buttonLabel}</Button>
        </div>
    );
}


ChatCitation.defaultProps = {
    text: "some text",
    path: "wwww.example.com",
  };
  

export default ChatCitation;

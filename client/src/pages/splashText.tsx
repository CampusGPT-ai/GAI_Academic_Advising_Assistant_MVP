import react from 'react';
import { Box } from '@mui/material';

interface SplashTextProps {
  textSwitch: boolean;
}

const SplashText: React.FC<SplashTextProps> = ({ textSwitch }) => {
    if (textSwitch) {
        return (
            <Box>
                <h1>Thank you for your participation. We have met our research quota.</h1>
                <p>
                At the moment we have reached our capacity of 300 research participants. 
                As such we are no longer accepting research participants for our study (aka any data you provide to the system will 
                not be used for research purposes and that you will not receive compensation for participating). 
                However, please feel free to continue to use our system. 
                </p><p>
                Please note that while this application is a prototype, performance may be slow and you should expect to wait up to 
                30 seconds for a response. We appreciate your patience and understanding as we gather feedback.
                </p><p>
                By continuing you acknowledge that you meet our selection criteria, and that you have read the HRP-254 
                Explanation of Research document that was attached to the recruitment announcement, 
                and that if you continue to use the system you are not considered a research participant.
                </p>
            </Box>
        );
    } else {
        return (
            <Box>
                <h1>Thank you for your participation.</h1>
                <p>
                At the moment you are one of our first 300 research participants. 
                This means that if you complete the necessary tasks you will receive compensation for your involvement with the study. 
                For your involvement in the user experience session, we will compensate you with a $20 Amazon voucher which will be 
                awarded within 2 weeks following UCF purchasing approval. To be compensated you must meaningfully participate by
                 asking the system 5 questions and providing answers to the feedback questions. This voucher will be sent your UCF 
                 email address. Failure to meaningfully provide 5 questions to the system, or providing incomplete data for the 
                 embedded questions will result in no compensation being provided. If you have questions, concerns, or complaints: 
                 Dr. Christopher Randles, Assistant Professor, Chemistry Department at (407) 823-5950 or Christopher.Randles@UCF.edu
                </p><p>
                Please note that while this application is a prototype, performance may be slow and you should expect to wait up to 
                30 seconds for a response. We appreciate your patience and understanding as we gather feedback.
                </p><p>
                By continuing you acknowledge that you meet our selection criteria, 
                and that you have read the HRP-254 Explanation of Research document 
                that was attached to the recruitment announcement.
                </p>
            </Box>
        );
    }
    };

    export default SplashText;
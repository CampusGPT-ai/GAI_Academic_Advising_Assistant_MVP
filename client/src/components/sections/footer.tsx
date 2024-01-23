import { Box, Button, Link } from '@mui/material';
import { FC } from 'react';
import logo from "../../assets/images/base_logo_white_background.png";
const Template: FC = () => {
    return (
        <div>
            <Box mt={5} display={'flex'} justifyContent={"center"} width={"100%"}>
                <Link href="https://www.campusevolve.ai/">
                <img src={logo} height={75}>
                    </img>
                    </Link>
                    </Box>
                    
           <Box display={'flex'} justifyContent={"center"} width={"100%"}><Button variant="text" href="https://www.campusevolve.ai/contact">Contact Us</Button></Box> 
        </div>
    );
}

export default Template;

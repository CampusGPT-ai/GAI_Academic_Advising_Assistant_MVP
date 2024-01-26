import { Box, Button, Link, Typography, useTheme } from '@mui/material';
import React, { FC } from 'react';
import logo from "../../assets/images/base_logo_transparent_background.png";
const Template: FC = () => {
    const theme = useTheme()
    return (
        <Box display={"flex"} flexDirection={"column"} alignContent={"center"}>
            <Box mt={5} display={'flex'} justifyContent={"center"} width={"100%"}>
                <Link href="https://www.campusevolve.ai/">
                <img src={logo} height={75}>
                    </img>
                    </Link>
                    </Box>
            <Typography color = {theme.palette.primary.light} textAlign={"center"}>Unlocking Potential | Empowering Minds</Typography>     
           <Box display={'flex'} justifyContent={"center"} width={"100%"}><Button variant="text" href="https://www.campusevolve.ai/contact">Contact Us</Button></Box> 
        </Box>
    );
}

export default Template;

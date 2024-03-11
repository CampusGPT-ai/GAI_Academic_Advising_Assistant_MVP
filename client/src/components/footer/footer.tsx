import { Box, Button, Link, Typography, useTheme } from '@mui/material';
import React, { FC } from 'react';
import logo from "../../assets/images/campusevolve_logo.png";
const Template: FC = () => {
    const theme = useTheme()
    return (
        <Box display={"flex"} flexDirection={"column"} alignContent={"center"} flexGrow={1}>
            <Box mt={5} display={'flex'} justifyContent={"center"} width={"100%"}>
                <Link href="https://www.campusevolve.ai/">
                <img src={logo} height={75} alt='CampusEvolve Logo'>
                    </img>
                    </Link>
                    </Box>

           </Box>
    );
}

export default Template;

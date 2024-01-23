import React, { FC, useState } from 'react';
import { Box, Typography} from '@mui/material';
import ButtonGroupComponent from './profileButtonGroup';

/**
 * Props for the ProfileMenu component.
 */
interface ProfileButtonContainerProps {
    inputList: string[];
    title: string; 
    handleSelectedValues: (list: string[]) => void;

}
const ProfileButtonContainer: FC<ProfileButtonContainerProps> = (
    {inputList, title, handleSelectedValues}
) => {
    return (
        <Box sx={{minWidth:"200px"}}>
            <Box width="100%" sx={{backgroundColor: (theme) => theme.palette.primary.main, mb: 3, p: 1}}>
                <Typography variant="h6" textAlign={"center"} color={(theme) => theme.palette.primary.contrastText}>{title}</Typography>
            </Box>

        <ButtonGroupComponent handleSelectedValues={handleSelectedValues} buttonList={inputList} />
        </Box>

    );
}

ProfileButtonContainer.defaultProps = {
    inputList: ["string1", "string2", "string3"],
    title: "Title",
    handleSelectedValues: (list: string[]) => {console.log(list)}
}

export default ProfileButtonContainer; 
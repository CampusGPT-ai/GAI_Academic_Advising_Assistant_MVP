import AccountCircle from "@mui/icons-material/AccountCircle";
import { FC } from 'react';
import jamal from '../../../assets/images/avatars/jamal.png';

interface ProfilePhotoProps {
    isLoggedIn: boolean;
    imgPath?: string | undefined; 
    height?: string;
    width?: string;
}

/**
 * Profile photo component that displays either the user's profile photo or a default icon if not logged in.
 * @param isLoggedIn - A boolean indicating if the user is logged in.
 * @param imgPath - A string representing the path to the user's profile photo.
 * @param height - A number representing the height of the profile photo.
 * @param width - A number representing the width of the profile photo.
 * @returns A JSX element that displays the user's profile photo or a default icon if not logged in.
 */
const ProfilePhoto: FC<ProfilePhotoProps> = ({ isLoggedIn, imgPath, height, width }) => { // Destructure size from props here


    return (
        <div>
        {isLoggedIn && 
        <img src={imgPath} height={height} width={width} alt="ProfilePhoto" style={{borderRadius: "50%"}}/>
        }
        {!isLoggedIn &&
        <AccountCircle fontSize="large" />}
        </div>
    );
}

ProfilePhoto.defaultProps = {
   height:"60px",
   width:"60px",
   isLoggedIn: true,
   imgPath: jamal,
}

export default ProfilePhoto;
